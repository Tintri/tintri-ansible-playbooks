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
module: add_hypervisor_config
short_description: Add hypervisor manager configuration to Tintri VMStore
options:
    server:
    	description: VMStore Server Name or IP
    user:
    	description: User to access VMStore, usually admin
    	required: true
    password:
    	description: Password for user
    	required: true
    host:
    	description: Host name for the hypervisor manager
    	required: true
    hypervisorType:
    	description: Type of for the hypervisor manager. Currently supports only "VMWARE".
    	required: true
    username:
    	description: Username for the hypervisor manager
    	required: true
    hypervisor_password:
    	description: Password for the hypervisor manager
    	required: true
'''

EXAMPLES = '''
- name: Add VMStore hypervisor manager config
  add_hypervisor_config:
    server: vmstore_servername
    user: admin
    password: xxx
    host: vcenter_test.org
    hypervisorType: VMWARE
    username: administrator@vshpere.local
    hypervisor_password: xxxxxx
  register: result
'''

"""
 This script that adds hypervisor configuration is specific for Ansible.

"""
import sys

from ansible.module_utils.basic import *
from tintri.v310 import Tintri
from tintri.v310 import HypervisorManagerConfig
from tintri.common import TintriServerError

DEFAULT_DATASTORE = "default"

# Get hypervisor configuration.
def get_hypervisor_configs(server):
    hyper_configs = server.get_hypervisor_manager_configs(DEFAULT_DATASTORE)
    return hyper_configs


# Add hypervisor configuration.
def add_hypervisor_config(server, new_hypervisor):
    server.create_hypervisor_manager_config(new_hypervisor, DEFAULT_DATASTORE)
    return


# Customize Objects Attributes/values output to list of string.
def customize_output(objs):
    output = []
    for obj in objs:
    	s = json.dumps(obj.__dict__)
    	output.append(s)
    return output


def main():
    # Get the Ansible parameters.
    # Note: that some of the parameters names are the same as the HypervisorConfig DTO attributes.
    module = AnsibleModule(
        argument_spec = dict(
            server = dict(required=True, type='str'),
            user = dict(required=True, type='str'),
            password = dict(required=True, type='str', no_log=True),
            host = dict(required=True, type='str'),
            hypervisorType = dict(required=True, choices=['VMWARE'], type='str'),
            #hypervisorType = dict(required=True,choices=['VMWARE','RHEV','HYPERV','UNKNOWN','OPENSTACK','XENSERVER','VMWARE_VVOL'], type='str'),
            username = dict(required=True,type='str'),
            hypervisor_password = dict(required=True, type='str', no_log=True)),
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

    # Forge the hypervisor manager configuration DTO.
    hypervisor_config = HypervisorManagerConfig()
    for key, value in m_args.iteritems():
    	if key not in param_skip:
    		if key == 'hypervisor_password':
    			setattr(hypervisor_config, 'password', value)
    		else:
    			setattr(hypervisor_config, key, value)

    # Add the hypervisor manager configuration.
    try:
        add_hypervisor_config(tintri, hypervisor_config)

        hyper_configs = get_hypervisor_configs(tintri)

    except TintriServerError as tse:
        module.fail_json(msg=tse.__str__())
        tintri.logout()

    # Log out VMSTore.
    tintri.logout()

    # Return the result to Ansible.
    results = customize_output(hyper_configs)
    module.exit_json(changed=True, meta=results)

if __name__ == '__main__':
    main()
