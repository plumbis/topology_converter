#!/usr/bin/env python
"""Test suite for validating the interface_remap.j2 template
"""
# pylint: disable=C0103
import jinja2
import topology_converter as tc

class TestInterfaceRemapJinja(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the interface_remap jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize with the Jinja2 environmental settings.
        This is similar to the code in tc.render_vagrantfile()
        Because /templates/Vagrantfile/interface_remap.j2 expects an argument "node"
        we need to recreate the Jinja settings and pass a "node".
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "libvirt", "-t",
                                                    "interface_remap.j2",
                                                    "Vagrantfile"])

        # It's required to set the jinja2 environment
        # so that the {% include %} statements within the Vagrantfile.j2
        # template knows where to look.
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader("./templates/Vagrantfile")
        self.env.filters["format_mac"] = tc.format_mac
        self.env.filters["get_plural"] = tc.get_plural
        self.template = self.env.get_template(self.cli.template[0][0])

        self.udev_lines = []
        self.udev_lines.append("")
        self.udev_lines.append("device.vm.provision :shell , :inline => <<-delete_udev_directory")
        self.udev_lines.append("if [ -d \"/etc/udev/rules.d/70-persistent-net.rules\" ]; then")
        self.udev_lines.append("    rm -rfv /etc/udev/rules.d/70-persistent-net.rules &> /dev/null")
        self.udev_lines.append("fi")
        self.udev_lines.append("rm -rfv /etc/udev/rules.d/70-persistent-net.rules &> /dev/null")
        self.udev_lines.append("delete_udev_directory")
        self.udev_include = "\n".join(self.udev_lines)


    def test_remap_with_libvirt(self): # pylint: disable=R0201
        """Test the interface_remap.j2 output when the provider is libvirt
        """
        self.cli.provider = "libvirt"
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("leaf01")

        result = self.template.render(jinja_variables)

        expected_result_file = "./tests/expected_jinja_outputs/reference_topology_interface_remap_jinja"  # pylint: disable=C0301

        print repr(result)
        print ""
        print repr(open(expected_result_file).read())
        assert result == open(expected_result_file).read()


    def test_remap_pxehost_with_libvirt(self): # pylint: disable=R0201
        """Test the interface remap jinja2 output when the provider is libvirt
        and it is a pxe enabled host
        """
        host01_node = tc.NetworkNode(hostname="host01", function="pxehost",
                                     memory="512", other_attributes={"pxehost": "True"})

        leaf02_node = tc.NetworkNode(hostname="leaf02", function="leaf",
                                     vm_os="CumulusCommunity/cumulus-vx",
                                     memory="512", config="./helper_scripts/oob_switch_config.sh")

        host01_interface1 = tc.NetworkInterface(hostname="host01",
                                                interface_name="swp51",
                                                mac=None, ip=None)

        leaf02_interface1 = tc.NetworkInterface(hostname="leaf02",
                                                interface_name="swp52",
                                                mac=None, ip=None)

        host01_interface2 = tc.NetworkInterface(hostname="host01",
                                                interface_name="swp52",
                                                mac=None, ip=None)
        leaf02_interface2 = tc.NetworkInterface(hostname="leaf02",
                                                interface_name="swp53",
                                                mac=None, ip=None)

        host01_interface1.pxe_priority = 1

        test_edge1 = tc.NetworkEdge(host01_interface1, leaf02_interface1)
        test_edge2 = tc.NetworkEdge(host01_interface2, leaf02_interface2)

        inventory = tc.Inventory()
        inventory.add_node(host01_node)
        inventory.add_node(leaf02_node)
        inventory.provider = "virtualbox"
        inventory.add_edge(test_edge1)
        inventory.add_edge(test_edge2)
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("host01")
        result = self.template.render(jinja_variables)

        assert "# NO REMAP for LIBVIRT PXE DEVICE" in result


    def test_remap_vagrant_interface(self): # pylint: disable=R0201
        """Test generating the output for the interface remap jinja template when the vagrant
        interface is defined
        """
        self.cli.provider = "libvirt"
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        inventory.get_node_by_name("leaf01").vagrant_interface = "swp49"
        jinja_variables["node"] = inventory.get_node_by_name("leaf01")

        result = self.template.render(jinja_variables)

        assert "Adding UDEV Rule: Vagrant interface = swp49'" in result
