#!/usr/bin/env python
"""   Topology Converter converts a given
topology.dot file to a Vagrantfile can use
the virtualbox or libvirt Vagrant providers
Initially written by Eric Pulvino 2015-10-19

 hosted @ https://github.com/cumulusnetworks/topology_converter
"""
# pylint: disable=C0302

import os
import re
import argparse
import ipaddress
import pydotplus
# import sys
# import time
# import pprint
# import jinja2

VERSION = "4.6.5"


class styles(object):# pylint: disable=C0103, R0903
    """Defines the terminal text colors for messages
    """
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

class NetworkNode(object):
    """Object that represents a specific node in the network.
    This is similar to a graphviz node.

    Attributes:
        hostname: the name of the node
        function: the function in network of the node (e.g., leaf, spine, oob-server)
        vm_os: the OS the node will use
        os_version: the version of OS to use
        memory: the amount of memory for the node
        tunnel_ip: if using libvirt, the tunnel IP that libvirt is to use
        other_attributes: a catch all for any other node specific attributes
    """

    # pylint: disable=R0902
    # pylint: disable=R0913
    def __init__(self, hostname, function, vm_os=None, memory=None,
                 config=None, os_version=None, tunnel_ip="127.0.0.1",
                 other_attributes=None):
        defaults = {
            "fake": {
                "os": "None",
                "memory": "1"
            },
            "oob-server": {
                "os": "yk0/ubuntu-xenial",
                "memory": "512",
                "config": "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh"
            },
            "oob-switch": {
                "os": "cumuluscommunity/cumulus-vx",
                "memory": "512",
                "config": "./helper_scripts/oob_switch_config.sh"
            },
            "host": {
                "os": "yk0/ubuntu-xenial",
                "memory": "512",
                "config": "./helper_scripts/extra_server_config.sh"
            },
            "pxehost": {
                "os": "None",
                "memory": "512",
                "config": "./helper_scripts/extra_server_config.sh"
            }
        }

        if self.check_hostname(hostname):
            self.hostname = hostname
        else:
            exit(1)

        self.function = function

        if self.function in defaults:
            if vm_os is None:
                vm_os = defaults[function]["os"]
            if memory is None:
                memory = defaults[function]["memory"]
            if config is None and function != "fake":
                config = defaults[function]["config"]
                if not os.path.isfile(config):
                    print(styles.WARNING + styles.BOLD +
                          "    WARNING: Node \"" + hostname +
                          " config file " + config + " does not exist" + styles.ENDC)

        try:
            if int(memory) <= 0:
                print(styles.FAIL + styles.BOLD +
                      " ### ERROR -- Memory must be greater than 0mb on " +
                      self.hostname + styles.ENDC)
                exit(1)
        except (ValueError, TypeError):
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR -- Memory value is invalid for " +
                  self.hostname + styles.ENDC)
            exit(1)

        if other_attributes is None:
            self.other_attributes = dict()
        else:
            self.other_attributes = other_attributes

        self.vm_os = vm_os
        self.memory = memory
        self.config = config
        self.tunnel_ip = tunnel_ip
        self.interfaces = {}
        self.os_version = os_version
        self.pxehost = "pxehost" in self.other_attributes
        self.has_pxe_interface = False

    @staticmethod
    def check_hostname(hostname):
        """Simple hostname validation.
        Using rules described in wikipedia article
        https://en.wikipedia.org/wiki/Hostname#Restrictions_on_valid_hostnames
        """

        # contain only the ASCII letters 'a' through 'z' (in a case-insensitive manner),
        # the digits '0' through '9', and the minus sign ('-').
        # The original specification of hostnames in RFC 952, mandated that labels could not
        # start with a digit or with a minus sign, and must not end with a minus sign.
        # However, a subsequent specification (RFC 1123) permitted hostname labels to start
        # with digits. No other symbols, punctuation characters, or white space are permitted.
        # While a hostname may not contain other characters, such as the underscore character (_)

        if len(hostname.strip()) <= 0:
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: Node name is blank" + styles.ENDC)

            return False

        # Hostname can only start with a letter or number
        if not re.compile('[A-Za-z0-9]').match(hostname[0]):
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: Node name can only start with letters or numbers " +
                  "'%s' is not valid!\n" % hostname + styles.ENDC)

            return False

        # Hostname can not end with a dash
        if not re.compile('[A-Za-z0-9]').match(hostname[-1]):
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: Node name can only end with letters or numbers " +
                  "'%s' is not valid!\n" % hostname + styles.ENDC)

            return False

        # Hostname can only contain A-Z, 0-9 and "-"
        if not re.compile('^[A-Za-z0-9\-]+$').match(hostname): # pylint: disable=W1401
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: Node name can only contain letters numbers and dash(-) " +
                  "'%s' is not valid!\n" % hostname + styles.ENDC)

            return False

        return True


    def get_interface(self, interface_name):
        """Returns the specificed NetworkInterface object for a given interface name.
        If the interface does not exist, returns None
        """
        if interface_name in self.interfaces:
            return self.interfaces[interface_name]

        return None


    def add_interface(self, network_interface):
        """Adds a NetworkInterface object to the interface collection.
        Returns the updated NetworkNode object.
        """

        # Check if any interface in this node is a pxe interface
        # and make sure there isn't a second interface
        # trying to be a pxe interface.
        if self.has_pxe_interface and network_interface.pxe_priority > 0:
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR -- Device " + self.hostname +
                  " sets pxebootinterface more than once." +
                  styles.ENDC)
            exit(1)

        # If this is the first time we've seen a pxe interface
        # then flip the flag on the Node
        elif network_interface.pxe_priority > 0:
            self.has_pxe_interface = True

        self.interfaces[network_interface.interface_name] = network_interface

        return self

    def __str__(self):
        output = []
        output.append("Hostname: " + (self.hostname or "None"))
        output.append("Function: " + (self.function or "None"))
        output.append("OS: " + (self.vm_os or "None"))
        output.append("OS Version: " + (self.os_version or "None"))
        output.append("Memory: " + (self.memory or "None"))
        output.append("Config: " + (self.config or "None"))
        output.append("Libvirt Tunnel IP: " + (self.tunnel_ip or "None"))
        output.append("Attributes: " + (str(self.other_attributes) or "None"))
        output.append("Interfaces: " + (str(self.interfaces) or "None"))
        return "\n".join(output)


