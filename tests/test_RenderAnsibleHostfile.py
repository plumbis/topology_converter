#!/usr/bin/env python
"""Test suite for generating the ansible
hostfile for the management network
"""
# pylint: disable=C0103
import topology_converter as tc

class TestRenderAnsible(object):  # pylint: disable=W0612,R0903
    """Test suite building ansible host files
    """

    def test_simple_topology(self): # pylint: disable=R0201
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

        print result

        assert result == open(expected_result_file).read()
