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
module: update_contact_config
short_description: Update contact configuration to Tintri VMStore
options:
    server:
    	description: VMStore Server Name or IP
    user:
    	description: User to access VMStore, usually admin
    	required: true
    password:
    	description: Password for user
    	required: true
    contact:
    	description: The customer contact name
    	required: false
    email:
    	description: The customer contact email addresss
    	required: false
    isEnabled:
    	description: 'True' indicates that auto-support is enabled, 'False' indicates that auto-support is disabled
    	required: false
    	default: True
    location:
    	description: The Tintri Appliance location
    	required: false
    phone:
    	description: The customer contact phone number
    	required: false
    webProxyHostname:
    	description: The web proxy host name for submitting autosupport telemetry to Tintri
    	required: false
    webProxyUsername:
    	description: The web proxy user name
    	required: false
    webProxyPassword:
    	description: The web proxy password
    	required: false
    webProxyPort:
    	description: The web proxy port number
    	required: false
'''

EXAMPLES = '''
- name: Update VMStore support contact config
  update_contact_config:
    server: vmstore_servername
    user: admin
    password: xxx
    contact: Roger Allen
    email: test@vmlevel.com
    isEnabled: True
    location: Rack#11,Building A,MountainView 
    phone: xxx-xxx-xxxx
    webProxyHostname: testproxy.orgA
    webProxyUsername: sampeluserA
    webProxyPassword: xxxx
    webProxyPort: 6567
  register: result
'''

"""
 This script that updates contact information is specific for Ansible.

"""

import sys

from ansible.module_utils.basic import *
from tintri.v310 import Tintri
from tintri.v310 import Appliance
from tintri.v310 import ApplianceSupport
from tintri.common import TintriServerError

DEFAULT_DATASTORE = "default"


# Obtain the contact information.
def get_contact_config(server):
    support_config = server.get_appliance_support(DEFAULT_DATASTORE)
    return support_config


# Update the contact information.
def update_contact_config(server, new_contact_dict):
    contact = get_contact_config(server)
    for key, value in new_contact_dict.iteritems():
    	if value is not None:
    		setattr(contact, key, value)
    server.update_appliance(None, DEFAULT_DATASTORE,  support_config = contact)
    return


# Remove list of keys from the dictiionary.
def remove_dict_keys(d, keys_list):
    for key in keys_list:
        del d[key]
    return d

def obj_to_str(obj):
    s = json.dumps(obj.__dict__)
    return s

def main():
    # Get the Ansible parameters.
    # Note: that some of the parameters names are the same as the contact DTO attributes.
    module = AnsibleModule(
        argument_spec = dict(
            server = dict(required=True, type='str'),
            user = dict(required=True, type='str'),
            password = dict(required=True, type='str', no_log=True),
            contact = dict(required=False, type='str'),
            email = dict(required=False, type='str'),
            isEnabled = dict(required=False, type='bool', default=True),
            location = dict(required=False, type='str'),
            phone = dict(required=False,type='str'),
            webProxyHostname = dict(required=False, type='str'),
            webProxyUsername = dict(required=False, type='str'),
            webProxyPassword = dict(required=False, type='str'),
            webProxyPort = dict(required=False, type='int')),
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
        update_contact_config(tintri, m_args)

        contact_conf = get_contact_config(tintri)

    except TintriServerError as tse:
        module.fail_json(msg=tse.__str__())
        tintri.logout()

    # Log out VMSTore.
    tintri.logout()

    # Return the result to Ansible.
    results = obj_to_str(contact_conf)
    module.exit_json(changed=True, meta=results)

if __name__ == '__main__':
    main()
