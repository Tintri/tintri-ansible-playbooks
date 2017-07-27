#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2017 Tintri, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


DOCUMENTAION = '''
---
module: update_datetime_config
short_description: Update Tintri VMStore datetime configuration
options:
    server:
    	description: VMStore Server Name or IP
    	required: true
    user:
    	description: User to access VMStore, usually admin
    	required: true
    password:
    	description: Password for user
    	required: true
    timezone:
    	description: Timezone for VMStore
    	required: true
    useNtp:
    	description: If set to true, NTP server will be used. year, month, day and time setting will be 0. If set to false, it is on 'Set the clock manually' mode. 
    	required: false
    	default: true
    ntpPrimary:
    	description: Primary NTP server
    	required: true
    ntpSecondary:
    	description: Secondary NTP server
    	required: false
        default: ""
    year:
    	description: For 'Set the clock manually' mode, set the year
    	required: false
    	default: 0
    month:
    	description: For 'Set the clock manually' mode, set the month
    	required: false
    	default: 0
    day:
    	description: For 'Set the clock manually' mode, set the day
    	required: false
    	default: 0
    time:
    	description: For 'Set the clock manually' mode, set the time
    	required: false
    	default: 0
'''

EXAMPLES = '''
- name: Update VMStore datetime config
  update_datetime_config:
    server: vmstore_servername
    user: admin
    password: xxxx
    timezone: US/Pacific
    useNtp: True
    ntpPrimary: 0.centos.pool.ntp.org
    ntpSecondary: 1.centos.pool.ntp.org
    year: 2017
    month: 06
    day: 16
    time: 03:56:23 PM
  register: result
'''

"""
 This script that adds hypervisor configuration is specific for Ansible.

"""

import sys

from ansible.module_utils.basic import *
from tintri.v310 import Tintri
from tintri.v310 import Appliance
from tintri.v310 import ApplianceDateTime
from tintri.common import TintriServerError

DEFAULT_DATASTORE = "default"


# Obtain the data and time from the VMstore.
def get_datetime(server):
    date_time = server.get_appliance_date_time(DEFAULT_DATASTORE)
    return date_time


# Update the data and time on the VMstore.
def update_datetime(server, new_date_time_dict):
    date_time = get_datetime(server)
    for key, value in new_date_time_dict.iteritems():
    	if value is not None:
    		setattr(date_time, key, value)
    server.update_appliance(None, DEFAULT_DATASTORE, date_time_config = date_time)
    return


# Remove list of keys from the dictionary.
def remove_dict_keys(d, keys_list):
    for key in keys_list:
        del d[key]
    return d


# Convert object to JSON string.
def obj_to_str(obj):
    s = json.dumps(obj.__dict__)
    return s


def main():
    module = AnsibleModule(
        argument_spec = dict(
            server = dict(required=True, type='str'),
            user = dict(required=True, type='str'),
            password = dict(required=True, type='str', no_log=True),
            timezone = dict(required=True, type='str'),
            useNtp = dict(required=False, type='bool'),
            ntpPrimary = dict(required=False, type='str'),
            ntpSecondary = dict(required=False, type='str'),
            year = dict(required=False, type='int'),
            month = dict(required=False, type='int'),
            day = dict(required=False, type='int'),
            time = dict(required=False, type='str')),
        supports_check_mode=True)

    m_args = module.params
    param_skip = ['server', 'user', 'password']

    try:
        # Instantiate the Tintri VMStore.
        tintri = Tintri(m_args['server'])

        # Login to VMStore.
        tintri.login(m_args['user'], m_args['password'])

    except TintriServerError as tse:
        module.fail_json(msg=tse.__str__())

    remove_dict_keys(m_args, param_skip)

    try:
    	update_datetime(tintri, m_args)

        results = obj_to_str(get_datetime(tintri))

    except TintriServerError as tse:
    	module.fail_json(msg=tse.__str__())
    	tintri.logout()

    # Log out VMSTore.
    tintri.logout()

    # Return the result to Ansible.
    module.exit_json(changed=True, meta=results)

if __name__ == '__main__':
    main()

