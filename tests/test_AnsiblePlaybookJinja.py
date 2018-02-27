#!/usr/bin/env python
"""Test suite for validating the ansible_playbook.j2 template
"""
# pylint: disable=C0103
import jinja2
import topology_converter as tc

class TestAnsiblePlaybookJinja(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the ansible_playbook jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize with the Jinja2 environmental settings.
        This is similar to the code in tc.render_vagrantfile()
        Because /templates/Vagrantfile/ansible_playbook.j2 expects an argument "node"
        we need to recreate the Jinja settings and pass a "node".
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "ansible_playbook.j2",
                                                    "Vagrantfile"])

        # It's required to set the jinja2 environment
        # so that the {% include %} statements within the Vagrantfile.j2
        # template knows where to look.
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader("./templates/Vagrantfile")
        self.env.filters["format_mac"] = tc.format_mac
        self.env.filters["get_plural"] = tc.get_plural
        self.template = self.env.get_template(self.cli.template[0][0])


    def test_ansible_playbook_jinja_simple_topology(self): # pylint: disable=R0201
        """Test generating the ansible playbook jinja template for the simple topology.dot
        """

        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.get_node_by_name("leaf01").other_attributes["playbook"] = "main.yml"
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("leaf01")
        include_result = "./tests/expected_jinja_outputs/simple_ansible_groups_jinja"

        result = self.template.render(jinja_variables)

        expected_output = []
        expected_output.append("# Ansible Playbook Configuration")
        expected_output.append("    device.vm.provision \"ansible\" do |ansible|")
        expected_output.append("      ansible.playbook = \"main.yml\"")
        expected_output.append("      " + open(include_result).read())
        expected_output.append("    end")
        expected_output.append("")

        print repr(result)
        print repr("\n".join(expected_output))
        assert result == "\n".join(expected_output)
