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
