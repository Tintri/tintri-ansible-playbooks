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
module: update_dns_config
short_description: Update dns configuration to Tintri VMStore
options:
    server:
    	description: VMStore Server Name or IP
    user:
    	description: User to access VMStore, usually admin
    	required: true
    password:
    	description: Password for user
    	required: true
    dnsPrimary:
    	description: Tintri Appliance primary DNS IP address
    	required: true
    dnsSecondary:
    	description: Tintri Appliance secondary DNS IP address
    	required: false
'''

EXAMPLES = '''
- name: Update VMStore data dns config
  update_dns_config:
    server: vmstore_servername
    user: admin
    password: xxx
    dnsPrimary: 10.10.2.100
    dnsSecondary: 10.10.2.110
  register: result
'''

"""
 This script that adds hypervisor configuration is specific for Ansible.

"""

import sys

from ansible.module_utils.basic import *
from tintri.v310 import Tintri
from tintri.v310 import Appliance
from tintri.v310 import ApplianceDns
from tintri.common import TintriServerError

DEFAULT_DATASTORE = "default"


# Get the current DNS configuration.
def get_dns_config(server):
    dns_config = server.get_appliance_dns(DEFAULT_DATASTORE)
    return dns_config


# Update the current DNS configuration.
def update_dns_config(server, new_dns_dict):
    dns = get_dns_config(server)
    for key, value in new_dns_dict.iteritems():
    	if value is not None:
    		setattr(dns, key, value)
    server.update_appliance(None, DEFAULT_DATASTORE, dns_config = dns)
    return


# Remove list of keys from the dictiionary .
def remove_dict_keys(d, keys_list):
    for key in keys_list:
    	del d[key]
    return d


# Convert object to JSON string.
def obj_to_str(obj):
    s = json.dumps(obj.__dict__)
    return s


def main():
    # Get the Ansible parameters.
    # Note: that some of the parameters names are the same as the DNS configuration dictionary.
    module = AnsibleModule(
        argument_spec = dict(
            server = dict(required=True, type='str'),
            user = dict(required=True, type='str'),
            password = dict(required=True, type='str', no_log=True),
            dnsPrimary = dict(required=True, type='str'),
            dnsSecondary = dict(required=False, type='str')),
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
        update_dns_config(tintri, m_args)

        dns_conf = get_dns_config(tintri)

    except TintriServerError as tse:
        module.fail_json(msg=tse.__str__())
        tintri.logout()

    # Log out VMSTore.
    tintri.logout()

    # Return the result to Ansible.
    results = obj_to_str(dns_conf)
    module.exit_json(changed=True, meta=results)

if __name__ == '__main__':
    main()
