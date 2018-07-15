#!/usr/bin/env python

from isc_dhcp_leases import IscDhcpLeases
from json import dump
from sys import stdout, argv
from collections import defaultdict

def get_lease():
    leases = IscDhcpLeases('/var/lib/dhcp/dhcpd.leases')
    return leases.get()

def get_group(name, delimiter):
    pos = name.index(delimiter)
    group = name[:pos]

    return group

def generate_hosts():
    leases = get_lease()
    hosts = dict()
    groups = dict()

    for l in leases:
        name = l.hostname
        group = get_group(name, '-')
        active = l.active and l.valid
        ip = l.ip

        if group not in groups.keys():
            groups[group] = dict(hosts=[])
        groups[group]['hosts'].append(name)

        hosts[l.hostname] = dict(ansible_host=ip, active=active, group=group)

    return {
            'hosts': hosts,
            'groups': groups
            }

def generate_inventory():
    inventory = generate_hosts()

    groups = inventory['groups']
    meta = dict(hostvars=inventory['hosts'])

    return dict(**inventory['groups'], _meta=meta)

def main(argv):
    result = generate_inventory()

    if argv[1] == '--host' and argv[2]:
        result = result['_meta']['hostvars'][argv[2]]

    return dump(result, stdout)

if __name__ == '__main__':
    main(argv)

