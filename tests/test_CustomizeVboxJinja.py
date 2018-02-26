#!/usr/bin/env python
"""Test suite for validating the customize_vbox.j2 template
"""
# pylint: disable=C0103
import jinja2
import topology_converter as tc

class TestCustomizeVbox(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the customize_vbox jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize with the Jinja2 environmental settings.
        This is similar to the code in tc.render_vagrantfile()
        Because /templates/Vagrantfile/customize_libvirt.j2 expects an argument "node"
        we need to recreate the Jinja settings and pass a "node".
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/customize_vbox.j2",
                                                    "Vagrantfile"])

        # It's required to set the jinja2 environment
        # so that the {% include %} statements within the Vagrantfile.j2
        # template knows where to look.
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader("./templates")
        self.env.filters["format_mac"] = tc.format_mac
        self.env.filters["get_plural"] = tc.get_plural
        self.template = self.env.get_template(self.cli.template[0][0])


    def test_host_two_interfaces(self): # pylint: disable=R0201
        """Test generating the customize_vbox jinja template for a host with two interfaces
        """
        leaf01_node = tc.NetworkNode(hostname="leaf01", function="leaf",
                                     vm_os="CumulusCommunity/cumulus-vx",
                                     memory="256", config="./helper_scripts/oob_switch_config.sh")

        leaf02_node = tc.NetworkNode(hostname="leaf02", function="leaf",
                                     vm_os="CumulusCommunity/cumulus-vx",
                                     memory="256", config="./helper_scripts/oob_switch_config.sh")

        leaf01_interface1 = tc.NetworkInterface(hostname="leaf01",
                                                interface_name="swp51",
                                                mac=None, ip=None)
        leaf02_interface1 = tc.NetworkInterface(hostname="leaf02",
                                                interface_name="swp51",
                                                mac=None, ip=None)

        leaf01_interface2 = tc.NetworkInterface(hostname="leaf01",
                                                interface_name="swp52",
                                                mac=None, ip=None)
        leaf02_interface2 = tc.NetworkInterface(hostname="leaf02",
                                                interface_name="swp52",
                                                mac=None, ip=None)

        test_edge1 = tc.NetworkEdge(leaf01_interface1, leaf02_interface1)
        test_edge2 = tc.NetworkEdge(leaf01_interface2, leaf02_interface2)

        inventory = tc.Inventory()
        inventory.add_node(leaf01_node)
        inventory.add_node(leaf02_node)
        inventory.provider = "virtualbox"
        inventory.add_edge(test_edge1)
        inventory.add_edge(test_edge2)

        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("leaf01")
        result = self.template.render(jinja_variables)

        expected_result = []
        expected_result.append("")
        expected_result.append("        v.customize [\"modifyvm\", :id, '--audiocontroller', 'AC97', '--audio', 'Null']")  # pylint: disable=C0301
        expected_result.append("        vbox.customize [\"modifyvm\", :id, '--nicpromisc2', 'allow-all']")  # pylint: disable=C0301
        expected_result.append("        vbox.customize [\"modifyvm\", :id, '--nicpromisc3', 'allow-all']")  # pylint: disable=C0301
        expected_result.append("        vbox.customize [\"modifyvm\", :id, '--nictype1', 'virtio']")  # pylint: disable=C0301

        print repr(result)
        print ""
        print repr("\n".join(expected_result))

        assert "\n".join(expected_result) == result

    def test_pxe_host_two_interfaces(self):
        """Test generating the customize_vbox jinja template on a pxehost with two interfaces
        """
        host01_node = tc.NetworkNode(hostname="host01", function="pxehost",
                                     memory="768", other_attributes={"pxehost": "True"})

        leaf02_node = tc.NetworkNode(hostname="leaf02", function="leaf",
                                     vm_os="CumulusCommunity/cumulus-vx",
                                     memory="768", config="./helper_scripts/oob_switch_config.sh")

        host01_interface1 = tc.NetworkInterface(hostname="host01",
                                                interface_name="swp51",
                                                mac=None, ip=None)

        leaf02_interface1 = tc.NetworkInterface(hostname="leaf02",
                                                interface_name="swp51",
                                                mac=None, ip=None)

        host01_interface2 = tc.NetworkInterface(hostname="host01",
                                                interface_name="swp52",
                                                mac=None, ip=None)
        leaf02_interface2 = tc.NetworkInterface(hostname="leaf02",
                                                interface_name="swp52",
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
        expected_result = []
        expected_result.append("")
        expected_result.append("        v.customize [\"modifyvm\", :id, '--audiocontroller', 'AC97', '--audio', 'Null']")  # pylint: disable=C0301
        expected_result.append("        vbox.customize [\"modifyvm\", :id, '--nicpromisc2', 'allow-all']")  # pylint: disable=C0301
        expected_result.append("        vbox.customize [\"modifyvm\", :id, '--nicpromisc3', 'allow-all']")  # pylint: disable=C0301
        expected_result.append("        vbox.customize [\"modifyvm\", :id, '--nictype1', 'virtio']")  # pylint: disable=C0301
        expected_result.append("")
        expected_result.append("    ### Setup Interfaces for PXEBOOT")
        expected_result.append("      # Adding network as a boot option.")
        expected_result.append("      vbox.customize [\"modifyvm\", :id, \"--boot4\", \"net\"]")
        expected_result.append("")
        expected_result.append("      # Setting Vagrant interface to lowest boot preference")
        expected_result.append("      vbox.customize [\"modifyvm\", :id, \"--nicbootprio1\", \"0\"]")  # pylint: disable=C0301
        expected_result.append("")
        expected_result.append("      # Setting Specified interface to highest preference.")
        expected_result.append("      vbox.customize [\"modifyvm\", :id, \"--nicbootprio2\", \"1\"]")  # pylint: disable=C0301

        print repr(result)
        print ""
        print repr("\n".join(expected_result))
        assert "\n".join(expected_result) == result
