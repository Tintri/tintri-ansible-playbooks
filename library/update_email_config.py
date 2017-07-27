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
module: update_email_config
short_description: Update email configuration to Tintri VMStore
options:
    server:
    	description: VMStore Server Name or IP
    user:
    	description: User to access VMStore, usually admin
    	required: true
    password:
    	description: Password for user
    	required: true
    toEmail:
    	description: Comma separated email addresses to send to
    	required: true
    	default: support@vmlevel.com
    smtpHost:
    	description: The SMTP host name
    	required: true
    emailNoticeLevel:
    	description: The email notice level setting. E-mail will be sent if notification is equal or above the notice level
                     select from ["ALERTS_ONLY", "ALERTS_AND_SOME_NOTICES", "ALERTS_AND_ALL_NOTICES"]
    	required: false
    	default: ALERTS_ONLY
    fromEmail:
    	description: The email address to receive from
    	required: true
    smtpIsLoginRequired:
    	description: Indicates if SMTP login is required. 'True' indicates SMTP login is required.
    	required: false
    	default: false
    smtpConnection:
    	description: The SMTP connection type. Select from ["NO_SECURE_CONNECTION", "TLS", "SSL"]
    	required: false
    	default: NO_SECURE_CONNECTION
    smtpPort:
    	description: The SMTP port number
    	required: false
    	default: -1
    smtpSSLPort:
    	description: The SMTP SSL port number
    	required: false
    	default: 25
    username:
    	description: The e-mail SMTP username
    	required: false
    email_password:
    	description: The e-mail SMTP password
    	required: false
'''

EXAMPLES = '''
- name: Update VMStore email config
  update_email_config:
    server: vmstore_servername
    user: admin
    password: xxx
    toEmail: support@vmlevel.com
    smtpHost: smtp.org
    emailNoticeLevel: ALERTS_ONLY
    fromEmail: admin@xx.org
    mtpIsLoginRequired: false
    smtpConnection: NO_SECURE_CONNECTION
    smtpPort: 25
    smtpSSLPort: -1
    username: test
    email_password: xxxx
  register: result
'''

"""
 This script that updates e-mail configuration is specific for Ansible.

"""

import sys

from ansible.module_utils.basic import *
from tintri.v310 import Tintri
from tintri.v310 import Appliance
from tintri.v310 import ApplianceEmail
from tintri.common import TintriServerError

DEFAULT_DATASTORE = "default"

# Get the current e-mail configuration.
def get_email_config(server):
    email_config = server.get_appliance_email(DEFAULT_DATASTORE)
    return email_config


# Update the current e-mail configuration.
def update_email_config(server, new_email_dict):
    email = get_email_config(server)
    for key, value in new_email_dict.iteritems():
    	if value is not None:
    		setattr(email, key, value)
    server.update_appliance(None, DEFAULT_DATASTORE, email_config = email)
    return


# Remove list of keys from the dictiionary.
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
    # Note: that some of the parameters names are the same as the e-mail configuration dictionary.
    module = AnsibleModule(
        argument_spec = dict(
            server = dict(required=True, type='str'),
            user = dict(required=True, type='str'),
            password = dict(required=True, type='str', no_log=True),
            toEmail = dict(required=False, type='str', default='support@vmlevel.com'),
            smtpHost = dict(required=True, type='str'),
            emailNoticeLevel = dict(required=False, choices=['ALERTS_ONLY','ALERTS_AND_SOME_NOTICES','ALERTS_AND_ALL_NOTICES'], type='str'),
            fromEmail = dict(required=True, type='str'),
            smtpIsLoginRequired = dict(required=False, type='bool'),
            smtpConnection = dict(required=False, choices=['NO_SECURE_CONNECTION','TLS','SSL'], type='str', default='NO_SECURE_CONNECTION'),
            smtpPort = dict(required=False, type='int', default=25),
            smtpSSLPort = dict(required=False, type='int'),
            username = dict(required=False, type='str'),
            email_password = dict(required=False, type='str', no_log=True)),
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

    if  m_args['email_password'] is not None:
    	m_args['password'] = m_args.pop('email_password')

    try:
    	update_email_config(tintri, m_args)

        email_conf = get_email_config(tintri)

    except TintriServerError as tse:
        module.fail_json(msg=tse.__str__())
        tintri.logout()

    # Log out VMSTore.
    tintri.logout()

    # Return the result to Ansible.
    results = obj_to_str(email_conf)
    module.exit_json(changed=True, meta=results)

if __name__ == '__main__':
    main()
