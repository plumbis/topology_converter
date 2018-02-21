#!/usr/bin/env python2.7
"""   Topology Converter converts a given
topology.dot file to a Vagrantfile can use
the virtualbox or libvirt Vagrant providers
Initially written by Eric Pulvino 2015-10-19

 hosted @ https://github.com/cumulusnetworks/topology_converter
"""
# C0302 - Too many lines in module.
# Classes should probably be broken out, future work.
# Ignoring
# pylint: disable=C0302

import os
import re
import argparse
import ipaddress
import time
from collections import OrderedDict
import pydotplus
import jinja2


VERSION = "5.0.0"
VERBOSE = False

# R0903 too few public methods
# Overall error message styling needs to be improved, ignoring until that happens.
class Styles(object): # pylint: disable=R0903
    """Defines the terminal text colors for messages
    """
    HEADER = ''
    BLUE = ''
    GREEN = '\033[92m'
    WARNING = ''
    FAIL = ''
    BOLD = ''
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

class NetworkNode(object):
    """Object that represents a specific node in the network.
    This is similar to a graphviz node.

    Many of the attributes that can be set for a node are captured
    as instance variables. Anything not explicitly managed can be
    accessed through "other_attributes".

    In general, anything that does not require additional processing
    or error checking can be managed through other_attributes.

    Attributes:
        hostname: the name of the node
        function: the function in network of the node (e.g., leaf, spine, oob-server)
        vm_os: the OS the node will use
        os_version: the version of OS to use
        memory: the amount of memory for the node
        tunnel_ip: if using libvirt, the tunnel IP that libvirt is to use
        other_attributes: a catch all for any other node specific attributes
    """

    # R0902: Too many instance attributes.
    # R0913: Too many arguments
    # R0912: Too many branches
    # R0915: Too many statements
    # pylint: disable=R0902,R0913,R0912,R0915
    def __init__(self, hostname, function, vm_os=None, memory=None,
                 config=None, os_version=None, tunnel_ip="127.0.0.1",
                 other_attributes=None):

        # define default parameters for known functions.
        # all will be overridden by any provided attributes.
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

        # ensure the hostname is valid
        if self.check_hostname(hostname):
            self.hostname = hostname
        else:
            exit(1)

        self.function = function

        # Set optional attribute defaults
        # If they are set, these values will be changed later
        self.pxehost = False
        self.playbook = False
        self.remap = True
        self.ports = False
        self.ssh_port = False
        self.vagrant_user = "vagrant"
        self.legacy = False
        self.vagrant_interface = "vagrant"

        if VERBOSE: # pragma: no cover
            print "Building NetworkNode " + self.hostname + ". Function set as " + self.function

        if other_attributes is None:
            if VERBOSE: # pragma: no cover
                print "No other attributes found"
            self.other_attributes = dict()
        else:
            self.other_attributes = other_attributes

        self.mgmt_ip = self.get_node_mgmt_ip()

        if "pxehost" in self.other_attributes:
            self.pxehost = self.other_attributes["pxehost"] == "True"
            if VERBOSE: # pragma: no cover
                print "Pxehost set for " + self.hostname \
                + ". Default OS assignment will be skipped"

        if self.function in defaults:
            if vm_os is None and not self.pxehost:
                vm_os = defaults[function]["os"]
                if VERBOSE: # pragma: no cover
                    print "OS not found, using default of : " + vm_os

            if memory is None:
                memory = defaults[function]["memory"]
                if VERBOSE: # pragma: no cover
                    print "No memory defined, using default of " + memory

            if config is None and function != "fake":
                config = defaults[function]["config"]
                if VERBOSE: # pragma: no cover
                    print "No config defined, using default of " + config
                if not os.path.isfile(config):
                    print_warning("Node \"" + hostname +
                                  " config file " + config + " does not exist")

        try:
            if int(memory) <= 0:
                print_error("Memory must be greater than 0mb on " + self.hostname)

        except (ValueError, TypeError):
            print_error("Memory value is invalid for " + self.hostname)

        if "playbook" in self.other_attributes:
            self.playbook = self.other_attributes["playbook"]
            if VERBOSE: # pragma: no cover
                print "Found playbook " + self.playbook

        if "remap" in self.other_attributes:
            self.remap = self.other_attributes["remap"] == "True"
            if VERBOSE: # pragma: no cover
                print "Remap found and set to " + str(self.remap)

        if "ports" in self.other_attributes:
            try:
                if int(self.other_attributes["ports"]) <= 0:
                    print_error("Ports value " + self.hostname + " must be greater than 0")
            except(ValueError, TypeError):
                print_error("Ports value is invalid for " + self.hostname)

            self.ports = self.other_attributes["ports"]
            if VERBOSE: # pragma: no cover
                print "Ports " + self.ports + " defined on " + self.hostname

        if "ssh_port" in self.other_attributes:
            try:
                if int(self.other_attributes["ssh_port"]) <= 1024:
                    print_error("SSH port value for " +
                                self.hostname + " must be greater than 1024")
            except(ValueError, TypeError):
                print_error("SSH port value is invalid for " + self.hostname)

            self.ssh_port = self.other_attributes["ssh_port"]
            if VERBOSE: # pragma: no cover
                print "SSH port " + self.ssh_port + " defined on " + self.hostname

        if "vagrant" in self.other_attributes:
            self.vagrant_interface = self.other_attributes["vagrant"]
            if VERBOSE: # pragma: no cover
                print "Vagrant interface " + self.vagrant_interface + " defined on " + self.hostname

        if "vagrant_user" in self.other_attributes:
            self.vagrant_user = self.other_attributes["vagrant_user"]
            if VERBOSE: # pragma: no cover
                print "Vagrant user " + self.vagrant_user + " defined on " + self.hostname

        if "legacy" in self.other_attributes:
            self.legacy = self.other_attributes["legacy"] == "True"
            if VERBOSE: # pragma: no cover
                print "Legacy flag set to " + self.legacy + " on " + self.hostname

        self.vm_os = vm_os
        self.memory = memory
        self.config = config
        self.tunnel_ip = tunnel_ip
        self.interfaces = {}
        self.os_version = os_version
        self.has_pxe_interface = False

    def get_node_mgmt_ip(self):
        """Determine the management IP and return it as an IPInterface object.
        """
        if "mgmt_ip" in self.other_attributes:
            try:
                # Check if there is a mask on the mgmt_ip attribute
                # or assume /24
                if self.other_attributes["mgmt_ip"].find("/") < 0:
                    if VERBOSE:  # pragma: no cover
                        print "Management IP " + self.other_attributes["mgmt_ip"]\
                                + " found on " + self.hostname + " without mask. Assuming /24"
                    return ipaddress.ip_interface(unicode(self.other_attributes["mgmt_ip"] + "/24"))
                else:
                    if VERBOSE:  # pragma: no cover
                        print "Management IP " + self.other_attributes["mgmt_ip"]\
                                + " found on " + self.hostname
                    return ipaddress.ip_interface(unicode(self.other_attributes["mgmt_ip"]))

            except Exception:  # pylint: disable=W0703
                print_error("Management IP address on " + self.hostname + " is invalid")

        return None

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
            print(Styles.FAIL + Styles.BOLD +
                  " ### ERROR: Node name is blank" + Styles.ENDC)

            return False

        # Hostname can only start with a letter or number
        if not re.compile('[A-Za-z0-9]').match(hostname[0]):
            print(Styles.FAIL + Styles.BOLD +
                  " ### ERROR: Node name can only start with letters or numbers " +
                  "'%s' is not valid!\n" % hostname + Styles.ENDC)

            return False

        # Hostname can not end with a dash
        if not re.compile('[A-Za-z0-9]').match(hostname[-1]):
            print(Styles.FAIL + Styles.BOLD +
                  " ### ERROR: Node name can only end with letters or numbers " +
                  "'%s' is not valid!\n" % hostname + Styles.ENDC)

            return False

        # Hostname can only contain A-Z, 0-9 and "-"
        if not re.compile('^[A-Za-z0-9\-]+$').match(hostname): # pylint: disable=W1401
            print(Styles.FAIL + Styles.BOLD +
                  " ### ERROR: Node name can only contain letters numbers and dash(-) " +
                  "'%s' is not valid!\n" % hostname + Styles.ENDC)

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
            print_error(" Device " + self.hostname + " sets pxebootinterface more than once.")

        # If this is the first time we've seen a pxe interface
        # then flip the flag on the Node
        elif network_interface.pxe_priority > 0:
            self.has_pxe_interface = True

        self.interfaces[network_interface.interface_name] = network_interface

        return self



