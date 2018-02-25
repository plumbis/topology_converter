#!/usr/bin/env python
"""Test suite for topology_converter.NetworkNode class
"""
# C0103 name doesn't confirm to snake case naming style
# R0201 method could be a function
# pylint: disable=C0103,R0201
import ipaddress
from nose.tools import raises
import topology_converter as tc

class Test_NetworkNode(object): # pylint: disable=R0904
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

    def test_init_minimum_settings(self):
        """Test buildinga  NetworkNode with only the required settings.
        """
        node = tc.NetworkNode(
            hostname="leaf01",
            function="leaf",
            memory="768")

        assert node.hostname == "leaf01"
        assert node.function == "leaf"
        assert node.vm_os is None
        assert node.os_version is None
        assert node.memory == "768"
        assert node.config is None
        assert node.libvirt_local_ip == "127.0.0.1"
        assert not node.playbook
        assert not node.pxehost
        assert node.remap
        assert not node.ports
        assert node.vagrant_interface == "vagrant"
        assert node.vagrant_user == "vagrant"
        assert not node.legacy

    def test_init_all_settings(self):
        """Test building a NetworkNode with all optional settings.
        """
        node = tc.NetworkNode(
            hostname="leaf01",
            function="leaf",
            vm_os="CumulusCommunity/cumulus-vx",
            os_version="3.5.1",
            memory="768",
            config="./helper_scripts/oob_switch_config.sh",
            libvirt_local_ip="127.0.0.1",
            other_attributes={
                "playbook":"scripts/ansible_playbook.yml",
                "pxehost":"True",
                "remap":"False",
                "ports":"32",
                "ssh_port":"1025",
                "vagrant":"eth0",
                "vagrant_user":"cumulus",
                "legacy":"True"
            })

        assert node.hostname == "leaf01"
        assert node.function == "leaf"
        assert node.vm_os == "CumulusCommunity/cumulus-vx"
        assert node.os_version == "3.5.1"
        assert node.memory == "768"
        assert node.config == "./helper_scripts/oob_switch_config.sh"
        assert node.libvirt_local_ip == "127.0.0.1"
        assert node.playbook == "scripts/ansible_playbook.yml"
        assert node.pxehost
        assert not node.remap
        assert node.ports == "32"
        assert node.vagrant_interface == "eth0"
        assert node.vagrant_user == "cumulus"
        assert node.legacy


    def test_check_hostname_valid(self):
        """Test valid hostnames are accepted and returns True
        """
        for hostname in self.valid_hostnames:
            assert self.node.check_hostname(hostname) is True


    @raises(SystemExit)
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

    @raises(SystemExit)
    def test_zero_ports(self):
        """Test that setting ports to zero causes exit
        """
        tc.NetworkNode(
            hostname="leaf01",
            function="leaf",
            memory="768",
            other_attributes={
                "ports":"0",
            })

    @raises(SystemExit)
    def test_non_number_ports(self):
        """Test that setting ports to non-int causes exit
        """
        tc.NetworkNode(
            hostname="leaf01",
            function="leaf",
            memory="768",
            other_attributes={
                "ports":"rocketturtle",
            })

    @raises(SystemExit)
    def test_zero_ssh_port(self):
        """Test that setting ssh_port to zero causes exit
        """
        tc.NetworkNode(
            hostname="leaf01",
            function="leaf",
            memory="768",
            other_attributes={
                "ssh_port":"0",
            })

    @raises(SystemExit)
    def test_less_than_1024_ssh_port(self):
        """Test that setting ssh_port to <1024 causes exit
        """
        tc.NetworkNode(
            hostname="leaf01",
            function="leaf",
            memory="768",
            other_attributes={
                "ssh_port":"22",
            })

    @raises(SystemExit)
    def test_non_number_ssh_port(self):
        """Test that setting ssh_port to non-int causes exit
        """
        tc.NetworkNode(
            hostname="leaf01",
            function="leaf",
            memory="768",
            other_attributes={
                "ssh_port":"rocketturtle",
            })

    @raises(SystemExit)
    def test_get_node_mgmt_ip_invalid(self):
        """Test setting an invalid management IP
        """
        tc.NetworkNode(
            hostname="leaf01",
            function="leaf",
            memory="768",
            other_attributes={
                "mgmt_ip":"rocketturtle",
            })

    def test_get_node_mgmt_ip_with_mask(self):
        """Test setting a management IP with a subnet mask
        """
        test_node = tc.NetworkNode(
            hostname="leaf01",
            function="leaf",
            memory="768",
            other_attributes={
                "mgmt_ip":"10.1.1.1/24",
            })

        assert test_node.mgmt_ip == ipaddress.ip_interface(u"10.1.1.1/24")

    def test_get_node_mgmt_ip_without_mask(self):
        """Test setting a management IP withtout a subnet mask
        """
        test_node = tc.NetworkNode(
            hostname="leaf01",
            function="leaf",
            memory="768",
            other_attributes={
                "mgmt_ip":"10.1.1.1",
            })

        assert test_node.mgmt_ip == ipaddress.ip_interface(u"10.1.1.1/24")
