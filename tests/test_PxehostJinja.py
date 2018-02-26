#!/usr/bin/env python
"""Test suite for validating the pxehost.j2 template
"""
# pylint: disable=C0103
import jinja2
import topology_converter as tc

class TestPxehostJinja(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the pxehost.j2 jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize with the Jinja2 environmental settings.
        This is similar to the code in tc.render_vagrantfile()
        Because /templates/Vagrantfile/pxehost.j2 expects an argument "node"
        we need to recreate the Jinja settings and pass a "node".
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/pxehost.j2",
                                                    "Vagrantfile"])

        # It's required to set the jinja2 environment
        # so that the {% include %} statements within the Vagrantfile.j2
        # template knows where to look.
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader("./templates")
        self.env.filters["format_mac"] = tc.format_mac
        self.env.filters["get_plural"] = tc.get_plural
        self.template = self.env.get_template(self.cli.template[0][0])

    def test_pxehost_virtualbox(self):  # pylint: disable=R0201
        """Test generating the pxehost jinja template when the provider is virtualbox
        """

        topology_file = "./tests/dot_files/pxehost.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)

        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("pxehost")

        result = self.template.render(jinja_variables)
        expected_output = []
        expected_output.append("device.ssh.insert_key = false")
        expected_output.append("")
        expected_output.append("    device.vm.box = \"yk0/ubuntu-xenial\"")
        expected_output.append("")

        print repr(result)
        print ""
        print repr("\n".join(expected_output))
        assert result == "\n".join(expected_output)

    def test_pxehost_libvirt(self):  # pylint: disable=R0201
        """Test generating the pxehost jinja template when the provider is libvirt
        """
        self.cli.provider = "libvirt"
        topology_file = "./tests/dot_files/pxehost.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory(provider="libvirt")
        inventory.add_parsed_topology(parsed_topology)

        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("pxehost")

        result = self.template.render(jinja_variables)
        expected_output = []
        expected_output.append("device.ssh.insert_key = false")
        expected_output.append("")
        expected_output.append("    # NO BOX USED FOR PXE DEVICE WITH LIBVIRT")

        print repr(result)
        print ""
        print repr("\n".join(expected_output))
        assert result == "\n".join(expected_output)
