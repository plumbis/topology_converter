#!/usr/bin/env python
import topology_converter as tc
from nose.tools import raises


# Create a CLI to set verbose to True/False
class CLI:

    def __init__(self):

        self.verbose = True


class Test_first_mac:
    def setup(self):
        self.inventory = {}
        self.inventory["macs"] = set()
        self.inventory["leaf01"] = {"interfaces": {"swp49": None}}
        self.inventory["leaf01"].update({"function": "leaf"})
        self.inventory["leaf01"].update({"config": "./helper_scripts/config_switch.sh"})
        self.inventory["leaf01"].update({"version": "3.4.3"})
        self.inventory["leaf01"].update({"os": "CumulusCommunity/cumulus-vx"})
        self.inventory["leaf01"].update({"memory": "512"})

        self.edge1 = ({"hostname": "leaf01", "interface": "swp49", "mac": None},
                      {"hostname": "leaf02", "interface": "swp49", "mac": None})

        self.edge2 = ({"hostname": "leaf03", "interface": "swp49", "mac": None},
                      {"hostname": "leaf04", "interface": "swp49", "mac": None})

        self.edge3 = ({"hostname": "leaf05", "interface": "swp49", "mac": None},
                      {"hostname": "leaf06", "interface": "swp49", "mac": None})

    def test_first_mac(self):
        """Test assigning macs to a single edge
        """

        cli = CLI()

        updated_inventory, edge = tc.mac_fetch(self.edge1, self.inventory, cli)
        result_macs = set(["443839000000", "443839000001"])

        # Make sure they are the same length
        assert len(updated_inventory["macs"]) == len(result_macs)

        # Make sure the set contents are the same
        assert len(updated_inventory["macs"] - result_macs) == 0

    def test_two_macs(self):
        """Test assigning macs to a second edge
        """

        cli = CLI()

        updated_inventory, edge1 = tc.mac_fetch(self.edge1, self.inventory, cli)
        final_inventory, edge2 = tc.mac_fetch(self.edge2, updated_inventory, cli)
        result_macs = set(["443839000000", "443839000001", "443839000002", "443839000003"])

        assert len(final_inventory["macs"]) == len(result_macs)
        assert len(updated_inventory["macs"] - result_macs) == 0

    def test_one_user_mac_once(self):
        """Test assigning a mac when user provides one of the macs
        """
        cli = CLI()

        self.edge1[0]["mac"] = "0000deadbeef"

        updated_inventory, edge = tc.mac_fetch(self.edge1, self.inventory, cli)
        result_macs = set(["443839000000", "0000deadbeef"])

        # Make sure they are the same length
        assert len(updated_inventory["macs"]) == len(result_macs)

        # We can't guess really guess what the dynamically assigned mac will be
        # Since we might skip a mac. It's likely 0001 but not safe to assume

        assert "0000deadbeef" in updated_inventory["macs"]

    def test_one_user_mac_twice(self):
        """Test assigning a mac when user provides one of the macs. But twice
        """
        cli = CLI()

        self.edge1[0]["mac"] = "0000deadbeef"
        self.edge2[0]["mac"] = "0000ace0f00d"

        self.inventory, self.edge1 = tc.mac_fetch(self.edge1, self.inventory, cli)
        self.inventory, self.edge2 = tc.mac_fetch(self.edge2, self.inventory, cli)

        # 2 macs per edge
        assert len(self.inventory["macs"]) == 4
        assert "0000deadbeef" in self.inventory["macs"]
        assert "0000ace0f00d" in self.inventory["macs"]

    def test_two_user_macs_once(self):
        """Test assigning both user macs to a single edge
        """
        cli = CLI()
        self.edge1[0]["mac"] = "0000deadbeef"
        self.edge1[1]["mac"] = "0000ace0f00d"

        self.inventory, self.edge1 = tc.mac_fetch(self.edge1, self.inventory, cli)

        assert len(self.inventory["macs"]) == 2
        assert "0000deadbeef" in self.inventory["macs"]
        assert "0000ace0f00d" in self.inventory["macs"]

    # @raises will catch non-zero exit code
    @raises(SystemExit)
    def test_invalid_mac(self):
        """Test passing an invalid MAC
        """
        cli = CLI()
        self.edge1[0]["mac"] = "0000zzzz0000"
        self.edge1[1]["mac"] = "0000zzzz9999"
        tc.mac_fetch(self.edge1, self.inventory, cli)

    def test_two_user_one_auto_mac(self):
        cli = CLI()

        self.edge1[0]["mac"] = "0000deadbeef"
        self.edge2[0]["mac"] = "0000ace0f00d"

        self.inventory, self.edge1 = tc.mac_fetch(self.edge1, self.inventory, cli)
        self.inventory, self.edge2 = tc.mac_fetch(self.edge2, self.inventory, cli)
        self.inventory, self.edge3 = tc.mac_fetch(self.edge3, self.inventory, cli)

        # 2 macs per edge
        assert len(self.inventory["macs"]) == 6
        assert "0000deadbeef" in self.inventory["macs"]
        assert "0000ace0f00d" in self.inventory["macs"]
