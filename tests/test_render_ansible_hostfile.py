#!/usr/bin/env python
"""Test suite for generating the ansible
hostfile for the management network
"""
# pylint: disable=C0103
from nose.tools import raises
import topology_converter as tc

class TestRenderAnsible(object):  # pylint: disable=W0612
    """Test suite building ansible host files
    """

    def test_simple_topology(self):
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)

        tc.render_ansible_hostfile(inventory, topology_file, "./templates/auto_mgmt_network/", "./tests/jinja_results/")

        assert True
