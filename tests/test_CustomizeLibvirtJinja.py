#!/usr/bin/env python
"""Test suite for validating the customize_libvirt.j2 template
"""
# pylint: disable=C0103
import jinja2
import topology_converter as tc

class TestCustomizeLibvirt(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the customize_libvirt jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize with the Jinja2 environmental settings.
        This is similar to the code in tc.render_vagrantfile()
        Because /templates/Vagrantfile/customize_libvirt.j2 expects an argument "node"
        we need to recreate the Jinja settings and pass a "node".
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/customize_libvirt.j2",
                                                    "Vagrantfile"])

        # It's required to set the jinja2 environment
        # so that the {% include %} statements within the Vagrantfile.j2
        # template knows where to look.
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader("./templates")
        self.env.filters["format_mac"] = tc.format_mac
        self.env.filters["get_plural"] = tc.get_plural
        self.template = self.env.get_template(self.cli.template[0][0])


    def test_customize_libvirt_pxe_node(self): # pylint: disable=R0201
        """Test generating the customize_libvirt jinja template for a pxe node
        """
        node = tc.NetworkNode(hostname="server01", function="unknown", memory="768",
                              other_attributes={"pxehost": "True"})
        inventory = tc.Inventory(provider="libvirt")
        inventory.add_node(node)

        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("server01")
        result = self.template.render(jinja_variables)
        expected_result = []
        expected_result.append("v.storage :file, :size => '100G', :type => 'qcow2', :bus => 'sata', :device => 'sda'")  # pylint: disable=C0301
        expected_result.append("v.boot 'hd'")
        expected_result.append("v.boot 'network'")
        expected_result.append("")

        assert "\n".join(expected_result) == result

    def test_customize_libvirt_host_node(self): # pylint: disable=R0201
        """Test generating the customize_libvirt jinja template for a non-pxe host
        """
        node = tc.NetworkNode(hostname="server01", function="host", memory="768")
        inventory = tc.Inventory(provider="libvirt")
        inventory.add_node(node)

        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("server01")
        result = self.template.render(jinja_variables)
        expected_result = []
        expected_result.append("v.nic_model_type = 'e1000'")
        expected_result.append("")

        assert "\n".join(expected_result) == result

    def test_customize_libvirt_host_and_pxe_node(self): # pylint: disable=R0201
        """Test generating the customize_libvirt jinja template for a pxehost
        defined as a host function
        """
        node = tc.NetworkNode(hostname="server01", function="host", memory="768",
                              other_attributes={"pxehost": "True"})
        inventory = tc.Inventory(provider="libvirt")
        inventory.add_node(node)

        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("server01")
        result = self.template.render(jinja_variables)
        expected_result = []
        expected_result.append("v.storage :file, :size => '100G', :type => 'qcow2', :bus => 'sata', :device => 'sda'")  # pylint: disable=C0301
        expected_result.append("v.boot 'hd'")
        expected_result.append("v.boot 'network'")
        expected_result.append("v.nic_model_type = 'e1000'")
        expected_result.append("")

        assert "\n".join(expected_result) == result

    def test_customize_libvirt_no_changes_node(self): # pylint: disable=R0201
        """Test generating the customize_libvirt jinja template when it's not a host
        """
        node = tc.NetworkNode(hostname="leaf01", function="leaf", memory="768")
        inventory = tc.Inventory(provider="libvirt")
        inventory.add_node(node)

        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("leaf01")
        result = self.template.render(jinja_variables)
        expected_result = [""]

        assert "\n".join(expected_result) == result
