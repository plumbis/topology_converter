#!/usr/bin/env python
import topology_converter as tc


class CLI(object):

    def __init__(self):

        self.verbose = False


def test_add_colon():
    mac = "0000deadbeef"
    cli = CLI()

    assert tc.add_mac_colon(mac, cli) == "00:00:de:ad:be:ef"


def test_add_colon_verbose():
    mac = "0000deadbeef"
    cli = CLI()
    cli.verbose = True
    assert tc.add_mac_colon(mac, cli) == "00:00:de:ad:be:ef"
