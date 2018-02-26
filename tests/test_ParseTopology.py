#!/usr/bin/env python
"""Test suite for the topology_converter.ParseTopology class
"""
# pylint: disable=C0103

from nose.tools import raises
import pydotplus as dot
import topology_converter as tc

# pylint: disable=W0232
class TestParseTopology(object):
    """Class to test ParseTopology
    """
    def setup(self):
        """Initalize each test suite with default objects
        """
        self.dot_files = "./tests/dot_files/"  # pylint: disable=W0201
        self.topology_object = tc.ParseGraphvizTopology()  # pylint: disable=W0201
        self.graphviz_topology = dot.graphviz.graph_from_dot_file("./tests/dot_files/simple.dot")  # pylint: disable=W0201


    @raises(SystemExit)
    def test_linter_file_not_found(self):
        """Test errors when topology file does not exist
        """
        assert not self.topology_object.lint_topology_file("fake_file.dot")


    def test_topo_files_generator(self):
        """Generate test cases for good and bad topology files
        """
        # Note: Good topologies may be invalid for other reasons.
        # These are topologies that are good according to graphviz
        #
        # For example, "incorrect_memory.dot" is a valid .dot file
        # but has an invalid attribute according to topology converter.
        # We are only testing the parsing of .dot files, so it is not
        # considered "bad" at this point
        good_topo_files = ["simple.dot", "reference_topology_3_4_3.dot",
                           "reference_topology_3_4_3_large_memory.dot",
                           "bento_box.dot", "incorrect_memory.dot", "no_os.dot",
                           "no_function.dot", "spine01_not_defined.dot", "test_attribute.dot",
                           "fake.dot"]

        bad_topo_files = ["bad_dash.dot", "bad_quotes.dot",
                          "bad_ticks.dot", "bad_unicode_character.dot"]

        for topo in good_topo_files:
            yield self.lint_good_topos, "./tests/dot_files/" + topo

        for topo in bad_topo_files:
            yield self.lint_bad_topos, "./tests/dot_files/" + topo


    def lint_good_topos(self, topology_file):
        """Validate known good topologies pass
        """
        print "Failure on file: " + topology_file
        assert self.topology_object.lint_topology_file(topology_file)

    @raises(SystemExit)
    def lint_bad_topos(self, topology_file):
        """Validate known bad topologies fail
        """
        print "Failure on file: " + topology_file
        assert not self.topology_object.lint_topology_file(topology_file)

    @raises(SystemExit)
    def test_parse_topology_with_lint_failure(self):
        """Ensure Lint failures cause the program to exit
        """
        self.topology_object.parse_topology("./tests/dot_files/bad_dash.dot")


    def test_create_edge_from_graphviz(self):
        """Test creating an TC edge object from a Graphviz edge object
        """
        left_interface = tc.NetworkInterface(hostname="leaf01",
                                             interface_name="swp51",
                                             mac=None, ip=None)

        right_interface = tc.NetworkInterface(hostname="spine01",
                                              interface_name="swp1",
                                              mac=None, ip=None)

        graphviz_edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp1\"")
        edge_result = self.topology_object.create_edge_from_graphviz(graphviz_edge)

        assert edge_result.left_side.hostname == left_interface.hostname
        assert edge_result.left_side.interface_name == left_interface.interface_name
        assert edge_result.left_side.ip == left_interface.ip
        assert edge_result.left_side.mac == left_interface.mac
        assert edge_result.left_side.network == left_interface.network
        assert edge_result.left_side.local_port == left_interface.local_port
        assert edge_result.left_side.remote_port == left_interface.remote_port
        assert edge_result.left_side.attributes == left_interface.attributes

        assert edge_result.right_side.hostname == right_interface.hostname
        assert edge_result.right_side.interface_name == right_interface.interface_name
        assert edge_result.right_side.ip == right_interface.ip
        assert edge_result.right_side.mac == right_interface.mac
        assert edge_result.right_side.network == right_interface.network
        assert edge_result.right_side.local_port == right_interface.local_port
        assert edge_result.right_side.remote_port == right_interface.remote_port
        assert edge_result.right_side.attributes == right_interface.attributes

    def test_create_edge_from_graphviz_left_mac(self):
        """Test creating an edge from a Graphviz object with the left mac assigned
        """
        # "leaf01":"swp51" -- "spine01":"swp1" [left_mac="00:03:00:11:11:01"]
        graphviz_edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp1\"")
        graphviz_edge.obj_dict["attributes"]["left_mac"] = "00:03:00:11:11:01"

        left_interface = tc.NetworkInterface(hostname="leaf01",
                                             interface_name="swp51",
                                             mac="000300111101",
                                             ip=None)
        right_interface = tc.NetworkInterface(hostname="spine01",
                                              interface_name="swp1",
                                              mac=None,
                                              ip=None)

        edge_result = self.topology_object.create_edge_from_graphviz(graphviz_edge)

        assert edge_result.left_side.mac == left_interface.mac
        assert edge_result.right_side.mac == right_interface.mac
        assert edge_result.left_side.attributes == left_interface.attributes
        assert edge_result.right_side.attributes == right_interface.attributes


    def test_create_edge_from_graphviz_right_mac(self):
        """Test creating an edge from a graphviz object with the right mac set
        """
        # "leaf01":"swp51" -- "spine01":"swp1" [right_mac="00:03:00:11:11:01"]
        graphviz_edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp1\"")
        graphviz_edge.obj_dict["attributes"]["right_mac"] = "00:03:00:11:11:01"

        left_interface = tc.NetworkInterface(hostname="leaf01",
                                             interface_name="swp51",
                                             mac=None,
                                             ip=None)
        right_interface = tc.NetworkInterface(hostname="spine01",
                                              interface_name="swp1",
                                              mac="000300111101",
                                              ip=None)

        edge_result = self.topology_object.create_edge_from_graphviz(graphviz_edge)

        assert edge_result.left_side.mac == left_interface.mac
        assert edge_result.right_side.mac == right_interface.mac
        assert edge_result.left_side.attributes == left_interface.attributes
        assert edge_result.right_side.attributes == right_interface.attributes

    def test_create_edge_from_graphviz_left_pxe(self):
        """Create an edge from a graphviz object with the left host set to pxe
        """
        # "leaf01":"swp51" -- "spine01":"swp1" [left_mac="00:03:00:11:11:01"]
        graphviz_edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp1\"")
        graphviz_edge.obj_dict["attributes"]["left_pxebootinterface"] = "True"

        edge_result = self.topology_object.create_edge_from_graphviz(graphviz_edge)

        print edge_result.right_side
        assert edge_result.left_side.pxe_priority == 1
        assert edge_result.right_side.pxe_priority == 0


    def test_create_edge_from_graphviz_right_pxe(self):
        """Create an edge from a graphviz object with the right host set to pxe
        """
        # "leaf01":"swp51" -- "spine01":"swp1" [left_mac="00:03:00:11:11:01"]
        graphviz_edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp1\"")
        graphviz_edge.obj_dict["attributes"]["right_pxebootinterface"] = "True"

        edge_result = self.topology_object.create_edge_from_graphviz(graphviz_edge)

        print edge_result.right_side
        assert edge_result.left_side.pxe_priority == 0
        assert edge_result.right_side.pxe_priority == 1


    def test_generic_left_attribute(self):
        """Test processing a graphviz edge with a left, non-keyword, attribute set
        """
        # "leaf01":"swp51" -- "spine01":"swp1" [right_mac="00:03:00:11:11:01"]
        graphviz_edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp5\"")
        graphviz_edge.obj_dict["attributes"]["left_superspine"] = "True"

        left_interface = tc.NetworkInterface(hostname="leaf01",
                                             interface_name="swp51",
                                             mac=None,
                                             ip=None)
        right_interface = tc.NetworkInterface(hostname="spine01",
                                              interface_name="swp1",
                                              mac=None,
                                              ip=None)

        left_interface.add_attribute({"superspine": "True"})

        edge_result = self.topology_object.create_edge_from_graphviz(graphviz_edge)

        assert edge_result.left_side.mac == left_interface.mac
        assert edge_result.right_side.mac == right_interface.mac
        assert edge_result.left_side.attributes == left_interface.attributes
        assert edge_result.right_side.attributes == right_interface.attributes


    def test_generic_right_attribute(self):
        """Test processing a graphviz edge with a right, non-keyword, attribute set
        """
        # "leaf01":"swp51" -- "spine01":"swp1" [right_mac="00:03:00:11:11:01"]
        graphviz_edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp5\"")
        graphviz_edge.obj_dict["attributes"]["right_superspine"] = "True"

        left_interface = tc.NetworkInterface(hostname="leaf01",
                                             interface_name="swp51",
                                             mac=None,
                                             ip=None)
        right_interface = tc.NetworkInterface(hostname="spine01",
                                              interface_name="swp1",
                                              mac=None,
                                              ip=None)

        right_interface.add_attribute({"superspine": "True"})

        edge_result = self.topology_object.create_edge_from_graphviz(graphviz_edge)

        assert edge_result.left_side.mac == left_interface.mac
        assert edge_result.right_side.mac == right_interface.mac
        assert edge_result.left_side.attributes == left_interface.attributes
        assert edge_result.right_side.attributes == right_interface.attributes


    def test_generic_attribute(self):
        """Test processing a graphviz edge with both left and right
        having, non-keyword, attributes set
        """
        # "leaf01":"swp51" -- "spine01":"swp1"
        graphviz_edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp1\"")
        graphviz_edge.obj_dict["attributes"]["superspine"] = "True"

        left_interface = tc.NetworkInterface(hostname="leaf01",
                                             interface_name="swp51",
                                             mac=None,
                                             ip=None)
        right_interface = tc.NetworkInterface(hostname="spine01",
                                              interface_name="swp1",
                                              mac=None,
                                              ip=None)

        left_interface.add_attribute({"superspine": "True"})
        right_interface.add_attribute({"superspine": "True"})
        edge_result = self.topology_object.create_edge_from_graphviz(graphviz_edge)

        assert edge_result.left_side.mac == left_interface.mac
        assert edge_result.right_side.mac == right_interface.mac
        assert edge_result.left_side.attributes == left_interface.attributes
        assert edge_result.right_side.attributes == right_interface.attributes


    def test_create_node_from_graphviz(self):
        """Test creating a node from a graphviz object
        """
        # pydot.get_node() returns a list of one object, use the first one
        result_node = self.topology_object.create_node_from_graphviz(
            self.graphviz_topology.get_node("\"spine01\"")[0])

        assert result_node.hostname == "spine01"
        assert result_node.function == "spine"
        assert result_node.vm_os == "CumulusCommunity/cumulus-vx"
        assert result_node.os_version == "3.4.3"
        assert result_node.memory == "768"
        assert result_node.config == "./helper_scripts/config_switch.sh"
        assert result_node.other_attributes == {}


    def test_create_node_from_graphviz_with_attributes(self):
        """Test creating a node from graphviz object when an attribute is set
        """
        graphviz_topology = dot.graphviz.graph_from_dot_file("./tests/dot_files/test_attribute.dot")

        # pydot.get_node() returns a list of one object, use the first one
        result_node = self.topology_object.create_node_from_graphviz(
            graphviz_topology.get_node("\"leaf01\"")[0])

        assert result_node.hostname == "leaf01"
        assert result_node.function == "leaf"
        assert result_node.vm_os == "CumulusCommunity/cumulus-vx"
        assert result_node.os_version == "3.4.3"
        assert result_node.memory == "768"
        assert result_node.config == "./helper_scripts/config_switch.sh"
        assert result_node.other_attributes == {"test_attribute": "True"}


    @raises(SystemExit)
    def test_create_node_from_graphviz_with_no_os(self):
        """Test that a graphviz object without an OS causes program exit when parsed
        """
        graphviz_topology = dot.graphviz.graph_from_dot_file("./tests/dot_files/no_os.dot")

        # pydot.get_node() returns a list of one object, use the first one
        self.topology_object.create_node_from_graphviz(graphviz_topology.get_node("\"spine01\"")[0])

    def test_parse_topology_valid_topology(self):  # pylint: disable=R0914
        """Test parsing a Graphviz topology file.
        Uses tests/dot_files/simple.dot as the test file
        """

        self.topology_object.parse_topology("./tests/dot_files/simple.dot")

        leaf01 = tc.NetworkNode(hostname="leaf01", function="leaf",
                                vm_os="CumulusCommunity/cumulus-vx", os_version="3.4.3",
                                memory="768", config="./helper_scripts/config_switch.sh")

        leaf02 = tc.NetworkNode(hostname="leaf02", function="leaf",
                                vm_os="CumulusCommunity/cumulus-vx", os_version="3.4.3",
                                memory="768", config="./helper_scripts/config_switch.sh")

        leaf03 = tc.NetworkNode(hostname="leaf03", function="leaf",
                                vm_os="CumulusCommunity/cumulus-vx", os_version="3.4.3",
                                memory="768", config="./helper_scripts/config_switch.sh")

        leaf04 = tc.NetworkNode(hostname="leaf04", function="leaf",
                                vm_os="CumulusCommunity/cumulus-vx", os_version="3.4.3",
                                memory="768", config="./helper_scripts/config_switch.sh")

        spine01 = tc.NetworkNode(hostname="spine01", function="spine",
                                 vm_os="CumulusCommunity/cumulus-vx", os_version="3.4.3",
                                 memory="768", config="./helper_scripts/config_switch.sh")

        leaf01_swp51 = tc.NetworkInterface(hostname="leaf01", interface_name="swp51")
        leaf02_swp51 = tc.NetworkInterface(hostname="leaf02", interface_name="swp51")
        leaf03_swp51 = tc.NetworkInterface(hostname="leaf03", interface_name="swp51")
        leaf01_swp49 = tc.NetworkInterface(hostname="leaf01", interface_name="swp49")
        leaf03_swp49 = tc.NetworkInterface(hostname="leaf03", interface_name="swp49")

        spine01_swp1 = tc.NetworkInterface(hostname="spine01", interface_name="swp1")
        spine01_swp2 = tc.NetworkInterface(hostname="spine01", interface_name="swp2")
        spine01_swp3 = tc.NetworkInterface(hostname="spine01", interface_name="swp3")

        leaf02_swp49 = tc.NetworkInterface(hostname="leaf02", interface_name="swp49")
        leaf04_swp49 = tc.NetworkInterface(hostname="leaf04", interface_name="swp49")

        leaf01_spine01 = tc.NetworkEdge(leaf01_swp51, spine01_swp1)
        leaf02_spine01 = tc.NetworkEdge(leaf02_swp51, spine01_swp2)
        leaf03_spine01 = tc.NetworkEdge(leaf03_swp51, spine01_swp3)

        leaf01_leaf02 = tc.NetworkEdge(leaf01_swp49, leaf02_swp49)
        leaf03_leaf04 = tc.NetworkEdge(leaf03_swp49, leaf04_swp49)

        expected_nodes = [spine01, leaf04, leaf03, leaf02, leaf01]
        expected_edges = [leaf01_spine01, leaf02_spine01, leaf03_spine01,
                          leaf01_leaf02, leaf03_leaf04]

        assert len(self.topology_object.nodes) == len(expected_nodes)
        for node in self.topology_object.nodes:

            if node.hostname == "spine01":
                assert node.hostname == spine01.hostname
                assert node.function == spine01.function

            if node.hostname == "leaf01":
                assert node.hostname == leaf01.hostname

            if node.function == "leaf":
                assert node.function == leaf01.function

            assert node.vm_os == leaf01.vm_os
            assert node.os_version == leaf01.os_version
            assert node.memory == leaf01.memory
            assert node.config == leaf01.config

        # This should be a better test, I'm lazy.
        assert len(self.topology_object.edges) == len(expected_edges)

    def test_parse_with_pxehost(self):
        """Test that parsing a dot file with a pxehost is correct
        """
        parsed_topo = self.topology_object.parse_topology("./tests/dot_files/pxehost.dot")
        inventory = tc.Inventory()

        inventory.provider = "virtualbox"
        inventory.add_parsed_topology(parsed_topo)

        assert len(self.topology_object.nodes) == 2
        for node in self.topology_object.nodes:
            if node.hostname == "server1":
                assert node.hostname == "server1"
                assert node.function == "host"
                assert node.config == "./helper_scripts/extra_server_config.sh"
                assert node.pxehost is False
                assert inventory.get_node_by_name(
                    "server1").get_interface("eth0").pxe_priority == 0

            elif node.hostname == "pxehost":
                assert node.hostname == "pxehost"
                assert node.function == "host"
                assert node.vm_os == "yk0/ubuntu-xenial"
                assert node.memory == "512"
                assert node.config == "./helper_scripts/pxe_config.sh"
                assert node.pxehost is True
                assert inventory.get_node_by_name(
                    "pxehost").get_interface("eth0").pxe_priority == 1


    # R0912 - Too many branches
    # R0915 - Too many statements
    def test_parse_reference_topology_virtualbox(self):  # pylint: disable=R0912,R0915
        """Test parsing the reference topology when virtualbox is the provider
        """
        parsed_topo = self.topology_object.parse_topology(
            "./tests/dot_files/reference_topology.dot")
        inventory = tc.Inventory()
        inventory.provider = "virtualbox"
        inventory.add_parsed_topology(parsed_topo)

        assert len(self.topology_object.nodes) == 16

        for node in self.topology_object.nodes:
            if node.hostname == "leaf01":
                assert node.hostname == "leaf01"
                assert node.function == "leaf"
                assert node.config == "./helper_scripts/config_switch.sh"
                assert node.pxehost is False
                assert node.memory == "768"
                assert node.os_version == "3.5.1"
                assert node.vm_os == "CumulusCommunity/cumulus-vx"
                assert node.interfaces["eth0"].mac == "a00000000011"

            elif node.hostname == "leaf02":
                assert node.hostname == "leaf02"
                assert node.function == "leaf"
                assert node.config == "./helper_scripts/config_switch.sh"
                assert node.pxehost is False
                assert node.memory == "768"
                assert node.os_version == "3.5.1"
                assert node.vm_os == "CumulusCommunity/cumulus-vx"
                assert node.interfaces["eth0"].mac == "a00000000012"

            elif node.hostname == "leaf03":
                assert node.hostname == "leaf03"
                assert node.function == "leaf"
                assert node.config == "./helper_scripts/config_switch.sh"
                assert node.pxehost is False
                assert node.memory == "768"
                assert node.os_version == "3.5.1"
                assert node.vm_os == "CumulusCommunity/cumulus-vx"
                assert node.interfaces["eth0"].mac == "a00000000013"

            elif node.hostname == "leaf04":
                assert node.hostname == "leaf04"
                assert node.function == "leaf"
                assert node.config == "./helper_scripts/config_switch.sh"
                assert node.pxehost is False
                assert node.memory == "768"
                assert node.os_version == "3.5.1"
                assert node.vm_os == "CumulusCommunity/cumulus-vx"
                assert node.interfaces["eth0"].mac == "a00000000014"

            elif node.hostname == "spine01":
                assert node.hostname == "spine01"
                assert node.function == "spine"
                assert node.config == "./helper_scripts/config_switch.sh"
                assert node.pxehost is False
                assert node.memory == "768"
                assert node.os_version == "3.5.1"
                assert node.vm_os == "CumulusCommunity/cumulus-vx"
                assert node.interfaces["eth0"].mac == "a00000000021"

            elif node.hostname == "spine02":
                assert node.hostname == "spine02"
                assert node.function == "spine"
                assert node.config == "./helper_scripts/config_switch.sh"
                assert node.pxehost is False
                assert node.memory == "768"
                assert node.os_version == "3.5.1"
                assert node.vm_os == "CumulusCommunity/cumulus-vx"
                assert node.interfaces["eth0"].mac == "a00000000022"

            elif node.hostname == "exit01":
                assert node.hostname == "exit01"
                assert node.function == "exit"
                assert node.config == "./helper_scripts/config_switch.sh"
                assert node.pxehost is False
                assert node.memory == "768"
                assert node.os_version == "3.5.1"
                assert node.vm_os == "CumulusCommunity/cumulus-vx"
                assert node.interfaces["eth0"].mac == "a00000000041"

            elif node.hostname == "exit02":
                assert node.hostname == "exit02"
                assert node.function == "exit"
                assert node.config == "./helper_scripts/config_switch.sh"
                assert node.pxehost is False
                assert node.memory == "768"
                assert node.os_version == "3.5.1"
                assert node.vm_os == "CumulusCommunity/cumulus-vx"
                assert node.interfaces["eth0"].mac == "a00000000042"

            elif node.hostname == "server01":
                assert node.hostname == "server01"
                assert node.function == "host"
                assert node.config == "./helper_scripts/config_server.sh"
                assert node.pxehost is False
                assert node.memory == "512"
                assert node.os_version is None
                assert node.vm_os == "yk0/ubuntu-xenial"
                assert node.interfaces["eth1"].mac == "000300111101"
                assert node.interfaces["eth2"].mac == "000300111102"
                assert node.interfaces["eth0"].mac == "a00000000031"

            elif node.hostname == "server02":
                assert node.hostname == "server02"
                assert node.function == "host"
                assert node.config == "./helper_scripts/config_server.sh"
                assert node.pxehost is False
                assert node.memory == "512"
                assert node.os_version is None
                assert node.vm_os == "yk0/ubuntu-xenial"
                assert node.interfaces["eth1"].mac == "000300222201"
                assert node.interfaces["eth2"].mac == "000300222202"
                assert node.interfaces["eth0"].mac == "a00000000032"

            elif node.hostname == "server03":
                assert node.hostname == "server03"
                assert node.function == "host"
                assert node.config == "./helper_scripts/config_server.sh"
                assert node.pxehost is False
                assert node.memory == "512"
                assert node.os_version is None
                assert node.vm_os == "yk0/ubuntu-xenial"
                assert node.interfaces["eth1"].mac == "000300333301"
                assert node.interfaces["eth2"].mac == "000300333302"
                assert node.interfaces["eth0"].mac == "a00000000033"

            elif node.hostname == "server04":
                assert node.hostname == "server04"
                assert node.function == "host"
                assert node.config == "./helper_scripts/config_server.sh"
                assert node.pxehost is False
                assert node.memory == "512"
                assert node.os_version is None
                assert node.vm_os == "yk0/ubuntu-xenial"
                assert node.interfaces["eth1"].mac == "000300444401"
                assert node.interfaces["eth2"].mac == "000300444402"
                assert node.interfaces["eth0"].mac == "a00000000034"

            elif node.hostname == "edge01":
                assert node.hostname == "edge01"
                assert node.function == "host"
                assert node.config == "./helper_scripts/config_server.sh"
                assert node.pxehost is False
                assert node.memory == "768"
                assert node.os_version is None
                assert node.vm_os == "yk0/ubuntu-xenial"
                assert node.interfaces["eth0"].mac == "a00000000051"

            elif node.hostname == "internet":
                assert node.hostname == "internet"
                assert node.function == "internet"
                assert node.config == "./helper_scripts/config_internet.sh"
                assert node.pxehost is False
                assert node.memory == "768"
                assert node.os_version == "3.5.1"
                assert node.vagrant_interface == "swp48"
                assert node.vm_os == "CumulusCommunity/cumulus-vx"
                assert node.interfaces["eth0"].mac == "a00000000050"

            elif node.hostname == "oob-mgmt-switch":
                assert node.hostname == "oob-mgmt-switch"
                assert node.function == "oob-switch"
                assert node.config == "./helper_scripts/config_oob_switch.sh"
                assert node.pxehost is False
                assert node.memory == "768"
                assert node.os_version == "3.5.1"
                assert node.vagrant_interface == "eth0"
                assert node.vm_os == "CumulusCommunity/cumulus-vx"
                assert node.interfaces["swp1"].mac == "a00000000061"

            elif node.hostname == "oob-mgmt-server":
                assert node.hostname == "oob-mgmt-server"
                assert node.function == "oob-server"
                assert node.config == "./helper_scripts/config_oob_server.sh"
                assert node.pxehost is False
                assert node.memory == "1024"
                assert node.os_version == "1.0.4"
                assert node.vagrant_interface == "eth0"
                assert node.vm_os == "CumulusCommunity/vx_oob_server"
