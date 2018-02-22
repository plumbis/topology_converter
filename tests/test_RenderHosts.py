#!/usr/bin/env python
"""Test suite for generating the ansible
hostfile for the management network
"""
# pylint: disable=C0103,R0201
from nose.tools import raises
import topology_converter as tc

class TestRenderHosts(object):  # pylint: disable=W0612,R0903
    """Test suite building hosts files
    """

    def test_dns_hosts_simple_topology(self):
        """Test generating the hosts for the simple topology.dot
        """
        topology_file = "./tests/dot_files/simple.dot"
        expected_result_file = "./tests/expected_jinja_outputs/simple_hosts"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.build_mgmt_network()
        result = tc.render_hosts_file(
            inventory, topology_file, "./templates/auto_mgmt_network/")

        assert result == open(expected_result_file).read()

    @raises(SystemExit)
    def test_dns_hosts_no_oob_server(self):
        """Test that no OOB server causes system exit
        """
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.build_mgmt_network()
        inventory.oob_server = None
        tc.render_hosts_file(inventory, topology_file, "./templates/auto_mgmt_network/")

    def test_dns_hosts_reference_topology(self):
        """Test generating the hosts for the simple topology.dot
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        expected_result_file = "./tests/expected_jinja_outputs/reference_topology_hosts"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_hosts_file(
            inventory, topology_file, "./templates/auto_mgmt_network/")

        assert result == open(expected_result_file).read()

    def test_dns_hosts_fake_device(self):
        """Test generating the ansible.hosts for an Inventory with a fake device
        """
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.add_node(tc.NetworkNode(hostname="fake01", memory="768", function="fake"))
        inventory.build_mgmt_network()
        result = tc.render_hosts_file(
            inventory, topology_file, "./templates/auto_mgmt_network/")

        for line in result.splitlines():
            assert "fake" not in line
