#!/usr/bin/env python
"""Test suite for validating the device_config.j2 template
"""
# pylint: disable=C0103
import jinja2
import topology_converter as tc

class TestDeviceConfigJinja(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the device_config.j2 jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize with the Jinja2 environmental settings.
        This is similar to the code in tc.render_vagrantfile()
        Because /templates/Vagrantfile/device_config.j2 expects an argument "node"
        we need to recreate the Jinja settings and pass a "node".
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/device_config.j2",
                                                    "Vagrantfile"])

        # It's required to set the jinja2 environment
        # so that the {% include %} statements within the Vagrantfile.j2
        # template knows where to look.
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader("./templates")
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
        inventory.add_node(tc.NetworkNode(hostname="oob-mgmt-server", function="oob-server"))
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("oob-mgmt-server")

        result = self.template.render(jinja_variables)
        expected_output = []
        expected_output.append("")
        expected_output.append("    # Run the Config specified in the Node Attributes")
        expected_output.append("    device.vm.provision :shell , privileged: false, :inline => 'echo \"$(whoami)\" > /tmp/normal_user'")  # pylint: disable=C0301
        expected_output.append("    device.vm.provision :shell , path: \"./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh\"") # pylint: disable=C0301

        print repr(result)
        print ""
        print repr("\n".join(expected_output))
        assert result == "\n".join(expected_output)