class NetworkInterface(object):
    """A NetworkInterface is a single interface that can be attached
    to a NetworkNode and is part of a NetworkEdge.

    Attributes:
    hostname - the hostname that this interface is attached to
    interface_name - the name of the interface
    mac - the MAC address of the interface
    ip - the IP address of the interface
    network - for Virtualbox only, the network name the interface belongs to
    local_port - for Libvirt only, the libvirt local_port
    remote_port - for Libvirt only, the libvirt remote_port
    """
    # pylint: disable=R0902, R0913
    def __init__(self, hostname, interface_name, mac=None, ip=None,
                 network=None, local_port=None, remote_port=None):
        self.hostname = hostname
        self.interface_name = self.remove_interface_slash(interface_name)
        self.ip = ip # pylint: disable=C0103
        self.mac = self.validate_mac(mac)
        self.network = network
        self.local_port = local_port
        self.remote_port = remote_port
        self.attributes = {}
        self.pxe_priority = 0

    # def add_mac_colon(self, mac_address, cli_args):
    #     if cli_args.verbose:
    #         print("MAC ADDRESS IS: \"%s\"" % mac_address)
    #     return ':'.join(map(''.join, zip(*[iter(mac_address)] * 2)))


    def remove_interface_slash(self, interface_name):
        """Remove a / character from an interface name
        """
        if "/" in interface_name:
            new_interface = interface_name.replace('/', '-')
            print(styles.WARNING + styles.BOLD +
                  "    WARNING: Device " + str(self.hostname) + " interface"
                  " " + str(interface_name) + " contains a slash"
                  " and will be convereted to " + str(new_interface),
                  styles.ENDC)

            return new_interface

        return interface_name


    def add_attribute(self, attribute):
        """Add an attribute dict to the existing attributes dict
        """
        self.attributes.update(attribute)


    def validate_mac(self, mac):
        """Validate that the input MAC address
        """
        if mac is None:
            return None

        mac = mac.replace(":", "")
        mac = mac.replace(".", "")
        mac = mac.strip().lower()

        if len(mac) > 12:
            print(styles.FAIL + styles.BOLD + " ### ERROR: " + self.hostname + " MAC "
                  + mac + " is too long" + styles.ENDC)
            exit(1)

        if len(mac) < 12:
            print(styles.FAIL + styles.BOLD + " ### ERROR: " + self.hostname + " MAC "
                  + mac + " is too short" + styles.ENDC)
            exit(1)

        try:
            int(mac, 16)

        except Exception: # pylint: disable=W0703
            print(styles.FAIL + styles.BOLD + " ### ERROR: " + self.hostname + " MAC "
                  + mac + " could not be converted to hex. " +
                  "Perhaps there are bad characters?" + styles.ENDC)
            exit(1)

        # Broadcast
        if mac == "ffffffffffff":
            print(styles.FAIL + styles.BOLD + " ### ERROR: " + self.hostname + " MAC "
                  + mac + " is a broadcast address" + styles.ENDC)
            exit(1)

        # Invalid
        if mac == "000000000000":
            print(styles.FAIL + styles.BOLD + " ### ERROR: " + self.hostname + " MAC "
                  + mac + " is an invalid all zero MAC" + styles.ENDC)
            exit(1)

        # Multicast
        if mac[:6] == "01005e":
            print(styles.FAIL + styles.BOLD + " ### ERROR: " + self.hostname + " MAC "
                  + mac + " is a multicast MAC" + styles.ENDC)
            exit(1)

        return mac


    def __str__(self):
        """Print out the contents of the interface object
        """
        output = []
        output.append("Hostname: " + (self.hostname or "None"))
        output.append("interface_name: " + (self.interface_name or "None"))
        output.append("IP: " + (self.ip or "None"))
        output.append("MAC: " + (self.mac or "None"))
        output.append("Network: " + (self.network or "None"))
        output.append("Libvirt localport: " + (self.local_port or "None"))
        output.append("Libvirt remote port: " + (self.remote_port or "None"))
        output.append("PXE Priority: " + str(self.pxe_priority) or "None")
        output.append("Attributes: " + (str(self.attributes) or "None"))

        return "\n".join(output)

# pylint: disable=R0903
class NetworkEdge(object):
    """A network edge is a collection of two NetworkInterface objects that share a link
    """
    def __init__(self, left_side, right_side):
        self.left_side = left_side
        self.right_side = right_side


