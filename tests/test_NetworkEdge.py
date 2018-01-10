#!/usr/bin/env python
"""Test Suite for topology_converter.NetworkEdge class
"""
# pylint: disable=W0232, C0103, R0903
import topology_converter as tc

class Test_NetworkEdge(object):
    """Class test for NetworkEdge
    """
    def test_init(self):  # pylint: disable=R0201
        """Validate that an edge is properly created
        """
        left_interface = tc.NetworkInterface(
            hostname="leaf01", interface_name="swp51", mac=None, ip=None)
        right_interface = tc.NetworkInterface(
            hostname="spine01", interface_name="swp1", mac=None, ip=None)

        edge = tc.NetworkEdge(left_interface, right_interface)

        assert edge.left_side == left_interface
        assert edge.right_side == right_interface
