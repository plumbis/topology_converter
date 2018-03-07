#!/usr/bin/env python
"""Test suite for generating the ansible
hostfile for the management network
"""
# pylint: disable=C0103, R0201
from nose.tools import raises

import topology_converter as tc

class TestRenderDhcpdHosts(object):  # pylint: disable=W0612,R0903
    """Test suite building ansible host files
    """

    def test_dhcp_hosts_simple_topology(self):
        """Test generating the ansible.hosts for the simple topology.dot
        """
        topology_file = "./tests/dot_files/simple.dot"
        expected_result_file = "./tests/expected_jinja_outputs/simple_dhcp.hosts"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.build_mgmt_network()
        result = tc.render_dhcpd_hosts(inventory, topology_file, "./templates/auto_mgmt_network/")

        assert result == open(expected_result_file).read()

    def test_dhcp_hosts_reference_topology(self): # pylint: disable=R0201
        """Test generating the ansible.hosts for the reference topology
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        expected_result_file = "./tests/expected_jinja_outputs/reference_topology_dhcpd.hosts"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_dhcpd_hosts(inventory, topology_file, "./templates/auto_mgmt_network/")

        assert result == open(expected_result_file).read()

    @raises(SystemExit)
    def test_dhcpd_hosts_no_oob_server(self):
        """Test that a problem with the OOB server causes system exit
        """
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.build_mgmt_network()
        inventory.oob_server = None
        tc.render_dhcpd_hosts(inventory, topology_file, "./templates/auto_mgmt_network/")

    def test_dhcpd_hosts_fake_device(self):
        """Test generating the dhcpd.hosts for an Inventory with a fake device
        """
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.add_node(tc.NetworkNode(hostname="fake01", memory="768", function="fake"))
        inventory.build_mgmt_network()

        result = tc.render_dhcpd_hosts(
            inventory, topology_file, "./templates/auto_mgmt_network/")

        for line in result.splitlines():
            assert "fake" not in line

    def test_dhcpd_hosts_ztp_attribute(self):
        """Test generating the dhcpd.hosts for an Inventory with the ztp script defined
        """
        topology_file = "./tests/dot_files/ztp_attribute.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.build_mgmt_network()

        result = tc.render_dhcpd_hosts(
            inventory, topology_file, "./templates/auto_mgmt_network/")

        ztp_line = "      option cumulus-provision-url \"http://192.168.200.254/leaf01_ztp.sh\";"
        assert ztp_line in result.splitlines()

    def test_create_mgmt_device_set(self):
        """Test generating with CMD set
        """
        topology_file = "./tests/dot_files/example_cmd.dot"
        expected_result_file = "./tests/expected_jinja_outputs/example_cmd_dhcpd.hosts"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.build_mgmt_network(create_mgmt_device=True)

        result = tc.render_dhcpd_hosts(inventory, topology_file, "./templates/auto_mgmt_network/")
        print result
        print ""
        print open(expected_result_file).read()
        assert result == open(expected_result_file).read()