class Inventory(object):
    """An Inventory represents the entire network, with all nodes and edges.
    """
    # pylint: disable=R0902
    def __init__(self, current_libvirt_port=1024, libvirt_gap=8000):
        self.parsed_topology = None
        self.provider = None
        self.node_collection = dict()
        self.mac_set = set()
        self.provider_offset = 1
        self.current_libvirt_port = current_libvirt_port
        self.libvirt_gap = libvirt_gap
        # current_mac default is based on Cumulus Networks mac range
        # https://support.cumulusnetworks.com/hc/en-us/articles/203837076-Reserved-MAC-Address-Range-for-Use-with-Cumulus-Linux
        self.current_mac = "0x443839000000"
        self.oob_server = None
        self.oob_switch = None


    def add_node(self, node):
        """Add a NetworkNode to the inventory. Returns the updated inventory
        """
        if self.provider == "libvirt":
            unsupported_images = ["boxcutter/ubuntu1604",
                                  "bento/ubuntu-16.04",
                                  "ubuntu/xenial64"]

            if node.vm_os in unsupported_images:
                print(styles.FAIL + styles.BOLD + " ### ERROR: device " + node.hostname +
                      " -- Incompatible OS for libvirt provider.")
                print "\tDo not attempt to use a mutated image"
                print " for Ubuntu16.04 on Libvirt"
                print "\tuse an ubuntu1604 image which is natively built for libvirt"
                print "\tlike yk0/ubuntu-xenial."
                print "\tSee https://github.com/CumulusNetworks/topology_converter/tree/master/documentation#vagrant-box-selection" # pylint: disable=C0301
                print "\tSee https://github.com/vagrant-libvirt/vagrant-libvirt/issues/607" # pylint: disable=C0301
                print "\tSee https://github.com/vagrant-libvirt/vagrant-libvirt/issues/609" + styles.ENDC # pylint: disable=C0301

                exit(1)

        if node.function == "oob-server":
            self.oob_server = node
        elif node.function == "oob-switch":
            self.oob_switch = node

        if node.hostname == "oob-mgmt-server" and self.oob_server is None:
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: oob-mgmt-server must be set to function = \"oob-server\"" +
                  styles.ENDC)
            exit(1)

        if node.hostname == "oob-mgmt-switch" and self.oob_switch is None:
            print(styles.FAIL + styles.BOLD +
                  "### ERROR: oob-mgmt-switch must be set to function = \"oob-switch\""
                  + styles.ENDC)
            exit(1)
        self.node_collection[node.hostname] = node

        return self


    def get_node_by_name(self, node_name):
        """Return a specific NetworkNode() in the inventory by it's name
        """
        if node_name not in self.node_collection:
            return None

        return self.node_collection[node_name]


    def add_edge(self, network_edge):
        """Add an edge to the inventory and links the edge to the associated NetworkNode objects.
        This assumes the NetworkNode objects have already been added to the inventory.
        This expectes a NetworkEdge() object and returns the updated inventory.

        Keyword Arguments:
        network_edge - a tuple of NetworkEdge objects
        """

        for side in [network_edge.left_side, network_edge.right_side]:

            # Check if the interface has already been used.
            if self.get_node_by_name(side.hostname).get_interface(side.interface_name) is not None:
                print(styles.FAIL + styles.BOLD + " ### ERROR -- Interface " + side.interface_name +
                      " Already used on device: " + side.hostname + styles.ENDC)
                exit(1)

            else:

                # Get a MAC address for the interface, if it doesn't already have one
                if side.mac is None:
                    side.mac = self.get_mac()


        # Build the network links for virtualbox
        if self.provider == "virtualbox":
            network_edge.left_side.network = "network" + str(self.provider_offset)
            network_edge.right_side.network = "network" + str(self.provider_offset)
            self.provider_offset += 1

        # Build the local and remote ports for libvirt
        if self.provider == "libvirt":
            if self.current_libvirt_port > self.libvirt_gap:
                print(styles.FAIL + styles.BOLD +
                      " ### ERROR: Configured Port_Gap: (" + str(self.libvirt_gap) + ") \
                      exceeds the number of links in the topology." \
                      "Read the help options to fix.\n\n" +
                      styles.ENDC)
                exit(1)

            network_edge.left_side.local_port = str(self.current_libvirt_port)
            network_edge.right_side.remote_port = str(self.current_libvirt_port)

            network_edge.left_side.remote_port = str(self.current_libvirt_port + self.libvirt_gap)
            network_edge.right_side.local_port = str(self.current_libvirt_port + self.libvirt_gap)

            self.current_libvirt_port += 1

        left_node = self.get_node_by_name(network_edge.left_side.hostname)
        right_node = self.get_node_by_name(network_edge.right_side.hostname)

        left_node.add_interface(network_edge.left_side)
        right_node.add_interface(network_edge.right_side)

        return self


    def get_mac(self):
        """Provides a unique mac address.

        Keyword Arguments:
        network_interface: the NetworkInterface() object to provide MAC addresses for
        """
        while self.current_mac in self.mac_set:
            # Hex is stored as strings in python
            # To add, we have to make it an int with base 16
            # But then this returns a base 10 int. wtf.
            # So we have to cast to hex() to get the 0x string back
            self.current_mac = hex(int(self.current_mac, 16) + 1)

        new_mac = self.current_mac
        self.mac_set.add(new_mac)

        self.current_mac = hex(int(self.current_mac, 16) + 1)

        return new_mac


    def add_parsed_topology(self, parsed_topology):
        """Provided with a ParseGraphvizTopology object which has
        been populated with a topology (nodes and edges).
        This will turn that collection of nodes and edges into an inventory
        """
        for node in parsed_topology.nodes:
            self.add_node(node)

        for edge in parsed_topology.edges:
            self.add_edge(edge)

        return self

    @staticmethod
    def get_oob_ip(oob_server):
        """Determine the correct IP for the oob server.
        Either the user provided IP or 192.168.200.254/24
        """
        if "mgmt_ip" in oob_server.other_attributes:
            try:
                # If the netmask isn't provided, assume /24
                if oob_server.other_attributes["mgmt_ip"].find("/") < 0:
                    return ipaddress.ip_interface(
                        unicode(oob_server.other_attributes["mgmt_ip"] + "/24"))

                # If they set the management IP manually
                # on the existing server, use that one
                return ipaddress.ip_interface(unicode(oob_server.other_attributes["mgmt_ip"]))
            except Exception:  # pylint: disable=W0703
                print(styles.FAIL + styles.BOLD +
                        "Configured oob-mgmt-server management IP is invalid")
                exit(1)

        return ipaddress.ip_interface(u'192.168.200.254/24')

    def build_mgmt_network(self):
        """Build a management network and add it to the inventory.
        This will create an oob-mgmt-switch and oob-mgmt-server
        NetworkNode if they do not exist and will
        attach every inventory device's eth0 interface to
        the oob-mgmt-server
        """

        mgmt_switch_port_count = 1
        current_lease = 10
        dhcp_pool_size = 40

        # Create an oob-server if the user didn't define one
        if self.get_node_by_name("oob-mgmt-server") is None:
            oob_server = NetworkNode(hostname="oob-mgmt-server", function="oob-server")
        else:
            oob_server = self.get_node_by_name("oob-mgmt-server")

        # Create an oob-sswitch if the user didn't define one
        if self.get_node_by_name("oob-mgmt-switch") is None:
            oob_switch = NetworkNode(hostname="oob-mgmt-switch", function="oob-switch")
        else:
            oob_switch = self.get_node_by_name("oob-mgmt-switch")

        oob_server_ip = self.get_oob_ip(oob_server)

        # Add the oob server and switch to the inventory
        self.add_node(oob_server)
        self.add_node(oob_switch)

        # Connect the oob server and switch
        mgmt_port = "swp" + str(mgmt_switch_port_count)
        self.add_edge(NetworkEdge(NetworkInterface(hostname="oob-mgmt-server",
                                                   interface_name="eth1",
                                                   ip=str(oob_server_ip)),
                                  NetworkInterface(hostname="oob-mgmt-switch",
                                                   interface_name=mgmt_port)))

        # Look at all the hosts in the inventory and connect eth0 to the management switch
        for hostname, node_object in self.node_collection.iteritems():

            # Increment the oob switch port count
            mgmt_switch_port_count += 1

            # Create the oob-switch links and assign IPs to the hosts.
            if "mgmt_ip" in node_object.other_attributes:
                try:
                    # Check if there is a mask on the mgmt_ip attribute
                    # or assume /24
                    if node_object.other_attributes["mgmt_ip"].find("/") < 0:
                        node_ip = ipaddress.ip_interface(
                            unicode(node_object.other_attributes["mgmt_ip"] + "/24"))
                    else:
                        node_ip = ipaddress.ip_interface(node_object.other_attributes["mgmt_ip"])
                except Exception: # pylint: disable=W0703
                    print "Management IP address on " + node_object.hostname + " is invalid"
                    exit(1)

                # Verify node_ip in subnet of oob-server ip
                if not oob_server_ip.network == node_ip.network:
                    print "Management IP address on " + node_object.hostname + \
                          " is not in the same subnet " + \
                          " as the OOB server. OOB Server is configured for " + \
                          str(oob_server_ip) + ". " + node_object.hostname + " is configured" + \
                          " for " + str(node_ip)

                    exit(1)

                mgmt_port = "swp" + str(mgmt_switch_port_count)
                self.add_edge(NetworkEdge(
                    NetworkInterface(hostname=hostname, interface_name="eth0",
                                     ip=str(node_ip)),
                    NetworkInterface(hostname="oob-mgmt-switch",
                                     interface_name=mgmt_port)))
            else:
                if current_lease > dhcp_pool_size:
                    print(styles.FAIL + styles.BOLD +
                          " ### ERROR: Number of devices in management " +
                          "network exceeds DCHP pool size (" + str(dhcp_pool_size) + ")")
                    exit(1)

                self.add_edge(NetworkEdge(
                    NetworkInterface(hostname=hostname, interface_name="eth0",
                                     ip=str(oob_server_ip.network[current_lease])),
                    NetworkInterface(hostname="oob-mgmt-switch",
                                     interface_name="swp" + str(mgmt_switch_port_count))))
                current_lease += 1


