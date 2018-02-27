#!/usr/bin/env python
"""Test suite for generating the bridge config for the oob mgmt switch
"""
# C0103 - Snake case naming
# R0201 - Method could be a function

# pylint: disable=C0103, R0201
from nose.tools import raises
import topology_converter as tc

class TestRenderBridgeUntagged(object):  # pylint: disable=W0612,R0903
    """Test suite building untagged bridge config from a jinja template
    """

    def test_bridge_untagged_simple_topology(self):  # pylint: disable=R0201
        """Test generating the bridge config for the simple topology.dot
        """
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.build_mgmt_network()
        result = tc.render_bridge_untagged(inventory, topology_file,
                                           "./templates/auto_mgmt_network/")
        expected_result = []
        expected_result.append("# Created by Topology-Converter v5.0.0")
        expected_result.append("#    Template Revision: v5.0.0")
        expected_result.append("")
        expected_result.append("auto bridge")
        expected_result.append("iface bridge")
        expected_result.append("    bridge-vlan-aware yes")
        expected_result.append("    bridge-vids 1")
        expected_result.append("    bridge-ports swp2 swp3 swp1 swp6 swp4 swp5")
        expected_result.append("  ")
        expected_result.append("")
        expected_result.append("auto vlan1")
        expected_result.append("iface vlan1")
        expected_result.append("   address 192.168.200.1/24")
        expected_result.append("   vlan-raw-device bridge")
        expected_result.append(" ")

        print repr(result)
        print ""
        print repr("\n".join(expected_result))
        assert result == "\n".join(expected_result)

    @raises(SystemExit)
    def test_bridge_config_no_oob_switch(self):
        """Test that generating the bridge config without an OOB switch exits
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.oob_switch = None
        tc.render_bridge_untagged(inventory, topology_file, "./templates/auto_mgmt_network/")
