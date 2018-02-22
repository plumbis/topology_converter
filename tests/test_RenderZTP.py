#!/usr/bin/env python
"""Test suite for generating the default contents of the ZTP script on the OOB Server
"""
# pylint: disable=C0103,R0201
from nose.tools import raises
import topology_converter as tc

class TestRenderZTP(object):  # pylint: disable=W0612,R0903
    """Test suite ZTP Script
    """

    def test_ztp_reference_topology(self):
        """Test generating the ZTP script for the reference topology
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        expected_result_file = "./tests/expected_jinja_outputs/reference_topology_ztp.sh"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_ztp_oob(inventory, topology_file, "./templates/auto_mgmt_network/")

        assert result == open(expected_result_file).read()

    @raises(SystemExit)
    def test_oob_config_no_oob_server(self):
        """Test that generating the ZTP script without an OOB server exits
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.oob_server = None
        tc.render_ztp_oob(inventory, topology_file, "./templates/auto_mgmt_network/")
