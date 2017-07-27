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
module: add_data_network_config
short_description: Add new data network configuration to Tintri VMStore
options:
    server:
    	description: VMStore Server Name or IP.
    user:
    	description: User to manage VMStore, usually admin.
    	required: true
    password:
    	description: Password for user.
    	required: true
    ip:
    	description: IP address for this network interface.
    	required: true
    netmask:
    	description: Netmask for this network interface.
    	required: true
    gateway:
    	description: Gateway address for this network interface.
    	required: true
    isJumboFrameEnabled:
    	description: 'True' indicates that jumbo frames are to be enabled, 'False' indicates that
                     jumbo frames are not to be enabled>
    	required: false
    	default: True
    vlanId:
    	description: VLAN ID for this network interface.
    	required: false
    	default: untagged
    networkBond:
    	description: Name of the associated network bond underlying this IP configuration. Types
                     are: "NET_BOND_UNKNOWN", "NET_BOND_ADMIN", "NET_BOND_DATA", "NET_BOND_REPL".
    	required: false
    	default: NET_BOND_DATA
'''

EXAMPLES = '''
- name: Add VMStore data network config
  add_data_network_config:
    server: vmstore_servername
    user: admin
    password: xxx
    ip: 10.10.10.10
    netmask: 255.255.255.0
    gateway: 10.10.10.1
    isJumboFrameEnabled: True
    vlanId: untagged
    networkBond: NET_BOND_DATA
  register: result
'''

"""
 This script that adds data IP network configuration is specific for Ansible.

"""

import sys

from ansible.module_utils.basic import *
from tintri.v310 import Tintri
from tintri.v310 import Appliance
from tintri.v310 import ApplianceIp
from tintri.common import TintriServerError

DATA_SERVICE_TYPE = "data"
DEFAULT_DATASTORE = "default"


# Obtain the current IP network configuration.
def get_ip_configs(server):
    networks = server.get_appliance_ips(DEFAULT_DATASTORE)
    return networks

# Customize Objects Attributes/values output to list of string
def customize_output(objs):
    output = []
    for obj in objs:
    	s = json.dumps(obj.__dict__)
    	output.append(s)
    return output


# Append a data IP network configuration.
def add_data_network_config(server, new_data_network):
    networks = get_ip_configs(server)
    networks.append(new_data_network)
    server.update_appliance(None, DEFAULT_DATASTORE, config_ips = networks)
    return


def main():
    # Get the Ansible parameters.
    # Note: that some of the parameters names are the same as the ApplianceIP DTO attributes.
    module = AnsibleModule(
        argument_spec = dict(
            server = dict(required=True, type='str'),
            user = dict(required=True, type='str'),
            password = dict(required=True, type='str', no_log=True),
            ip = dict(required=True, type='str'),
            netmask = dict(required=True, type='str'),
            gateway = dict(required=True, type='str'),
            isJumboFrameEnabled = dict(required=False, type='bool', default=True),
            vlanId = dict(required=False, type='str', default='untagged'),
            networkBond = dict(required=False, type='str', default='NET_BOND_DATA')),
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

    # Forge the DTO to update the IP network configuration.
    new_network = ApplianceIp()
    m_args['serviceType'] = DATA_SERVICE_TYPE

    for key, value in m_args.iteritems():
    	if key not in param_skip:
    		setattr(new_network, key, value)

    # Append the new data IP network configuration.
    try:
        add_data_network_config(tintri, new_network)

        ip_configs = get_ip_configs(tintri)

    except TintriServerError as tse:
        module.fail_json(msg=tse.__str__())
        tintri.logout()


    # Log out VMstore.
    tintri.logout()

    # Return the result to Ansible.
    results = customize_output(ip_configs)
    module.exit_json(changed=True, meta=results)

if __name__ == '__main__':
    main()