# A class for this may not be the best thing,
# but seems easier than stand alone methods
class ParseGraphvizTopology(object):
    """Parses a graphviz dot file and creates an object with
    a list of NetworkNode and NetworkEdge objects
    """

    def __init__(self):

        self.topology_file = None
        self.nodes = list()
        self.edges = list()



    def parse_topology(self, topology_file):
        """
        Parse the provide graphviz topology object.

        Returns a NetworkInventory() object.
        """

        # Pass through simple linter first to identify easy problems
        if not self.lint_topology_file(topology_file):
            exit(1)

        # Open the .dot file and parse with graphviz
        try:
            graphviz_topology = pydotplus.graphviz.graph_from_dot_file(topology_file)

        except Exception:  # pragma: no cover # pylint: disable=W0703
            # Two known ways to get here:
            # 1.) The file changed or was deleted between lint_topology_file() and graphviz call
            # 2.) lint topo file should be extended to handle missed failure.
            # as a result this isn't in coverage
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: Cannot parse the provided topology.dot \
                  file (%s)\n     There is probably a syntax error \
                  of some kind, common causes include failing to \
                  close quotation marks and hidden characters from \
                  copy/pasting device names into the topology file."
                  % (topology_file) + styles.ENDC)

            exit(1)

        try:
            graphviz_nodes = graphviz_topology.get_node_list()
            graphviz_edges = graphviz_topology.get_edge_list()

        except Exception as exception:  # pragma: no cover # pylint: disable=W0703
            # Like the previous exception
            # if this is hit, it's either a corner, like file change
            # or we need to expand the linter
            print exception
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: There is a syntax error in your topology file \
                  (%s). Read the error output above for any clues as to the source."
                  % (self.topology_file) + styles.ENDC)

            exit(1)


        for node in graphviz_nodes:
            self.nodes.append(self.create_node_from_graphviz(node))

        for edge in graphviz_edges:
            self.edges.append(self.create_edge_from_graphviz(edge))

        return self

    @staticmethod
    def lint_topology_file(topology_file):
        """Validate the contents of the .dot topology file

        This is a simple linter for dot files to help identify
        where file errors are. This is independent of the full
        .dot file parser provided by pydot.

        This will check for:
         - ASCII encoding
         - Balanced double quotes ("")
         - Balanced single quotes/ticks ('')
         - That "--" exists to denote each side of the link

        Keyword arguments:
        topology_file - an ASCII encoded text file representing the topology
        """
        try:
            with open(topology_file, "r") as topo_file:
                line_list = topo_file.readlines()
                count = 0

                for line in line_list:
                    count += 1
                    # Try to encode into ascii
                    # TODO: understand if UTF-8 support is possible  # pylint: disable=W0511
                    # seems supported by pydot
                    try:
                        line.encode('ascii', 'ignore')

                    except UnicodeDecodeError:
                        print(styles.FAIL + styles.BOLD +
                              " ### ERROR: Line %s:\n %s\n         --> \"%s\" \n     \
                              Has hidden unicode characters in it which prevent it \
                              from being converted to ASCII cleanly. Try manually \
                              typing it instead of copying and pasting."
                              % (count, line, re.sub(r'[^\x00-\x7F]+', '?', line)) + styles.ENDC)
                        return False

                    if line.count("\"") % 2 == 1:
                        print(styles.FAIL + styles.BOLD +
                              " ### ERROR: Line %s: Has an odd \
                              number of quotation characters \
                              (\").\n     %s\n" % (count, line) + styles.ENDC)
                        return False

                    if line.count("'") % 2 == 1:
                        print(styles.FAIL + styles.BOLD +
                              " ### ERROR: Line %s: Has an odd \
                              number of quotation characters \
                              (').\n     %s\n" % (count, line) + styles.ENDC)
                        return False

                    if line.count(":") == 2:
                        if " -- " not in line:
                            print(styles.FAIL + styles.BOLD +
                                  " ### ERROR: Line %s: Does not \
                                  contain the following sequence \" -- \" \
                                  to seperate the different ends of the link.\n     %s\n"
                                  % (count, line) + styles.ENDC)

                            return False
        except Exception: # pylint: disable=W0703
            print(styles.FAIL + styles.BOLD +
                  "Problem opening file, " + topology_file + " perhaps it doesn't exist?" +
                  styles.ENDC)
            return False

        return True

    @staticmethod
    def create_edge_from_graphviz(graphviz_edge):
        """Take in a graphviz edge object and
        returns a new NetworkEdge object
        """

        left_hostname = graphviz_edge.get_source().split(":")[0].replace('"', '')
        left_interface = graphviz_edge.get_source().split(":")[1].replace('"', '')
        left_mac = graphviz_edge.get("left_mac")
        left_pxe = graphviz_edge.get("left_pxebootinterface")

        right_hostname = graphviz_edge.get_destination().split(":")[0].replace('"', '')
        right_interface = graphviz_edge.get_destination().split(":")[1].replace('"', '')
        right_mac = graphviz_edge.get("right_mac")
        right_pxe = graphviz_edge.get("right_pxebootinterface")

        left = NetworkInterface(hostname=left_hostname,
                                interface_name=left_interface, mac=left_mac)
        right = NetworkInterface(hostname=right_hostname,
                                 interface_name=right_interface, mac=right_mac)

        if left_pxe:
            left.pxe_priority = 1

        if right_pxe:
            right.pxe_priority = 1

        # Process passthrough attributes
        for attribute in graphviz_edge.get_attributes():
            value = graphviz_edge.get(attribute).strip("\"")

            # Since we already pulled out the mac, skip it
            if attribute == "left_mac" or attribute == "right_mac":
                continue

            if attribute.startswith('left_'):
                left.add_attribute({attribute[5:]: value})

            elif attribute.startswith('right_'):
                right.add_attribute({attribute[6:]: value})

            else:
                left.add_attribute({attribute: value})
                right.add_attribute({attribute: value})

        return NetworkEdge(left, right)

    @staticmethod
    def create_node_from_graphviz(graphviz_node):
        """Returns a NetworkNode object from a graphviz node object
        """
        hostname = graphviz_node.get_name().replace('"', '')

        # get_attributes() returns the list of settings at the top of the file
        # ex. {'function': '"spine"', 'config': '"./helper_scripts/config_switch.sh"',
        #      'version': '"3.4.3"', 'os': '"CumulusCommunity/cumulus-vx"', 'memory': '"768"'}
        #
        # all the graphviz object elements are wrapped in quotes.
        # Remember to remove them before processing
        graphviz_attributes = graphviz_node.get_attributes()

        vm_os = None
        function = "unknown"
        memory = None
        config = None
        other_attributes = {}
        pxehost = False

        for attribute_key in graphviz_attributes.keys():
            if attribute_key == "os":
                vm_os = graphviz_attributes["os"].replace("\"", "")

            elif attribute_key == "function":
                function = graphviz_attributes["function"].replace("\"", "").lower()

            elif attribute_key == "memory":
                memory = graphviz_attributes["memory"].replace("\"", "")

            elif attribute_key == "config":
                config = graphviz_attributes["config"].replace("\"", "").lower()

            elif attribute_key == "version":
                os_version = graphviz_attributes["version"].replace("\"", "").lower()

            # For any unhandled attributes, pass them through unmodified
            else:
                other_attributes.update({attribute_key.replace("\"", ""):
                                         graphviz_attributes[attribute_key].replace("\"", "")})

            if attribute_key == "pxehost":
                pxehost = True

        # Verify that they provided an OS for devices that aren't pxehost
        if vm_os is None and not pxehost:
            print styles.FAIL + styles.BOLD + \
                  " ### ERROR: OS not provided for " + hostname + styles.ENDC
            exit(1)

        return NetworkNode(hostname=hostname, function=function, vm_os=vm_os, memory=memory,
                           config=config, os_version=os_version, other_attributes=other_attributes)


