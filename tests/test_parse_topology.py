#!/usr/bin/env python
from nose.tools import raises
import topology_converter as tc
import pydotplus as dot
import pprint


# Create a CLI to set verbose to True/False
class CLI:

    def __init__(self):

        self.verbose = False
        self.provider = "virtualbox"


class Test_nodes:
    def setup(self):
        """Setup the environment based on the simple.dot file.
        Populate the "mac" value with an empty set
        """
        topology = dot.graphviz.graph_from_dot_file("./tests/dot_files/simple.dot")
        self.nodes = topology.get_node_list()

    def test_simple_topology(self):

        cli = CLI()

        cli.topology_file = "./tests/dot_files/simple.dot"
        results = tc.parse_topology(cli)

        """
         "leaf01":"swp51" -- "spine01":"swp1"
         "leaf02":"swp51" -- "spine01":"swp2"
         "leaf03":"swp51" -- "spine01":"swp3"

         "leaf01":"swp49" -- "leaf02":"swp49"
         "leaf03":"swp49" -- "leaf04":"swp49"
        """

        leaf01 = {"leaf01": {
                    "function": "leaf",
                    "config": "./helper_scripts/config_switch.sh",
                    "memory": "768",
                    "os": "cumuluscommunity/cumulus-vx",
                    "version": "3.4.3",
                    "interfaces": {
                        "swp51": {
                            "mac": "443839000000",
                            "network": "net0"
                        },
                        "swp49": {
                            "mac": "443839000006",
                            "network": "net4"
                        }
                }}}

        leaf02 = {"leaf02": {
                    "function": "leaf",
                    "config": "./helper_scripts/config_switch.sh",
                    "memory": "768",
                    "os": "cumuluscommunity/cumulus-vx",
                    "version": "3.4.3",
                    "interfaces": {
                        "swp51": {
                            "mac": "443839000002",
                            "network": "net1"
                        },
                        "swp49": {
                            "mac": "443839000007",
                            "network": "net4"
                        }
                }}}

        leaf03 = {"leaf03": {
                    "function": "leaf",
                    "config": "./helper_scripts/config_switch.sh",
                    "memory": "768",
                    "os": "cumuluscommunity/cumulus-vx",
                    "version": "3.4.3",
                    "interfaces": {
                        "swp51": {
                            "mac": "443839000004",
                            "network": "net2"
                        },
                        "swp49": {
                            "mac": "443839000008",
                            "network": "net5"
                        }
                }}}

        leaf04 = {"leaf04": {
                    "function": "leaf",
                    "config": "./helper_scripts/config_switch.sh",
                    "memory": "768",
                    "os": "cumuluscommunity/cumulus-vx",
                    "version": "3.4.3",
                    "interfaces": {
                        "swp49": {
                            "mac": "443839000009",
                            "network": "net5"
                        }
                }}}

        spine01 = {"spine01": {
                    "function": "spine",
                    "config": "./helper_scripts/config_switch.sh",
                    "memory": "768",
                    "os": "cumuluscommunity/cumulus-vx",
                    "version": "3.4.3",
                    "interfaces": {
                        "swp1": {
                            "mac": "443839000001",
                            "network": "net0"
                        },
                        "swp2": {
                            "mac": "443839000003",
                            "network": "net1"
                        },
                        "swp3": {
                            "mac": "443839000005",
                            "network": "net2"
                        },
                }}}

        mac_set = set(["443839000000", "443839000001", "443839000002", "443839000003", "443839000004", "443839000005",
                      "443839000006", "443839000007", "443839000008", "443839000009"])
        expected_results = dict()
        expected_results.update(leaf01)
        expected_results.update(leaf02)
        expected_results.update(leaf03)
        expected_results.update(leaf04)
        expected_results.update(spine01)
        expected_results["linkcount"] = 5
        expected_results["macs"] = mac_set

        # We don't test the MACs because we can't guarantee the order which the links parsed
        # MACs are assigned first come, first serve. Without a known order, we don't know which mac
        # will be assigned to which interface

        assert results["linkcount"] == expected_results["linkcount"]
        assert results["macs"] == expected_results["macs"]

        # Check that everything within a node matches, except the network and macs
        for key,value in expected_results.iteritems():
            if key == "linkcount" or key == "macs":
                continue

            for node_attribute, attribute_value in expected_results[key].iteritems():
                # Because we don't know the order that the interfaces will be processed
                # We don't know what mac or link they will be assigned
                # So just check that the same interfaces exist in both
                if node_attribute == "interfaces":
                    assert results[key]["interfaces"].keys() == expected_results[key]["interfaces"].keys()
                    continue

                # For all other node attributes make sure they are exact matches
                assert results[key][node_attribute] == expected_results[key][node_attribute]

        assert results["leaf01"]["interfaces"]["swp51"]["network"] == results["spine01"]["interfaces"]["swp1"]["network"]
        assert results["leaf02"]["interfaces"]["swp51"]["network"] == results["spine01"]["interfaces"]["swp2"]["network"]
        assert results["leaf03"]["interfaces"]["swp51"]["network"] == results["spine01"]["interfaces"]["swp3"]["network"]
        assert results["leaf01"]["interfaces"]["swp49"]["network"] == results["leaf02"]["interfaces"]["swp49"]["network"]
        assert results["leaf03"]["interfaces"]["swp49"]["network"] == results["leaf04"]["interfaces"]["swp49"]["network"]


    def test_reference_topology_vbox(self):

            cli = CLI()
            pp = pprint.PrettyPrinter(indent=2)
            cli.topology_file = "./tests/dot_files/reference_topology_3_4_3.dot"
            results = tc.parse_topology(cli)


            leaf01 = {"leaf01": {
                        "function": "leaf",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000011",
                                "network": "net4"
                            }
                    }}}

            leaf02 = {"leaf02": {
                        "function": "leaf",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000012",
                                "network": "net4"
                            }
                    }}}

            leaf03 = {"leaf03": {
                        "function": "leaf",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000013",
                                "network": "net4"
                            }
                    }}}

            leaf04 = {"leaf04": {
                        "function": "leaf",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000014",
                                "network": "net4"
                            }
                    }}}

            spine01 = {"spine01": {
                        "function": "spine",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp1": {
                                "mac": "443839000001",
                                "network": "net0"
                            },
                            "swp2": {
                                "mac": "443839000003",
                                "network": "net1"
                            },
                            "swp3": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp3": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp4": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp29": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp30": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp31": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp32": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "eth0": {
                                "mac": "a00000000021",
                                "network": "net2"
                            }
                    }}}

            spine02 = {"spine02": {
                        "function": "spine",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp1": {
                                "mac": "443839000001",
                                "network": "net0"
                            },
                            "swp2": {
                                "mac": "443839000003",
                                "network": "net1"
                            },
                            "swp3": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp3": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp4": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp29": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp30": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp31": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp32": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "eth0": {
                                "mac": "a00000000022",
                                "network": "net2"
                            }
                    }}}

            exit01 = {"exit01": {
                        "function": "exit",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp44": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000041",
                                "network": "net4"
                            }
                    }}}
            exit02 = {"exit02": {
                        "function": "exit",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp44": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000042",
                                "network": "net4"
                            }
                    }}}

            internet = {"internet": {
                        "function": "internet",
                        "config": "./helper_scripts/config_internet.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "vagrant": "swp48",
                        "interfaces": {
                            "swp1": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000050",
                                "network": "net4"
                            }
                    }}}

            server01 = {"server01": {
                        "function": "host",
                        "config": "./helper_scripts/config_server.sh",
                        "memory": "512",
                        "os": "yk0/ubuntu-xenial",
                        "interfaces": {
                            "eth1": {
                                "mac": "000300111101",
                                "network": "net0"
                            },
                            "eth2": {
                                "mac": "000300111102",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000031",
                                "network": "net4"
                            }
                    }}}

            server02 = {"server02": {
                        "function": "host",
                        "config": "./helper_scripts/config_server.sh",
                        "memory": "512",
                        "os": "yk0/ubuntu-xenial",
                        "interfaces": {
                            "eth1": {
                                "mac": "000300222201",
                                "network": "net0"
                            },
                            "eth2": {
                                "mac": "000300222202",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000032",
                                "network": "net4"
                            }
                    }}}

            server03 = {"server03": {
                        "function": "host",
                        "config": "./helper_scripts/config_server.sh",
                        "memory": "512",
                        "os": "yk0/ubuntu-xenial",
                        "interfaces": {
                            "eth1": {
                                "mac": "000300333301",
                                "network": "net0"
                            },
                            "eth2": {
                                "mac": "000300333302",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000033",
                                "network": "net4"
                            }
                    }}}

            server04 = {"server04": {
                        "function": "host",
                        "config": "./helper_scripts/config_server.sh",
                        "memory": "512",
                        "os": "yk0/ubuntu-xenial",
                        "interfaces": {
                            "eth1": {
                                "mac": "000300444401",
                                "network": "net0"
                            },
                            "eth2": {
                                "mac": "000300444402",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000034",
                                "network": "net4"
                            }
                    }}}

            edge01 = {"edge01": {
                        "function": "host",
                        "config": "./helper_scripts/config_server.sh",
                        "memory": "768",
                        "os": "yk0/ubuntu-xenial",
                        "interfaces": {
                            "eth1": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "eth2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000051",
                                "network": "net4"
                            }
                    }}}

            oob_server = {"oob-mgmt-server": {
                        "function": "oob-server",
                        "config": "./helper_scripts/config_oob_server.sh",
                        "memory": "1024",
                        "os": "cumuluscommunity/vx_oob_server",
                        "vagrant": "eth0",
                        "version": "1.0.4",
                        "interfaces": {
                            "eth1": {
                                "mac": "443839000000",
                                "network": "net0"
                            }
                    }}}

            oob_switch = {"oob-mgmt-switch": {
                        "function": "oob-switch",
                        "config": "./helper_scripts/config_oob_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "vagrant": "eth0",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp1": {
                                "mac": "a00000000061",
                                "network": "net0"
                            },
                            "swp2": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp3": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp4": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp5": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp6": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp7": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp8": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp9": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp10": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp11": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp12": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp13": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp14": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp15": {
                                "mac": "443839000000",
                                "network": "net0"
                            },

                    }}}

            expected_results = dict()
            expected_results.update(leaf01)
            expected_results.update(leaf02)
            expected_results.update(leaf03)
            expected_results.update(leaf04)
            expected_results.update(spine01)
            expected_results.update(spine02)
            expected_results.update(server01)
            expected_results.update(server02)
            expected_results.update(server03)
            expected_results.update(server04)
            expected_results.update(server04)
            expected_results.update(exit01)
            expected_results.update(exit02)
            expected_results.update(internet)
            expected_results.update(edge01)
            expected_results.update(oob_server)
            expected_results.update(oob_switch)
            expected_results["linkcount"] = 59

            # We don't test the MACs because we can't guarantee the order which the links parsed
            # MACs are assigned first come, first serve. Without a known order, we don't know which mac
            # will be assigned to which interface

            assert results["linkcount"] == expected_results["linkcount"]

            # Check that everything within a node matches, except the network and macs
            for key,value in expected_results.iteritems():
                if key == "linkcount" or key == "macs":
                    continue

                for node_attribute, attribute_value in expected_results[key].iteritems():
                    # Because we don't know the order that the interfaces will be processed
                    # We don't know what mac or link they will be assigned
                    # So just check that the same interfaces exist in both
                    if node_attribute == "interfaces":
                        if sorted(results[key]["interfaces"].keys()) != sorted(expected_results[key]["interfaces"].keys()):
                            print "Device: " + key
                            print "Result:"
                            pp.pprint(sorted(results[key]["interfaces"].keys()))
                            print "Expected:"
                            pp.pprint(sorted(expected_results[key]["interfaces"].keys()))
                        assert sorted(results[key]["interfaces"].keys()) == sorted(expected_results[key]["interfaces"].keys())
                        continue

                    # For all other node attributes make sure they are exact matches
                    if results[key][node_attribute] != expected_results[key][node_attribute]:
                        print "Result: " + results[key][node_attribute]
                        print "Expected: " + expected_results[key][node_attribute]
                    assert results[key][node_attribute] == expected_results[key][node_attribute]

            # Check all the topology defined MAC addresses
            assert results["server01"]["interfaces"]["eth1"]["mac"] == expected_results["server01"]["interfaces"]["eth1"]["mac"]
            assert results["server01"]["interfaces"]["eth2"]["mac"] == expected_results["server01"]["interfaces"]["eth2"]["mac"]
            assert results["server02"]["interfaces"]["eth1"]["mac"] == expected_results["server02"]["interfaces"]["eth1"]["mac"]
            assert results["server02"]["interfaces"]["eth2"]["mac"] == expected_results["server02"]["interfaces"]["eth2"]["mac"]
            assert results["server03"]["interfaces"]["eth1"]["mac"] == expected_results["server03"]["interfaces"]["eth1"]["mac"]
            assert results["server03"]["interfaces"]["eth2"]["mac"] == expected_results["server03"]["interfaces"]["eth2"]["mac"]
            assert results["server04"]["interfaces"]["eth1"]["mac"] == expected_results["server04"]["interfaces"]["eth1"]["mac"]
            assert results["server04"]["interfaces"]["eth2"]["mac"] == expected_results["server04"]["interfaces"]["eth2"]["mac"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp1"]["mac"] == expected_results["oob-mgmt-switch"]["interfaces"]["swp1"]["mac"]
            assert results["server01"]["interfaces"]["eth0"]["mac"] == expected_results["server01"]["interfaces"]["eth0"]["mac"]
            assert results["server02"]["interfaces"]["eth0"]["mac"] == expected_results["server02"]["interfaces"]["eth0"]["mac"]
            assert results["server03"]["interfaces"]["eth0"]["mac"] == expected_results["server03"]["interfaces"]["eth0"]["mac"]
            assert results["server04"]["interfaces"]["eth0"]["mac"] == expected_results["server04"]["interfaces"]["eth0"]["mac"]
            assert results["leaf01"]["interfaces"]["eth0"]["mac"] == expected_results["leaf01"]["interfaces"]["eth0"]["mac"]
            assert results["leaf02"]["interfaces"]["eth0"]["mac"] == expected_results["leaf02"]["interfaces"]["eth0"]["mac"]
            assert results["leaf03"]["interfaces"]["eth0"]["mac"] == expected_results["leaf03"]["interfaces"]["eth0"]["mac"]
            assert results["leaf04"]["interfaces"]["eth0"]["mac"] == expected_results["leaf04"]["interfaces"]["eth0"]["mac"]
            assert results["spine01"]["interfaces"]["eth0"]["mac"] == expected_results["spine01"]["interfaces"]["eth0"]["mac"]
            assert results["spine02"]["interfaces"]["eth0"]["mac"] == expected_results["spine02"]["interfaces"]["eth0"]["mac"]
            assert results["exit01"]["interfaces"]["eth0"]["mac"] == expected_results["exit01"]["interfaces"]["eth0"]["mac"]
            assert results["exit02"]["interfaces"]["eth0"]["mac"] == expected_results["exit02"]["interfaces"]["eth0"]["mac"]
            assert results["edge01"]["interfaces"]["eth0"]["mac"] == expected_results["edge01"]["interfaces"]["eth0"]["mac"]
            assert results["internet"]["interfaces"]["eth0"]["mac"] == expected_results["internet"]["interfaces"]["eth0"]["mac"]

            # Check that the network connections match
            assert results["leaf01"]["interfaces"]["swp51"]["network"] == results["spine01"]["interfaces"]["swp1"]["network"]
            assert results["leaf01"]["interfaces"]["swp52"]["network"] == results["spine02"]["interfaces"]["swp1"]["network"]
            assert results["leaf01"]["interfaces"]["swp49"]["network"] == results["leaf02"]["interfaces"]["swp49"]["network"]
            assert results["leaf01"]["interfaces"]["swp50"]["network"] == results["leaf02"]["interfaces"]["swp50"]["network"]
            assert results["leaf01"]["interfaces"]["swp1"]["network"] == results["server01"]["interfaces"]["eth1"]["network"]
            assert results["leaf01"]["interfaces"]["swp2"]["network"] == results["server02"]["interfaces"]["eth1"]["network"]

            assert results["leaf02"]["interfaces"]["swp51"]["network"] == results["spine01"]["interfaces"]["swp2"]["network"]
            assert results["leaf02"]["interfaces"]["swp52"]["network"] == results["spine02"]["interfaces"]["swp2"]["network"]
            assert results["leaf02"]["interfaces"]["swp49"]["network"] == results["leaf01"]["interfaces"]["swp49"]["network"]
            assert results["leaf02"]["interfaces"]["swp50"]["network"] == results["leaf01"]["interfaces"]["swp50"]["network"]
            assert results["leaf02"]["interfaces"]["swp1"]["network"] == results["server01"]["interfaces"]["eth2"]["network"]
            assert results["leaf02"]["interfaces"]["swp2"]["network"] == results["server02"]["interfaces"]["eth2"]["network"]

            assert results["leaf03"]["interfaces"]["swp51"]["network"] == results["spine01"]["interfaces"]["swp3"]["network"]
            assert results["leaf03"]["interfaces"]["swp52"]["network"] == results["spine02"]["interfaces"]["swp3"]["network"]
            assert results["leaf03"]["interfaces"]["swp49"]["network"] == results["leaf04"]["interfaces"]["swp49"]["network"]
            assert results["leaf03"]["interfaces"]["swp50"]["network"] == results["leaf04"]["interfaces"]["swp50"]["network"]
            assert results["leaf03"]["interfaces"]["swp1"]["network"] == results["server03"]["interfaces"]["eth1"]["network"]
            assert results["leaf03"]["interfaces"]["swp2"]["network"] == results["server04"]["interfaces"]["eth1"]["network"]

            assert results["leaf04"]["interfaces"]["swp51"]["network"] == results["spine01"]["interfaces"]["swp4"]["network"]
            assert results["leaf04"]["interfaces"]["swp52"]["network"] == results["spine02"]["interfaces"]["swp4"]["network"]
            assert results["leaf04"]["interfaces"]["swp49"]["network"] == results["leaf03"]["interfaces"]["swp49"]["network"]
            assert results["leaf04"]["interfaces"]["swp50"]["network"] == results["leaf03"]["interfaces"]["swp50"]["network"]
            assert results["leaf04"]["interfaces"]["swp1"]["network"] == results["server03"]["interfaces"]["eth2"]["network"]
            assert results["leaf04"]["interfaces"]["swp2"]["network"] == results["server04"]["interfaces"]["eth2"]["network"]

            assert results["exit01"]["interfaces"]["swp51"]["network"] == results["spine01"]["interfaces"]["swp30"]["network"]
            assert results["exit01"]["interfaces"]["swp52"]["network"] == results["spine02"]["interfaces"]["swp30"]["network"]
            assert results["exit01"]["interfaces"]["swp49"]["network"] == results["exit02"]["interfaces"]["swp49"]["network"]
            assert results["exit01"]["interfaces"]["swp50"]["network"] == results["exit02"]["interfaces"]["swp50"]["network"]
            assert results["exit01"]["interfaces"]["swp44"]["network"] == results["internet"]["interfaces"]["swp1"]["network"]
            assert results["exit01"]["interfaces"]["swp1"]["network"] == results["edge01"]["interfaces"]["eth1"]["network"]

            assert results["exit02"]["interfaces"]["swp51"]["network"] == results["spine01"]["interfaces"]["swp29"]["network"]
            assert results["exit02"]["interfaces"]["swp52"]["network"] == results["spine02"]["interfaces"]["swp29"]["network"]
            assert results["exit02"]["interfaces"]["swp49"]["network"] == results["exit01"]["interfaces"]["swp49"]["network"]
            assert results["exit02"]["interfaces"]["swp50"]["network"] == results["exit01"]["interfaces"]["swp50"]["network"]
            assert results["exit02"]["interfaces"]["swp44"]["network"] == results["internet"]["interfaces"]["swp2"]["network"]
            assert results["exit02"]["interfaces"]["swp1"]["network"] == results["edge01"]["interfaces"]["eth2"]["network"]

            assert results["spine01"]["interfaces"]["swp31"]["network"] == results["spine02"]["interfaces"]["swp31"]["network"]
            assert results["spine01"]["interfaces"]["swp32"]["network"] == results["spine02"]["interfaces"]["swp32"]["network"]

            assert results["oob-mgmt-switch"]["interfaces"]["swp1"]["network"] == results["oob-mgmt-server"]["interfaces"]["eth1"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp2"]["network"] == results["server01"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp3"]["network"] == results["server02"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp4"]["network"] == results["server03"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp5"]["network"] == results["server04"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp6"]["network"] == results["leaf01"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp7"]["network"] == results["leaf02"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp8"]["network"] == results["leaf03"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp9"]["network"] == results["leaf04"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp10"]["network"] == results["spine01"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp11"]["network"] == results["spine02"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp12"]["network"] == results["exit01"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp13"]["network"] == results["exit02"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp14"]["network"] == results["edge01"]["interfaces"]["eth0"]["network"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp15"]["network"] == results["internet"]["interfaces"]["eth0"]["network"]

    def test_reference_topology_libvirt(self):

            cli = CLI()
            pp = pprint.PrettyPrinter(indent=2)
            cli.topology_file = "./tests/dot_files/reference_topology_3_4_3.dot"
            cli.provider = "libvirt"
            cli.port_gap = "1000"
            cli.start_port = "1"
            results = tc.parse_topology(cli)


            leaf01 = {"leaf01": {
                        "function": "leaf",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000011",
                                "network": "net4"
                            }
                    }}}

            leaf02 = {"leaf02": {
                        "function": "leaf",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000012",
                                "network": "net4"
                            }
                    }}}

            leaf03 = {"leaf03": {
                        "function": "leaf",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000013",
                                "network": "net4"
                            }
                    }}}

            leaf04 = {"leaf04": {
                        "function": "leaf",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000014",
                                "network": "net4"
                            }
                    }}}

            spine01 = {"spine01": {
                        "function": "spine",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp1": {
                                "mac": "443839000001",
                                "network": "net0"
                            },
                            "swp2": {
                                "mac": "443839000003",
                                "network": "net1"
                            },
                            "swp3": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp3": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp4": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp29": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp30": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp31": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp32": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "eth0": {
                                "mac": "a00000000021",
                                "network": "net2"
                            }
                    }}}

            spine02 = {"spine02": {
                        "function": "spine",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp1": {
                                "mac": "443839000001",
                                "network": "net0"
                            },
                            "swp2": {
                                "mac": "443839000003",
                                "network": "net1"
                            },
                            "swp3": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp3": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp4": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp29": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp30": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp31": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "swp32": {
                                "mac": "443839000005",
                                "network": "net2"
                            },
                            "eth0": {
                                "mac": "a00000000022",
                                "network": "net2"
                            }
                    }}}

            exit01 = {"exit01": {
                        "function": "exit",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp44": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000041",
                                "network": "net4"
                            }
                    }}}
            exit02 = {"exit02": {
                        "function": "exit",
                        "config": "./helper_scripts/config_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp45": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp46": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp44": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp48": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp47": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp51": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp52": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp49": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp50": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "swp1": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000042",
                                "network": "net4"
                            }
                    }}}

            internet = {"internet": {
                        "function": "internet",
                        "config": "./helper_scripts/config_internet.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "version": "3.4.3",
                        "vagrant": "swp48",
                        "interfaces": {
                            "swp1": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000050",
                                "network": "net4"
                            }
                    }}}

            server01 = {"server01": {
                        "function": "host",
                        "config": "./helper_scripts/config_server.sh",
                        "memory": "512",
                        "os": "yk0/ubuntu-xenial",
                        "interfaces": {
                            "eth1": {
                                "mac": "000300111101",
                                "network": "net0"
                            },
                            "eth2": {
                                "mac": "000300111102",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000031",
                                "network": "net4"
                            }
                    }}}

            server02 = {"server02": {
                        "function": "host",
                        "config": "./helper_scripts/config_server.sh",
                        "memory": "512",
                        "os": "yk0/ubuntu-xenial",
                        "interfaces": {
                            "eth1": {
                                "mac": "000300222201",
                                "network": "net0"
                            },
                            "eth2": {
                                "mac": "000300222202",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000032",
                                "network": "net4"
                            }
                    }}}

            server03 = {"server03": {
                        "function": "host",
                        "config": "./helper_scripts/config_server.sh",
                        "memory": "512",
                        "os": "yk0/ubuntu-xenial",
                        "interfaces": {
                            "eth1": {
                                "mac": "000300333301",
                                "network": "net0"
                            },
                            "eth2": {
                                "mac": "000300333302",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000033",
                                "network": "net4"
                            }
                    }}}

            server04 = {"server04": {
                        "function": "host",
                        "config": "./helper_scripts/config_server.sh",
                        "memory": "512",
                        "os": "yk0/ubuntu-xenial",
                        "interfaces": {
                            "eth1": {
                                "mac": "000300444401",
                                "network": "net0"
                            },
                            "eth2": {
                                "mac": "000300444402",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000034",
                                "network": "net4"
                            }
                    }}}

            edge01 = {"edge01": {
                        "function": "host",
                        "config": "./helper_scripts/config_server.sh",
                        "memory": "768",
                        "os": "yk0/ubuntu-xenial",
                        "interfaces": {
                            "eth1": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "eth2": {
                                "mac": "443839000006",
                                "network": "net4"
                            },
                            "eth0": {
                                "mac": "a00000000051",
                                "network": "net4"
                            }
                    }}}

            oob_server = {"oob-mgmt-server": {
                        "function": "oob-server",
                        "config": "./helper_scripts/config_oob_server.sh",
                        "memory": "1024",
                        "os": "cumuluscommunity/vx_oob_server",
                        "vagrant": "eth0",
                        "version": "1.0.4",
                        "interfaces": {
                            "eth1": {
                                "mac": "443839000000",
                                "network": "net0"
                            }
                    }}}

            oob_switch = {"oob-mgmt-switch": {
                        "function": "oob-switch",
                        "config": "./helper_scripts/config_oob_switch.sh",
                        "memory": "768",
                        "os": "cumuluscommunity/cumulus-vx",
                        "vagrant": "eth0",
                        "version": "3.4.3",
                        "interfaces": {
                            "swp1": {
                                "mac": "a00000000061",
                                "network": "net0"
                            },
                            "swp2": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp3": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp4": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp5": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp6": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp7": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp8": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp9": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp10": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp11": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp12": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp13": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp14": {
                                "mac": "443839000000",
                                "network": "net0"
                            },
                            "swp15": {
                                "mac": "443839000000",
                                "network": "net0"
                            },

                    }}}

            expected_results = dict()
            expected_results.update(leaf01)
            expected_results.update(leaf02)
            expected_results.update(leaf03)
            expected_results.update(leaf04)
            expected_results.update(spine01)
            expected_results.update(spine02)
            expected_results.update(server01)
            expected_results.update(server02)
            expected_results.update(server03)
            expected_results.update(server04)
            expected_results.update(server04)
            expected_results.update(exit01)
            expected_results.update(exit02)
            expected_results.update(internet)
            expected_results.update(edge01)
            expected_results.update(oob_server)
            expected_results.update(oob_switch)
            expected_results["linkcount"] = 59

            # We don't test the MACs because we can't guarantee the order which the links parsed
            # MACs are assigned first come, first serve. Without a known order, we don't know which mac
            # will be assigned to which interface

            assert results["linkcount"] == expected_results["linkcount"]

            # Check that everything within a node matches, except the network and macs
            for key,value in expected_results.iteritems():
                if key == "linkcount" or key == "macs":
                    continue

                for node_attribute, attribute_value in expected_results[key].iteritems():
                    # Because we don't know the order that the interfaces will be processed
                    # We don't know what mac or link they will be assigned
                    # So just check that the same interfaces exist in both
                    if node_attribute == "interfaces":
                        if sorted(results[key]["interfaces"].keys()) != sorted(expected_results[key]["interfaces"].keys()):
                            print "Device: " + key
                            print "Result:"
                            pp.pprint(sorted(results[key]["interfaces"].keys()))
                            print "Expected:"
                            pp.pprint(sorted(expected_results[key]["interfaces"].keys()))
                        assert sorted(results[key]["interfaces"].keys()) == sorted(expected_results[key]["interfaces"].keys())
                        continue

                    # For all other node attributes make sure they are exact matches
                    if results[key][node_attribute] != expected_results[key][node_attribute]:
                        print "Result: " + results[key][node_attribute]
                        print "Expected: " + expected_results[key][node_attribute]
                    assert results[key][node_attribute] == expected_results[key][node_attribute]

            # Check all the topology defined MAC addresses
            assert results["server01"]["interfaces"]["eth1"]["mac"] == expected_results["server01"]["interfaces"]["eth1"]["mac"]
            assert results["server01"]["interfaces"]["eth2"]["mac"] == expected_results["server01"]["interfaces"]["eth2"]["mac"]
            assert results["server02"]["interfaces"]["eth1"]["mac"] == expected_results["server02"]["interfaces"]["eth1"]["mac"]
            assert results["server02"]["interfaces"]["eth2"]["mac"] == expected_results["server02"]["interfaces"]["eth2"]["mac"]
            assert results["server03"]["interfaces"]["eth1"]["mac"] == expected_results["server03"]["interfaces"]["eth1"]["mac"]
            assert results["server03"]["interfaces"]["eth2"]["mac"] == expected_results["server03"]["interfaces"]["eth2"]["mac"]
            assert results["server04"]["interfaces"]["eth1"]["mac"] == expected_results["server04"]["interfaces"]["eth1"]["mac"]
            assert results["server04"]["interfaces"]["eth2"]["mac"] == expected_results["server04"]["interfaces"]["eth2"]["mac"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp1"]["mac"] == expected_results["oob-mgmt-switch"]["interfaces"]["swp1"]["mac"]
            assert results["server01"]["interfaces"]["eth0"]["mac"] == expected_results["server01"]["interfaces"]["eth0"]["mac"]
            assert results["server02"]["interfaces"]["eth0"]["mac"] == expected_results["server02"]["interfaces"]["eth0"]["mac"]
            assert results["server03"]["interfaces"]["eth0"]["mac"] == expected_results["server03"]["interfaces"]["eth0"]["mac"]
            assert results["server04"]["interfaces"]["eth0"]["mac"] == expected_results["server04"]["interfaces"]["eth0"]["mac"]
            assert results["leaf01"]["interfaces"]["eth0"]["mac"] == expected_results["leaf01"]["interfaces"]["eth0"]["mac"]
            assert results["leaf02"]["interfaces"]["eth0"]["mac"] == expected_results["leaf02"]["interfaces"]["eth0"]["mac"]
            assert results["leaf03"]["interfaces"]["eth0"]["mac"] == expected_results["leaf03"]["interfaces"]["eth0"]["mac"]
            assert results["leaf04"]["interfaces"]["eth0"]["mac"] == expected_results["leaf04"]["interfaces"]["eth0"]["mac"]
            assert results["spine01"]["interfaces"]["eth0"]["mac"] == expected_results["spine01"]["interfaces"]["eth0"]["mac"]
            assert results["spine02"]["interfaces"]["eth0"]["mac"] == expected_results["spine02"]["interfaces"]["eth0"]["mac"]
            assert results["exit01"]["interfaces"]["eth0"]["mac"] == expected_results["exit01"]["interfaces"]["eth0"]["mac"]
            assert results["exit02"]["interfaces"]["eth0"]["mac"] == expected_results["exit02"]["interfaces"]["eth0"]["mac"]
            assert results["edge01"]["interfaces"]["eth0"]["mac"] == expected_results["edge01"]["interfaces"]["eth0"]["mac"]
            assert results["internet"]["interfaces"]["eth0"]["mac"] == expected_results["internet"]["interfaces"]["eth0"]["mac"]

            # Check that the network connections match
            assert results["leaf01"]["interfaces"]["swp51"]["network"]["port"]["local"] == results["spine01"]["interfaces"]["swp1"]["network"]["port"]["remote"]
            assert results["leaf01"]["interfaces"]["swp52"]["network"]["port"]["local"] == results["spine02"]["interfaces"]["swp1"]["network"]["port"]["remote"]
            assert results["leaf01"]["interfaces"]["swp49"]["network"]["port"]["local"] == results["leaf02"]["interfaces"]["swp49"]["network"]["port"]["remote"]
            assert results["leaf01"]["interfaces"]["swp50"]["network"]["port"]["local"] == results["leaf02"]["interfaces"]["swp50"]["network"]["port"]["remote"]
            assert results["leaf01"]["interfaces"]["swp1"]["network"]["port"]["local"] == results["server01"]["interfaces"]["eth1"]["network"]["port"]["remote"]
            assert results["leaf01"]["interfaces"]["swp2"]["network"]["port"]["local"] == results["server02"]["interfaces"]["eth1"]["network"]["port"]["remote"]

            assert results["leaf02"]["interfaces"]["swp51"]["network"]["port"]["local"] == results["spine01"]["interfaces"]["swp2"]["network"]["port"]["remote"]
            assert results["leaf02"]["interfaces"]["swp52"]["network"]["port"]["local"] == results["spine02"]["interfaces"]["swp2"]["network"]["port"]["remote"]
            assert results["leaf02"]["interfaces"]["swp49"]["network"]["port"]["local"] == results["leaf01"]["interfaces"]["swp49"]["network"]["port"]["remote"]
            assert results["leaf02"]["interfaces"]["swp50"]["network"]["port"]["local"] == results["leaf01"]["interfaces"]["swp50"]["network"]["port"]["remote"]
            assert results["leaf02"]["interfaces"]["swp1"]["network"]["port"]["local"] == results["server01"]["interfaces"]["eth2"]["network"]["port"]["remote"]
            assert results["leaf02"]["interfaces"]["swp2"]["network"]["port"]["local"] == results["server02"]["interfaces"]["eth2"]["network"]["port"]["remote"]

            assert results["leaf03"]["interfaces"]["swp51"]["network"]["port"]["local"] == results["spine01"]["interfaces"]["swp3"]["network"]["port"]["remote"]
            assert results["leaf03"]["interfaces"]["swp52"]["network"]["port"]["local"] == results["spine02"]["interfaces"]["swp3"]["network"]["port"]["remote"]
            assert results["leaf03"]["interfaces"]["swp49"]["network"]["port"]["local"] == results["leaf04"]["interfaces"]["swp49"]["network"]["port"]["remote"]
            assert results["leaf03"]["interfaces"]["swp50"]["network"]["port"]["local"] == results["leaf04"]["interfaces"]["swp50"]["network"]["port"]["remote"]
            assert results["leaf03"]["interfaces"]["swp1"]["network"]["port"]["local"] == results["server03"]["interfaces"]["eth1"]["network"]["port"]["remote"]
            assert results["leaf03"]["interfaces"]["swp2"]["network"]["port"]["local"] == results["server04"]["interfaces"]["eth1"]["network"]["port"]["remote"]

            assert results["leaf04"]["interfaces"]["swp51"]["network"]["port"]["local"] == results["spine01"]["interfaces"]["swp4"]["network"]["port"]["remote"]
            assert results["leaf04"]["interfaces"]["swp52"]["network"]["port"]["local"] == results["spine02"]["interfaces"]["swp4"]["network"]["port"]["remote"]
            assert results["leaf04"]["interfaces"]["swp49"]["network"]["port"]["local"] == results["leaf03"]["interfaces"]["swp49"]["network"]["port"]["remote"]
            assert results["leaf04"]["interfaces"]["swp50"]["network"]["port"]["local"] == results["leaf03"]["interfaces"]["swp50"]["network"]["port"]["remote"]
            assert results["leaf04"]["interfaces"]["swp1"]["network"]["port"]["local"] == results["server03"]["interfaces"]["eth2"]["network"]["port"]["remote"]
            assert results["leaf04"]["interfaces"]["swp2"]["network"]["port"]["local"] == results["server04"]["interfaces"]["eth2"]["network"]["port"]["remote"]

            assert results["exit01"]["interfaces"]["swp51"]["network"]["port"]["local"] == results["spine01"]["interfaces"]["swp30"]["network"]["port"]["remote"]
            assert results["exit01"]["interfaces"]["swp52"]["network"]["port"]["local"] == results["spine02"]["interfaces"]["swp30"]["network"]["port"]["remote"]
            assert results["exit01"]["interfaces"]["swp49"]["network"]["port"]["local"] == results["exit02"]["interfaces"]["swp49"]["network"]["port"]["remote"]
            assert results["exit01"]["interfaces"]["swp50"]["network"]["port"]["local"] == results["exit02"]["interfaces"]["swp50"]["network"]["port"]["remote"]
            assert results["exit01"]["interfaces"]["swp44"]["network"]["port"]["local"] == results["internet"]["interfaces"]["swp1"]["network"]["port"]["remote"]
            assert results["exit01"]["interfaces"]["swp1"]["network"]["port"]["local"] == results["edge01"]["interfaces"]["eth1"]["network"]["port"]["remote"]

            assert results["exit02"]["interfaces"]["swp51"]["network"]["port"]["local"] == results["spine01"]["interfaces"]["swp29"]["network"]["port"]["remote"]
            assert results["exit02"]["interfaces"]["swp52"]["network"]["port"]["local"] == results["spine02"]["interfaces"]["swp29"]["network"]["port"]["remote"]
            assert results["exit02"]["interfaces"]["swp49"]["network"]["port"]["local"] == results["exit01"]["interfaces"]["swp49"]["network"]["port"]["remote"]
            assert results["exit02"]["interfaces"]["swp50"]["network"]["port"]["local"] == results["exit01"]["interfaces"]["swp50"]["network"]["port"]["remote"]
            assert results["exit02"]["interfaces"]["swp44"]["network"]["port"]["local"] == results["internet"]["interfaces"]["swp2"]["network"]["port"]["remote"]
            assert results["exit02"]["interfaces"]["swp1"]["network"]["port"]["local"] == results["edge01"]["interfaces"]["eth2"]["network"]["port"]["remote"]

            assert results["spine01"]["interfaces"]["swp31"]["network"]["port"]["local"] == results["spine02"]["interfaces"]["swp31"]["network"]["port"]["remote"]
            assert results["spine01"]["interfaces"]["swp32"]["network"]["port"]["local"] == results["spine02"]["interfaces"]["swp32"]["network"]["port"]["remote"]

            assert results["oob-mgmt-switch"]["interfaces"]["swp1"]["network"]["port"]["local"] == results["oob-mgmt-server"]["interfaces"]["eth1"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp2"]["network"]["port"]["local"] == results["server01"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp3"]["network"]["port"]["local"] == results["server02"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp4"]["network"]["port"]["local"] == results["server03"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp5"]["network"]["port"]["local"] == results["server04"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp6"]["network"]["port"]["local"] == results["leaf01"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp7"]["network"]["port"]["local"] == results["leaf02"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp8"]["network"]["port"]["local"] == results["leaf03"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp9"]["network"]["port"]["local"] == results["leaf04"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp10"]["network"]["port"]["local"] == results["spine01"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp11"]["network"]["port"]["local"] == results["spine02"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp12"]["network"]["port"]["local"] == results["exit01"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp13"]["network"]["port"]["local"] == results["exit02"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp14"]["network"]["port"]["local"] == results["edge01"]["interfaces"]["eth0"]["network"]["port"]["remote"]
            assert results["oob-mgmt-switch"]["interfaces"]["swp15"]["network"]["port"]["local"] == results["internet"]["interfaces"]["eth0"]["network"]["port"]["remote"]
