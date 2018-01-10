#!/usr/bin/env python
"""Test suite for topology_converter.NetworkInterface class
"""
# pylint: disable=C0103
from nose.tools import raises
import topology_converter as tc


class TestNetworkInterface(object):   # pylint: disable=W0232, C0103
    """Class for NetworkInterface test suite
    """
    def test_init(self):  # pylint: disable=R0201
        """Setup baseline interface object for testing
        """
        interface = tc.NetworkInterface(
            hostname="leaf01", interface_name="swp51", mac=None, ip=None)

        assert interface.hostname == "leaf01"
        assert interface.interface_name == "swp51"
        assert interface.mac is None

    def test_remove_interface_slash(self):  # pylint: disable=R0201
        """Test that an interface with a / in the name is changed to -
        """
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp5/1",
                                        mac=None,
                                        ip=None)

        assert interface.hostname == "leaf01"
        assert interface.interface_name == "swp5-1"
        assert interface.mac is None

    def test_add_attribute(self):  # pylint: disable=R0201
        """Test that an attribute is properly added to an interface
        """
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp51",
                                        mac=None,
                                        ip=None)
        attribute = {"newattribute": "some value"}
        interface.add_attribute(attribute)

        assert interface.hostname == "leaf01"
        assert interface.interface_name == "swp51"
        assert interface.mac is None
        assert interface.attributes == attribute


    def test_valid_mac(self):  # pylint: disable=R0201
        """Test that valid mac formats are accepted
        """
        valid_macs = ["443839ff0000", "44:38:39:ff:00:00", "44.38.39.ff.00.00", "4438.39ff.0000"]
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp51",
                                        mac=None, ip=None)
        for mac in valid_macs:
            print mac
            assert interface.validate_mac(mac) == "443839ff0000"


    def test_invalid_mac_generator(self):
        """Generator for testing invalid macs
        """
        invalid_macs = ["443839zz0000", "01005e000000", "ffffffffffff", "000000000000", "0000",
                        "00000000000000", "0000beefcake"]

        for mac in invalid_macs:
            yield self.invalid_mac_values, mac

    @raises(SystemExit)
    def invalid_mac_values(self, mac):  # pylint: disable=R0201
        """Invalid macs cause system exit
        """
        tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=mac, ip=None)

    def test_print_simple_interface(self):  # pylint: disable=R0201
        """Verify print output
        """
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp51",
                                        mac="443839000000",
                                        ip="10.1.1.1")
        interface.network = "NetA"
        interface.local_port = "1024"
        interface.remote_port = "9024"

        output = []
        output.append("Hostname: " + interface.hostname)
        output.append("interface_name: " + interface.interface_name)
        output.append("IP: " + interface.ip)
        output.append("MAC: " + interface.mac)
        output.append("Network: " + interface.network)
        output.append("Libvirt localport: " + interface.local_port)
        output.append("Libvirt remote port: " + interface.remote_port)
        output.append("PXE Priority: " + "0")
        output.append("Attributes: " + str({}))

        assert str(interface) == "\n".join(output)

    def test_print_none_hostname(self):  # pylint: disable=R0201
        """Verify print output without a hostname defined
        """
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp51",
                                        mac=None,
                                        ip=None)

        interface.hostname = None
        output = []
        output.append("Hostname: " + "None")
        output.append("interface_name: " + interface.interface_name)
        output.append("IP: " + "None")
        output.append("MAC: " + "None")
        output.append("Network: " + "None")
        output.append("Libvirt localport: " + "None")
        output.append("Libvirt remote port: " + "None")
        output.append("PXE Priority: " + "0")
        output.append("Attributes: " + str({}))

        assert str(interface) == "\n".join(output)

    def test_print_none_interface(self):  # pylint: disable=R0201
        """Verify print output without an interface defined
        """
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp51",
                                        mac=None,
                                        ip=None)

        interface.interface_name = None
        output = []
        output.append("Hostname: " + interface.hostname)
        output.append("interface_name: " + "None")
        output.append("IP: " + "None")
        output.append("MAC: " + "None")
        output.append("Network: " + "None")
        output.append("Libvirt localport: " + "None")
        output.append("Libvirt remote port: " + "None")
        output.append("PXE Priority: " + "0")
        output.append("Attributes: " + str({}))

        assert str(interface) == "\n".join(output)


    def test_print_none_attributes_interface(self):  # pylint: disable=R0201
        """Verify print output with attributes as None
        """
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp51",
                                        mac=None,
                                        ip=None)

        interface.attributes = None
        output = []
        output.append("Hostname: " + interface.hostname)
        output.append("interface_name: " + interface.interface_name)
        output.append("IP: " + "None")
        output.append("MAC: " + "None")
        output.append("Network: " + "None")
        output.append("Libvirt localport: " + "None")
        output.append("Libvirt remote port: " + "None")
        output.append("PXE Priority: " + "0")
        output.append("Attributes: " + "None")

        assert str(interface) == "\n".join(output)


    def test_print_none_pxe(self):  # pylint: disable=R0201
        """Verify print output with pxepirority as none
        """
        interface = tc.NetworkInterface(hostname="leaf01",
                                        interface_name="swp51",
                                        mac=None,
                                        ip=None)

        interface.pxe_priority = None
        output = []
        output.append("Hostname: " + interface.hostname)
        output.append("interface_name: " + interface.interface_name)
        output.append("IP: " + "None")
        output.append("MAC: " + "None")
        output.append("Network: " + "None")
        output.append("Libvirt localport: " + "None")
        output.append("Libvirt remote port: " + "None")
        output.append("PXE Priority: " + "None")
        output.append("Attributes: " + str({}))

        assert str(interface) == "\n".join(output)
