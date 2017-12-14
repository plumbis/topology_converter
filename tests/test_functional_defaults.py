#!/usr/bin/env python

import topology_converter as tc

test_dict = {"os": "CumulusCommunity/cumulus-vx",
             "memory": "512",
             "config": "./helper_scripts/extra_switch_config.sh"}


def test_fake():
    test_dict["os"] = "None"
    test_dict["memory"] = "1"
    del test_dict["config"]

    assert tc.get_function_defaults("fake") == test_dict


def test_oob_server():
    test_dict["os"] = "yk0/ubuntu-xenial"
    test_dict["memory"] = "512"
    test_dict["config"] = "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh"

    assert tc.get_function_defaults("oob-server") == test_dict


def test_oob_switch():
    test_dict["os"] = "CumulusCommunity/cumulus-vx"
    test_dict["memory"] = "512"
    test_dict["config"] = "./helper_scripts/oob_switch_config.sh"

    assert tc.get_function_defaults("oob-switch") == test_dict


def test_host():
    test_dict["os"] = "yk0/ubuntu-xenial"
    test_dict["memory"] = "512"
    test_dict["config"] = "./helper_scripts/extra_server_config.sh"

    assert tc.get_function_defaults("host") == test_dict


def test_pxehost():
    test_dict["os"] = "None"
    test_dict["memory"] = "512"
    test_dict["config"] = "./helper_scripts/extra_server_config.sh"

    assert tc.get_function_defaults("pxehost") == test_dict


def test_other():
    test_dict["os"] = "CumulusCommunity/cumulus-vx"
    test_dict["memory"] = "512"
    test_dict["config"] = "./helper_scripts/extra_switch_config.sh"

    assert tc.get_function_defaults("MyHost") == test_dict


def test_quotes():
    test_dict["os"] = "CumulusCommunity/cumulus-vx"
    test_dict["memory"] = "512"
    test_dict["config"] = "./helper_scripts/oob_switch_config.sh"

    assert tc.get_function_defaults("\"oob-switch\"") == test_dict
