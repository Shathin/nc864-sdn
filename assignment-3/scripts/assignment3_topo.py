#! /usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import (
    Node,
    Host,
    OVSSwitch,
    RemoteController,
    DefaultController,
)
from mininet.log import setLogLevel, info
from mininet.cli import CLI, Cmd


class CustomTopology(Topo):
    """Creates the target network"""

    def __init__(self):
        """Constructor"""
        Topo.__init__(self)

        # * Create hosts
        h12 = self.addHost("h12", ip="10.0.1.2/24")
        h13 = self.addHost("h13", ip="10.0.1.3/24")
        h22 = self.addHost("h22", ip="10.0.2.2/24")
        h32 = self.addHost("h32", ip="10.0.3.2/24")
        h42 = self.addHost("h42", ip="10.0.4.2/24")
        h43 = self.addHost("h43", ip="10.0.4.3/24")

        # * Create switches
        s1 = self.addSwitch("s1")
        s4 = self.addSwitch("s4")

        # * Create routers (switches)
        r1 = self.addSwitch("r1")
        r2 = self.addSwitch("r2")
        r3 = self.addSwitch("r3")
        r4 = self.addSwitch("r4")

        # * Connect network under r1
        self.addLink(h12, s1)
        self.addLink(h13, s1)

        self.addLink(s1, r1, intfName2="r1-eth0")
        # * Connect network under r2
        self.addLink(h22, r2, intfName2="r2-eth0")

        # * Connect network under r3
        self.addLink(h32, r3, intfName2="r3-eth0")

        # * Connect network under r4
        self.addLink(h42, s4)
        self.addLink(h43, s4)
        self.addLink(s4, r4, intfName2="r4-eth0")

        # * Connect routers  (switches)
        self.addLink(
            r1,
            r3,
            intfName1="r1-eth1",
            intfName2="r3-eth1",
        )
        self.addLink(
            r1,
            r2,
            intfName1="r1-eth2",
            intfName2="r2-eth2",
        )
        self.addLink(
            r2,
            r4,
            intfName1="r2-eth1",
            intfName2="r4-eth1",
        )


setLogLevel("info")


# * Create the topology
topology = CustomTopology()

# * Create the network
net = Mininet(
    topo=topology,
    controller=DefaultController,
    switch=OVSSwitch,
    autoSetMacs=True,
    autoStaticArp=True,
    waitConnected=True,
)

# * Start the simulation
net.start()

# * Add the default route of 0.0.0.0 to each host
for host in net.hosts:
    intf = host.defaultIntf()
    host.setDefaultRoute(intf)

# * Transfer control to terminal
cli = CLI(net)

# * Stop the simulation
net.stop()
