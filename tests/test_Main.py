#!/usr/bin/env python
"""Test suite for validating the main() function
"""
# pylint: disable=C0103
import sys
import difflib
from mock import patch
import topology_converter as tc


class TestMain(object):  # pylint: disable=W0612,R0903
    """Test suite for validating the main function of TC
    """
    def get_diff(self, diff):  # pylint: disable=R0201
        """Take a Differ().compare output and return an easy to read version that skips
        the simid value
        """
        return_value = []
        line_num = 1

        # Iterate over every diff line (which is the entire file)
        for line in diff:
            # We only care about diff lines that havea  diff
            if line.startswith("-") or line.startswith("+"):
                # When vbox is in use, the simid is generated by a timestamp
                # This means it's always different. I don't know how else to skip it
                if "simid = " in line:
                    line_num += 1
                    continue

                return_value.append(str(line_num) + ": " + line)
            line_num += 1

        return return_value


    def test_basic_execution(self): # pylint: disable=R0201
        """Test running the program against the reference topology with no optional arguments
        """

        testargs = ["reference_topology.py", "./tests/dot_files/reference_topology.dot"]
        with patch.object(sys, 'argv', testargs):
            expected_result_file = "./tests/expected_jinja_outputs/main_default_arguments.vagrantfile"  # pylint: disable=C0301
            tc.main()

            vagrant_output = open("Vagrantfile").read().splitlines()
            expected_output = open(expected_result_file).read().splitlines()

            # Get a diff of the files, makes troubleshooting errors easier
            diff = list(difflib.Differ().compare(vagrant_output, expected_output))

            diff_output = self.get_diff(diff)

            print "\n".join(diff_output)

            assert not diff_output


    def test_basic_execution_libvirt(self): # pylint: disable=R0201
        """Test running the program against the reference topology with only libvirt option
        """

        testargs = ["reference_topology.py", "-p", "libvirt",
                    "./tests/dot_files/reference_topology.dot"]
        with patch.object(sys, 'argv', testargs):
            expected_result_file = "./tests/expected_jinja_outputs/main_default_arguments_libvirt.vagrantfile"  # pylint: disable=C0301
            tc.main()

            vagrant_output = open("Vagrantfile").read().splitlines()
            expected_output = open(expected_result_file).read().splitlines()

            # Get a diff of the files, makes troubleshooting errors easier
            diff = list(difflib.Differ().compare(vagrant_output, expected_output))

            diff_output = self.get_diff(diff)

            print "\n".join(diff_output)

            assert not diff_output

    def test_create_mgmt_network(self): # pylint: disable=R0201
        """Test creating a management network
        """

        testargs = ["reference_topology.py", "-c", "./tests/dot_files/simple.dot"]
        expected_result_file = "./tests/expected_jinja_outputs/main_create_mgmt_network.vagrantfile"  # pylint: disable=C0301

        # The list of helper script file names to test
        helper_scripts = ["ansible_hostfile", "bridge-untagged", "dhcpd.conf",
                          "hosts", "oob_server_config_auto_mgmt.sh", "ztp_oob.sh"]

        with patch.object(sys, 'argv', testargs):

            tc.main()

            vagrant_output = open("Vagrantfile").read().splitlines()
            expected_output = open(expected_result_file).read().splitlines()

            # Get a diff of the files, makes troubleshooting errors easier
            diff = list(difflib.Differ().compare(vagrant_output, expected_output))

            diff_output = self.get_diff(diff)

            print "\n".join(diff_output)

            assert not diff_output

            for filename in helper_scripts:
                generated_helper_output = open(
                    "helper_scripts/auto_mgmt_network/" + filename).read().splitlines()
                expected_helper_output = open(
                    "./tests/expected_helper_scripts/main_test_create_mgmt_network/" + filename).read().splitlines()  # pylint: disable=C0301

                helper_diff = list(difflib.Differ().compare(generated_helper_output, expected_helper_output))  # pylint: disable=C0301

                helper_diff_output = self.get_diff(helper_diff)

                print "\n".join(diff_output)

                assert not helper_diff_output
