#!/usr/bin/env python
"""Test suite for check_files method
"""
# pylint: disable=C0103
from nose.tools import raises
import topology_converter as tc

class TestCheckFiles(object):  # pylint: disable=R0903
    """Test suite to validate files exist
    """

    def test_Vagrantfile_j2(self): # pylint: disable=R0201
        """Test validating Vagrantfile.j2
        """
        cli = tc.parse_arguments()
        args = cli.parse_args(["tests/simple.dot", "-v"])

        tc.check_files(args, "templates/Vagrantfile/Vagrantfile.j2")

        assert True


    @raises(SystemExit)
    def test_invalid_Vagrantfile_j2(self): # pylint: disable=R0201
        """Test that the default Vagrantfile.j2 missing exits
        """
        cli = tc.parse_arguments()
        args = cli.parse_args(["tests/simple.dot", "-v"])

        tc.check_files(args, "templates/fake_Vagrantfile.j2")


    def test_custom_template(self): # pylint: disable=R0201
        """Test passing a custom template
        """
        cli = tc.parse_arguments()
        args = cli.parse_args(
            ["tests/simple.dot", "-t", "templates/Vagrantfile/Vagrantfile.j2", "Vagrantfile"])

        tc.check_files(args, "templates/Vagrantfile/Vagrantfile.j2")

        assert True

    @raises(SystemExit)
    def test_invalid_custom_template(self): # pylint: disable=R0201
        """Test passing a non-existent custom template
        """
        cli = tc.parse_arguments()
        args = cli.parse_args(
            ["tests/simple.dot", "-t", "templates/fake_Vagrantfile.j2", "Vagrantfile"])

        tc.check_files(args, "templates/Vagrantfile.j2")

        assert True