def parse_arguments():
    """ Parse command line arguments, and return a dict of values."""
    parser = argparse.ArgumentParser(description='Topology Converter -- Convert \
                                     topology.dot files into Vagrantfiles')
    parser.add_argument('topology_file',
                        help='provide a topology file as input')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enables verbose logging mode')
    parser.add_argument('-p', '--provider', choices=["libvirt", "virtualbox"], default="virtualbox",
                        help='specifies the provider to be used in the Vagrantfile, \
                        script supports "virtualbox" or "libvirt", default is virtualbox.')
    parser.add_argument('-a', '--ansible-hostfile', action='store_true',
                        help='When specified, ansible hostfile will be generated \
                        from a dummy playbook run.')
    parser.add_argument('-c', '--create-mgmt-network', action='store_true',
                        help='When specified, a mgmt switch and server will be created. \
                        A /24 is assumed for the mgmt network. mgmt_ip=X.X.X.X will be \
                        read from each device to create a Static DHCP mapping for \
                        the oob-mgmt-server.')
    parser.add_argument('-cco', '--create-mgmt-configs-only', action='store_true',
                        help='Calling this option does NOT regenerate the Vagrantfile \
                        but it DOES regenerate the configuration files that come \
                        packaged with the mgmt-server in the "-c" option. This option \
                        is typically used after the "-c" has been called to generate \
                        a Vagrantfile with an oob-mgmt-server and oob-mgmt-switch to \
                        modify the configuraiton files placed on the oob-mgmt-server \
                        device. Useful when you do not want to regenerate the \
                        vagrantfile but you do want to make changes to the \
                        OOB-mgmt-server configuration templates.')
    parser.add_argument('-cmd', '--create-mgmt-device', action='store_true',
                        help='Calling this option creates the mgmt device and runs the \
                        auto_mgmt_network template engine to load configurations on to \
                        the mgmt device but it does not create the OOB-MGMT-SWITCH or \
                        associated connections. Useful when you are manually specifying \
                        the construction of the management network but still want to have \
                        the OOB-mgmt-server created automatically.')
    parser.add_argument('-t', '--template', action='append', nargs=2,
                        help='Specify an additional jinja2 template and a destination \
                        for that file to be rendered to.')
    parser.add_argument('-s', '--start-port', type=int, default=8000,
                        help='FOR LIBVIRT PROVIDER: this option overrides \
                        the default starting-port 8000 with a new value. \
                        Use ports over 1024 to avoid permissions issues. If using \
                        this option with the virtualbox provider it will be ignored.')
    parser.add_argument('-g', '--port-gap', type=int, default=1000,
                        help='FOR LIBVIRT PROVIDER: this option overrides the \
                        default port-gap of 1000 with a new value. This number \
                        is added to the start-port value to determine the port \
                        to be used by the remote-side. Port-gap also defines the \
                        max number of links that can exist in the topology. EX. \
                        If start-port is 8000 and port-gap is 1000 the first link \
                        will use ports 8001 and 9001 for the construction of the \
                        UDP tunnel. If using this option with the virtualbox \
                        provider it will be ignored.')
    parser.add_argument('-dd', '--display-datastructures', action='store_true',
                        help='When specified, the datastructures which are passed \
                        to the template are displayed to screen. Note: Using \
                        this option does not write a Vagrantfile and \
                        supercedes other options.')
    parser.add_argument('--synced-folder', action='store_true',
                        help='Using this option enables the default Vagrant \
                        synced folder which we disable by default. \
                        See: https://www.vagrantup.com/docs/synced-folders/basic_usage.html')
    parser.add_argument('--version', action='version', version="Topology \
                        Converter version is v%s" % VERSION,
                        help='Using this option displays the version of Topology Converter')

    # arg_string = " ".join(sys.argv)

    # if args.template:
    #     for templatefile, destination in args.template:
    #         TEMPLATES.append([templatefile, destination])

    # for templatefile, destination in TEMPLATES:
    #     if not os.path.isfile(templatefile):
    #         print(styles.FAIL + styles.BOLD + " ### ERROR: provided template file-- \"" +
    #               templatefile + "\" does not exist!" + styles.ENDC)
    #         exit(1)

    # if if args.verbose:
    #     print("Arguments:")
    #     print(args)

    return parser



