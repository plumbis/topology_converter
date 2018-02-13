#!/usr/bin/env python
"""Test suite for the NetworkInterface topology converter object
"""
# pylint: disable=C0103, W0201

import topology_converter as tc


class TestNetworkInterface(object):  # pylint: disable=W0232, R0904
    """Test suite for the NetworkInterface() topology converter object
    """

    def setup(self):
        """Initalize the tests with a basic CLI
        """
        self.cli = tc.parse_arguments().parse_args(["./tests/dot_files/simple.dot"])

    def test_simple_network(self):

        """Test building the management network for the simple topology
        """
        self.cli.provider = "virtualbox"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(self.cli.topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        assert True

#         ########
#         # This method call will write the file ./helper_scripts/auto-mgmt_network/ansible.hosts
#         # We need to figure out how to mock the write.
#         # The contents that are written are tested in test_render_ansible_hostfile
#         #tc.generate_management_devices(inventory, self.cli)
