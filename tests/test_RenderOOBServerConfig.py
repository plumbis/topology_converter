#!/usr/bin/env python
"""Test suite for generating the server config file
for the OOB mgmt server
"""
# pylint: disable=C0103,R0201
from nose.tools import raises
import topology_converter as tc

class TestRenderOobConfig(object):  # pylint: disable=W0612,R0903
    """Test suite building OOB server config files
    """

    def test_oob_config_reference_topology(self):
        """Test generating the OOB config for the reference topology
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        expected_result_file = "./tests/expected_jinja_outputs/reference_topology_OOB_Server_Config.sh"  # pylint: disable=C0301
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_oob_server_sh(inventory, topology_file, "./templates/auto_mgmt_network/")

        print repr(result)
        print ""
        print ""
        print repr(open(expected_result_file).read())
        assert result == open(expected_result_file).read()

    @raises(SystemExit)
    def test_oob_config_no_oob_server(self):
        """Test that generating the OOB config without an OOB server exits
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.oob_server = None
        tc.render_oob_server_sh(inventory, topology_file, "./templates/auto_mgmt_network/")

    def test_oob_config_with_ntp_attribute(self):
        """Test building the OOB config with a custom NTP server attribute
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.get_node_by_name(
            "oob-mgmt-server").other_attributes["ntp"] = "clock.rdu.cumulusnetworks.com"
        result = tc.render_oob_server_sh(
            inventory, topology_file, "./templates/auto_mgmt_network/")

        assert "pool.ntp.org" not in result
        assert "clock.rdu.cumulusnetworks.com" in result