############
## TODO   # pylint: disable=W0511
############

# Parse Arguments
# network_functions = ['oob-switch', 'internet', 'exit', 'superspine', 'spine', 'leaf', 'tor']
# function_group = {}
# provider = "virtualbox"
# generate_ansible_hostfile = False
# create_mgmt_device = False
# create_mgmt_network = False
# create_mgmt_configs_only = False
# verbose = False
# start_port = 8000
# port_gap = 1000
# synced_folder = False
# display_datastructures = False
# VAGRANTFILE = 'Vagrantfile'
# VAGRANTFILE_template = 'templates/Vagrantfile.j2'
# customer = os.path.basename(os.path.dirname(os.getcwd()))
# TEMPLATES = [[VAGRANTFILE_template, VAGRANTFILE]]

###################################
#### MAC Address Configuration ####
###################################

# # The starting MAC for assignment for any devices not in mac_map
# # Cumulus Range ( https://support.cumulusnetworks.com/hc/en-us/articles/203837076-Reserved-MAC-Address-Range-for-Use-with-Cumulus-Linux ) # pylint: disable=C0301
# start_mac = "443839000000"

# # This file is generated to store the mapping between macs and mgmt interfaces
# dhcp_mac_file = "./dhcp_mac_map"

# ######################################################
# #############    Everything Else     #################
# ######################################################

