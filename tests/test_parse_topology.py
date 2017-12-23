#!/usr/bin/env python
from nose.tools import raises
import topology_converter as tc
import pydotplus as dot
import pprint


# Create a CLI to set verbose to True/False
class CLI:

    def __init__(self):

        self.verbose = False
        self.provider = "virtualbox"


class Test_nodes:
    def setup(self):
        """Setup the environment based on the simple.dot file.
        Populate the "mac" value with an empty set
        """
        topology = dot.graphviz.graph_from_dot_file("tests/dot_files/simple.dot")
        self.nodes = topology.get_node_list()
        self.expected_inventory = dict()
        self.expected_inventory["macs"] = set()

    # def test_simple_topology(self):
    #     cli = CLI()
    #     cli.topology_file = "tests/dot_files/simple.dot"
    #     tc.parse_topology(cli)

    #     assert True

   # @raises will catch non-zero exit code
    @raises(SystemExit)
    def test_failed_linting(self):
        """Test a a file that fails linting
        The actual lint coverage is in test_lint_topo_file
        This is to validate exit
        """
        cli = CLI()
        cli.topology_file = "tests/dot_files/bad_quotes.dot"
        tc.parse_topology(cli)
