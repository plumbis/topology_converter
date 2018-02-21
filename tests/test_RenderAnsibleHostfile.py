#!/usr/bin/env python
"""Test suite for generating the ansible
hostfile for the management network
"""
# C0103 - does not confirm to snake case naming
# R0201 - Method could be a function
# pylint: disable=R0201,C0103
import topology_converter as tc

class TestRenderAnsible(object):  # pylint: disable=W0612,R0903
    """Test suite building ansible host files
    """

    def test_ansible_hosts_simple_topology(self): # pylint: disable=R0201
        """Test generating the ansible.hosts for the simple topology.dot
        """
        topology_file = "./tests/dot_files/simple.dot"
        expected_result_file = "./tests/expected_jinja_outputs/simple_ansible.hosts"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_ansible_hostfile(
            inventory, topology_file, "./templates/auto_mgmt_network/")

        assert result == open(expected_result_file).read()

    def test_ansible_hosts_fake_device(self):
        """Test generating the ansible.hosts for an Inventory with a fake device
        """
        topology_file = "fake_file.dot"
        expected_result_file = "./tests/expected_jinja_outputs/fake_hosts_ansible.hosts"
        inventory = tc.Inventory()
        inventory.add_node(tc.NetworkNode(hostname="leaf01", memory="768", function="leaf"))
        inventory.add_node(tc.NetworkNode(hostname="fake01", memory="768", function="fake"))

        result = tc.render_ansible_hostfile(
            inventory, topology_file, "./templates/auto_mgmt_network/")

        assert result == open(expected_result_file).read()

    def test_reference_topology(self):
        """Test generating the ansible.hosts for the reference topology dot file
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        expected_result_file = "./tests/expected_jinja_outputs/reference_topology.hosts"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_ansible_hostfile(
            inventory, topology_file, "./templates/auto_mgmt_network/")

        assert result == open(expected_result_file).read()
