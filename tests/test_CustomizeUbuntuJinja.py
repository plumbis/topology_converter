#!/usr/bin/env python
"""Test suite for validating the customize_ubuntu.j2 template
"""
# pylint: disable=C0103
import jinja2
import topology_converter as tc

class TestCustomizeUbuntu(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the customize_ubuntu jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize with the Jinja2 environmental settings.
        This is similar to the code in tc.render_vagrantfile()
        Because /templates/Vagrantfile/customize_ubuntu.j2 expects an argument "node"
        we need to recreate the Jinja settings and pass a "node".
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/customize_ubuntu.j2",
                                                    "Vagrantfile"])

        # It's required to set the jinja2 environment
        # so that the {% include %} statements within the Vagrantfile.j2
        # template knows where to look.
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader("./templates")
        self.env.filters["format_mac"] = tc.format_mac
        self.env.filters["get_plural"] = tc.get_plural
        self.template = self.env.get_template(self.cli.template[0][0])


    def test_customize_ubuntu_host(self): # pylint: disable=R0201
        """Test generating the customize_libvirt jinja template for a pxe node
        """
        node = tc.NetworkNode(hostname="server01", function="host")
        inventory = tc.Inventory(provider="libvirt")
        inventory.add_node(node)

        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("server01")
        result = self.template.render(jinja_variables)
        expected_result = []
        expected_result.append("")
        expected_result.append("    # Shorten Boot Process - Applies to Ubuntu Only - remove \\\"Wait for Network\\\"")  # pylint: disable=C0301
        expected_result.append("    device.vm.provision :shell , inline: \"sed -i 's/sleep [0-9]*/sleep 1/' /etc/init/failsafe.conf 2>/dev/null || true\"")  # pylint: disable=C0301
        expected_result.append("")
        assert "\n".join(expected_result) == result

    def test_customize_ubuntu_other_os(self): # pylint: disable=R0201
        """Test that customize_ubuntu does not produce output for non-ubuntu host
        """
        node = tc.NetworkNode(hostname="oob-mgmt-switch", function="oob-switch")
        inventory = tc.Inventory()
        inventory.add_node(node)

        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("oob-mgmt-switch")
        result = self.template.render(jinja_variables)
        expected_result = []
        expected_result.append("")
        assert "\n".join(expected_result) == result
