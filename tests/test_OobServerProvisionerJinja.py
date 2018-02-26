#!/usr/bin/env python
"""Test suite for validating the oob_mgmt_server_provisioner.j2 template
"""
# pylint: disable=C0103
import topology_converter as tc

class TestOobServerProvisionerJinja(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the OOB Server provisioner jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize the tests with a basic CLI
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/oob_mgmt_server_provisioner.j2",
                                                    "Vagrantfile"])

    def test_oob_server_provisioner_output(self): # pylint: disable=R0201
        """Test generating the oob server provisioner jinja template
        """
        topology_file = "./tests/dot_files/reference_topology.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_vagrantfile(inventory, "./templates/", self.cli)

        expected_result = []
        expected_result.append("")
        expected_result.append("# Copy over DHCP files and MGMT Network Files")
        expected_result.append("device.vm.provision \"file\", source: \"./auto_mgmt_network/dhcpd.conf\", destination: \"~/dhcpd.conf\"")  # pylint: disable=C0301
        expected_result.append("device.vm.provision \"file\", source: \"./auto_mgmt_network/dhcpd.hosts\", destination: \"~/dhcpd.hosts\"")  # pylint: disable=C0301
        expected_result.append("device.vm.provision \"file\", source: \"./auto_mgmt_network/hosts\", destination: \"~/hosts\"")  # pylint: disable=C0301
        expected_result.append("device.vm.provision \"file\", source: \"./auto_mgmt_network/ansible_hostfile\", destination: \"~/ansible_hostfile\"")  # pylint: disable=C0301
        expected_result.append("device.vm.provision \"file\", source: \"./auto_mgmt_network/ztp_oob.sh\", destination: \"~/ztp_oob.sh\"")  # pylint: disable=C0301
        expected_result.append("")

        print repr(result)
        print ""
        print repr("\n".join(expected_result))
        assert result == "\n".join(expected_result)