class NetworkInterface(object):
    """A NetworkInterface is a single interface that can be attached
    to a NetworkNode and is part of a NetworkEdge.

    A NetworkInterface should belong to exactly one NetworkNode,
    exactly once.

    The NetworkInterface is a unique object as a way to track the
    attributes that are unique/specific to that NetworkInterface.

    Note, that NetworkInterface is for a physical interface that
    would be part of the virtual topology within the environment.
    This means a bridge or loopback can not be a NetworkInterface object.

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
        self.remote_hostname = None
        self.remote_interface = None
        self.remote_ip = None

    def remove_interface_slash(self, interface_name):
        """Remove a / character from an interface name and
        replace it with "-" i.e., g0/0 becomes g0-0
        """
        if "/" in interface_name:
            new_interface = interface_name.replace('/', '-')
            print_warning("Device " + str(self.hostname) + " interface"
                          " " + str(interface_name) + " contains a slash"
                          " and will be convereted to " + str(new_interface))

            return new_interface

        return interface_name


    def add_attribute(self, attribute):
        """Add an attribute dict to the existing attributes dict
        """
        self.attributes.update(attribute)


    def validate_mac(self, mac):
        """Validate that the input MAC address is valid.
        This includes filtering out things like broadcast,
        multicast and all zero mac
        """
        if mac is None:
            return None

        mac = mac.replace(":", "")
        mac = mac.replace(".", "")
        mac = mac.strip().lower()

        if len(mac) > 12:
            print_error(self.hostname + " MAC " + mac + " is too long")

        if len(mac) < 12:
            print_error(self.hostname + " MAC " + mac + " is too short")

        try:
            int(mac, 16)

        except Exception: # pylint: disable=W0703
            print_error(self.hostname + " MAC " + mac + " could not be converted to hex. "\
             + "Perhaps there are bad characters?")

        # Broadcast
        if mac == "ffffffffffff":
            print_error(self.hostname + " MAC " + mac + " is a broadcast address")

        # Invalid
        if mac == "000000000000":
            print_error(self.hostname + " MAC " + mac + " is an invalid all zero MAC")

        # Multicast
        if mac[:6] == "01005e":
            print_error(self.hostname + " MAC " + mac + " is a multicast MAC")

        return mac


# pylint: disable=R0903
# Too few public methods.
class NetworkEdge(object):
    """A network edge is a collection of two NetworkInterface objects that share a link.
    This is a simple object to make accessing the interfaces easier.
    """
    def __init__(self, left_side, right_side):
        self.left_side = left_side
        self.right_side = right_side

        # Set the remote port information in the interfaces
        self.right_side.remote_hostname = self.left_side.hostname
        self.right_side.remote_interface = self.left_side.interface_name
        self.left_side.hostname = self.right_side.remote_hostname
        self.left_side.interface_name = self.right_side.remote_interface


class Inventory(object):
    """An Inventory represents the entire network, with all nodes and edges.
    The Inventory contains everything in the environment. All links, hosts, attributes, etc.

    The Inventory object is the final datastructure representing the dot file.
    """

    # TODO: Add support for displaying total inventory memory usage pylint: disable=W0511

    # pylint: disable=R0902
    # Too many instance attributes.
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
        self.mgmt_ips = set() # This is the set of management IPs in the network
        # this is used to prevent duplicates.
        # all of the elements should be of type ipaddress.ip_interface
        # ip_interface objects are in CIDR notation (10.1.1.1/24)
        # By default if no mask is provided it will create a /32, which isn't what we want.


    def calculate_memory(self):
        """Look at all nodes in the Inventory
        and return the total memory they will consume
        """
        total_memory = 0

        for node in self.node_collection.itervalues():
            total_memory += int(node.memory)

        return total_memory

    def add_node(self, node):
        """Add a NetworkNode to the inventory. Returns the updated inventory
        """
        if self.provider == "libvirt":
            unsupported_images = ["boxcutter/ubuntu1604",
                                  "bento/ubuntu-16.04",
                                  "ubuntu/xenial64"]

            # There are some OS images we know do not work
            # Prevent them from being loaded.
            if node.vm_os in unsupported_images:
                print_error("Incompatible libvirt OS on " + node.hostname\
                            + "\tDo not attempt to use a mutated image"
                            + " for Ubuntu16.04 on Libvirt"
                            + "\tuse an ubuntu1604 image which is natively built for libvirt"
                            + "\tlike yk0/ubuntu-xenial."
                            + "\tSee https://github.com/CumulusNetworks/topology_converter/tree/master/documentation#vagrant-box-selection"  # pylint: disable=C0301
                            + "\tSee https://github.com/vagrant-libvirt/vagrant-libvirt/issues/607"
                            + "\tSee https://github.com/vagrant-libvirt/vagrant-libvirt/issues/609")

        # Identify the oob switch and server if they exist.
        if node.function == "oob-server":
            self.oob_server = node
            if VERBOSE: # pragma: no cover
                print "Found OOB Server " + node.hostname

        elif node.function == "oob-switch":
            self.oob_switch = node
            if VERBOSE: # pragma: no cover
                print "Found OOB Switch " + node.nosthame

        # Don't allow something to be called "oob-mgmt-server"
        # if it isn't the oob-mgmt-server.
        # This could be made an option check, but is to prevent annoying
        # problems if you forget to set the function.
        if node.hostname == "oob-mgmt-server" and self.oob_server is None:
            print_error("The node namded oob-mgmt-server must be set to function = \"oob-server\"")

        # Same rules for the oob-mgmt-switch as above for the oob-mgmt-server.
        if node.hostname == "oob-mgmt-switch" and self.oob_switch is None:
            print_error("The node named oob-mgmt-switch must be set to function = \"oob-switch\"")

        if node.mgmt_ip is not None and node.mgmt_ip in self.mgmt_ips:
            print_error("Management IP address on " + node.hostname
                        + " is already in use. Likely it matches another static IP")
        else:
            self.mgmt_ips.add(node.mgmt_ip)

        self.node_collection[node.hostname] = node

        if VERBOSE: # pragma: no cover
            print "Added " + node.hostname + " to inventory"

        return self


    def get_node_by_name(self, node_name):
        """Return a specific NetworkNode() in the inventory by it's name.
        If the node can not be found None is returned.
        """
        if node_name not in self.node_collection:
            return None

        return self.node_collection[node_name]


    def add_edge(self, network_edge):
        """Add a NetworkEdge to the inventory and links the
        edge to the associated NetworkNode objects.
        This assumes the NetworkNode objects have already been added to the inventory.
        This expectes a NetworkEdge() object and returns the updated inventory.

        Keyword Arguments:
        network_edge - a NetworkEdge object
        """

        for side in [network_edge.left_side, network_edge.right_side]:

            # Check if the interface has already been used.
            # Multiaccess interfaces are not supported.
            if self.get_node_by_name(side.hostname).get_interface(side.interface_name) is not None:
                print_error("Interface " + side.interface_name +
                            " already used on device " + side.hostname)

            else:

                # Get a MAC address for the interface, if it doesn't already have one
                if side.mac is None:
                    side.mac = self.get_mac()
                    if VERBOSE: # pragma: no cover
                        print "Interface " + side.interface_name + " on " + side.hostname\
                              + " assigned MAC " + side.mac

        # Build the network links for virtualbox
        if self.provider == "virtualbox":
            network_edge.left_side.network = "network" + str(self.provider_offset)
            network_edge.right_side.network = "network" + str(self.provider_offset)
            if VERBOSE: # pragma: no cover
                print network_edge.left_side.hostname + ":"\
                      + network_edge.left_side.interface_name + " -- "\
                      + network_edge.right_side.hostname + ":"\
                      + network_edge.right_side.interface_name + " assigned offset "\
                      + self.provider_offset

            self.provider_offset += 1

        # Build the local and remote ports for libvirt
        if self.provider == "libvirt":
            if self.current_libvirt_port > self.libvirt_gap:
                print_error("Configured Port_Gap: (" + str(self.libvirt_gap) + ") "
                            "exceeds the number of links in the topology. "
                            "Read the help options to fix.\n\n")

            network_edge.left_side.local_port = str(self.current_libvirt_port)
            network_edge.right_side.remote_port = str(self.current_libvirt_port)

            network_edge.left_side.remote_port = str(self.current_libvirt_port + self.libvirt_gap)
            network_edge.right_side.local_port = str(self.current_libvirt_port + self.libvirt_gap)

            if VERBOSE: # pragma: no cover
                print network_edge.left_side.hostname + ":" + network_edge.left_side.interface_name\
                      + " local port: " + network_edge.left_side.local_port\
                      + " remote port: " + network_edge.left_side.remote_port
                print network_edge.right_side.hostname + ":"\
                      + network_edge.right_side.interface_name\
                      + " local port: " + network_edge.right_side.local_port\
                      + " remote port: " + network_edge.right_side.remote_port

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


    # R0912 - too many branches
    # R0915 - too many statements
    # R0914 - too many local variables
    def build_mgmt_network(self): # pylint: disable=R0912,R0915, R0914
        """Build a management network and add it to the inventory.
        This will create an oob-mgmt-switch and
        oob-mgmt-server NetworkNode if they do not exist and will
        attach every inventory device's eth0 interface to
        the oob-mgmt-server
        """

    # TODO: This is broken. Currently if oob server is .1 the oob-switch will be in conflict
    # Likely need to make a function to find the next IP
    # and keep the pool info globally.

        mgmt_switch_port_count = 1

        # Create an oob-server if the user didn't define one
        if self.oob_server is None:
            # If the OOB server isn't created we need a management IP to
            # base the rest of the network off of.
            # So enforce that the OOB server is 192.168.200.254/24
            # If the user wants something else or a larger subnet,
            # then they need to manually create the
            # OOB server and set the mgmt IP and we can do the rest
            oob_server = NetworkNode(hostname="oob-mgmt-server", function="oob-server",
                                     other_attributes={"mgmt_ip": "192.168.200.254/24"})
            self.add_node(oob_server)
            if VERBOSE: # pragma: no cover
                print "No oob-server found, one has been created"
        else:
            oob_server = self.oob_server
            if self.oob_server.mgmt_ip is None:
                self.oob_server.mgmt_ip = ipaddress.ip_interface(u'192.168.200.254/24')
                self.mgmt_ips.add(self.oob_server.mgmt_ip)


        # Define the DHCP Pool settings based on the OOB IP
        # If the default IP is used, the pool will start at 192.168.200.10
        # And be of size 244. This is 256 in a /24, -2 for the network/broadcast
        # -10 for the starting offset.
        #
        # Otherwise, let's dynamically size based on the provided OOB IP
        # This allows for much larger dynamic pools if required
        dhcp_pool_size = (self.oob_server.mgmt_ip.network.num_addresses - 2)
        current_lease = 1

        if dhcp_pool_size <= 3:
            # /29 gives 6 usable hosts, allowing for oob server, switch and hosts
            print_error("OOB Server subnet is too small for a valid DHCP pool."\
                        + " Minimum subnet mask is /29")


        # Create an oob-switch if the user didn't define one
        if self.oob_switch is None:
            self.add_node(NetworkNode(hostname="oob-mgmt-switch", function="oob-switch"))

            if VERBOSE: # pragma: no cover
                print "No oob-switch found, one has been created"

        # The management switch is a bit special
        # it's the only device with a logical management interface
        # as a result, we are going to put the IP and MAC in oob-mgmt-switch Node's attributes
        # because we can't create an edge since it's not connected to anything.

        switch_mac = self.get_mac()

        if self.oob_switch.mgmt_ip is None:

            # Everything is stored as ipaddress.IPInterface (in CIDR)
            # the .network[current_lease] returns an IPAddress without a mask
            oob_server_mask = "/" + \
                str(self.oob_server.mgmt_ip)[str(self.oob_server.mgmt_ip).find("/") + 1 :]
            candidate_lease = str(
                self.oob_server.mgmt_ip.network[current_lease])
            candidate_ip_object = ipaddress.ip_interface(unicode(candidate_lease + oob_server_mask))

            # Check if this IP is taken, if so, keep trying until we find the next free IP
            while candidate_ip_object in self.mgmt_ips:

                current_lease += 1
                candidate_lease = str(self.oob_server.mgmt_ip.network[current_lease])
                candidate_ip_object = ipaddress.ip_interface(
                    unicode(candidate_lease + oob_server_mask))

            oob_switch_ip = candidate_ip_object

            self.oob_switch.mgmt_ip = oob_switch_ip
            self.mgmt_ips.add(oob_switch_ip)

            if VERBOSE:  # pragma: no cover
                print "OOB-Switch dynamically assigned IP " + self.oob_switch.mgmt_ip

        self.oob_switch.other_attributes["bridge"] = {"mac": switch_mac,
                                                      "ip": self.oob_switch.mgmt_ip}
        if VERBOSE:  # pragma: no cover
            print  "OOB-Switch bridge created with MAC " + switch_mac + " and IP "\
                  + self.oob_switch.mgmt_ip

        # Connect the oob server and switch
        mgmt_port = "swp" + str(mgmt_switch_port_count)
        self.add_edge(NetworkEdge(NetworkInterface(hostname=self.oob_server.hostname,
                                                   interface_name="eth1",
                                                   ip=str(self.oob_server.mgmt_ip)),
                                  NetworkInterface(hostname=self.oob_switch.hostname,
                                                   interface_name=mgmt_port)))

        if VERBOSE: # pragma: no cover
            print "Management Link Added: "
            print self.oob_server.hostname + ":eth1 -- " + self.oob_switch.hostname + mgmt_port
            print ""

        for hostname, node_object in self.node_collection.iteritems():
            if hostname == "oob-mgmt-server" or hostname == "oob-mgmt-switch":
                continue

            # Increment the oob switch port count
            mgmt_switch_port_count += 1

            if node_object.mgmt_ip is not None:
                # Verify node_ip in subnet of oob-server ip
                if not self.oob_server.mgmt_ip.network == node_object.mgmt_ip.network:
                    print_error("Management IP address on " + node_object.hostname
                                + " is not in the same subnet as the OOB server."
                                + " OOB Server is configured for "
                                + str(self.oob_server.mgmt_ip) + ". "
                                + node_object.hostname + " is configured for "
                                + str(node_object.mgmt_ip))

                mgmt_port = "swp" + str(mgmt_switch_port_count)
                self.add_edge(NetworkEdge(
                    NetworkInterface(hostname=hostname, interface_name="eth0",
                                     ip=str(node_object.mgmt_ip)),
                    NetworkInterface(hostname="oob-mgmt-switch",
                                     interface_name=mgmt_port)))

            else:

                candidate_lease = str(self.oob_server.mgmt_ip.network[current_lease])
                candidate_ip_object = ipaddress.ip_interface(
                    unicode(candidate_lease + oob_server_mask))

                # Check if this IP is taken, if so, keep trying until we find the next free IP
                while candidate_ip_object in self.mgmt_ips:
                    # If picking the next IP exceeds the pool, exit.
                    if current_lease + 1 > dhcp_pool_size:
                        print_error("Number of devices in management "
                                    + "network exceeds DCHP pool size ("
                                    + str(dhcp_pool_size) + ")")

                    current_lease += 1
                    candidate_lease = str(self.oob_server.mgmt_ip.network[current_lease])
                    candidate_ip_object = ipaddress.ip_interface(
                        unicode(candidate_lease + oob_server_mask))

                self.add_edge(NetworkEdge(
                    NetworkInterface(hostname=hostname, interface_name="eth0",
                                     ip=str(candidate_ip_object)),
                    NetworkInterface(hostname="oob-mgmt-switch",
                                     interface_name="swp" + str(mgmt_switch_port_count))))
                node_object.mgmt_ip = candidate_ip_object
                self.mgmt_ips.add(candidate_ip_object)
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
        self.lint_topology_file(topology_file)

        # Open the .dot file and parse with graphviz
        try:
            graphviz_topology = pydotplus.graphviz.graph_from_dot_file(topology_file)

        except Exception:  # pragma: no cover # pylint: disable=W0703
            # Two known ways to get here:
            # 1.) The file changed or was deleted between lint_topology_file() and graphviz call
            # 2.) lint topo file should be extended to handle missed failure.
            # as a result this isn't in coverage
            print_error("Cannot parse the provided topology.dot file (%s)\n"\
                        + "There is probably a syntax error of some kind "\
                        + "common causes include failing to close quotation "\
                        + "marks and hidden characters from copy/pasting device"\
                        + "names into the topology file.")
        try:
            graphviz_nodes = graphviz_topology.get_node_list()
            graphviz_edges = graphviz_topology.get_edge_list()

        except Exception as exception:  # pragma: no cover # pylint: disable=W0703
            # Like the previous exception
            # if this is hit, it's either a corner, like file change
            # or we need to expand the linter
            print exception
            print_error("There is a syntax error in your topology file."\
                        + "Read the error output above for any clues as to the source.")

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
                    try:
                        line.encode('ascii', 'ignore')

                    except UnicodeDecodeError:
                        print_error("Line " + str(count) + ":\n"\
                                    + str(line) + "\n"\
                                    + "Has hidden unicode characters in it which"\
                                    + " prevent it from being converted to ASCII"\
                                    + " Try manually typing it instead of copying and pasting.")

                    if line.count("\"") % 2 == 1:
                        print_error("Line " + str(count) + ": Has an odd"\
                                    + " number of quotation characters \n"\
                                    + str(line))

                    if line.count("'") % 2 == 1:
                        print_error("Line " + str(count) + ": Has an odd"\
                                    + " number of quotation characters \n"\
                                    + str(line))

                    if line.count(":") == 2:
                        if " -- " not in line:
                            print_error("Line " + str(count) + " does not"\
                                        + "contain the required \" -- \" to"\
                                        + " seperate a link")

        #W0703 - Exception too broad
        except Exception: # pylint: disable=W0703
            print_error("Problem opening file, " + topology_file + " perhaps it doesn't exist?")

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

        if left_mac:
            left_mac = left_mac.replace('"', '')

        if right_mac:
            right_mac = right_mac.replace('"', '')

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
        os_version = None
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
            print_error("OS not provided for " + hostname)

        return NetworkNode(hostname=hostname, function=function, vm_os=vm_os, memory=memory,
                           config=config, os_version=os_version, other_attributes=other_attributes)


def parse_arguments():
    """ Parse command line arguments, and return a dict of values.
    """
    parser = argparse.ArgumentParser(description="Topology Converter -- Convert \
                                     topology.dot files into Vagrantfiles")

    parser.add_argument("topology_file",
                        help="provide a topology file as input")

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="enables verbose logging mode")

    parser.add_argument("-p", "--provider", choices=["libvirt", "virtualbox"], default="virtualbox",
                        help="specifies the provider to be used in the Vagrantfile, \
                        script supports 'virtualbox' or 'libvirt', default is virtualbox.")

    parser.add_argument("-a", "--ansible-hostfile", action="store_true",
                        help="When specified, ansible hostfile will be generated \
                        from a dummy playbook run.")

    parser.add_argument("-c", "--create-mgmt-network", action="store_true",
                        help="When specified, a mgmt switch and server will be created. \
                        A /24 is assumed for the mgmt network. mgmt_ip=X.X.X.X will be \
                        read from each device to create a Static DHCP mapping for \
                        the oob-mgmt-server.")

    parser.add_argument("-cco", "--create-mgmt-configs-only", action="store_true",
                        help="Calling this option does NOT regenerate the Vagrantfile \
                        but it DOES regenerate the configuration files that come \
                        packaged with the mgmt-server in the '-c' option. This option \
                        is typically used after the '-c' has been called to generate \
                        a Vagrantfile with an oob-mgmt-server and oob-mgmt-switch to \
                        modify the configuraiton files placed on the oob-mgmt-server \
                        device. Useful when you do not want to regenerate the \
                        vagrantfile but you do want to make changes to the \
                        OOB-mgmt-server configuration templates.")

    parser.add_argument("-cmd", "--create-mgmt-device", action="store_true",
                        help="Calling this option creates the mgmt device and runs the \
                        auto_mgmt_network template engine to load configurations on to \
                        the mgmt device but it does not create the OOB-MGMT-SWITCH or \
                        associated connections. Useful when you are manually specifying \
                        the construction of the management network but still want to have \
                        the OOB-mgmt-server created automatically.")

    parser.add_argument("-t", "--template", action="append", nargs=2,
                        help="Specify an additional jinja2 template and a destination \
                        for that file to be rendered to.")

    parser.add_argument("-s", "--start-port", type=int, default=8000,
                        help="FOR LIBVIRT PROVIDER: this option overrides \
                        the default starting-port 8000 with a new value. \
                        Use ports over 1024 to avoid permissions issues. If using \
                        this option with the virtualbox provider it will be ignored.")

    parser.add_argument("-g", "--port-gap", type=int, default=1000,
                        help="FOR LIBVIRT PROVIDER: this option overrides the \
                        default port-gap of 1000 with a new value. This number \
                        is added to the start-port value to determine the port \
                        to be used by the remote-side. Port-gap also defines the \
                        max number of links that can exist in the topology. EX. \
                        If start-port is 8000 and port-gap is 1000 the first link \
                        will use ports 8001 and 9001 for the construction of the \
                        UDP tunnel. If using this option with the virtualbox \
                        provider it will be ignored.")

    parser.add_argument("-dd", "--display-datastructures", action="store_true",
                        help="When specified, the datastructures which are passed \
                        to the template are displayed to screen. Note: Using \
                        this option does not write a Vagrantfile and \
                        supercedes other options.")

    parser.add_argument("--synced-folder", action="store_true",
                        help="Using this option enables the default Vagrant \
                        synced folder which we disable by default. \
                        See: https://www.vagrantup.com/docs/synced-folders/basic_usage.html")

    parser.add_argument("--version", action="version", version="Topology \
                        Converter version is v%s" % VERSION,
                        help="Using this option displays the version of Topology Converter")

    parser.add_argument("--vagrantfile", default="Vagrantfile",
                        help="Define a customer file to output instead of 'Vagrantfile'")

    return parser


def check_files(cli_args, vagrant_template):
    """Verify that all required files can be opened.
    This includes the template file based by the command line
    and the default vagrantfile .j2 jinja template
    """

    if cli_args.template:
        custom_template = str(cli_args.template[0][0])
        if not os.path.isfile(custom_template):
            print_error("Provided template file-- \""\
                        + custom_template + "\" does not exist!")

    if not os.path.isfile(vagrant_template):
        print_error("Default Vagrant Template \"" + vagrant_template + "\" does not exist!")

    return True

def format_mac(mac_address):
    """Take in a mac address string like 00a22345feff0012
    and return a mac formatted as 00:a2:23:45:fe:ff:00:12
    """
    return ':'.join(map(''.join, zip(*[iter(mac_address)] * 2)))


def render_ansible_hostfile(inventory, topology_file, input_dir):
    """Provides the logic to build an ansible hosts file from a jinja2 template
    """
    hostfile_template = os.path.join(input_dir, "ansible_hostfile.j2")

    # the variables that will be passed to the template
    jinja_variables = {"version": VERSION, "topology": topology_file}

    node_dict = {}
    es_plural_suffix = ["ss", "sh", "ch", "x", "z", "s"]

    for node in inventory.node_collection.itervalues():
        # Don't do anything for fake devices
        if node.function == "fake":
            continue

        ansible_function = node.function

        # If the plural of the word is "es" then
        # add an e for when the jinja template adds an "s"
        # For examples, switches
        if node.function[-2:] in es_plural_suffix or node.function[-1:] in es_plural_suffix:
            ansible_function = node.function + "e"

        if ansible_function in node_dict:
            node_dict[ansible_function].append(node)
        else:
            node_dict[ansible_function] = [node]


    jinja_variables["node_dict"] = node_dict
    template = jinja2.Template(open(hostfile_template).read())

    return template.render(jinja_variables)


def render_dhcpd_conf(inventory, topology_file, input_dir):
    """Generate a dhcpd.conf output based on the inventory using the jinja2 template
    """

    dhcpd_conf_template = os.path.join(input_dir, "dhcpd.conf.j2")

    jinja_variables = {"version": VERSION, "topology": topology_file}

    # we wouldn't be building this if the oob-mgmt-server doesn't exist
    oob_server = inventory.oob_server

    # but check just in case
    if oob_server is None:
        print_error("Something went wrong, no OOB Server exists. Failed to build dhcpd.conf")

    #ipaddress.network returns CIDR 192.168.1.0/24
    oob_ipaddress = ipaddress.ip_interface(unicode((oob_server.get_interface("eth1").ip)))
    jinja_variables["dhcp_subnet"] = str(oob_ipaddress.network).split("/")[0]
    jinja_variables["dhcp_netmask"] = str(oob_ipaddress.netmask)
    jinja_variables["oob_server_ip"] = str(oob_ipaddress).split("/")[0]

    # TODO: Make this dynamic
    jinja_variables["dhcp_start"] = "192.168.200.10"
    jinja_variables["dhcp_end"] = "192.168.200.138"

    template = jinja2.Template(open(dhcpd_conf_template).read())

    return template.render(jinja_variables)


def render_dhcpd_hosts(inventory, topology_file, input_dir):
    """Generate the contents of a dhcpd.hosts static DHCP binding file
    based on a jinja2 template
    """
    dhcpd_hosts_template = os.path.join(input_dir, "dhcpd.hosts.j2")

    # the variables that will be passed to the template
    jinja_variables = {"version": VERSION, "topology": topology_file}

    # we wouldn't be building this if the oob-mgmt-server doesn't exist
    oob_server = inventory.oob_server

    # but check just in case
    if oob_server is None:
        print_error("Something went wrong, no OOB Server exists. Failed to build dhcpd.hosts")

    oob_ipaddress = ipaddress.ip_interface(unicode((oob_server.get_interface("eth1").ip)))
    jinja_variables["oob_server_ip"] = str(oob_ipaddress).split("/")[0]

    node_dict = {}

    for node in inventory.node_collection.itervalues():
        # Don't do anything for fake devices
        if node.function == "fake":
            continue

        # OOB Mgmt Server doesn't use DHCP
        if node.function == "oob-server":
            continue

        if node.function == "oob-switch":
            # Assign OOB IP to the oob-switch bridge interface
            mac_address = format_mac(node.other_attributes["bridge"]["mac"][2:])
            node_dict[node.hostname] = {
                "mac": mac_address, "ip": node.other_attributes["bridge"]["ip"]}

        else:
            dhcp_interface = "eth0"
            # The mac is stored as 0x...., send the substring without the 0x part to be formatted
            mac_address = format_mac(node.interfaces[dhcp_interface].mac[2:])
            node_dict[node.hostname] = {
                "mac": mac_address, "ip": node.interfaces[dhcp_interface].ip}

        if "ztp" in node.other_attributes:
            node_dict[node.hostname]["ztp"] = node.other_attributes["ztp"]
        else:
            if node.function in ("leaf", "spine", "oob-switch"):
                node_dict[node.hostname]["ztp"] = "ztp_oob.sh"

    jinja_variables["node_dict"] = node_dict
    template = jinja2.Template(open(dhcpd_hosts_template).read())

    return template.render(jinja_variables)


def render_hosts_file(inventory, topology_file, input_dir):
    """Generate the contents of a hosts static DNS lookup file
    based on a jinja2 template
    """
    dns_hosts = os.path.join(input_dir, "hosts.j2")

    # the variables that will be passed to the template
    jinja_variables = {"version": VERSION, "topology": topology_file}

    # we wouldn't be building this if the oob-mgmt-server doesn't exist
    oob_server = inventory.oob_server

    # but check just in case
    if oob_server is None:
        print_error("Something went wrong, no OOB Server exists. Failed to build DNS hosts")

    oob_ipaddress = ipaddress.ip_interface(unicode((oob_server.get_interface("eth1").ip)))
    jinja_variables["oob_server_ip"] = str(oob_ipaddress).split("/")[0]
    jinja_variables["oob_hostname"] = oob_server.hostname

    node_dict = {}

    for node in inventory.node_collection.itervalues():

        # We already have what we need for the oob server
        if node.function == "oob-server":
            continue

        # Don't do anything for fake devices
        if node.function == "fake":
            continue

        if node.function == "oob-switch":
            node_dict[node.hostname] = {
                "ip": str(node.other_attributes["bridge"]["ip"]).split("/")[0]}

        else:
            node_dict[node.hostname] = {"ip": node.interfaces["eth0"].ip}

    jinja_variables["node_dict"] = node_dict
    template = jinja2.Template(open(dns_hosts).read())

    return template.render(jinja_variables)


def render_oob_server_sh(inventory, topology_file, input_dir):
    """Generate the contents of the oob server config.sh
    file based on a jinja2 template
    """
    oob_config = os.path.join(input_dir, "OOB_Server_config_auto_mgmt.sh.j2")

    # the variables that will be passed to the template
    jinja_variables = {"version": VERSION, "topology": topology_file}

    # we wouldn't be building this if the oob-mgmt-server doesn't exist
    oob_server = inventory.oob_server

    # but check just in case
    if oob_server is None:
        print_error("Something went wrong, no OOB Server exists. Failed to build"\
                    + "OOB_Server_config_auto_mgmt.sh")

    oob_ipaddress = ipaddress.ip_interface(unicode((oob_server.get_interface("eth1").ip)))
    jinja_variables["oob_server_ip"] = str(oob_ipaddress).split("/")[0]
    jinja_variables["oob_cidr"] = str(oob_ipaddress)

    if "ntp" in oob_server.other_attributes:
        jinja_variables["oob"] = {"ntp": oob_server.other_attributes["ntp"]}
    else:
        jinja_variables["oob"] = {"ntp": "pool.ntp.org"}

    template = jinja2.Template(open(oob_config).read())

    return template.render(jinja_variables)


def render_ztp_oob(inventory, topology_file, input_dir):
    """Generate the contents of the default ztp script
    based on a jinja2 template
    """
    oob_config = os.path.join(input_dir, "ztp_oob.sh.j2")

    # the variables that will be passed to the template
    jinja_variables = {"version": VERSION, "topology": topology_file}

    # we wouldn't be building this if the oob-mgmt-server doesn't exist
    oob_server = inventory.oob_server

    # but check just in case
    if oob_server is None:
        print_error("Something went wrong, no OOB Server exists. Failed to build ztp_oob.sh")
        exit(1)

    oob_ipaddress = ipaddress.ip_interface(unicode((oob_server.get_interface("eth1").ip)))
    jinja_variables["oob_server_ip"] = str(oob_ipaddress).split("/")[0]

    template = jinja2.Template(open(oob_config).read())

    return template.render(jinja_variables)


def render_vagrantfile(inventory, input_dir, cli): #pylint: disable=R0912
    """Generate the contents of the Vagrantfile
    based on a jinja2 template
    """
    if cli.template:
        vagrant_template = cli.template
    else:
        vagrant_template = "Vagrantfile.j2"

    # the variables that will be passed to the template
    jinja_variables = {"version": VERSION, "topology": cli.topology_file, "cli_args": cli}

    # time.time() returns float 1518118901.04, the whole number is good enough
    jinja_variables["epoch_time"] = str(time.time()).split(".")[0]

    # Dict of all functions in the topology
    # key is the function
    # value is list of hostnames
    function_dict = {}
    jinja_variables["known_functions"] = ["oob-switch", "internet", "hosts"
                                          "exit", "superspine", "spine", "leaf", "tor"]
    node_dict = OrderedDict()

    # Iterate over all of the nodes
    # Put them in both a function: node dict
    # as well as a hostname: node dict
    # this makes processing in the j2 file easier.
    for node in inventory.node_collection.itervalues():
        # Don't do anything for fake devices
        if node.function == "fake":
            continue

        # if we've seen this function before
        # append the hostname to the list
        if node.function in function_dict:
            function_dict[node.function].append(node)

        else:
            function_dict[node.function] = [node]


    # We need an ordered collection of the devices in the network
    # This allows us to bring up devices in a defined order.
    # oob-server, oob-switch, exit, superspine, spine, leaf, tor, host
    #
    # To do this, check if we have anything of that function from function_dict
    # if so, take the list of nodes with that function and put it in our OrderedDict
    if "oob-server" in function_dict:
        node_dict["oob-server"] = function_dict["oob-server"]

    if "oob-switch" in function_dict:
        node_dict["oob-switch"] = function_dict["oob-switch"]

    if "exit" in function_dict:
        node_dict["exit"] = function_dict["exit"]

    if "superspine" in function_dict:
        node_dict["superspine"] = function_dict["superspine"]

    if "spine" in function_dict:
        node_dict["spine"] = function_dict["spine"]

    if "leaf" in function_dict:
        node_dict["leaf"] = function_dict["leaf"]

    if "tor" in function_dict:
        node_dict["tor"] = function_dict["tor"]

    if "host" in function_dict:
        node_dict["host"] = function_dict["host"]

    for function in function_dict:
        if function not in node_dict:
            node_dict[function] = function_dict[function]


    jinja_variables["function_dict"] = function_dict
    jinja_variables["nodes"] = node_dict

    # It's required to set the jinja2 environment
    # so that the {% include %} statements within the Vagrantfile.j2
    # template knows where to look.
    env = jinja2.Environment()
    env.loader = jinja2.FileSystemLoader(input_dir)

    # pass the format_mac() method to jinja2 as a filter
    env.filters["format_mac"] = format_mac
    template = env.get_template(vagrant_template)

    return template.render(jinja_variables)


def write_file(location, contents):
    """Writes contents to a file
    Keyword Arguments
    location - the path of the file to write
    contents - the string contents to write to the file
    """
    try:
        with open(location, 'w') as output_file:
            output_file.write(contents)
    except:  #pylint: disable=W0702
        print_error("ERROR: Could not write file " + location)


# def generate_management_devices(inventory, cli_args):
#     """Generate a management network
#     """
#     mgmt_template_dir = "./templates/auto_mgmt_network/"
#     mgmt_output = "./helper_scripts/auto-mgmt_network/"

