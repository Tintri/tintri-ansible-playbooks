# Tintri Ansible Out of the box Playbook #
This role is a for VMstore out of the box (OOB) configuration with a VMware hypervisor.
It replaces the VMstore GUI OOB configuration.  Note: Currently only VMware hypervisor
is supported.  More to come.

Currently the roles only have tests.  A main.yml will be forth coming. In the mean time,
here is the order for initial OOB:

1. Add data network
2. Update DNS 
3. Update datetime 
4. Update contact
5. Update Email 
6. Restart Webserver because of DNS change

Optional:
1. Add Hypervisor Manager
2. Update password

Copy python scripts to library location. Library path can be defined in /etc/ansible/ansible.cfg

## Questions or Comments ##
For questions and comments, please go to the [Tintricity Automation Discussion Group](http://hub.tintricity.com/discussions/automation).
