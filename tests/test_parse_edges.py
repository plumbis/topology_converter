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


class Test_edges:


    def test_simple_edge_vbox(self):
        """Test creating an inventory out of the simple topology
        """
        pp = pprint.PrettyPrinter(indent=2)
        cli = CLI()
        topology = dot.graphviz.graph_from_dot_file("tests/dot_files/simple.dot")
        self.edges = topology.get_edge_list()
        self.nodes = topology.get_node_list()

        # parse_edges() expects parse_nodes() to have been called first
        # it may be better to hand-build the output to test parse_edges
        # but I want to test that the dependency works
        node_inventory = tc.parse_nodes(self.nodes, cli)


        test_result = tc.parse_edges(self.edges, node_inventory, cli)

        """
         "leaf01":"swp51" -- "spine01":"swp1"
         "leaf02":"swp51" -- "spine01":"swp2"
         "leaf03":"swp51" -- "spine01":"swp3"

         "leaf01":"swp49" -- "leaf02":"swp49"
         "leaf03":"swp49" -- "leaf04":"swp49"
        """
        # We don't test the MACs because we can't guarantee the order which the links parsed
        # MACs are assigned first come, first serve. Without a known order, we don't know which mac
        # will be assigned to which interface

        assert test_result["leaf01"]["interfaces"]["swp51"]["network"] == test_result["spine01"]["interfaces"]["swp1"]["network"]
        assert test_result["leaf02"]["interfaces"]["swp51"]["network"] == test_result["spine01"]["interfaces"]["swp2"]["network"]
        assert test_result["leaf03"]["interfaces"]["swp51"]["network"] == test_result["spine01"]["interfaces"]["swp3"]["network"]
        assert test_result["leaf01"]["interfaces"]["swp49"]["network"] == test_result["leaf02"]["interfaces"]["swp49"]["network"]
        assert test_result["leaf03"]["interfaces"]["swp49"]["network"] == test_result["leaf04"]["interfaces"]["swp49"]["network"]
        assert test_result["linkcount"] == 5


    def test_simple_edge_libvirt(self):
        """Test creating an inventory out of the simple topology
        """
        pp = pprint.PrettyPrinter(indent=2)
        cli = CLI()
        cli.provider = "libvirt"
        cli.port_gap = "1000"
        cli.start_port = "1"

        topology = dot.graphviz.graph_from_dot_file("tests/dot_files/simple.dot")
        self.edges = topology.get_edge_list()
        self.nodes = topology.get_node_list()

        # parse_edges() expects parse_nodes() to have been called first
        # it may be better to hand-build the output to test parse_edges
        # but I want to test that the dependency works
        node_inventory = tc.parse_nodes(self.nodes, cli)


        test_result = tc.parse_edges(self.edges, node_inventory, cli)

        """
         "leaf01":"swp51" -- "spine01":"swp1"
         "leaf02":"swp51" -- "spine01":"swp2"
         "leaf03":"swp51" -- "spine01":"swp3"

         "leaf01":"swp49" -- "leaf02":"swp49"
         "leaf03":"swp49" -- "leaf04":"swp49"
        """
        # We don't test the MACs because we can't guarantee the order which the links parsed
        # MACs are assigned first come, first serve. Without a known order, we don't know which mac
        # will be assigned to which interface

        assert test_result["leaf01"]["interfaces"]["swp51"]["network"]["port"]["local"] == test_result["spine01"]["interfaces"]["swp1"]["network"]["port"]["remote"]
        assert test_result["leaf02"]["interfaces"]["swp51"]["network"]["port"]["local"] == test_result["spine01"]["interfaces"]["swp2"]["network"]["port"]["remote"]
        assert test_result["leaf03"]["interfaces"]["swp51"]["network"]["port"]["local"] == test_result["spine01"]["interfaces"]["swp3"]["network"]["port"]["remote"]
        assert test_result["leaf01"]["interfaces"]["swp49"]["network"]["port"]["local"] == test_result["leaf02"]["interfaces"]["swp49"]["network"]["port"]["remote"]
        assert test_result["leaf03"]["interfaces"]["swp49"]["network"]["port"]["local"] == test_result["leaf04"]["interfaces"]["swp49"]["network"]["port"]["remote"]
        assert test_result["linkcount"] == 5

    def test_reference_topology_vbox(self):
        """Test creating an inventory out of the reference topology
        """
        pp = pprint.PrettyPrinter(indent=2)
        cli = CLI()
        topology = dot.graphviz.graph_from_dot_file("tests/dot_files/reference_topology_3_4_3.dot")
        self.edges = topology.get_edge_list()
        self.nodes = topology.get_node_list()
        # parse_edges() expects parse_nodes() to have been called first
        # it may be better to hand-build the output to test parse_edges
        # but I want to test that the dependency works
        node_inventory = tc.parse_nodes(self.nodes, cli)


        test_result = tc.parse_edges(self.edges, node_inventory, cli)

        # We don't test the MACs because we can't guarantee the order which the links parsed
        # MACs are assigned first come, first serve. Without a known order, we don't know which mac
        # will be assigned to which interface

        assert test_result["leaf01"]["interfaces"]["swp51"]["network"] == test_result["spine01"]["interfaces"]["swp1"]["network"]
        assert test_result["leaf01"]["interfaces"]["swp52"]["network"] == test_result["spine02"]["interfaces"]["swp1"]["network"]
        assert test_result["leaf01"]["interfaces"]["swp49"]["network"] == test_result["leaf02"]["interfaces"]["swp49"]["network"]
        assert test_result["leaf01"]["interfaces"]["swp50"]["network"] == test_result["leaf02"]["interfaces"]["swp50"]["network"]
        assert test_result["leaf01"]["interfaces"]["swp1"]["network"] == test_result["server01"]["interfaces"]["eth1"]["network"]
        assert test_result["leaf01"]["interfaces"]["swp2"]["network"] == test_result["server02"]["interfaces"]["eth1"]["network"]

        assert test_result["leaf02"]["interfaces"]["swp51"]["network"] == test_result["spine01"]["interfaces"]["swp2"]["network"]
        assert test_result["leaf02"]["interfaces"]["swp52"]["network"] == test_result["spine02"]["interfaces"]["swp2"]["network"]
        assert test_result["leaf02"]["interfaces"]["swp49"]["network"] == test_result["leaf01"]["interfaces"]["swp49"]["network"]
        assert test_result["leaf02"]["interfaces"]["swp50"]["network"] == test_result["leaf01"]["interfaces"]["swp50"]["network"]
        assert test_result["leaf02"]["interfaces"]["swp1"]["network"] == test_result["server01"]["interfaces"]["eth2"]["network"]
        assert test_result["leaf02"]["interfaces"]["swp2"]["network"] == test_result["server02"]["interfaces"]["eth2"]["network"]

        assert test_result["leaf03"]["interfaces"]["swp51"]["network"] == test_result["spine01"]["interfaces"]["swp3"]["network"]
        assert test_result["leaf03"]["interfaces"]["swp52"]["network"] == test_result["spine02"]["interfaces"]["swp3"]["network"]
        assert test_result["leaf03"]["interfaces"]["swp49"]["network"] == test_result["leaf04"]["interfaces"]["swp49"]["network"]
        assert test_result["leaf03"]["interfaces"]["swp50"]["network"] == test_result["leaf04"]["interfaces"]["swp50"]["network"]
        assert test_result["leaf03"]["interfaces"]["swp1"]["network"] == test_result["server03"]["interfaces"]["eth1"]["network"]
        assert test_result["leaf03"]["interfaces"]["swp2"]["network"] == test_result["server04"]["interfaces"]["eth1"]["network"]

        assert test_result["leaf04"]["interfaces"]["swp51"]["network"] == test_result["spine01"]["interfaces"]["swp4"]["network"]
        assert test_result["leaf04"]["interfaces"]["swp52"]["network"] == test_result["spine02"]["interfaces"]["swp4"]["network"]
        assert test_result["leaf04"]["interfaces"]["swp49"]["network"] == test_result["leaf03"]["interfaces"]["swp49"]["network"]
        assert test_result["leaf04"]["interfaces"]["swp50"]["network"] == test_result["leaf03"]["interfaces"]["swp50"]["network"]
        assert test_result["leaf04"]["interfaces"]["swp1"]["network"] == test_result["server03"]["interfaces"]["eth2"]["network"]
        assert test_result["leaf04"]["interfaces"]["swp2"]["network"] == test_result["server04"]["interfaces"]["eth2"]["network"]

        assert test_result["exit01"]["interfaces"]["swp51"]["network"] == test_result["spine01"]["interfaces"]["swp30"]["network"]
        assert test_result["exit01"]["interfaces"]["swp52"]["network"] == test_result["spine02"]["interfaces"]["swp30"]["network"]
        assert test_result["exit01"]["interfaces"]["swp49"]["network"] == test_result["exit02"]["interfaces"]["swp49"]["network"]
        assert test_result["exit01"]["interfaces"]["swp50"]["network"] == test_result["exit02"]["interfaces"]["swp50"]["network"]
        assert test_result["exit01"]["interfaces"]["swp44"]["network"] == test_result["internet"]["interfaces"]["swp1"]["network"]
        assert test_result["exit01"]["interfaces"]["swp1"]["network"] == test_result["edge01"]["interfaces"]["eth1"]["network"]

        assert test_result["exit02"]["interfaces"]["swp51"]["network"] == test_result["spine01"]["interfaces"]["swp29"]["network"]
        assert test_result["exit02"]["interfaces"]["swp52"]["network"] == test_result["spine02"]["interfaces"]["swp29"]["network"]
        assert test_result["exit02"]["interfaces"]["swp49"]["network"] == test_result["exit01"]["interfaces"]["swp49"]["network"]
        assert test_result["exit02"]["interfaces"]["swp50"]["network"] == test_result["exit01"]["interfaces"]["swp50"]["network"]
        assert test_result["exit02"]["interfaces"]["swp44"]["network"] == test_result["internet"]["interfaces"]["swp2"]["network"]
        assert test_result["exit02"]["interfaces"]["swp1"]["network"] == test_result["edge01"]["interfaces"]["eth2"]["network"]

        assert test_result["spine01"]["interfaces"]["swp31"]["network"] == test_result["spine02"]["interfaces"]["swp31"]["network"]
        assert test_result["spine01"]["interfaces"]["swp32"]["network"] == test_result["spine02"]["interfaces"]["swp32"]["network"]

        assert test_result["oob-mgmt-switch"]["interfaces"]["swp1"]["network"] == test_result["oob-mgmt-server"]["interfaces"]["eth1"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp2"]["network"] == test_result["server01"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp3"]["network"] == test_result["server02"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp4"]["network"] == test_result["server03"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp5"]["network"] == test_result["server04"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp6"]["network"] == test_result["leaf01"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp7"]["network"] == test_result["leaf02"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp8"]["network"] == test_result["leaf03"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp9"]["network"] == test_result["leaf04"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp10"]["network"] == test_result["spine01"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp11"]["network"] == test_result["spine02"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp12"]["network"] == test_result["exit01"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp13"]["network"] == test_result["exit02"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp14"]["network"] == test_result["edge01"]["interfaces"]["eth0"]["network"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp15"]["network"] == test_result["internet"]["interfaces"]["eth0"]["network"]

        assert test_result["linkcount"] == 59

    def test_reference_topology_libvirt(self):
        """Test creating an inventory out of the reference topology
        """
        pp = pprint.PrettyPrinter(indent=2)
        cli = CLI()
        cli.provider = "libvirt"
        cli.port_gap = "1000"
        cli.start_port = "1"
        topology = dot.graphviz.graph_from_dot_file("tests/dot_files/reference_topology_3_4_3.dot")
        self.edges = topology.get_edge_list()
        self.nodes = topology.get_node_list()
        # parse_edges() expects parse_nodes() to have been called first
        # it may be better to hand-build the output to test parse_edges
        # but I want to test that the dependency works
        node_inventory = tc.parse_nodes(self.nodes, cli)


        test_result = tc.parse_edges(self.edges, node_inventory, cli)

        # We don't test the MACs because we can't guarantee the order which the links parsed
        # MACs are assigned first come, first serve. Without a known order, we don't know which mac
        # will be assigned to which interface

        assert test_result["leaf01"]["interfaces"]["swp51"]["network"]["port"]["local"] == test_result["spine01"]["interfaces"]["swp1"]["network"]["port"]["remote"]
        assert test_result["leaf01"]["interfaces"]["swp52"]["network"]["port"]["local"] == test_result["spine02"]["interfaces"]["swp1"]["network"]["port"]["remote"]
        assert test_result["leaf01"]["interfaces"]["swp49"]["network"]["port"]["local"] == test_result["leaf02"]["interfaces"]["swp49"]["network"]["port"]["remote"]
        assert test_result["leaf01"]["interfaces"]["swp50"]["network"]["port"]["local"] == test_result["leaf02"]["interfaces"]["swp50"]["network"]["port"]["remote"]
        assert test_result["leaf01"]["interfaces"]["swp1"]["network"]["port"]["local"] == test_result["server01"]["interfaces"]["eth1"]["network"]["port"]["remote"]
        assert test_result["leaf01"]["interfaces"]["swp2"]["network"]["port"]["local"] == test_result["server02"]["interfaces"]["eth1"]["network"]["port"]["remote"]

        assert test_result["leaf02"]["interfaces"]["swp51"]["network"]["port"]["local"] == test_result["spine01"]["interfaces"]["swp2"]["network"]["port"]["remote"]
        assert test_result["leaf02"]["interfaces"]["swp52"]["network"]["port"]["local"] == test_result["spine02"]["interfaces"]["swp2"]["network"]["port"]["remote"]
        assert test_result["leaf02"]["interfaces"]["swp49"]["network"]["port"]["local"] == test_result["leaf01"]["interfaces"]["swp49"]["network"]["port"]["remote"]
        assert test_result["leaf02"]["interfaces"]["swp50"]["network"]["port"]["local"] == test_result["leaf01"]["interfaces"]["swp50"]["network"]["port"]["remote"]
        assert test_result["leaf02"]["interfaces"]["swp1"]["network"]["port"]["local"] == test_result["server01"]["interfaces"]["eth2"]["network"]["port"]["remote"]
        assert test_result["leaf02"]["interfaces"]["swp2"]["network"]["port"]["local"] == test_result["server02"]["interfaces"]["eth2"]["network"]["port"]["remote"]

        assert test_result["leaf03"]["interfaces"]["swp51"]["network"]["port"]["local"] == test_result["spine01"]["interfaces"]["swp3"]["network"]["port"]["remote"]
        assert test_result["leaf03"]["interfaces"]["swp52"]["network"]["port"]["local"] == test_result["spine02"]["interfaces"]["swp3"]["network"]["port"]["remote"]
        assert test_result["leaf03"]["interfaces"]["swp49"]["network"]["port"]["local"] == test_result["leaf04"]["interfaces"]["swp49"]["network"]["port"]["remote"]
        assert test_result["leaf03"]["interfaces"]["swp50"]["network"]["port"]["local"] == test_result["leaf04"]["interfaces"]["swp50"]["network"]["port"]["remote"]
        assert test_result["leaf03"]["interfaces"]["swp1"]["network"]["port"]["local"] == test_result["server03"]["interfaces"]["eth1"]["network"]["port"]["remote"]
        assert test_result["leaf03"]["interfaces"]["swp2"]["network"]["port"]["local"] == test_result["server04"]["interfaces"]["eth1"]["network"]["port"]["remote"]

        assert test_result["leaf04"]["interfaces"]["swp51"]["network"]["port"]["local"] == test_result["spine01"]["interfaces"]["swp4"]["network"]["port"]["remote"]
        assert test_result["leaf04"]["interfaces"]["swp52"]["network"]["port"]["local"] == test_result["spine02"]["interfaces"]["swp4"]["network"]["port"]["remote"]
        assert test_result["leaf04"]["interfaces"]["swp49"]["network"]["port"]["local"] == test_result["leaf03"]["interfaces"]["swp49"]["network"]["port"]["remote"]
        assert test_result["leaf04"]["interfaces"]["swp50"]["network"]["port"]["local"] == test_result["leaf03"]["interfaces"]["swp50"]["network"]["port"]["remote"]
        assert test_result["leaf04"]["interfaces"]["swp1"]["network"]["port"]["local"] == test_result["server03"]["interfaces"]["eth2"]["network"]["port"]["remote"]
        assert test_result["leaf04"]["interfaces"]["swp2"]["network"]["port"]["local"] == test_result["server04"]["interfaces"]["eth2"]["network"]["port"]["remote"]

        assert test_result["exit01"]["interfaces"]["swp51"]["network"]["port"]["local"] == test_result["spine01"]["interfaces"]["swp30"]["network"]["port"]["remote"]
        assert test_result["exit01"]["interfaces"]["swp52"]["network"]["port"]["local"] == test_result["spine02"]["interfaces"]["swp30"]["network"]["port"]["remote"]
        assert test_result["exit01"]["interfaces"]["swp49"]["network"]["port"]["local"] == test_result["exit02"]["interfaces"]["swp49"]["network"]["port"]["remote"]
        assert test_result["exit01"]["interfaces"]["swp50"]["network"]["port"]["local"] == test_result["exit02"]["interfaces"]["swp50"]["network"]["port"]["remote"]
        assert test_result["exit01"]["interfaces"]["swp44"]["network"]["port"]["local"] == test_result["internet"]["interfaces"]["swp1"]["network"]["port"]["remote"]
        assert test_result["exit01"]["interfaces"]["swp1"]["network"]["port"]["local"] == test_result["edge01"]["interfaces"]["eth1"]["network"]["port"]["remote"]

        assert test_result["exit02"]["interfaces"]["swp51"]["network"]["port"]["local"] == test_result["spine01"]["interfaces"]["swp29"]["network"]["port"]["remote"]
        assert test_result["exit02"]["interfaces"]["swp52"]["network"]["port"]["local"] == test_result["spine02"]["interfaces"]["swp29"]["network"]["port"]["remote"]
        assert test_result["exit02"]["interfaces"]["swp49"]["network"]["port"]["local"] == test_result["exit01"]["interfaces"]["swp49"]["network"]["port"]["remote"]
        assert test_result["exit02"]["interfaces"]["swp50"]["network"]["port"]["local"] == test_result["exit01"]["interfaces"]["swp50"]["network"]["port"]["remote"]
        assert test_result["exit02"]["interfaces"]["swp44"]["network"]["port"]["local"] == test_result["internet"]["interfaces"]["swp2"]["network"]["port"]["remote"]
        assert test_result["exit02"]["interfaces"]["swp1"]["network"]["port"]["local"] == test_result["edge01"]["interfaces"]["eth2"]["network"]["port"]["remote"]

        assert test_result["spine01"]["interfaces"]["swp31"]["network"]["port"]["local"] == test_result["spine02"]["interfaces"]["swp31"]["network"]["port"]["remote"]
        assert test_result["spine01"]["interfaces"]["swp32"]["network"]["port"]["local"] == test_result["spine02"]["interfaces"]["swp32"]["network"]["port"]["remote"]

        assert test_result["oob-mgmt-switch"]["interfaces"]["swp1"]["network"]["port"]["local"] == test_result["oob-mgmt-server"]["interfaces"]["eth1"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp2"]["network"]["port"]["local"] == test_result["server01"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp3"]["network"]["port"]["local"] == test_result["server02"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp4"]["network"]["port"]["local"] == test_result["server03"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp5"]["network"]["port"]["local"] == test_result["server04"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp6"]["network"]["port"]["local"] == test_result["leaf01"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp7"]["network"]["port"]["local"] == test_result["leaf02"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp8"]["network"]["port"]["local"] == test_result["leaf03"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp9"]["network"]["port"]["local"] == test_result["leaf04"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp10"]["network"]["port"]["local"] == test_result["spine01"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp11"]["network"]["port"]["local"] == test_result["spine02"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp12"]["network"]["port"]["local"] == test_result["exit01"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp13"]["network"]["port"]["local"] == test_result["exit02"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp14"]["network"]["port"]["local"] == test_result["edge01"]["interfaces"]["eth0"]["network"]["port"]["remote"]
        assert test_result["oob-mgmt-switch"]["interfaces"]["swp15"]["network"]["port"]["local"] == test_result["internet"]["interfaces"]["eth0"]["network"]["port"]["remote"]

        assert test_result["linkcount"] == 59
