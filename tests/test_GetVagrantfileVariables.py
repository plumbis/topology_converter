#!/usr/bin/env python
"""Test suite for generating variables to be used in the Vagrantfile
"""
# pylint: disable=C0103
import topology_converter as tc

class TestGetVagrantFileVariables(object):  # pylint: disable=W0612,R0903
    """Test suite for generating variables to be used inside the Vagrantfile jinja2 template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize the tests with a basic CLI
        """
        self.cli = tc.parse_arguments()
        self.known_functions = ["oob-server", "oob-switch", "exit", "superspine",
                                "spine", "leaf", "tor", "host"]

    def test_variables_simple_topology(self): # pylint: disable=R0201
        """Test generating the Vagrant for the simple topology.dot
        """
        cli = self.cli.parse_args(["tests/simple.dot", "-p", "virtualbox", "-a"])
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)

        result = tc.get_vagrantfile_variables(inventory, cli)

        assert "epoch_time" in result
        assert result["known_functions"] == self.known_functions

        # Only leaf and spine functions
        assert len(result["nodes"].keys()) == 2

        # Spine should be ordered first based on boot order
        assert result["nodes"].keys()[0] == "spine"
        assert result["nodes"].keys()[1] == "leaf"

        # The only spine should be spine01
        assert len(result["nodes"]["spine"]) == 1
        assert result["nodes"]["spine"][0].hostname == "spine01"

        # Verify that only four leafs exist
        # and they are the expected hosts
        leaf_hostnames = ["leaf01", "leaf02", "leaf03", "leaf04"]
        assert len(result["nodes"]["leaf"]) == 4
        for node in result["nodes"]["leaf"]:
            assert node.hostname in leaf_hostnames

    def test_variables_reference_topology(self): # pylint: disable=R0201
        """Test generating the Vagrant for the reference topology
        """
        cli = self.cli.parse_args(["tests/simple.dot", "-p", "virtualbox", "-a"])
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)

        result = tc.get_vagrantfile_variables(inventory, cli)

        assert "epoch_time" in result
        assert result["known_functions"] == self.known_functions

        # Leaf, Spine, OOB switch, OOB Server, exit, internet, hosts
        assert len(result["nodes"].keys()) == 7

        # Spine should be ordered first based on boot order
        assert result["nodes"].keys()[0] == "oob-server"
        assert result["nodes"].keys()[1] == "oob-switch"
        assert result["nodes"].keys()[2] == "exit"
        assert result["nodes"].keys()[3] == "spine"
        assert result["nodes"].keys()[4] == "leaf"
        assert result["nodes"].keys()[5] == "host"
        assert result["nodes"].keys()[6] == "internet"

        # 1 oob-server
        assert len(result["nodes"]["oob-server"]) == 1
        # 1 oob-switch
        assert len(result["nodes"]["oob-switch"]) == 1
        # 2 Exit
        assert len(result["nodes"]["exit"]) == 2
        # 2 Spines
        assert len(result["nodes"]["spine"]) == 2
        # 4 Leafs
        assert len(result["nodes"]["leaf"]) == 4
        # 5 Host
        assert len(result["nodes"]["host"]) == 5
        # 1 Internet
        assert len(result["nodes"]["internet"]) == 1

        oob_server_names = ["oob-mgmt-server"]
        oob_switch_names = ["oob-mgmt-switch"]
        exit_names = ["exit01", "exit02"]
        spine_names = ["spine01", "spine02"]
        leaf_names = ["leaf01", "leaf02", "leaf03", "leaf04"]
        host_names = ["server01", "server02", "server03", "server04", "edge01"]
        internet_names = ["internet"]

        for node in result["nodes"]["oob-server"]:
            assert node.hostname in oob_server_names

        for node in result["nodes"]["oob-switch"]:
            assert node.hostname in oob_switch_names

        for node in result["nodes"]["exit"]:
            assert node.hostname in exit_names

        for node in result["nodes"]["spine"]:
            assert node.hostname in spine_names

        for node in result["nodes"]["leaf"]:
            assert node.hostname in leaf_names

        for node in result["nodes"]["host"]:
            assert node.hostname in host_names

        for node in result["nodes"]["internet"]:
            assert node.hostname in internet_names

    def test_variables_fake_node(self): # pylint: disable=R0201
        """Test generating the variables for a topology with a fake device
        """
        cli = self.cli.parse_args(["tests/simple.dot", "-p", "virtualbox", "-a"])
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.add_node(tc.NetworkNode(hostname="fake01", memory="768", function="fake"))
        result = tc.get_vagrantfile_variables(inventory, cli)

        assert "epoch_time" in result
        assert result["known_functions"] == self.known_functions

        # Only leaf and spine functions
        assert len(result["nodes"].keys()) == 2

        # Spine should be ordered first based on boot order
        assert result["nodes"].keys()[0] == "spine"
        assert result["nodes"].keys()[1] == "leaf"

        # The only spine should be spine01
        assert len(result["nodes"]["spine"]) == 1
        assert result["nodes"]["spine"][0].hostname == "spine01"

        # Verify that only four leafs exist
        # and they are the expected hosts
        leaf_hostnames = ["leaf01", "leaf02", "leaf03", "leaf04"]
        assert len(result["nodes"]["leaf"]) == 4
        for node in result["nodes"]["leaf"]:
            assert node.hostname in leaf_hostnames


    def test_variables_tor_node(self): # pylint: disable=R0201
        """Test generating the variables for a topology with a fake device
        """
        cli = self.cli.parse_args(["tests/simple.dot", "-p", "virtualbox", "-a"])
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.add_node(tc.NetworkNode(hostname="tor01", memory="768", function="tor"))
        result = tc.get_vagrantfile_variables(inventory, cli)

        assert "epoch_time" in result
        assert result["known_functions"] == self.known_functions

        # Only leaf, spine and tor functions
        assert len(result["nodes"].keys()) == 3

        # Spine should be ordered first based on boot order
        assert result["nodes"].keys()[0] == "spine"
        assert result["nodes"].keys()[1] == "leaf"
        assert result["nodes"].keys()[2] == "tor"

        # The only spine should be spine01
        assert len(result["nodes"]["spine"]) == 1
        assert result["nodes"]["spine"][0].hostname == "spine01"

        # Verify that only four leafs exist
        # and they are the expected hosts
        leaf_hostnames = ["leaf01", "leaf02", "leaf03", "leaf04"]
        assert len(result["nodes"]["leaf"]) == 4
        for node in result["nodes"]["leaf"]:
            assert node.hostname in leaf_hostnames

        assert len(result["nodes"]["tor"]) == 1

    def test_variables_superspine_node(self): # pylint: disable=R0201
        """Test generating the variables for a topology with a superspine device
        """
        cli = self.cli.parse_args(["tests/simple.dot", "-p", "virtualbox", "-a"])
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.add_node(tc.NetworkNode(hostname="superspine",
                                          memory="768", function="superspine"))
        result = tc.get_vagrantfile_variables(inventory, cli)

        assert "epoch_time" in result
        assert result["known_functions"] == self.known_functions

        # Only leaf, spine and superspine functions
        assert len(result["nodes"].keys()) == 3

        # Superspine should be ordered first based on boot order
        assert result["nodes"].keys()[0] == "superspine"
        assert result["nodes"].keys()[1] == "spine"
        assert result["nodes"].keys()[2] == "leaf"


        # The only spine should be spine01
        assert len(result["nodes"]["spine"]) == 1
        assert result["nodes"]["spine"][0].hostname == "spine01"

        # Verify that only four leafs exist
        # and they are the expected hosts
        leaf_hostnames = ["leaf01", "leaf02", "leaf03", "leaf04"]
        assert len(result["nodes"]["leaf"]) == 4
        for node in result["nodes"]["leaf"]:
            assert node.hostname in leaf_hostnames

        assert len(result["nodes"]["superspine"]) == 1
