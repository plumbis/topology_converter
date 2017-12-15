#!/usr/bin/env python
import topology_converter as tc
import pydotplus as dot


def test_simple_valid_edge():
    # "leaf01":"swp49" -- "leaf02":"swp49"
    edge = dot.graphviz.Edge("\"leaf01\":\"swp49\"", "\"leaf02\":\"swp49\"")

    result = ({"hostname": "leaf01", "interface": "swp49", "mac": None},
              {"hostname": "leaf02", "interface": "swp49", "mac": None})

    assert tc.graphviz_edge_to_tuple(edge) == result


def test_left_mac_attribute():
    # "leaf01":"swp51" -- "spine01":"swp1" [left_mac="00:03:00:11:11:01"]
    edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp5\"")
    edge.obj_dict["attributes"]["left_mac"] = "00:03:00:11:11:01"

    result = ({"hostname": "leaf01", "interface": "swp51", "mac": "000300111101"},
              {"hostname": "spine01", "interface": "swp5", "mac": None})

    assert tc.graphviz_edge_to_tuple(edge) == result


def test_right_mac_attribute():
    # "leaf01":"swp51" -- "spine01":"swp1" [right_mac="00:03:00:11:11:01"]
    edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp5\"")
    edge.obj_dict["attributes"]["right_mac"] = "00:03:00:11:11:01"

    result = ({"hostname": "leaf01", "interface": "swp51", "mac": None},
              {"hostname": "spine01", "interface": "swp5", "mac": "000300111101"})

    assert tc.graphviz_edge_to_tuple(edge) == result


def test_generic_attribute():
    # "leaf01":"swp51" -- "spine01":"swp1" [right_mac="00:03:00:11:11:01"]
    edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp5\"")
    edge.obj_dict["attributes"]["superspine"] = "True"

    result = ({"hostname": "leaf01", "interface": "swp51", "mac": None, "superspine": "True"},
              {"hostname": "spine01", "interface": "swp5", "mac": None, "superspine": "True"})

    assert tc.graphviz_edge_to_tuple(edge) == result


def test_generic_left_attribute():
    # "leaf01":"swp51" -- "spine01":"swp1" [right_mac="00:03:00:11:11:01"]
    edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp5\"")
    edge.obj_dict["attributes"]["left_superspine"] = "True"

    result = ({"hostname": "leaf01", "interface": "swp51", "mac": None, "superspine": "True"},
              {"hostname": "spine01", "interface": "swp5", "mac": None})

    assert tc.graphviz_edge_to_tuple(edge) == result


def test_generic_right_attribute():
    # "leaf01":"swp51" -- "spine01":"swp1" [right_mac="00:03:00:11:11:01"]
    edge = dot.graphviz.Edge("\"leaf01\":\"swp51\"", "\"spine01\":\"swp5\"")
    edge.obj_dict["attributes"]["right_superspine"] = "True"

    result = ({"hostname": "leaf01", "interface": "swp51", "mac": None},
              {"hostname": "spine01", "interface": "swp5", "mac": None, "superspine": "True"})

    assert tc.graphviz_edge_to_tuple(edge) == result
