#!/usr/bin/env python
"""Test suite for the topology converter command line arguments
"""
# pylint: disable=C0103
from nose.tools import raises
import topology_converter as tc

class TestCLI(object):  # pylint: disable=W0612
    """Test suite for the CLI() topology converter object
    """

    def setup(self):
        """Test setup. Start with a blank Inventory object
        """
        self.short_parser = tc.parse_arguments()  # pylint: disable=W0201
        self.long_parser = tc.parse_arguments()  # pylint: disable=W0201


    def test_topology_file_only(self):
        """Test passing a topology_file argument is successful
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot"])
        assert parsed.topology_file == "tests/simple.dot"
        assert not parsed.verbose
        assert parsed.provider == "virtualbox"
        assert not parsed.ansible_hostfile
        assert not parsed.create_mgmt_network
        assert not parsed.create_mgmt_configs_only
        assert not parsed.create_mgmt_device
        assert not parsed.template
        assert parsed.start_port == 8000
        assert parsed.port_gap == 1000
        assert not parsed.display_datastructures
        assert not parsed.synced_folder


    def test_verbose(self):
        """Test setting the verbose flag
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot", "-v"])
        assert parsed.topology_file == "tests/simple.dot"
        assert parsed.verbose

        long_parse = self.long_parser.parse_args(["tests/simple.dot", "--verbose"])
        assert long_parse.verbose

    def test_provider_libvirt(self):
        """Test setting the provider flag for libvirt
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot", "-p", "libvirt"])
        assert parsed.topology_file == "tests/simple.dot"
        assert parsed.provider == "libvirt"

        long_parse = self.long_parser.parse_args(["tests/simple.dot", "--provider", "libvirt"])
        assert long_parse.provider == "libvirt"

    def test_provider_virtualbox(self):
        """Test setting the provider flag for virtualbox
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot", "-p", "virtualbox"])
        assert parsed.topology_file == "tests/simple.dot"
        assert parsed.provider == "virtualbox"

        long_parse = self.long_parser.parse_args(["tests/simple.dot", "--provider", "virtualbox"])
        assert long_parse.provider == "virtualbox"

    @raises(SystemExit)
    def test_provider_invalid_short(self):
        """Test that an invalid provider with -p exits
        """
        self.short_parser.parse_args(["tests/simple.dot", "-p", "bogus"])


    @raises(SystemExit)
    def test_provider_invalid_long(self):
        """Test that an invalid provider with --provider exits
        """
        self.long_parser.parse_args(["tests/simple.dot", "--provider", "bogus"])

    def test_ansible_hostfile(self):
        """Test setting an ansible hostfile
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot", "-a"])
        assert parsed.topology_file == "tests/simple.dot"
        assert parsed.ansible_hostfile

        long_parse = self.long_parser.parse_args(["tests/simple.dot", "--ansible-hostfile"])
        assert long_parse.ansible_hostfile

    def test_create_management_network(self):
        """Test creating a management network
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot", "-c"])
        assert parsed.topology_file == "tests/simple.dot"
        assert parsed.create_mgmt_network

        long_parse = self.long_parser.parse_args(["tests/simple.dot", "--create-mgmt-network"])
        assert long_parse.create_mgmt_network

    def test_create_management_configs(self):
        """Test creating a management configs only
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot", "-cco"])
        assert parsed.topology_file == "tests/simple.dot"
        assert parsed.create_mgmt_configs_only

        long_parse = self.long_parser.parse_args(["tests/simple.dot", "--create-mgmt-configs-only"])
        assert long_parse.create_mgmt_configs_only

    def test_create_management_device(self):
        """Test creating a management device
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot", "-cmd"])
        assert parsed.topology_file == "tests/simple.dot"
        assert parsed.create_mgmt_device

        long_parse = self.long_parser.parse_args(["tests/simple.dot", "--create-mgmt-device"])
        assert long_parse.create_mgmt_device

    def test_template_correct_args(self):
        """Test template argument with valid arguments
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot", "-t", "test.j2", "Vagrantfile"])
        assert parsed.topology_file == "tests/simple.dot"
        assert parsed.template == [["test.j2", "Vagrantfile"]]

        long_parse = self.long_parser.parse_args(
            ["tests/simple.dot", "--template", "test.j2", "Vagrantfile"])
        assert long_parse.template == [["test.j2", "Vagrantfile"]]

    @raises(SystemExit)
    def test_template_short_invalid_args(self):  # pylint: disable=C0103
        """Test that -t without a template file exits
        """
        self.short_parser.parse_args(["tests/simple.dot", "-t"])


    @raises(SystemExit)
    def test_template_long_invalid_args(self):
        """Test that --template without a template file exits
        """
        self.long_parser.parse_args(["tests/simple.dot", "--template", "test.j2"])

    def test_start_port(self):
        """Test start_port argumement
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot", "-s", "1024"])
        assert parsed.topology_file == "tests/simple.dot"
        assert parsed.start_port == 1024

        long_parse = self.long_parser.parse_args(["tests/simple.dot", "--start-port", "1024"])
        assert long_parse.start_port == 1024

    def test_port_gap(self):
        """Test port gap argumement
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot", "-g", "4096"])
        assert parsed.topology_file == "tests/simple.dot"
        assert parsed.port_gap == 4096

        long_parse = self.long_parser.parse_args(["tests/simple.dot", "--port-gap", "4096"])
        assert long_parse.port_gap == 4096

    def test_display_datastructures(self):
        """Test display datastructures argumement
        """
        parsed = self.short_parser.parse_args(["tests/simple.dot", "-dd"])
        assert parsed.topology_file == "tests/simple.dot"
        assert parsed.display_datastructures

        long_parse = self.long_parser.parse_args(["tests/simple.dot", "--display-datastructures"])
        assert long_parse.display_datastructures

    def test_synced_folder(self):
        """Test synced-folder argumement
        """
        long_parse = self.long_parser.parse_args(["tests/simple.dot", "--synced-folder"])
        assert long_parse.synced_folder
