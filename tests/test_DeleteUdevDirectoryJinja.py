#!/usr/bin/env python
"""Test suite for validating the delete_udev_directory.j2 termplate
"""
# pylint: disable=C0103
import topology_converter as tc

class TestDeleteUdevDirectory(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the output of the delete_udev_directory jinja template
    """
    # pylint: disable=W0201
    def setup(self):
        """Initalize the tests with a basic CLI
        """
        self.cli = tc.parse_arguments().parse_args(["tests/simple.dot", "-p", "virtualbox", "-t",
                                                    "./Vagrantfile/delete_udev_directory.j2",
                                                    "Vagrantfile"])

    def test_delete_udev_directory_output(self): # pylint: disable=R0201
        """Test that the udev directory jinja template output is as expected
        """
        topology_file = "./tests/dot_files/simple.dot"
        parser = tc.ParseGraphvizTopology()
        parsed_topology = parser.parse_topology(topology_file)
        inventory = tc.Inventory()
        inventory.add_parsed_topology(parsed_topology)
        result = tc.render_vagrantfile(inventory, "./templates/", self.cli)
        expected_output = []
        expected_output.append("")
        expected_output.append("device.vm.provision :shell , :inline => <<-delete_udev_directory")
        expected_output.append("if [ -d \"/etc/udev/rules.d/70-persistent-net.rules\" ]; then")
        expected_output.append("    rm -rfv /etc/udev/rules.d/70-persistent-net.rules &> /dev/null")
        expected_output.append("fi")
        expected_output.append("rm -rfv /etc/udev/rules.d/70-persistent-net.rules &> /dev/null")
        expected_output.append("delete_udev_directory")

        print repr(result)
        print ""
        print repr("\n".join(expected_output))
        assert result == "\n".join(expected_output)