# # Hardcoded Variables
# script_storage = "./helper_scripts"
# epoch_time = str(int(time.time()))
# mac_map = {}


# def clean_datastructure(devices):
#     # Sort the devices by function
#     devices.sort(key=getKeyDevices)
#     for device in devices:
#         device['interfaces'] = sorted_interfaces(device['interfaces'])

#     if display_datastructures:
#         return devices
#     for device in devices:
#         print(styles.GREEN + styles.BOLD + ">> DEVICE: " + device['hostname'] + styles.ENDC)
#         print("     code: " + device['os'])

#         if 'memory' in device:
#             print("     memory: " + device['memory'])

#         for attribute in device:
#             if attribute == 'memory' or attribute == 'os' or attribute == 'interfaces':
#                 continue
#             print("     " + str(attribute) + ": " + str(device[attribute]))

#         for interface_entry in device['interfaces']:
#             print("       LINK: " + interface_entry["local_interface"])
#             for attribute in interface_entry:
#                 if attribute != "local_interface":
#                     print("               " + attribute + ": " + interface_entry[attribute])

#     # Remove Fake Devices
#     indexes_to_remove = []
#     for i in range(0, len(devices)):
#         if 'function' in devices[i]:
#             if devices[i]['function'] == 'fake':
#                 indexes_to_remove.append(i)
#     for index in sorted(indexes_to_remove, reverse=True):
#         del devices[index]
#     return devices


# def remove_generated_files():
#     if display_datastructures:
#         return
#     if verbose:
#         print("Removing existing DHCP FILE...")
#     if os.path.isfile(dhcp_mac_file):
#         os.remove(dhcp_mac_file)


# # _nsre = re.compile('([0-9]+)')


# def natural_sort_key(s):
#     return [int(text) if text.isdigit() else text.lower()
#             for text in re.split(_nsre, s)]


# def getKeyDevices(device):
#     # Used to order the devices for printing into the vagrantfile
#     if device['function'] == "oob-server":
#         return 1
#     elif device['function'] == "oob-switch":
#         return 2
#     elif device['function'] == "exit":
#         return 3
#     elif device['function'] == "superspine":
#         return 4
#     elif device['function'] == "spine":
#         return 5
#     elif device['function'] == "leaf":
#         return 6
#     elif device['function'] == "tor":
#         return 7
#     elif device['function'] == "host":
#         return 8
#     else:
#         return 9


# def sorted_interfaces(interface_dictionary):
#     sorted_list = []
#     interface_list = []

#     for link in interface_dictionary:
#         sorted_list.append(link)

#     sorted_list.sort(key=natural_sort_key)

#     for link in sorted_list:
#         interface_dictionary[link]["local_interface"] = link
#         interface_list.append(interface_dictionary[link])

#     return interface_list


# def generate_dhcp_mac_file(mac_map):
#     if verbose:
#         print("GENERATING DHCP MAC FILE...")

#     mac_file = open(dhcp_mac_file, "a")

#     if '' in mac_map:
#         del mac_map['']

#     dhcp_display_list = []

#     for line in mac_map:
#         dhcp_display_list.append(mac_map[line] + "," + line)

#     dhcp_display_list.sort()

#     for line in dhcp_display_list:
#         mac_file.write(line + "\n")

#     mac_file.close()


# def populate_data_structures(inventory):
#     global function_group
#     devices = []

#     for device in inventory:
#         inventory[device]['hostname'] = device
#         devices.append(inventory[device])

#     devices_clean = clean_datastructure(devices)

#     # Create Functional Group Map
#     for device in devices_clean:

#         if device['function'] not in function_group:
#             function_group[device['function']] = []

#         function_group[device['function']].append(device['hostname'])

#     return devices_clean


# def render_jinja_templates(devices):
#     global function_group

#     if display_datastructures:
#         print_datastructures(devices)

#     if verbose:
#         print("RENDERING JINJA TEMPLATES...")

#     # Render the MGMT Network stuff
#     if create_mgmt_device:
#         # Check that MGMT Template Dir exists
#         mgmt_template_dir = "./templates/auto_mgmt_network/"
#         if not os.path.isdir("./templates/auto_mgmt_network"):
#             print(styles.FAIL + styles.BOLD +
#                   "ERROR: " + mgmt_template_dir +
#                   " does not exist. Cannot populate templates!" +
#                   styles.ENDC)

#             exit(1)

#         # Scan MGMT Template Dir for .j2 files
#         mgmt_templates = []

#         for file in os.listdir(mgmt_template_dir):

#             if file.endswith(".j2"):
#                 mgmt_templates.append(file)

