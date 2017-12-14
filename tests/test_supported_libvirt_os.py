#!/usr/bin/env python

import topology_converter as tc


def test_boxcutter_16_04():
    node = {"function": "host",
            "os": "boxcutter/ubuntu1604",
            "config": "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh",
            "memory": "512"
            }

    assert tc.supported_libvirt_os(node) is False


def test_bento_16_04():
    node = {"function": "host",
            "os": "bento/ubuntu-16.04",
            "config": "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh",
            "memory": "512"
            }

    assert tc.supported_libvirt_os(node) is False


def test_xenial64():
    node = {"function": "host",
            "os": "ubuntu/xenial64",
            "config": "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh",
            "memory": "512"
            }

    assert tc.supported_libvirt_os(node) is False


def test_CumulusVx():
    node = {"function": "host",
            "os": "CumulusCommunity/cumulus-vx",
            "config": "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh",
            "memory": "512"
            }

    assert tc.supported_libvirt_os(node) is True


def test_yk0_xenial():
    node = {"function": "host",
            "os": "yk0/ubuntu-xenial",
            "config": "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh",
            "memory": "512"
            }

    assert tc.supported_libvirt_os(node) is True


def test_None():
    node = {"function": "host",
            "os": "None",
            "config": "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh",
            "memory": "512"
            }

    assert tc.supported_libvirt_os(node) is True
