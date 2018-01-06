import os
import topology_converter as tc


DOT_FILES = "./tests/dot_files/"


def test_file_not_found():
    assert tc.lint_topo_file("fake_file.dot") is False


def test_topo_files():
    for file in os.listdir(DOT_FILES):
        print file
        if "bad" not in file:
            yield lint_good_topos, "./tests/dot_files/" + file

        else:
            print file
            yield lint_bad_topos, "./tests/dot_files/" + file


def lint_good_topos(topo_file):
    assert tc.lint_topo_file(topo_file)


def lint_bad_topos(topo_file):
    assert not tc.lint_topo_file(topo_file)