#         if verbose:
#             print(" detected mgmt_templates:")
#             print(mgmt_templates)

#         # Create output location for MGMT template files
#         mgmt_destination_dir = "./helper_scripts/auto_mgmt_network/"
#         if not os.path.isdir(mgmt_destination_dir):
#             if verbose:
#                 print("Making Directory for MGMT Helper Files: " + mgmt_destination_dir)

#             try:
#                 os.mkdir(mgmt_destination_dir)

#             except:
#                 print(styles.FAIL + styles.BOLD +
#                       "ERROR: Could not create output directory for mgmt template renders!" +
#                       styles.ENDC)
#                 exit(1)

#         # Render out the templates
#         for template in mgmt_templates:
#             render_destination = os.path.join(mgmt_destination_dir, template[0:-3])
#             template_source = os.path.join(mgmt_template_dir, template)

#             if verbose:
#                 print("    Rendering: " + template + " --> " + render_destination)

#             template = jinja2.Template(open(template_source).read())

#             with open(render_destination, 'w') as outfile:
#                 outfile.write(template.render(devices=devices,
#                                               synced_folder=synced_folder,
#                                               provider=provider,
#                                               version=version,
#                                               customer=customer,
#                                               topology_file=topology_file,
#                                               arg_string=arg_string,
#                                               epoch_time=epoch_time,
#                                               script_storage=script_storage,
#                                               generate_ansible_hostfile=generate_ansible_hostfile,
#                                               create_mgmt_device=create_mgmt_device,
#                                               function_group=function_group,
#                                               network_functions=network_functions,))

#     # Render the main Vagrantfile
#     if create_mgmt_device and create_mgmt_configs_only:
#         return 0

#     for templatefile, destination in TEMPLATES:

#         if verbose:
#             print("    Rendering: " + templatefile + " --> " + destination)

#         template = jinja2.Template(open(templatefile).read())

#         with open(destination, 'w') as outfile:
#             outfile.write(template.render(devices=devices,
#                                           synced_folder=synced_folder,
#                                           provider=provider,
#                                           version=version,
#                                           topology_file=topology_file,
#                                           arg_string=arg_string,
#                                           epoch_time=epoch_time,
#                                           script_storage=script_storage,
#                                           generate_ansible_hostfile=generate_ansible_hostfile,
#                                           create_mgmt_device=create_mgmt_device,
#                                           function_group=function_group,
#                                           network_functions=network_functions,))


# def print_datastructures(devices):
#     print("\n\n######################################")
#     print("   DATASTRUCTURES SENT TO TEMPLATE:")
#     print("######################################\n")
#     print("provider=" + provider)
#     print("synced_folder=" + str(synced_folder))
#     print("version=" + str(version))
#     print("topology_file=" + topology_file)
#     print("arg_string=" + arg_string)
#     print("epoch_time=" + str(epoch_time))
#     print("script_storage=" + script_storage)
#     print("generate_ansible_hostfile=" + str(generate_ansible_hostfile))
#     print("create_mgmt_device=" + str(create_mgmt_device))
#     print("function_group=")
#     pp.pprint(function_group)
#     print("network_functions=")
#     pp.pprint(network_functions)
#     print("devices=")
#     pp.pprint(devices)
#     exit(0)


# def generate_ansible_files():
#     if not generate_ansible_hostfile:
#         return

#     if verbose:
#         print("Generating Ansible Files...")

#     with open("./helper_scripts/empty_playbook.yml", "w") as playbook:
#         playbook.write("""---
# - hosts: all
#   user: vagrant
#   gather_facts: no
#   tasks:
#     - command: "uname -a"
# """)

#     with open("./ansible.cfg", "w") as ansible_cfg:
#         ansible_cfg.write("""[defaults]
# inventory = ./.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory
# hostfile= ./.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory
# host_key_checking=False
# callback_whitelist = profile_tasks
# jinja2_extensions=jinja2.ext.do""")


def main():
    """Main point of entry to parse a topology file,
    build an inventory and product a Vagrantfile
    """
    cli = parse_arguments()
    cli_args = cli.parse_args()

    print styles.HEADER + "\n######################################"
    print styles.HEADER + "          Topology Converter"
    print styles.HEADER + "######################################"
    print styles.BLUE + "           originally written by Eric Pulvino"

    parser = ParseGraphvizTopology()
    parsed_topology = parser.parse_topology(cli_args.topology_file)
    inventory = Inventory(parsed_topology, cli_args)

    if cli_args.create_mgmt_device:
        inventory.build_mgmt_network()

    # devices = populate_data_structures(inventory)

    # remove_generated_files()

    # render_jinja_templates(devices)

    # generate_dhcp_mac_file(mac_map)

    # generate_ansible_files()

    # if create_mgmt_configs_only:
    #     print(styles.GREEN + styles.BOLD +
    #           "\n############\nSUCCESS: MGMT Network Templates have been regenerated!\n############" +
    #           styles.ENDC)
    # else:
    #     print(styles.GREEN + styles.BOLD +
    #           "\n############\nSUCCESS: Vagrantfile has been generated!\n############" +
    #           styles.ENDC)
    #     print(styles.GREEN + styles.BOLD +
    #           "\n            %s devices under simulation." % (len(devices)) +
    #           styles.ENDC)

    # for device in inventory:
    #     print(styles.GREEN + styles.BOLD +
    #           "                %s" % (inventory[device]['hostname']) +
    #           styles.ENDC)

    # for warn_msg in warning:
    #     print(warn_msg)

    # print("\nDONE!\n")

    exit(0)

if __name__ == "__main__":
    main()
