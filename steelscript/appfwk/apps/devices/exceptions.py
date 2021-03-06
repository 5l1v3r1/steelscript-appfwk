# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


class DeviceModuleNotFound(Exception):
    """ Exception raised if module for a specified device is not found. """
    pass
