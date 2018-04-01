#!/usr/bin/env python
"""Test suite for validating the oob_mgmt_switch_provisioner.j2 template
"""
# pylint: disable=C0103
import topology_converter as tc

class TestOobSwitchProvisionerJinja(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the OOB Switch provisioner jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize the tests with a basic CLI
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/oob_mgmt_switch_provisioner.j2",
                                                    "Vagrantfile"])

    def test_oob_switch_provisioner_output(self): # pylint: disable=R0201
        """Test generating the oob swtich provisioner jinja template
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_vagrantfile(inventory, "./templates/", self.cli)

        expected_result = []
        expected_result.append("")
        expected_result.append(" ")
        expected_result.append("    # Transfer Bridge File")
        expected_result.append("    device.vm.provision \"file\", source: \"./helper_scripts/auto_mgmt_network/bridge-untagged\", destination: \"~/bridge-untagged\"")  # pylint: disable=C0301
        expected_result.append("    device.vm.provision :shell , path: \"./helper_scripts/oob_switch_config.sh\"")  # pylint: disable=C0301

        print repr(result)
        print ""
        print repr("\n".join(expected_result))
        assert result == "\n".join(expected_result)
