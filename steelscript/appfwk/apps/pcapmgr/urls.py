# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from steelscript.appfwk.apps.pcapmgr.views import PcapFileList, \
    PcapFileDetail


urlpatterns = patterns(
    '',

    url(r'^$',
        PcapFileList.as_view(),
        name='pcapfile-list'),

    url(r'^(?P<pcapfile_id>[0-9]+)/$',
        PcapFileDetail.as_view(),
        name='pcapfile-detail'),

    url(r'^add/$',
        PcapFileDetail.as_view(),
        name='pcapfile-add'),

)

urlpatterns = format_suffix_patterns(urlpatterns)
