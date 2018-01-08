#!/usr/bin/env python

import topology_converter as tc
from nose.tools import raises, with_setup

class TestNetworkInterface:

    def setup(self):
        self.inventory = tc.Inventory()


    def test_add_node_virtualbox(self):
        """Test adding a valid node with a virtualbox provider
        """
        self.inventory.provider == "virtualbox"

        test_node = tc.NetworkNode(hostname="leaf01", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        self.inventory.add_node(test_node)

        assert len(self.inventory.node_collection) == 1
        assert "leaf01" in self.inventory.node_collection


    def test_add_node_libvirt(self):
        """Test adding a valid node with a libvirt provider
        """
        self.inventory.provider = "libvirt"

        test_node = tc.NetworkNode(hostname="leaf01", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        self.inventory.add_node(test_node)

        assert len(self.inventory.node_collection) == 1
        assert "leaf01" in self.inventory.node_collection


    def test_add_node_libvirt_invalid_box_generator(self):
        """Generate tests for all known invalid libvirt box images
        """
        invalid_box_images = ["boxcutter/ubuntu1604",
                              "bento/ubuntu-16.04",
                              "ubuntu/xenial64"]


        for image in invalid_box_images:
            yield self.invalid_libvirt_box, image


    @raises(SystemExit)
    def invalid_libvirt_box(self, image):
        """Test that known bad libvirt box images exit
        """
        self.inventory = tc.Inventory()
        self.inventory.provider = "libvirt"
        test_node = tc.NetworkNode(hostname="leaf01", function="leaf",
                                   vm_os=image,
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")


        self.inventory.add_node(test_node)


    def test_get_node_by_name(self):
        """Test getting a specific NetworkNode by hostname lookup
        """
        test_node = tc.NetworkNode(hostname="leaf01", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        self.inventory.node_collection["leaf01"] = test_node

        result_node = self.inventory.get_node_by_name("leaf01")

        assert test_node.hostname == result_node.hostname
        assert test_node.function == result_node.function
        assert test_node.vm_os == result_node.vm_os

    def test_get_one_new_mac(self):
        """Test generating one new mac
        """
        leaf01_interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )

        #print self.inventory.get_mac(leaf01_interface)
        assert self.inventory.get_mac(leaf01_interface) == "0x443839000000"

    def test_get_two_macs(self):
        """Test generating two macs.
        This validates that a new mac can be created when one exists.
        """
        leaf01_interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )
        leaf02_interface = tc.NetworkInterface(hostname="leaf02", interface_name="swp51", mac=None, ip=None )

        assert self.inventory.get_mac(leaf01_interface) == "0x443839000000"
        assert self.inventory.get_mac(leaf02_interface) == "0x443839000001"

    def test_get_eleven_macs(self):
        """Test generating 11 macs.
        This tests that hex is working and the 11th mac is 0x...a and not 0x...10
        """
        iface1 = tc.NetworkInterface(hostname="leaf01", interface_name="swp50", mac=None, ip=None )
        iface2 = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )
        iface3 = tc.NetworkInterface(hostname="leaf01", interface_name="swp52", mac=None, ip=None )
        iface4 = tc.NetworkInterface(hostname="leaf01", interface_name="swp53", mac=None, ip=None )
        iface5 = tc.NetworkInterface(hostname="leaf01", interface_name="swp54", mac=None, ip=None )
        iface6 = tc.NetworkInterface(hostname="leaf01", interface_name="swp55", mac=None, ip=None )
        iface7 = tc.NetworkInterface(hostname="leaf01", interface_name="swp56", mac=None, ip=None )
        iface8 = tc.NetworkInterface(hostname="leaf01", interface_name="swp57", mac=None, ip=None )
        iface9 = tc.NetworkInterface(hostname="leaf01", interface_name="swp58", mac=None, ip=None )
        iface10 = tc.NetworkInterface(hostname="leaf01", interface_name="swp59", mac=None, ip=None )
        iface11 = tc.NetworkInterface(hostname="leaf01", interface_name="swp60", mac=None, ip=None )

        assert self.inventory.get_mac(iface1) == "0x443839000000"
        assert self.inventory.get_mac(iface2) == "0x443839000001"
        assert self.inventory.get_mac(iface3) == "0x443839000002"
        assert self.inventory.get_mac(iface4) == "0x443839000003"
        assert self.inventory.get_mac(iface5) == "0x443839000004"
        assert self.inventory.get_mac(iface6) == "0x443839000005"
        assert self.inventory.get_mac(iface7) == "0x443839000006"
        assert self.inventory.get_mac(iface8) == "0x443839000007"
        assert self.inventory.get_mac(iface9) == "0x443839000008"
        assert self.inventory.get_mac(iface10) == "0x443839000009"
        assert self.inventory.get_mac(iface11) == "0x44383900000a"

    def test_get_mac_with_existing(self):
        """Test getting a MAC when a static MAC was already assigned
        """
        iface1 = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )
        iface2 = tc.NetworkInterface(hostname="leaf02", interface_name="swp51", mac="443839000001", ip=None )
        iface3 = tc.NetworkInterface(hostname="leaf03", interface_name="swp51", mac=None, ip=None )

        self.inventory.get_mac(iface1)
        self.inventory.mac_set.add("0x443839000001")
        assert self.inventory.get_mac(iface3) == "0x443839000002"

    def test_add_edge_virtualbox(self):
        leaf01_node = tc.NetworkNode(hostname="leaf01", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        leaf02_node = tc.NetworkNode(hostname="leaf02", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        leaf01_interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )
        leaf02_interface = tc.NetworkInterface(hostname="leaf02", interface_name="swp51", mac=None, ip=None )

        test_edge = tc.NetworkEdge(leaf01_interface, leaf02_interface)

        self.inventory.add_node(leaf01_node)
        self.inventory.add_node(leaf02_node)
        self.inventory.provider = "virtualbox"

        self.inventory.add_edge(test_edge)

        inventory_leaf01 = self.inventory.node_collection["leaf01"]
        inventory_leaf02 = self.inventory.node_collection["leaf02"]

        assert inventory_leaf01.hostname == "leaf01"
        assert inventory_leaf01.function == "leaf"
        assert inventory_leaf02.hostname == "leaf02"
        assert inventory_leaf02.function == "leaf"

        assert inventory_leaf01.interfaces["swp51"].hostname == "leaf01"
        assert inventory_leaf01.interfaces["swp51"].interface_name == "swp51"
        assert inventory_leaf01.interfaces["swp51"].mac is not None

        assert inventory_leaf02.interfaces["swp51"].hostname == "leaf02"
        assert inventory_leaf02.interfaces["swp51"].interface_name == "swp51"
        assert inventory_leaf02.interfaces["swp51"].mac is not None

        # Ensure we set the ports and they line up
        assert inventory_leaf01.interfaces["swp51"].network is not None
        assert inventory_leaf02.interfaces["swp51"].network is not None
        assert inventory_leaf01.interfaces["swp51"].network == inventory_leaf02.interfaces["swp51"].network


    def test_add_edge_libvirt(self):
        leaf01_node = tc.NetworkNode(hostname="leaf01", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        leaf02_node = tc.NetworkNode(hostname="leaf02", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        leaf01_interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )
        leaf02_interface = tc.NetworkInterface(hostname="leaf02", interface_name="swp51", mac=None, ip=None )

        test_edge = tc.NetworkEdge(leaf01_interface, leaf02_interface)

        self.inventory.add_node(leaf01_node)
        self.inventory.add_node(leaf02_node)
        self.inventory.provider = "libvirt"

        self.inventory.add_edge(test_edge)

        inventory_leaf01 = self.inventory.node_collection["leaf01"]
        inventory_leaf02 = self.inventory.node_collection["leaf02"]

        assert inventory_leaf01.hostname == "leaf01"
        assert inventory_leaf01.function == "leaf"
        assert inventory_leaf02.hostname == "leaf02"
        assert inventory_leaf02.function == "leaf"

        assert inventory_leaf01.interfaces["swp51"].hostname == "leaf01"
        assert inventory_leaf01.interfaces["swp51"].interface_name == "swp51"
        assert inventory_leaf01.interfaces["swp51"].mac is not None

        assert inventory_leaf02.interfaces["swp51"].hostname == "leaf02"
        assert inventory_leaf02.interfaces["swp51"].interface_name == "swp51"
        assert inventory_leaf02.interfaces["swp51"].mac is not None

        # Ensure we set the ports and they line up.
        assert inventory_leaf01.interfaces["swp51"].local_port is not None
        assert inventory_leaf02.interfaces["swp51"].remote_port is not None
        assert inventory_leaf01.interfaces["swp51"].remote_port is not None
        assert inventory_leaf02.interfaces["swp51"].local_port is not None
        assert inventory_leaf01.interfaces["swp51"].local_port == inventory_leaf02.interfaces["swp51"].remote_port
        assert inventory_leaf01.interfaces["swp51"].remote_port == inventory_leaf02.interfaces["swp51"].local_port


    @raises(SystemExit)
    def test_add_edge_duplicate_interface(self):
        leaf01_node = tc.NetworkNode(hostname="leaf01", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        leaf02_node = tc.NetworkNode(hostname="leaf02", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        leaf01_interface1 = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )
        leaf02_interface1 = tc.NetworkInterface(hostname="leaf02", interface_name="swp51", mac=None, ip=None )
        leaf01_interface2 = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )
        leaf02_interface2 = tc.NetworkInterface(hostname="leaf02", interface_name="swp52", mac=None, ip=None )

        test_edge1 = tc.NetworkEdge(leaf01_interface1, leaf02_interface1)
        test_edge2 = tc.NetworkEdge(leaf01_interface2, leaf02_interface2)

        self.inventory.add_node(leaf01_node)
        self.inventory.add_node(leaf02_node)
        self.inventory.provider = "libvirt"

        self.inventory.add_edge(test_edge1)
        self.inventory.add_edge(test_edge2)


    @raises(SystemExit)
    def test_port_gap_too_short(self):
        leaf01_node = tc.NetworkNode(hostname="leaf01", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        leaf02_node = tc.NetworkNode(hostname="leaf02", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        leaf01_interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )
        leaf02_interface = tc.NetworkInterface(hostname="leaf02", interface_name="swp51", mac=None, ip=None )

        test_edge = tc.NetworkEdge(leaf01_interface, leaf02_interface)

        self.inventory.add_node(leaf01_node)
        self.inventory.add_node(leaf02_node)
        self.inventory.provider = "libvirt"
        self.inventory.libvirt_gap = 1

        self.inventory.add_edge(test_edge)

        self.inventory.node_collection["leaf01"]
        self.inventory.node_collection["leaf02"]


    def test_add_parsed_topology_virtualbox(self):
        """Test parsing a Graphviz topology file.
        Uses tests/dot_files/simple.dot as the test file
        """

        parser = tc.ParseGraphvizTopology()
        parser.parse_topology("./tests/dot_files/simple.dot")

        self.inventory.provider = "virtualbox"

        self.inventory.add_parsed_topology(parser)

        assert len(self.inventory.node_collection) == 5
        assert "leaf01" in self.inventory.node_collection
        assert "leaf02" in self.inventory.node_collection
        assert "leaf03" in self.inventory.node_collection
        assert "leaf04" in self.inventory.node_collection
        assert "spine01" in self.inventory.node_collection

        assert self.inventory.node_collection["leaf01"].function == "leaf"
        assert self.inventory.node_collection["leaf01"].vm_os == "CumulusCommunity/cumulus-vx"
        assert self.inventory.node_collection["leaf01"].memory == "768"
        assert self.inventory.node_collection["leaf01"].os_version == "3.4.3"
        assert self.inventory.node_collection["leaf01"].tunnel_ip == "127.0.0.1"
        assert self.inventory.node_collection["leaf01"].other_attributes == {}
        assert len(self.inventory.node_collection["leaf01"].interfaces) == 2
        assert self.inventory.node_collection["leaf01"].interfaces["swp51"].hostname == "leaf01"
        assert self.inventory.node_collection["leaf01"].interfaces["swp51"].interface_name == "swp51"
        assert self.inventory.node_collection["leaf01"].interfaces["swp51"].mac is not None
        assert self.inventory.node_collection["leaf01"].interfaces["swp51"].network == \
               self.inventory.node_collection["spine01"].interfaces["swp1"] .network

        assert self.inventory.node_collection["leaf01"].interfaces["swp49"].network == \
               self.inventory.node_collection["leaf02"].interfaces["swp49"] .network

        assert self.inventory.node_collection["leaf02"].function == "leaf"
        assert self.inventory.node_collection["leaf02"].vm_os == "CumulusCommunity/cumulus-vx"
        assert self.inventory.node_collection["leaf02"].memory == "768"
        assert self.inventory.node_collection["leaf02"].os_version == "3.4.3"
        assert self.inventory.node_collection["leaf02"].tunnel_ip == "127.0.0.1"
        assert self.inventory.node_collection["leaf02"].other_attributes == {}
        assert len(self.inventory.node_collection["leaf02"].interfaces) == 2
        assert self.inventory.node_collection["leaf02"].interfaces["swp51"].hostname == "leaf02"
        assert self.inventory.node_collection["leaf02"].interfaces["swp51"].interface_name == "swp51"
        assert self.inventory.node_collection["leaf02"].interfaces["swp51"].mac is not None
        assert self.inventory.node_collection["leaf02"].interfaces["swp51"].network == \
               self.inventory.node_collection["spine01"].interfaces["swp2"] .network

        assert self.inventory.node_collection["leaf03"].function == "leaf"
        assert self.inventory.node_collection["leaf03"].vm_os == "CumulusCommunity/cumulus-vx"
        assert self.inventory.node_collection["leaf03"].memory == "768"
        assert self.inventory.node_collection["leaf03"].os_version == "3.4.3"
        assert self.inventory.node_collection["leaf03"].tunnel_ip == "127.0.0.1"
        assert self.inventory.node_collection["leaf03"].other_attributes == {}
        assert len(self.inventory.node_collection["leaf03"].interfaces) == 2
        assert self.inventory.node_collection["leaf03"].interfaces["swp51"].hostname == "leaf03"
        assert self.inventory.node_collection["leaf03"].interfaces["swp51"].interface_name == "swp51"
        assert self.inventory.node_collection["leaf03"].interfaces["swp51"].mac is not None
        assert self.inventory.node_collection["leaf03"].interfaces["swp51"].network == \
               self.inventory.node_collection["spine01"].interfaces["swp3"] .network

        assert self.inventory.node_collection["leaf04"].function == "leaf"
        assert self.inventory.node_collection["leaf04"].vm_os == "CumulusCommunity/cumulus-vx"
        assert self.inventory.node_collection["leaf04"].memory == "768"
        assert self.inventory.node_collection["leaf04"].os_version == "3.4.3"
        assert self.inventory.node_collection["leaf04"].tunnel_ip == "127.0.0.1"
        assert self.inventory.node_collection["leaf04"].other_attributes == {}
        assert len(self.inventory.node_collection["leaf04"].interfaces) == 1
        assert self.inventory.node_collection["leaf04"].interfaces["swp49"].hostname == "leaf04"
        assert self.inventory.node_collection["leaf04"].interfaces["swp49"].interface_name == "swp49"
        assert self.inventory.node_collection["leaf04"].interfaces["swp49"].mac is not None
        assert self.inventory.node_collection["leaf04"].interfaces["swp49"].network == \
               self.inventory.node_collection["leaf03"].interfaces["swp49"] .network

    def test_add_parsed_topology_libvirt(self):
        """Test parsing a Graphviz topology file.
        Uses tests/dot_files/simple.dot as the test file
        """

        parser = tc.ParseGraphvizTopology()
        parser.parse_topology("./tests/dot_files/simple.dot")

        self.inventory.provider = "libvirt"

        self.inventory.add_parsed_topology(parser)

        assert len(self.inventory.node_collection) == 5
        assert "leaf01" in self.inventory.node_collection
        assert "leaf02" in self.inventory.node_collection
        assert "leaf03" in self.inventory.node_collection
        assert "leaf04" in self.inventory.node_collection
        assert "spine01" in self.inventory.node_collection

        assert self.inventory.node_collection["leaf01"].function == "leaf"
        assert self.inventory.node_collection["leaf01"].vm_os == "CumulusCommunity/cumulus-vx"
        assert self.inventory.node_collection["leaf01"].memory == "768"
        assert self.inventory.node_collection["leaf01"].os_version == "3.4.3"
        assert self.inventory.node_collection["leaf01"].tunnel_ip == "127.0.0.1"
        assert self.inventory.node_collection["leaf01"].other_attributes == {}
        assert len(self.inventory.node_collection["leaf01"].interfaces) == 2
        assert self.inventory.node_collection["leaf01"].interfaces["swp51"].hostname == "leaf01"
        assert self.inventory.node_collection["leaf01"].interfaces["swp51"].interface_name == "swp51"
        assert self.inventory.node_collection["leaf01"].interfaces["swp51"].mac is not None
        assert self.inventory.node_collection["leaf01"].interfaces["swp51"].local_port  is not None
        assert self.inventory.node_collection["spine01"].interfaces["swp1"].remote_port is not None
        assert self.inventory.node_collection["leaf01"].interfaces["swp51"].remote_port  is not None
        assert self.inventory.node_collection["spine01"].interfaces["swp1"].local_port is not None
        assert self.inventory.node_collection["leaf01"].interfaces["swp51"].local_port == \
               self.inventory.node_collection["spine01"].interfaces["swp1"].remote_port

        assert self.inventory.node_collection["leaf01"].interfaces["swp49"].local_port is not None
        assert self.inventory.node_collection["leaf01"].interfaces["swp49"].remote_port is not None
        assert self.inventory.node_collection["leaf02"].interfaces["swp49"].local_port is not None
        assert self.inventory.node_collection["leaf02"].interfaces["swp49"].remote_port is not None

        assert self.inventory.node_collection["leaf01"].interfaces["swp49"].local_port == \
               self.inventory.node_collection["leaf02"].interfaces["swp49"].remote_port

        assert self.inventory.node_collection["leaf02"].function == "leaf"
        assert self.inventory.node_collection["leaf02"].vm_os == "CumulusCommunity/cumulus-vx"
        assert self.inventory.node_collection["leaf02"].memory == "768"
        assert self.inventory.node_collection["leaf02"].os_version == "3.4.3"
        assert self.inventory.node_collection["leaf02"].tunnel_ip == "127.0.0.1"
        assert self.inventory.node_collection["leaf02"].other_attributes == {}
        assert len(self.inventory.node_collection["leaf02"].interfaces) == 2
        assert self.inventory.node_collection["leaf02"].interfaces["swp51"].hostname == "leaf02"
        assert self.inventory.node_collection["leaf02"].interfaces["swp51"].interface_name == "swp51"
        assert self.inventory.node_collection["leaf02"].interfaces["swp51"].mac is not None
        assert self.inventory.node_collection["leaf02"].interfaces["swp51"].local_port  is not None
        assert self.inventory.node_collection["spine01"].interfaces["swp2"].remote_port is not None
        assert self.inventory.node_collection["leaf02"].interfaces["swp51"].remote_port  is not None
        assert self.inventory.node_collection["spine01"].interfaces["swp2"].local_port is not None
        assert self.inventory.node_collection["leaf02"].interfaces["swp51"].local_port == \
               self.inventory.node_collection["spine01"].interfaces["swp2"].remote_port

        assert self.inventory.node_collection["leaf03"].function == "leaf"
        assert self.inventory.node_collection["leaf03"].vm_os == "CumulusCommunity/cumulus-vx"
        assert self.inventory.node_collection["leaf03"].memory == "768"
        assert self.inventory.node_collection["leaf03"].os_version == "3.4.3"
        assert self.inventory.node_collection["leaf03"].tunnel_ip == "127.0.0.1"
        assert self.inventory.node_collection["leaf03"].other_attributes == {}
        assert len(self.inventory.node_collection["leaf03"].interfaces) == 2
        assert self.inventory.node_collection["leaf03"].interfaces["swp51"].hostname == "leaf03"
        assert self.inventory.node_collection["leaf03"].interfaces["swp51"].interface_name == "swp51"
        assert self.inventory.node_collection["leaf03"].interfaces["swp51"].mac is not None
        assert self.inventory.node_collection["leaf03"].interfaces["swp51"].local_port  is not None
        assert self.inventory.node_collection["spine01"].interfaces["swp3"].remote_port is not None
        assert self.inventory.node_collection["leaf03"].interfaces["swp51"].remote_port  is not None
        assert self.inventory.node_collection["spine01"].interfaces["swp3"].local_port is not None
        assert self.inventory.node_collection["leaf03"].interfaces["swp51"].local_port == \
               self.inventory.node_collection["spine01"].interfaces["swp3"].remote_port

        assert self.inventory.node_collection["leaf04"].function == "leaf"
        assert self.inventory.node_collection["leaf04"].vm_os == "CumulusCommunity/cumulus-vx"
        assert self.inventory.node_collection["leaf04"].memory == "768"
        assert self.inventory.node_collection["leaf04"].os_version == "3.4.3"
        assert self.inventory.node_collection["leaf04"].tunnel_ip == "127.0.0.1"
        assert self.inventory.node_collection["leaf04"].other_attributes == {}
        assert len(self.inventory.node_collection["leaf04"].interfaces) == 1
        assert self.inventory.node_collection["leaf04"].interfaces["swp49"].hostname == "leaf04"
        assert self.inventory.node_collection["leaf04"].interfaces["swp49"].interface_name == "swp49"
        assert self.inventory.node_collection["leaf04"].interfaces["swp49"].mac is not None

        assert self.inventory.node_collection["leaf04"].interfaces["swp49"].local_port is not None
        assert self.inventory.node_collection["leaf04"].interfaces["swp49"].remote_port is not None

        assert self.inventory.node_collection["leaf03"].interfaces["swp49"].local_port is not None
        assert self.inventory.node_collection["leaf03"].interfaces["swp49"].remote_port is not None

        assert self.inventory.node_collection["leaf04"].interfaces["swp49"].local_port == \
               self.inventory.node_collection["leaf03"].interfaces["swp49"].remote_port

