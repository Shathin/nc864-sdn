#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.node import Controller, OVSSwitch, RemoteController
from mininet.link import TCLink

import random

from getArguments import getArguments

# ! This script generates a network by creating a custom topology class `CustomTopology`


class CustomTopology(Topo):
    """
    Creates a randomized topology
    """

    def createHosts(self, count: int) -> list[str]:
        """
        Creates `count` number of hosts in this topology

        The name assigned to each of them follows the pattern => Host {i}
        The IP assigned to each of them follows the pattern => 10.0.0.{i} / 24
        """
        return [
            self.addHost(
                f"h{iter}",
                ip=f"10.0.0.{iter}/24",
                mac=f"00:00:00:00:00:{'{:02d}'.format(iter)}",
            )
            for iter in range(1, count + 1)
        ]

    def createSwitches(
        self,
        count: int,
    ) -> list[str]:
        """
        Create `count` number of switches in this topology

        The name assigned to each of them follows the patter => Switch {i}
        """
        return [
            self.addSwitch(f"s{iter}", protocols="OpenFlow13")
            for iter in range(1, count + 1)
        ]

    def createLinks(
        self, bandwidthRange: tuple[int, int], linkDelayRange: tuple[int, int]
    ):
        """
        Randomly connects a host to a switch and then linearly connects all the switches

        Returns a dictionary that shows the host-switch mapping
        """

        hostSwitchMapping: dict = {}

        # Connect a host to a random switch
        for host in self.hostList:

            switch = random.choice(self.switchList)
            bw = random.randint(bandwidthRange[0], bandwidthRange[1])
            delay = f"{random.randint(linkDelayRange[0], linkDelayRange[1])}ms"

            if switch in hostSwitchMapping:
                hostSwitchMapping[switch].append((host, f"{bw} Mbps", delay))
            else:
                hostSwitchMapping[switch] = [(host, f"{bw} Mbps", delay)]

            self.addLink(
                host,
                switch,
                bw=bw,
                delay=delay,
            )

        # Connect switches in a linear fashion
        for switchIter in range(len(self.switchList) - 1):

            bw = random.randint(bandwidthRange[0], bandwidthRange[1])
            delay = f"{random.randint(linkDelayRange[0], linkDelayRange[1])}ms"

            switch1 = self.switchList[switchIter]
            switch2 = self.switchList[switchIter + 1]

            if switch1 in hostSwitchMapping:
                hostSwitchMapping[switch1].append((switch2, f"{bw} Mbps", delay))
            else:
                hostSwitchMapping[switch1] = [(switch2, f"{bw} Mbps", delay)]

            self.addLink(
                switch1,
                switch2,
                bw=bw,
                delay=delay,
            )

        return hostSwitchMapping

    def __init__(
        self,
        hostCount: int = 12,
        switchCount: int = 4,
        bandwidthRange: tuple[int, int] = (1, 100),
        linkDelayRange: tuple[int, int] = (1, 10),
    ):
        """
        Creates a randomized topology with `hostCount` number of hosts and `switchCount` number of switches
        and randomly assigns a host to a switch

        The bandwidth and link delay for each link is randomly assigned within the `bandwidthRange` and `linkDelayRange`.
        """
        # Initialize topology
        Topo.__init__(self)

        # Create hosts
        self.hostList: list[str] = self.createHosts(hostCount)

        # Create switches
        self.switchList: list[str] = self.createSwitches(switchCount)

        # Create links => Connect hosts to switches
        self.hostSwitchMapping = self.createLinks(bandwidthRange, linkDelayRange)


arguments: dict = getArguments()

# Create the topology
customTopology = CustomTopology(
    hostCount=arguments["hosts"],
    switchCount=arguments["switches"],
    bandwidthRange=arguments["bw"],
    linkDelayRange=arguments["delay"],
)

# Create the network
net = Mininet(
    topo=customTopology,  # Use the custom topology
    controller=lambda name: RemoteController(
        name,
        ip=arguments["controller"],
    ),  # Use the remote controller [ODL]
    switch=OVSSwitch,  # Use Open V Switch
    link=TCLink,
)

print("Node mapping :")
for key in customTopology.hostSwitchMapping:
    print("\t", key)
    for value in customTopology.hostSwitchMapping[key]:
        print("\t\t", "<-", value)

# Start the simulation
net.start()

# Transfer control to the terminal after the network is set up
CLI(net)

# Stop the simulation
net.stop()