#     # Verify that the directory for the templates exists
#     if not os.path.isdir(mgmt_template_dir):
#         print(Styles.FAIL + Styles.BOLD +
#               "ERROR: " + mgmt_template_dir + " does not exist. " \
#               "Cannot populate templates!" +
#               Styles.ENDC)
#         exit(1)

#     # Verify the directory to write to exists
#     if not os.path.isdir(mgmt_output):
#         try:
#             os.mkdir(mgmt_output)
#         except:  #pylint: disable=W0702
#             print(Styles.FAIL + Styles.BOLD +
#                   "ERROR: Could not create output directory " +
#                   mgmt_output + "for mgmt template renders!" +
#                   Styles.ENDC)
#             exit(1)

#     # Get the contents to put in the Ansible hosts file
#     hostfile_contents = render_ansible_hostfile(inventory, cli_args, mgmt_template_dir)
#     ansible_hosts_location = os.path.join(mgmt_output, "ansible.hosts")

#     write_file(ansible_hosts_location, hostfile_contents)

def print_warning(warning_string):
    """Format and print warning messages
    """
    warning_format = "\033[93m"
    bold_format = "\033[1m"
    endc = '\033[0m'
    print warning_format + bold_format + "    WARNING: " + warning_string + endc


def print_error(error_string):
    """Format and print error messages.
    Also exit the program
    """
    error_format = "\033[91m"
    bold_format = "\033[1m"
    endc = '\033[0m'
    print error_format + bold_format + " ### ERROR -- " + error_string + endc
    exit(1)

