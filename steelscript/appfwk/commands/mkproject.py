# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os
import shutil
import pkg_resources
from random import choice

from steelscript.commands.steel import BaseCommand, prompt, console, debug, shell


LOCAL_CONTENT = """
from steelscript.appfwk.project.settings import *

PROJECT_ROOT = os.getcwd()
DATAHOME = os.getenv('DATAHOME', PROJECT_ROOT)
DATA_CACHE = os.path.join(DATAHOME, 'data', 'datacache')
INITIAL_DATA = os.path.join(DATAHOME, 'data', 'initial_data')

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
MEDIA_ROOT = DATA_CACHE

# Optionally add additional applications specific to this project instance

LOCAL_APPS = (
    # additional apps can be listed here
)
INSTALLED_APPS += LOCAL_APPS

# Configure database for development or production.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',      # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(DATAHOME, 'project.db'),  # Or path to database file if using sqlite3.
        #'TEST_NAME': os.path.join(DATAHOME, 'test_project.db'),  # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Setup loggers to local directory
LOGGING['handlers']['logfile']['filename'] = os.path.join(DATAHOME, 'logs', 'log.txt')
LOGGING['handlers']['backend-log']['filename'] = os.path.join(DATAHOME, 'logs', 'log-db.txt')

# To enable syslog handling instead of local logging, uncomment next block of LOGGING
# statements

# remove these loggers since the configuration will attempt to write the
# files even if they don't have a logger declared for them
#LOGGING['disable_existing_loggers'] = True
#LOGGING['handlers'].pop('logfile')
#LOGGING['handlers'].pop('backend-log')
#
#LOGGING['loggers'] = {
#    'django.db.backends': {
#        'handlers': ['null'],
#        'level': 'DEBUG',
#        'propagate': False,
#    },
#    '': {
#        'handlers': ['syslog'],
#        'level': 'INFO',
#        'propagate': True,
#    },
#}

"""

LOCAL_FOOTER = """
# Add other settings customizations below, which will be local to this
# machine only, and not recorded by git. This could include database or
# other authentications, LDAP settings, or any other overrides.

# For example LDAP configurations, see the file
# `project/ldap_example.py`.
"""


class Command(BaseCommand):
    help = 'Install new local App Framework project'

    def add_options(self, parser):
        parser.add_option('-d', '--dir', action='store',
                          help='Optional path for new project location')
        parser.add_option('-v', '--verbose', action='store_true',
                          help='Extra verbose output')

    def debug(self, msg, newline=True):
        if self.options.verbose:
            debug(msg, newline=newline)

    def mkdir(self, dirname):
        """Creates directory if it doesn't already exist."""
        if not os.path.exists(dirname):
            os.mkdir(dirname)

    def create_local_settings(self, dirname):
        """Creates local settings configuration."""

        secret = ''.join([
            choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
            for i in range(50)
        ])

        fname = os.path.join(dirname, 'local_settings.py')
        if not os.path.exists(fname):
            console('Writing local settings %s ... ' % fname, newline=False)
            with open(fname, 'w') as f:
                f.write(LOCAL_CONTENT)
                f.write("SECRET_KEY = '%s'\n" % secret)
                f.write(LOCAL_FOOTER)
            console('done.')
        else:
            console('Skipping local settings generation.')

    def link_pkg_dir(self, pkgname, src_path, dest_dir, symlink=True,
                     replace=True):
        """Create a link from a resource within an installed package.

        :param pkgname: name of installed package
        :param src_path: relative path within package to resource
        :param dest_dir: absolute path to location to link/copy
        :param symlink: create a symlink or copy files
        :param replace: if True, will unlink/delete before linking
        """
        src_dir = pkg_resources.resource_filename(pkgname, src_path)

        if os.path.islink(dest_dir) and not os.path.exists(dest_dir):
            self.debug(' unlinking %s ...' % dest_dir)
            os.unlink(dest_dir)

        if os.path.exists(dest_dir):
            if not replace:
                return

            if os.path.islink(dest_dir):
                self.debug(' unlinking %s ...' % dest_dir)
                os.unlink(dest_dir)
            else:
                self.debug(' removing %s ...' % dest_dir)
                shutil.rmtree(dest_dir)

        if symlink:
            self.debug(' linking %s --> %s' % (src_dir, dest_dir))
            os.symlink(src_dir, dest_dir)
        else:
            self.debug(' copying %s --> %s' % (src_dir, dest_dir))
            shutil.copytree(src_dir, dest_dir)

    def create_project_directory(self, dirpath):
        """Creates project directory and copies/links necessary files."""
        console('Creating project directory %s ...' % dirpath)
        self.mkdir(dirpath)

        # link manage.py and media directories
        for p in ('manage.py', 'media', 'thirdparty'):
            self.link_pkg_dir('steelscript.appfwk.apps',
                              '../' + p,
                              os.path.join(dirpath, p))

        # copy and make folders
        self.mkdir(os.path.join(dirpath, 'logs'))

        datapath = os.path.join(dirpath, 'data')
        self.mkdir(datapath)
        self.link_pkg_dir('steelscript.appfwk.apps',
                          '../initial_data',
                          os.path.join(datapath, 'initial_data'),
                          symlink=False)
        self.mkdir(os.path.join(datapath, 'datacache'))

        # copy default reports
        self.link_pkg_dir('steelscript.appfwk.apps',
                          '../reports',
                          os.path.join(dirpath, 'reports'),
                          symlink=False)

    def main(self):
        console('Generating new Application Framework project ...')

        dirpath = self.options.dir
        while not dirpath or not os.path.isabs(dirpath):
            default = os.path.join(os.getcwd(), 'appfwk_project')
            dirpath = prompt('\nEnter absolute path for project files',
                             default=default)

        if os.path.exists(dirpath):
            console('Project directory already exists, aborting.')
            return

        self.create_project_directory(dirpath)
        self.create_local_settings(dirpath)

        console('\n*****\n')
        console('App Framework project created.')
        console("Change to that directory and run "
                "'steel appfwk init' to initialize the project.")