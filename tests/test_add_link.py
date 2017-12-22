#!/usr/bin/env python
import topology_converter as tc
from nose.tools import raises
import pprint
import copy


class CLI:

    def __init__(self):

        self.verbose = False
        self.topology_file = "./tests/dot_files/simple.dot"
        self.provider = "virtualbox"
        self.start_port = 8000
        self.port_gap = 1000


class Test_macs:
    def setup(self):
        self.inventory = {}
        self.inventory["macs"] = set()

        self.inventory["leaf01"] = {"interfaces": {}}
        self.inventory["leaf01"].update({"function": "leaf"})
        self.inventory["leaf01"].update({"config": "./helper_scripts/config_switch.sh"})
        self.inventory["leaf01"].update({"version": "3.4.3"})
        self.inventory["leaf01"].update({"os": "CumulusCommunity/cumulus-vx"})
        self.inventory["leaf01"].update({"memory": "512"})

        self.inventory["leaf02"] = {"interfaces": {}}
        self.inventory["leaf02"].update({"function": "leaf"})
        self.inventory["leaf02"].update({"config": "./helper_scripts/config_switch.sh"})
        self.inventory["leaf02"].update({"version": "3.4.3"})
        self.inventory["leaf02"].update({"os": "CumulusCommunity/cumulus-vx"})
        self.inventory["leaf02"].update({"memory": "512"})

        self.inventory["leaf03"] = {"interfaces": {}}
        self.inventory["leaf03"].update({"function": "leaf"})
        self.inventory["leaf03"].update({"config": "./helper_scripts/config_switch.sh"})
        self.inventory["leaf03"].update({"version": "3.4.3"})
        self.inventory["leaf03"].update({"os": "CumulusCommunity/cumulus-vx"})
        self.inventory["leaf03"].update({"memory": "512"})

        self.inventory["leaf04"] = {"interfaces": {}}
        self.inventory["leaf04"].update({"function": "leaf"})
        self.inventory["leaf04"].update({"config": "./helper_scripts/config_switch.sh"})
        self.inventory["leaf04"].update({"version": "3.4.3"})
        self.inventory["leaf04"].update({"os": "CumulusCommunity/cumulus-vx"})
        self.inventory["leaf04"].update({"memory": "512"})

        self.edge1 = ({"hostname": "leaf01", "interface": "swp49", "mac": "443839000001"},
                      {"hostname": "leaf02", "interface": "swp49", "mac": "443839000002"})

        self.edge2 = ({"hostname": "leaf03", "interface": "swp49", "mac": "443839000003"},
                      {"hostname": "leaf04", "interface": "swp49", "mac": "443839000004"})

        self.edge3 = ({"hostname": "leaf01", "interface": "swp50", "mac": "443839000005"},
                      {"hostname": "leaf02", "interface": "swp50", "mac": "443839000006"})

        self.edge4 = ({"hostname": "leaf03", "interface": "swp50", "mac": "443839000007"},
                      {"hostname": "leaf04", "interface": "swp50", "mac": "443839000008"})

        self.inventory["macs"].add("443839000001")
        self.inventory["macs"].add("443839000002")
        self.inventory["macs"].add("443839000003")
        self.inventory["macs"].add("443839000004")
        self.inventory["macs"].add("443839000005")
        self.inventory["macs"].add("443839000006")
        self.inventory["macs"].add("443839000007")
        self.inventory["macs"].add("443839000008")

    def test_vobx_add_one_edge(self):
        """Test adding a single edge to the inventory with vbox
        """

        cli = CLI()
        my_inventory = copy.deepcopy(self.inventory)

        result_inventory = tc.add_link(self.edge1, self.inventory, cli)

        my_inventory["leaf01"]["interfaces"] = {"swp49": {"network": "net0"}}
        my_inventory["leaf02"]["interfaces"] = {"swp49": {"network": "net0"}}

        # Don't mess up and make what we are comparing the same internal object
        assert id(my_inventory) != id(result_inventory)

        # Check that the two links are on the same network
        assert (result_inventory["leaf01"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf02"]["interfaces"]["swp49"]["network"])

        # Check that the network leaf01 is on is what we expect
        assert (my_inventory["leaf01"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf01"]["interfaces"]["swp49"]["network"])

        # Check that the network leaf02 is on is what we expect
        assert (my_inventory["leaf02"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf02"]["interfaces"]["swp49"]["network"])

    def test_vbox_add_two_edges(self):
        """Test adding two edges to the inventory with vbox
        """
        cli = CLI()
        my_inventory = copy.deepcopy(self.inventory)

        result_inventory = tc.add_link(self.edge1, self.inventory, cli)
        result_inventory = tc.add_link(self.edge2, result_inventory, cli)

        my_inventory["leaf01"]["interfaces"] = {"swp49": {"network": "net0"}}
        my_inventory["leaf02"]["interfaces"] = {"swp49": {"network": "net0"}}

        my_inventory["leaf03"]["interfaces"] = {"swp49": {"network": "net1"}}
        my_inventory["leaf04"]["interfaces"] = {"swp49": {"network": "net1"}}

        # Don't mess up and make what we are comparing the same internal object
        assert id(my_inventory) != id(result_inventory)

        assert (result_inventory["leaf01"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf02"]["interfaces"]["swp49"]["network"])

        assert (my_inventory["leaf01"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf01"]["interfaces"]["swp49"]["network"])

        assert (my_inventory["leaf02"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf02"]["interfaces"]["swp49"]["network"])

        assert (result_inventory["leaf03"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf04"]["interfaces"]["swp49"]["network"])

        assert (my_inventory["leaf03"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf03"]["interfaces"]["swp49"]["network"])

        assert (my_inventory["leaf04"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf04"]["interfaces"]["swp49"]["network"])

    # @raises will catch non-zero exit code
    @raises(SystemExit)
    def test_vbox_add_same_port(self):
        """Test adding an edge who's port has already been used with vbox
        """

        cli = CLI()

        result_inventory = tc.add_link(self.edge1, self.inventory, cli)

        tc.add_link(self.edge1, result_inventory, cli)

    def test_libvirt_add_one_edge(self):
        """Test adding a single edge to the inventory with libvirt
        """
        cli = CLI()
        cli.provider = "libvirt"
        my_inventory = copy.deepcopy(self.inventory)

        result_inventory = tc.add_link(self.edge1, self.inventory, cli)

        my_inventory["leaf01"]["interfaces"] = {"swp49": {"network":
                                                {"port": {"local": "8000", "remote": "9000"}}}}
        my_inventory["leaf02"]["interfaces"] = {"swp49": {"network":
                                                {"port": {"local": "9000", "remote": "8000"}}}}

        assert id(my_inventory) != id(result_inventory)

        # Check that the two links are on the same network
        assert (result_inventory["leaf01"]["interfaces"]["swp49"]["network"]["port"]["local"] ==
                result_inventory["leaf02"]["interfaces"]["swp49"]["network"]["port"]["remote"])

        assert (result_inventory["leaf01"]["interfaces"]["swp49"]["network"]["port"]["remote"] ==
                result_inventory["leaf02"]["interfaces"]["swp49"]["network"]["port"]["local"])

        # Check that the network leaf01 is on is what we expect
        assert (my_inventory["leaf01"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf01"]["interfaces"]["swp49"]["network"])

        # Check that the network leaf02 is on is what we expect
        assert (my_inventory["leaf02"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf02"]["interfaces"]["swp49"]["network"])

    def test_libvirt_add_two_edges(self):
        """Test adding two edges with libvirt
        """
        cli = CLI()
        cli.provider = "libvirt"
        my_inventory = copy.deepcopy(self.inventory)

        result_inventory = tc.add_link(self.edge1, self.inventory, cli)
        result_inventory = tc.add_link(self.edge2, result_inventory, cli)

        my_inventory["leaf01"]["interfaces"] = {"swp49": {"network":
                                                {"port": {"local": "8000", "remote": "9000"}}}}
        my_inventory["leaf02"]["interfaces"] = {"swp49": {"network":
                                                {"port": {"local": "9000", "remote": "8000"}}}}

        my_inventory["leaf03"]["interfaces"] = {"swp49": {"network":
                                                {"port": {"local": "8001", "remote": "9001"}}}}
        my_inventory["leaf04"]["interfaces"] = {"swp49": {"network":
                                                {"port": {"local": "9001", "remote": "8001"}}}}

        assert id(my_inventory) != id(result_inventory)

        # Check that the two links are on the same network
        assert (result_inventory["leaf01"]["interfaces"]["swp49"]["network"]["port"]["local"] ==
                result_inventory["leaf02"]["interfaces"]["swp49"]["network"]["port"]["remote"])

        assert (result_inventory["leaf01"]["interfaces"]["swp49"]["network"]["port"]["remote"] ==
                result_inventory["leaf02"]["interfaces"]["swp49"]["network"]["port"]["local"])

        assert (result_inventory["leaf03"]["interfaces"]["swp49"]["network"]["port"]["local"] ==
                result_inventory["leaf04"]["interfaces"]["swp49"]["network"]["port"]["remote"])

        assert (result_inventory["leaf03"]["interfaces"]["swp49"]["network"]["port"]["remote"] ==
                result_inventory["leaf04"]["interfaces"]["swp49"]["network"]["port"]["local"])

        # Check that the network leaf01 is on is what we expect
        assert (my_inventory["leaf01"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf01"]["interfaces"]["swp49"]["network"])

        # Check that the network leaf02 is on is what we expect
        assert (my_inventory["leaf02"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf02"]["interfaces"]["swp49"]["network"])

        # Check that the network leaf03 is on is what we expect
        assert (my_inventory["leaf03"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf03"]["interfaces"]["swp49"]["network"])

        # Check that the network leaf04 is on is what we expect
        assert (my_inventory["leaf04"]["interfaces"]["swp49"]["network"] ==
                result_inventory["leaf04"]["interfaces"]["swp49"]["network"])

    @raises(SystemExit)
    def test_libvirt_add_same_port(self):
        """Test adding an edge who's port has already been used with libvirt
        """
        cli = CLI()
        cli.provider = "libvirt"

        result_inventory = tc.add_link(self.edge1, self.inventory, cli)

        tc.add_link(self.edge1, result_inventory, cli)

    @raises(SystemExit)
    def test_bad_libvirt_offset(self):
        """Test a libvirt offset that can't be used
        """
        cli = CLI()
        cli.provider = "libvirt"
        cli.port_gap = "1"
        cli.start_port = "1"

        result_inventory = tc.add_link(self.edge1, self.inventory, cli)
        result_inventory = tc.add_link(self.edge2, result_inventory, cli)
        result_inventory = tc.add_link(self.edge3, result_inventory, cli)
        result_inventory = tc.add_link(self.edge4, result_inventory, cli)

        assert False
