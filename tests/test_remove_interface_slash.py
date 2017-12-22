#!/usr/bin/env python
import topology_converter as tc


def test_no_slash():

    edge = ({"hostname": "leaf01", "interface": "swp49", "mac": None},
            {"hostname": "leaf02", "interface": "swp49", "mac": None})

    result = ({"hostname": "leaf01", "interface": "swp49", "mac": None},
              {"hostname": "leaf02", "interface": "swp49", "mac": None})

    assert tc.remove_interface_slash(edge) == result


def test_right_slash():

    edge = ({"hostname": "leaf01", "interface": "swp49", "mac": None},
            {"hostname": "leaf02", "interface": "g0/0", "mac": None})

    result = ({"hostname": "leaf01", "interface": "swp49", "mac": None},
              {"hostname": "leaf02", "interface": "g0-0", "mac": None})

    assert tc.remove_interface_slash(edge) == result


def test_left_slash():

    edge = ({"hostname": "leaf01", "interface": "g0/0", "mac": None},
            {"hostname": "leaf02", "interface": "swp49", "mac": None})

    result = ({"hostname": "leaf01", "interface": "g0-0", "mac": None},
              {"hostname": "leaf02", "interface": "swp49", "mac": None})

    assert tc.remove_interface_slash(edge) == result


def test_double_slash():

    edge = ({"hostname": "leaf01", "interface": "g0/0", "mac": None},
            {"hostname": "leaf02", "interface": "g0/0", "mac": None})

    result = ({"hostname": "leaf01", "interface": "g0-0", "mac": None},
              {"hostname": "leaf02", "interface": "g0-0", "mac": None})

    assert tc.remove_interface_slash(edge) == result
