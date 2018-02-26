#!/usr/bin/env python
"""Test suite for validating the vbox_interfaces.j2 template
"""
# pylint: disable=C0103
import jinja2
import topology_converter as tc

class TestVboxInterfaces(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the vbox_interfaces jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize with the Jinja2 environmental settings.
        This is similar to the code in tc.render_vagrantfile()
        Because /templates/Vagrantfile/vbox_interfaces.j2 expects an argument "interface"
        we need to recreate the Jinja settings and pass an "interface".
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "libvirt", "-t",
                                                    "./Vagrantfile/vbox_interfaces.j2",
                                                    "Vagrantfile"])

        # It's required to set the jinja2 environment
        # so that the {% include %} statements within the Vagrantfile.j2
        # template knows where to look.
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader("./templates")
        self.env.filters["format_mac"] = tc.format_mac
        self.env.filters["get_plural"] = tc.get_plural
        self.template = self.env.get_template(self.cli.template[0][0])


    def test_vbox_interface(self): # pylint: disable=R0201
        """Test the vbox_interfaces.j2 output
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["interface"] = inventory.get_node_by_name("leaf01").interfaces["swp49"]

        result = self.template.render(jinja_variables)

        expected_result = "\n    device.vm.network \"private_network\", virtualbox__intnet: \"#{simid}_network10\", auto_config: false , :mac => \"443839000010\""  # pylint: disable=C0301

        print repr(result)
        assert result == expected_result
