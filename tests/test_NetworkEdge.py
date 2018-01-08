#!/usr/bin/env python

import topology_converter as tc

class Test_NetworkEdge:

    def test_init(self):
        left_interface = tc.NetworkInterface(hostname="leaf01", interface_name="swp51", mac=None, ip=None )
        right_interface = tc.NetworkInterface(hostname="spine01", interface_name="swp1", mac=None, ip=None )

        edge = tc.NetworkEdge(left_interface, right_interface)

        assert edge.left_side == left_interface
        assert edge.right_side == right_interface



