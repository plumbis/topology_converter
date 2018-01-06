#!/usr/bin/env python
from nose.tools import raises
import topology_converter as tc
import pydotplus as dot
import pprint


# Create a CLI to set verbose to True/False
class CLI:

    def __init__(self):

        self.verbose = False
        self.provider = "virtualbox"


class Test_nodes:

    def setup(self):
        """Setup the environment based on the simple.dot file.
        Populate the "mac" value with an empty set
        """
        topology = dot.graphviz.graph_from_dot_file("tests/dot_files/simple.dot")
        self.nodes = topology.get_node_list()
        self.expected_inventory = dict()
        self.expected_inventory["macs"] = set()

    def test_simple_node(self):
        """Test that the simple.dot file is valid.
        This should check memory, function, os, version and config
        """
        cli = CLI()
        test_result = tc.parse_nodes(self.nodes, cli)

        # Note: all attributes are passed through .lower()
        # watch case in tests
        leaf_attributes = {"interfaces": {}, "function": "leaf", "os": "cumuluscommunity/cumulus-vx", "version": "3.4.3", "memory": "768", "config": "./helper_scripts/config_switch.sh"}
        spine_attributes = {"interfaces": {}, "function": "spine", "os": "cumuluscommunity/cumulus-vx", "version": "3.4.3", "memory": "768", "config": "./helper_scripts/config_switch.sh"}
        
        self.expected_inventory["leaf01"] = leaf_attributes
        self.expected_inventory["leaf02"] = leaf_attributes
        self.expected_inventory["leaf03"] = leaf_attributes
        self.expected_inventory["leaf04"] = leaf_attributes
        self.expected_inventory["spine01"] = spine_attributes

        pp = pprint.PrettyPrinter(indent=2)
        print "Expected_Inventory:"
        pp.pprint(self.expected_inventory)
        print ""
        print "Result"
        pp.pprint(test_result)

        assert self.expected_inventory == test_result

    # @raises will catch non-zero exit code
    @raises(SystemExit)
    def test_bad_hostname(self):
        """Test an incorrect hostname.
        The hostname parsing is tested in test_check_hostname
        We only need to test that it exits
        """
        cli = CLI()
        self.nodes[0].set_name("leaf.1")
        tc.parse_nodes(self.nodes, cli)

    def test_no_function(self):
        """Test a valid dot file but with no function defined
        """
        cli = CLI()
        cli.verbose = True
        topology = dot.graphviz.graph_from_dot_file("tests/dot_files/no_function.dot")
        nodes = topology.get_node_list()
        expected_inventory = dict()
        expected_inventory["macs"] = set()
        test_result = tc.parse_nodes(nodes, cli)

        # Note: all attributes are passed through .lower()
        # watch case in tests
        leaf_attributes = {"interfaces": {}, "function": "unknown", "os": "cumuluscommunity/cumulus-vx", "version": "3.4.3", "memory": "768", "config": "./helper_scripts/config_switch.sh"}

        self.expected_inventory["leaf01"] = leaf_attributes
        self.expected_inventory["leaf02"] = leaf_attributes
        self.expected_inventory["leaf03"] = leaf_attributes
        self.expected_inventory["leaf04"] = leaf_attributes

        pp = pprint.PrettyPrinter(indent=2)
        print "Expected_Inventory:"
        pp.pprint(self.expected_inventory)
        print ""
        print "Result"
        pp.pprint(test_result)
        assert self.expected_inventory == test_result

    @raises(SystemExit)
    def test_bad_libvirt_images(self):
        """Test using a known invalid box image.
        Actual parsing of the box images is done by test_supported_libvirt_os
        This just tests that it exits
        """
        cli = CLI()
        cli.provider = "libvirt"
        topology = dot.graphviz.graph_from_dot_file("tests/dot_files/bento_box.dot")
        nodes = topology.get_node_list()
        expected_inventory = dict()
        expected_inventory["macs"] = set()
        tc.parse_nodes(nodes, cli)

    @raises(SystemExit)
    def test_bad_attribute(self):
        """Test passing a bad attribute, like negative memory value.
        Actual attribute parsing is tested in test_valid_attributes
        This only tests exiting
        """
        cli = CLI()
        cli.provider = "libvirt"
        topology = dot.graphviz.graph_from_dot_file("tests/dot_files/incorrect_memory.dot")
        nodes = topology.get_node_list()
        expected_inventory = dict()
        expected_inventory["macs"] = set()
        tc.parse_nodes(nodes, cli)
