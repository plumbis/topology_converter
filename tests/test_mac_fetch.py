#!/usr/bin/env python
import topology_converter as tc

inventory = {}

inventory["macs"] = set()
inventory["leaf01"] = {"interfaces": {"swp49": None}}
inventory["leaf01"].update({"function": "leaf"})
inventory["leaf01"].update({"config": "./helper_scripts/config_switch.sh"})
inventory["leaf01"].update({"version": "3.4.3"})
inventory["leaf01"].update({"os": "CumulusCommunity/cumulus-vx"})
inventory["leaf01"].update({"memory": "512"})


class CLI(object):

    def __init__(self):

        self.verbose = False


def test_first_mac():

    edge = ({"hostname": "leaf01", "interface": "swp49", "mac": None},
            {"hostname": "leaf02", "interface": "swp49", "mac": None})

    cli = CLI()

    tc.mac_fetch(edge, inventory, cli)
    assert False
    # assert tc.remove_interface_slash(edge) == result
