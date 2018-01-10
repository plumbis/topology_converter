#!/usr/bin/env python
"""Test suite for topology_converter.NetworkNode class
"""
# pylint: disable=C0103
from nose.tools import raises
import topology_converter as tc

class Test_NetworkNode(object):
    """Test class for NetworkNode tests
    """
    # pylint: disable=W0201
    def setup(self):
        """Build a basic NetworkNode
        """
        self.node = tc.NetworkNode(hostname="leaf01", function="leaf",
                                   vm_os="CumulusCommunity/cumulus-vx",
                                   memory="768", config="./helper_scripts/oob_switch_config.sh")

        self.valid_hostnames = ["leaf", "0000", "leaf01", "01leaf", "leaf-01"]
        self.invalid_hostnames = [".leaf", "-leaf", "_leaf", "lea.f", "leaf.", "leaf-", " leaf"
                                  "leaf ", "le af", "   "]

    def test_init(self):  # pylint: disable=R0201
        """Test building a NetworkNode
        """
        node = tc.NetworkNode("leaf01", "leaf", "cumuluscommunity/cumulus-vx",
                              "768", "./helper_scripts/oob_switch_config.sh")

        assert node.hostname == "leaf01"
        assert node.function == "leaf"
        assert node.vm_os == "cumuluscommunity/cumulus-vx"
        assert node.memory == "768"


    def test_check_hostname_valid(self):
        """Test valid hostnames are accepted and returns True
        """
        for hostname in self.valid_hostnames:
            assert self.node.check_hostname(hostname) is True


    def test_check_hostname_invalid(self):
        """Test invalid hostnames are rejected and returns False
        """
        for hostname in self.invalid_hostnames:
            assert self.node.check_hostname(hostname) is False


    def test_invalid_hostname_init_generator(self):
        """Generator for creating NetworkNode objects with invalid hostnames
        """
        invalid_hostnames = [".leaf", "-leaf", "_leaf", "lea.f", "leaf.", "leaf-", " leaf"
                             "leaf ", "le af", "   "]
        for hostname in invalid_hostnames:
            yield self.invalid_hostname_init, hostname


    @raises(SystemExit)
    def invalid_hostname_init(self, hostname):  # pylint: disable=R0201
        """Test that creating a NetworkNode with an invalid name exits
        """
        tc.NetworkNode(hostname, "leaf", "cumuluscommunity/cumulus-vx",
                       "768", "./helper_scripts/oob_switch_config.sh")


    def test_fake_function_defaults(self):  # pylint: disable=R0201
        """Test the defaults of a "fake" function
        """
        node = tc.NetworkNode("leaf01", "fake")

        assert node.vm_os == "None"
        assert node.memory == "1"


    def test_oob_server_function_defaults(self):  # pylint: disable=R0201
        """Test the defaults of the "oob-server" function
        """
        node = tc.NetworkNode("leaf01", "oob-server")

        assert node.vm_os == "yk0/ubuntu-xenial"
        assert node.memory == "512"
        assert node.config == "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh"


    def test_oob_switch_function_defaults(self):  # pylint: disable=R0201
        """Test the defaults of the "oob-switch" funcion
        """
        node = tc.NetworkNode("leaf01", "oob-switch")

        assert node.vm_os == "cumuluscommunity/cumulus-vx"
        assert node.memory == "512"
        assert node.config == "./helper_scripts/oob_switch_config.sh"


    def test_host_function_defaults(self):  # pylint: disable=R0201
        """Test the defaults of the "host" function
        """
        node = tc.NetworkNode("server01", "host")

        assert node.vm_os == "yk0/ubuntu-xenial"
        assert node.memory == "512"
        assert node.config == "./helper_scripts/extra_server_config.sh"


    def test_pxehost_function_defaults(self):  # pylint: disable=R0201
        """Test the defaults of the "pxehost" function
        """
        node = tc.NetworkNode("server01", "pxehost")

        assert node.vm_os == "None"
        assert node.memory == "512"
        assert node.config == "./helper_scripts/extra_server_config.sh"


    def test_invalid_memory_generator(self):
        """Test genereator for invalid memory attributes
        """
        memory_values = ["0", "-1", "a", "0x123"]

        for value in memory_values:
            yield self.invalid_memory_values, value


    @raises(SystemExit)
    def invalid_memory_values(self, value):
        """Test that the system exits when an invalid memory value is provided
        """
        self.node = tc.NetworkNode("leaf01", "leaf", "cumuluscommunity/cumulus-vx",
                                   value, "./helper_scripts/oob_switch_config.sh")


    def test_get_interface_not_exist(self):
        """Test getting an interface that doesn't exist in the NetworkNode
        """
        assert self.node.get_interface("swp1") is None

    def test_get_interface_exists(self):
        """Test getting an interface that exists within a node
        """
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp51",
                                        mac=None, ip=None)
        self.node.interfaces["swp51"] = interface

        result_interface = self.node.get_interface("swp51")
        assert result_interface.hostname == "leaf01"
        assert result_interface.interface_name == "swp51"
        assert result_interface.mac is None
        assert result_interface.ip is None

    def test_add_interface(self):
        """Test adding an interface to a node
        """
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp51",
                                        mac=None, ip=None)

        self.node.add_interface(interface)
        result_interface = self.node.interfaces["swp51"]
        assert result_interface.hostname == "leaf01"
        assert result_interface.interface_name == "swp51"
        assert result_interface.mac is None
        assert result_interface.ip is None

    def test_add_interface_first_pxe(self):
        """Test adding a pxe interface to a host
        """
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp51",
                                        mac=None, ip=None)
        interface.pxe_priority = 1

        self.node.add_interface(interface)
        result_interface = self.node.interfaces["swp51"]
        assert result_interface.hostname == "leaf01"
        assert result_interface.interface_name == "swp51"
        assert result_interface.mac is None
        assert result_interface.ip is None
        assert self.node.has_pxe_interface


    @raises(SystemExit)
    def test_add_interface_two_pxe(self):
        """Test adding a second pxe interface to a host
        """
        interface1 = tc.NetworkInterface(hostname="leaf01",
                                         interface_name="swp51",
                                         mac=None, ip=None)
        interface1.pxe_priority = 1

        interface2 = tc.NetworkInterface(hostname="leaf01",
                                         interface_name="swp52",
                                         mac=None, ip=None)
        interface2.pxe_priority = 1

        self.node.add_interface(interface1)
        self.node.add_interface(interface2)


    def test_str_all_values(self):
        """Test that print output is as expected with all values set
        """
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp51",
                                        mac=None, ip=None)

        self.node.os_version = "3.4.3"
        self.node.other_attributes = {"superspine": "True"}
        self.node.add_interface(interface)
        output = []
        output.append("Hostname: " + "leaf01")
        output.append("Function: " + "leaf")
        output.append("OS: " + "CumulusCommunity/cumulus-vx")
        output.append("OS Version: " + "3.4.3")
        output.append("Memory: " + "768")
        output.append("Config: " + "./helper_scripts/oob_switch_config.sh")
        output.append("Libvirt Tunnel IP: " + "127.0.0.1")
        output.append("Attributes: " + str({"superspine": "True"}))
        output.append("Interfaces: " + str({"swp51": interface}))
        expected_result = "\n".join(output)
        assert expected_result == str(self.node)

    def test_str_no_values(self):
        """Test that string output is correct with no values set
        """
        self.node.hostname = None
        self.node.function = None
        self.node.vm_os = None
        self.node.os_version = None
        self.node.memory = None
        self.node.config = None
        self.node.tunnel_ip = None
        self.node.other_attributes = None
        self.node.interfaces = None

        output = []
        output.append("Hostname: " + "None")
        output.append("Function: " + "None")
        output.append("OS: " + "None")
        output.append("OS Version: " + "None")
        output.append("Memory: " + "None")
        output.append("Config: " + "None")
        output.append("Libvirt Tunnel IP: " + "None")
        output.append("Attributes: " + "None")
        output.append("Interfaces: " + "None")

        expected_result = "\n".join(output)
        assert expected_result == str(self.node)
