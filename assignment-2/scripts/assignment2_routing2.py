#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, OVSSwitch, DefaultController
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd("sysctl net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl net.ipv4.ip_forward=0")
        super(LinuxRouter, self).terminate()


class RouterTopology(Topo):
    def build(self, **_opts):
        info("\n*** Creating topology\n")
        # * Add 4 routers
        info("*** *** Adding routers\n")
        r1 = self.addNode("r1", cls=LinuxRouter, ip="10.0.1.1/24")
        r2 = self.addNode("r2", cls=LinuxRouter, ip="10.0.2.1/24")
        r3 = self.addNode("r3", cls=LinuxRouter, ip="10.0.3.1/24")
        r4 = self.addNode("r4", cls=LinuxRouter, ip="10.0.4.1/24")

        # * Create network under r1
        info("*** *** Adding network under Router r1\n")
        s1 = self.addSwitch("s1")
        self.addLink(s1, r1, intfName2="r1-eth0", params2={"ip": "10.0.1.1/24"})
        h12 = self.addHost(name="h12", ip="10.0.1.2/24", defaultRoute="via 10.0.1.1")
        h13 = self.addHost(name="h13", ip="10.0.1.3/24", defaultRoute="via 10.0.1.1")
        self.addLink(s1, h12)
        self.addLink(s1, h13)

        # * Create network under r2
        info("*** *** Adding network under Router r2\n")
        h22 = self.addHost(name="h22", ip="10.0.2.2/24", defaultRoute="via 10.0.2.1")
        self.addLink(h22, r2, intfName2="r2-eth0", params2={"ip": "10.0.2.1/24"})

        # * Create network under r3
        info("*** *** Adding network under Router r3\n")
        h32 = self.addHost(name="h32", ip="10.0.3.2/24", defaultRoute="via 10.0.3.1")
        self.addLink(h32, r3, intfName2="r3-eth0", params2={"ip": "10.0.3.1/24"})

        # * Create network under r4
        info("*** *** Adding network under Router r4\n")
        s2 = self.addSwitch("s2")
        self.addLink(s2, r4, intfName2="r4-eth0", params2={"ip": "10.0.4.1/24"})
        h42 = self.addHost(name="h42", ip="10.0.4.2/24", defaultRoute="via 10.0.4.1")
        h43 = self.addHost(name="h43", ip="10.0.4.3/24", defaultRoute="via 10.0.4.1")
        self.addLink(s2, h42)
        self.addLink(s2, h43)

        # * Connect all routers
        info("*** *** Connecting routers\n")
        self.addLink(
            r1,
            r3,
            intfName1="r1-eth1",
            intfName2="r3-eth1",
            params1={"ip": "192.168.0.1/24"},
            params2={"ip": "192.168.0.3/24"},
        )
        self.addLink(
            r2,
            r4,
            intfName1="r2-eth1",
            intfName2="r4-eth1",
            params1={"ip": "192.168.2.2/24"},
            params2={"ip": "192.168.2.4/24"},
        )
        self.addLink(
            r1,
            r2,
            intfName1="r1-eth2",
            intfName2="r2-eth2",
            params1={"ip": "192.168.1.1/24"},
            params2={"ip": "192.168.1.2/24"},
        )

        info("*** Topology creation complete\n")


setLogLevel("info")

net: Mininet = Mininet(topo=RouterTopology())

# * Start mininet network
net.start()

pingTimeout: float = 0.25

info("\n*** Testing connectivity before setting up routing rules\n")
net.pingAll(timeout=pingTimeout)  # ? Timeout in seconds

# * Setup routing rules
info("\n*** Setup routing rules\n")
# ? ip route add dest_network via dest_network_outer_ip dev src_net_outer_intf
net["r1"].cmd("ip route add 10.0.2.0/24 via 192.168.1.2")  # * r1 -> r2
net["r1"].cmd("ip route add 10.0.3.0/24 via 192.168.0.3")  # * r1 -> r3
net["r1"].cmd("ip route add 10.0.4.0/24 via 192.168.1.2")  # * r1 -> r4

net["r2"].cmd("ip route add 10.0.1.0/24 via 192.168.1.1")  # * r2 -> r1
net["r2"].cmd("ip route add 10.0.3.0/24 via 192.168.1.1")  # * r2 -> r3
net["r2"].cmd("ip route add 10.0.4.0/24 via 192.168.2.4")  # * r2 -> r4

net["r3"].cmd("ip route add 10.0.1.0/24 via 192.168.0.1")  # * r3 -> r1
net["r3"].cmd("ip route add 10.0.2.0/24 via 192.168.0.1")  # * r3 -> r2
net["r3"].cmd("ip route add 10.0.4.0/24 via 192.168.0.1")  # * r3 -> r4

net["r4"].cmd("ip route add 10.0.1.0/24 via 192.168.2.2")  # * r4 -> r1
net["r4"].cmd("ip route add 10.0.2.0/24 via 192.168.2.2")  # * r4 -> r2
net["r4"].cmd("ip route add 10.0.3.0/24 via 192.168.2.2")  # * r4 -> r3


info("\n*** Testing connectivity after setting up routing rules\n")
net.pingAll(timeout=pingTimeout)

info("\n*** Adding new routing rule to make h22 not pingable from h12")
# * h12 <-x-> h22
net["r2"].cmd("iptables -A FORWARD -s 10.0.1.2 -d 10.0.2.2 -j REJECT") # * iptables method
# net["r2"].cmd("ip rule add prohibit from 10.0.1.2 to 10.0.2.2") # * ip rule method

info("\n*** Testing connectivity after updating routing rules ")
net.pingAll(timeout=pingTimeout)

# * Transfer control to command line interface
CLI(net)

# * Stop network
net.stop()
