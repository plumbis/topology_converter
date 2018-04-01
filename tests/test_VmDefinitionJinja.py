#!/usr/bin/env python
"""Test suite for validating the vm_definition.j2 template
"""
# pylint: disable=C0103
import jinja2
import topology_converter as tc

class TestVmDefinition(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the vm_definition jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize with the Jinja2 environmental settings.
        This is similar to the code in tc.render_vagrantfile()
        Because /templates/Vagrantfile/vm_definition.j2 expects an argument "node"
        we need to recreate the Jinja settings and pass a "node".
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "vm_definition.j2",
                                                    "Vagrantfile"])

        # It's required to set the jinja2 environment
        # so that the {% include %} statements within the Vagrantfile.j2
        # template knows where to look.
        self.env = jinja2.Environment()
        self.env.loader = jinja2.FileSystemLoader("./templates/Vagrantfile")
        self.env.filters["format_mac"] = tc.format_mac
        self.env.filters["get_plural"] = tc.get_plural
        self.template = self.env.get_template(self.cli.template[0][0])


    def test_vm_definition_vbox_pxehost_topology(self): # pylint: disable=R0201
        """Test the vm_definition.j2 template against a two node topology with Virtualbox
        """
        topology_file = "./tests/dot_files/pxehost.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("server1")
        expected_result_file = "./tests/expected_jinja_outputs/vm_definition_vbox_pxehost_topology.txt"  # pylint: disable=C0301
        result = self.template.render(jinja_variables)

        print repr(result)
        print ""
        print repr(open(expected_result_file).read())
        assert result == open(expected_result_file).read()

    def test_vm_definition_vbox_pxehost_topology_virtualbox_legacy(self): # pylint: disable=R0201
        """Test the vm_definition.j2 template against a two node topology with vagrant user set
        """
        topology_file = "./tests/dot_files/pxehost.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.get_node_by_name("server1").legacy = True
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("server1")

        result = self.template.render(jinja_variables)

        print result
        assert "    device.vm.hostname = \"server1\"" not in result.splitlines()

    def test_vm_definition_vbox_pxehost_pxe_device(self): # pylint: disable=R0201
        """Test the vm_definition.j2 template against a two node topology with a pxehost
        """
        topology_file = "./tests/dot_files/pxehost.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("pxehost")
        expected_result_file = "./tests/expected_jinja_outputs/vm_definition_vbox_pxehost.txt"

        result = self.template.render(jinja_variables)

        print repr(result)
        print ""
        print repr(open(expected_result_file).read())
        assert result == open(expected_result_file).read()


    def test_vm_definition_vbox_pxehost_ssh_port(self): # pylint: disable=R0201
        """Test the vm_definition.j2 template against a two node topology with a custom ssh port
        """
        topology_file = "./tests/dot_files/pxehost.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.get_node_by_name("server1").ssh_port = "2222"
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("server1")

        result = self.template.render(jinja_variables)
        print result
        assert "    device.vm.network :forwarded_port, guest: 22, host: 2222, host_ip: \"0.0.0.0\", id: \"ssh\", auto_correct:true" in result  # pylint: disable=C0301

    def test_vm_definition_vbox_pxehost_synched_folder(self): # pylint: disable=R0201
        """Test the vm_definition.j2 template against a two node topology with a synched folder
        """
        self.cli.synced_folder = True
        topology_file = "./tests/dot_files/pxehost.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("server1")

        result = self.template.render(jinja_variables)
        assert "    device.vm.synced_folder \".\", \"/vagrant\", disabled: true" not in result

    def test_vm_definition_vbox_oob_server(self): # pylint: disable=R0201
        """Test the vm_definition.j2 template with the oob server defined
        """
        self.cli.create_mgmt_network = True
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.build_mgmt_network()
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("oob-mgmt-server")

        result = self.template.render(jinja_variables)
        print result
        assert "    # Copy over DHCP files and MGMT Network Files" in result
        assert "    device.vm.provision \"file\", source: \"./helper_scripts/auto_mgmt_network/dhcpd.conf\", destination: \"~/dhcpd.conf\"" in result  # pylint: disable=C0301
        assert "    device.vm.provision \"file\", source: \"./helper_scripts/auto_mgmt_network/dhcpd.hosts\", destination: \"~/dhcpd.hosts\"" in result  # pylint: disable=C0301
        assert "    device.vm.provision \"file\", source: \"./helper_scripts/auto_mgmt_network/hosts\", destination: \"~/hosts\"" in result  # pylint: disable=C0301
        assert "    device.vm.provision \"file\", source: \"./helper_scripts/auto_mgmt_network/ansible_hostfile\", destination: \"~/ansible_hostfile\"" in result  # pylint: disable=C0301
        assert "    device.vm.provision \"file\", source: \"./helper_scripts/auto_mgmt_network/ztp_oob.sh\", destination: \"~/ztp_oob.sh\"" in result  # pylint: disable=C0301

    def test_vm_definition_vbox_oob_switch(self): # pylint: disable=R0201
        """Test the vm_definition.j2 template with the oob switch defined
        """
        self.cli.create_mgmt_network = True
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        inventory.build_mgmt_network()
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("oob-mgmt-switch")

        result = self.template.render(jinja_variables)
        print result
        assert "    device.vm.provision \"file\", source: \"./helper_scripts/auto_mgmt_network/bridge-untagged\", destination: \"~/bridge-untagged\"" in result  # pylint: disable=C0301

    def test_vm_definition_libvirt_pxehost_topology(self): # pylint: disable=R0201
        """Test the vm_definition.j2 template against a two node topology with libvirt
        """
        self.cli.provider = "libvirt"
        topology_file = "./tests/dot_files/pxehost.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory(provider="libvirt")
        inventory.add_parsed_topology(parsed_topology)
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("server1")
        expected_result_file = "./tests/expected_jinja_outputs/vm_definition_libvirt_pxehost_topology.txt"  # pylint: disable=C0301
        result = self.template.render(jinja_variables)

        print repr(result)
        print ""
        print repr(open(expected_result_file).read())
        assert result == open(expected_result_file).read()

    def test_vm_definition_libvirt_pxehost_pxe_device(self): # pylint: disable=R0201
        """Test the vm_definition.j2 template against libvirt with a pxehost
        """
        self.cli.provider = "libvirt"
        topology_file = "./tests/dot_files/pxehost.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory(provider="libvirt")
        inventory.add_parsed_topology(parsed_topology)
        jinja_variables = tc.get_vagrantfile_variables(inventory, self.cli)
        jinja_variables["node"] = inventory.get_node_by_name("pxehost")
        expected_result_file = "./tests/expected_jinja_outputs/vm_definition_libvirt_pxehost.txt"

        result = self.template.render(jinja_variables)

        print result
        print ""
        print open(expected_result_file).read()

        assert result == open(expected_result_file).read()
