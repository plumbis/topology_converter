#!/usr/bin/env python
"""Test suite for validating the libvirt_interfaces.j2 template
"""
# pylint: disable=C0103
import jinja2
import topology_converter as tc

class TestLibvirtInterfaces(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the libvirt_interfaces jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize with the Jinja2 environmental settings.
        This is similar to the code in tc.render_vagrantfile()
        Because /templates/Vagrantfile/libvirt_interfaces.j2 expects an argument "node"
        we need to recreate the Jinja settings and pass a "node".
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "libvirt", "-t",
                                                    "./Vagrantfile/libvirt_interfaces.j2",
                                                    "Vagrantfile"])

        # It's required to set the jinja2 environment
        # so that the {% include %} statements within the Vagrantfile.j2
        # template knows where to look.
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader("./templates")
        self.env.filters["format_mac"] = tc.format_mac
        self.env.filters["get_plural"] = tc.get_plural
        self.template = self.env.get_template(self.cli.template[0][0])


    def test_libvirt_interfaces_reference_topology(self): # pylint: disable=R0201
        """Test the interface_remap.j2 output with the reference topology
        """

        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory(provider="libvirt")
        inventory.add_parsed_topology(parsed_topology)
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("leaf01")
        jinja_variables["interface"] = inventory.get_node_by_name("leaf01").interfaces["eth0"]
        expected_result = []
        expected_result.append("device.vm.network \"private_network\",")
        expected_result.append("    :mac => 'a0:00:00:00:00:11',")
        expected_result.append("    :libvirt__tunnel_type => 'udp',")
        expected_result.append("    :libvirt__tunnel_local_ip => '127.0.0.1',")
        expected_result.append("    :libvirt__tunnel_local_port => '1043',")
        expected_result.append("    :libvirt__tunnel_ip => '127.0.0.1',")
        expected_result.append("    :libvirt__tunnel_port => '9043',")
        expected_result.append("    :libvirt__iface_name => 'eth0',")
        expected_result.append("    auto_config: false")

        result = self.template.render(jinja_variables)

        print repr(result)
        print ""
        print repr("\n".join(expected_result))

        assert result == "\n".join(expected_result)
