#!/usr/bin/env python
"""Test suite for generating the ansible
hostfile for the management network
"""
# pylint: disable=C0103
import topology_converter as tc

class TestRenderDhcpd(object):  # pylint: disable=W0612,R0903
    """Test suite building dhcpd.conf file from jinja2 template
    """

    def test_dhcpd_conf_simple_topology(self):  # pylint: disable=R0201
        """Test generating the dhcpd.conf for the simple topology.dot
        """
        topology_file = "./tests/dot_files/simple.dot"
        expected_result_file = "./tests/expected_jinja_outputs/simple_dhcpd.conf"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.build_mgmt_network()
        result = tc.render_dhcpd_conf(inventory, topology_file, "./templates/auto_mgmt_network/")

        assert result == open(expected_result_file).read()