def print_header(output_string):
    """Format and print header messages
    """
    header_format = "\033[95m"

    print header_format + output_string

def print_blue(output_string):
    """Print a string in blue
    """
    blue_format = "\033[94m"
    print blue_format + output_string

def main():
    """Main point of entry to parse a topology file,
    build an inventory and product a Vagrantfile
    """
    # W0603 - use of global statement
    global VERBOSE # pylint: disable=W0603
    vagrant_template = "templates/Vagrantfile.j2"
    cli = parse_arguments()
    cli_args = cli.parse_args()
    check_files(cli_args, vagrant_template)

    if cli_args.verbose:
        VERBOSE = True

    print_header("\n######################################")
    print_header("          Topology Converter")
    print_header("######################################")
    print_blue("           originally written by Eric Pulvino")

    parser = ParseGraphvizTopology()
    parsed_topology = parser.parse_topology(cli_args.topology_file)
    inventory = Inventory(parsed_topology)

    if cli_args.create_mgmt_network:
        inventory.build_mgmt_network()

    if cli_args.memory:
        print inventory.calculate_memory()
        exit(0)

    exit(0)

if __name__ == "__main__":
    main()

# Support very large OOB networks. Figure out how to split at 64 ports or so
# Allow the ability to add/modify links without requiring full
#       vagrant destroy/vagrant up. Export datastructure somehow
# Allow a server to be added to OOB while the full OOB is generated automatically.
# Allow selective DHCP default route
# Allow selective mgmt VRF in ZTP
# Change management network to /16
# oob-mgmt-switch bridge interface needs an IP and MAC.
#    Currently it will not be assigned in dhcpd.hosts
#    problem is that everying expects physical interfaces/edge.
#    May be possible with a FAKE device connected
