#!/usr/bin/env python

import topology_converter as tc
from nose.tools import raises

class TestNetworkInterface:

    def test_init(self):
        interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )

        assert interface.hostname == "leaf01"
        assert interface.interface_name == "swp51"
        assert interface.mac == None

    def test_remove_interface_slash(self):
        interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp5/1", mac=None, ip=None )

        assert interface.hostname == "leaf01"
        assert interface.interface_name == "swp5-1"
        assert interface.mac == None

    def test_add_attribute(self):
        interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )
        attribute = {"newattribute": "some value"}
        interface.add_attribute(attribute)

        assert interface.hostname == "leaf01"
        assert interface.interface_name == "swp51"
        assert interface.mac == None
        assert interface.attributes == attribute


    def test_valid_mac(self):
        valid_macs = ["443839ff0000", "44:38:39:ff:00:00", "44.38.39.ff.00.00", "4438.39ff.0000"]
        interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None)
        for mac in valid_macs:
            print mac
            assert interface.validate_mac(mac) == "443839ff0000"


    def test_invalid_mac_generator(self):
        invalid_macs = ["443839zz0000", "01005e000000", "ffffffffffff", "000000000000", "0000",
                        "00000000000000", "0000beefcake"]

        for mac in invalid_macs:
            yield self.invalid_mac_values, mac

    @raises(SystemExit)
    def invalid_mac_values(self, mac):
        tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=mac, ip=None)

    def test_print_simple_interface(self):
        interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac="443839000000", ip="10.1.1.1" )
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

    def test_print_none_hostname(self):
        interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )

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

    def test_print_none_interface(self):
        interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )

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

    def test_print_ip_interface(self):
        interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )

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

    def test_print_none_attributes_interface(self):
        interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )

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


    def test_print_none_pxe(self):
        interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )

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
