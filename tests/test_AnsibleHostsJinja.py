#!/usr/bin/env python
"""Test suite for validating the ansible_hosts.j2 template
"""
# pylint: disable=C0103
import topology_converter as tc

class TestAnsibleGroupsJinja(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the ansible_hosts jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize the tests with a basic CLI
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/ansible_hosts.j2",
                                                    "Vagrantfile"])

    def test_ansible_jinja_simple_topology(self): # pylint: disable=R0201
        """Test generating the ansible jinja template for the simple topology.dot
        """
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_vagrantfile(inventory, "./templates/", self.cli)
        include_result = "./tests/expected_jinja_outputs/simple_ansible_groups_jinja"
        expected_output = []
        expected_output.append("  #Generating Ansible Host File at following location:")
        expected_output.append("  #    ./.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory")  # pylint: disable=C0301
        expected_output.append("  config.vm.provision \"ansible\" do |ansible|")
        expected_output.append("    ansible.playbook = \"./helper_scripts/empty_playbook.yml\"")
        expected_output.append("")
        expected_output.append("    " + open(include_result).read())
        expected_output.append("")
        expected_output.append("  end")
        expected_output.append("")

        assert result == "\n".join(expected_output)

    def test_ansible_jinja_reference_topology(self):
        """Test generating the ansible jinja template for the reference topology
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_vagrantfile(inventory, "./templates/", self.cli)
        include_result = "./tests/expected_jinja_outputs/reference_topology_ansible_groups_jinja"  # pylint: disable=C0301
        expected_output = []
        expected_output.append("  #Generating Ansible Host File at following location:")
        expected_output.append("  #    ./.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory")
        expected_output.append("  config.vm.provision \"ansible\" do |ansible|")
        expected_output.append("    ansible.playbook = \"./helper_scripts/empty_playbook.yml\"")
        expected_output.append("")
        expected_output.append("    " + open(include_result).read())
        expected_output.append("")
        expected_output.append("  end")
        expected_output.append("")
        assert result == "\n".join(expected_output)

