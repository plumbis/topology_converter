#!/usr/bin/env python
"""Test suite for validating the header.j2 template
"""
# pylint: disable=C0103
import topology_converter as tc

class TestHeaderJinja(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the header jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize the tests with a basic CLI
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/header.j2",
                                                    "Vagrantfile"])

    def test_header_virtualbox_provider(self): # pylint: disable=R0201
        """Test generating the header jinja template for a virtualbox provider
        """
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_vagrantfile(inventory, "./templates/", self.cli)


        assert result == "#       -Virtualbox installed: https://www.virtualbox.org/wiki/Downloads"


    def test_header_libvirt_provider(self): # pylint: disable=R0201
        """Test generating the header jinja template for a libvirt provider
        """
        self.cli.provider = "libvirt"
        self.cli.start_port = "8000"
        self.cli.port_gap = "1000"
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_vagrantfile(inventory, "./templates/", self.cli)

        expected_result = []
        expected_result.append("#        - Libvirt Installed -- guide to come")
        expected_result.append("#        - Vagrant-Libvirt Plugin installed: $ vagrant plugin install vagrant-libvirt")  # pylint: disable=C0301
        expected_result.append("#        - Start with \"vagrant up --provider=libvirt --no-parallel\"")  # pylint: disable=C0301
        expected_result.append("#")
        expected_result.append("#  Libvirt Start Port: 8000")
        expected_result.append("#  Libvirt Port Gap: 1000")
        expected_result.append("")
        expected_result.append("# Set the default provider to libvirt in the case they forget")
        expected_result.append("# --provider=libvirt or if someone destroys a machine it reverts to virtualbox")  # pylint: disable=C0301
        expected_result.append("ENV['VAGRANT_DEFAULT_PROVIDER'] = 'libvirt'")
        expected_result.append("")
        expected_result.append("# Check required plugins")
        expected_result.append("REQUIRED_PLUGINS_LIBVIRT = %w(vagrant-libvirt)")
        expected_result.append("exit unless REQUIRED_PLUGINS_LIBVIRT.all? do |plugin|")
        expected_result.append("  Vagrant.has_plugin?(plugin) || (")
        expected_result.append("    puts \"The #{plugin} plugin is required. Please install it with:\"")  # pylint: disable=C0301
        expected_result.append("    puts \"$ vagrant plugin install #{plugin}\"")
        expected_result.append("    false")
        expected_result.append("  )")
        expected_result.append("end")

        print repr(result)
        print ""
        print repr("\n".join(expected_result))
        assert result == "\n".join(expected_result)
