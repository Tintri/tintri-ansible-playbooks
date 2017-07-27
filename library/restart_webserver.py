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
module: restart_webserver
short_description: restart Tintri VMStore web server
options:
    server:
    	description: VMStore Server Name or IP
    user:
    	description: User to access VMStore, usually admin
    	required: true
    password:
    	description: Password for user
    	required: true
'''

EXAMPLES = '''
- name: restart_webserver
  restart_webserver:
    server: vmstore_servername
    user: admin
    password: xxx
  register: result
'''

"""
 This script that restarts the web server is specific for Ansible.

"""

import sys

from ansible.module_utils.basic import *
from tintri.v310 import Tintri
from tintri.common import TintriServerError

DEFAULT_DATASTORE = "default"

def main():
    # Get the Ansible parameters.
    module = AnsibleModule(
        argument_spec = dict(
            server = dict(required=True, type='str'),
            user = dict(required=True, type='str'),
            password = dict(required=True, type='str',no_log=True)),
        supports_check_mode=True)

    m_args = module.params

    try:
        # Instantiate the Tintri VMStore.
        tintri = Tintri(m_args['server'])

        # Login to VMStore.
        tintri.login(m_args['user'], m_args['password'])

    except TintriServerError as tse:
        module.fail_json(msg=tse.__str__())

    try:
        tintri.restart_webserver(DEFAULT_DATASTORE)

    except TintriServerError as tse:
        module.fail_json(msg=tse.__str__())
        tintri.logout()

    # Log out VMSTore.
    tintri.logout()

    # Return the result to Ansible.
    module.exit_json(changed=True)

if __name__ == '__main__':
    main()
