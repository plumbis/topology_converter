#!/usr/bin/env python
"""Test suite for validating the provider_config.j2 template
"""
# pylint: disable=C0103
import topology_converter as tc

class TestProviderConfig(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the provider config jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize the tests with a basic CLI
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/provider_config.j2",
                                                    "Vagrantfile"])

    def test_provider_config_virtualbox(self): # pylint: disable=R0201
        """Test generating the provider config jinja template for a virtualbox provider
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_vagrantfile(inventory, "./templates/", self.cli).splitlines()


        assert result[0] == "Vagrant.configure(\"2\") do |config|"
        assert result[1] == ""
        # simid is determined at runtime. Just make sure it's not a blank value
        assert len(result[2]) > 10
        assert result[3] == ""
        assert result[4] == "  config.vm.provider \"virtualbox\" do |v|"
        assert result[5] == "    v.gui = false"
        assert result[6] == "  end"
        assert result[7] == ""


    def test_provider_config_libvirt(self): # pylint: disable=R0201
        """Test generating the provider config jinja template for a libvirt provider
        """
        self.cli.provider = "libvirt"
        self.cli.start_port = "8000"
        self.cli.port_gap = "1000"
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_vagrantfile(inventory, "./templates/", self.cli)

        expected_result = []
        expected_result.append("Vagrant.configure(\"2\") do |config|")
        expected_result.append("")
        expected_result.append("  config.vm.provider :libvirt do |domain|")
        expected_result.append("    # increase nic adapter count to be greater than 8 for all VMs.")
        expected_result.append("    domain.nic_adapter_count = 130")
        expected_result.append("  end")
        expected_result.append("")
        expected_result.append("")

        print repr(result)
        print ""
        print repr("\n".join(expected_result))
        assert result == "\n".join(expected_result)
