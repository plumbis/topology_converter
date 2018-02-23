#!/usr/bin/env python
"""Test suite for validating the cumulus_os_provisioner.j2 template
"""
# pylint: disable=C0103
import topology_converter as tc

class TestCumulusOSProvisionerJinja(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the cumulus_os_provisioner jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initialize a basic CLI
        """
        self.cli = tc.parse_arguments().parse_args(["./tests/dot_files/reference_topology.dot",
                                                    "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/cumulus_os_provisioner.j2",
                                                    "Vagrantfile"])


    def test_ansible_playbook_jinja_reference_topology(self): # pylint: disable=R0201
        """Test generating the cumulus_os_provisioner jinja template for the reference topology
        """

        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_vagrantfile(inventory, "./templates/", self.cli)
        expected_result = []
        expected_result.append("")
        expected_result.append("#Copy over Topology.dot File")
        expected_result.append("device.vm.provision \"file\", source: \"./tests/dot_files/reference_topology.dot\", destination: \"~/topology.dot\"")  # pylint: disable=C0301
        expected_result.append("device.vm.provision :shell, privileged: false, inline: \"sudo mv ~/topology.dot /etc/ptm.d/topology.dot\"") # pylint: disable=C0301

        assert "\n".join(expected_result) == result
