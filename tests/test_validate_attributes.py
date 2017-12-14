#!/usr/bin/env python

import topology_converter as tc


def test_os_present():
    node = {"function": "host",
            "os": "boxcutter/ubuntu1604",
            "config": "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh",
            "memory": "512"
            }

    assert tc.validate_attributes(node, "leaf01") is True


def test_os_not_present():
    node = {"function": "host",
            "config": "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh",
            "memory": "512"
            }

    assert tc.validate_attributes(node, "leaf01") is False


def test_negative_memory():
    node = {"function": "host",
            "os": "boxcutter/ubuntu1604",
            "config": "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh",
            "memory": "-1"
            }

    assert tc.validate_attributes(node, "leaf01") is False


def test_zero_memory():
    node = {"function": "host",
            "os": "boxcutter/ubuntu1604",
            "config": "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh",
            "memory": "0"
            }

    assert tc.validate_attributes(node, "leaf01") is False
