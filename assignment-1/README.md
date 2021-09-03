# Assignment 1 - Creating Topology and Flow Rules

## Problem Statement

_[View problem statement](./NC864_Assignment_1.pdf)_

## Reports
  
Read the report _[here](./Report.pdf)_ or  on _[Notion](https://shathin.notion.site/NC864-SDN-Assignment-1-6e8098d3c06c41e9931d70c76279c7fd)._

---

## The Script
`script.py` creates a network with a randomized topology using the Python Mininet API. 

The hosts are randomly connected to a switch and the switches are connected sequentially i.e., $S_1 \rightarrow S_2 \rightarrow ... \rightarrow S_n$. 

Each host $h_i$ is assigned the IP address $10.0.0.i/24$ and a MAC address of $00:00:00:00:00:i$. 

OpenDayLight is used as the remote controller for the generated network.

```bash
sudo python3 script.py [options]  
```

**Options**

- `--controller` → Defines the OpenDayLight controller's IP address. This is a mandatory option.

    Usage example: `--controller=192.168.122.61`

- `--hosts` → Defines the number of hosts to be created in the network. This option is optional, skipping this defaults the value of the number of hosts to $12$.

    Usage example: `--hosts=12`

- `--switches` → Defines the number of switches to be created in the network. This option is optional, skipping this defaults the value of the number of switches to $4$.

    Usage example: `--switches=4`

- `--bw` → Defines the bandwidth range to be used. Bandwidth is in $Mbps$. This option is optional, skipping this defaults the value to the range $0 \rightarrow 5 \ Mbps$.

    Usage example: `--bw=0,5`

- `--delay` → Defines the link delay range to be used. Delay is in $ms$. This option is optional, skipping this defaults the value to the range $2 \rightarrow 30 \ ms$.

    Usage example: `--delay=2,30`

Be sure to clean up before executing the script for another time. Run `sudo mn -c` command to perform the cleanup.

--- 

## Mininet Commands

- `net` → List network connections.

- `pingall` → Ping between all hosts.

- `<host-a> ping <host-b>`  → Host $A$ pings Host $B$.

- `dump` → Dump node info. Contains node type and name, node's IP for each interface and PID.

- `nodes` → List all nodes.

- `links` → Report on links.

- `<host> ifconfig` → Get network details of `host`.

- `<switch> ifconfig` → Get network details of `switch`.

- `py host.IP()` → Display `host`'s IP address.

- `py host.MAC()` → Dispay `host`'s MAC address

---

## OpenDaylight

The topology of the network can be viewed on the DLUX UI which is accessible at - `http://<controllerIP>:8181/index.html#/topology`
Note: DLUX is only available in pre-Flourine versions of OpenDaylight

---

# OpenVSwitch

If the following commands are executed inside the Mininet prompt then prepend the below commands with `sh`. Also, add the `--protocols=OpenFlow13` options to all the command since we use OpenFlow13 protocol in the program.

- `ovs-ofctl dump-flows sw` → List out all the flow rules for the switch `sw`.
- `ovs-ofctl del-flows sw` → Delete all the flows rules of the switch `sw`
- `ovs-ofctl add-flow sw priority=p,ip,nw_src=src,nw_dst=dst,actions=act` →Add a flow rule to switch `sw` based on the source IP `src` and destination IP `dst` addresses. To drop the packet specify the action as `drop`.  
    The following adds a flow rule to Switch `s4` to drop the packets sent from Host `h4` [$10.0.0.4$] to Host `h2` [$10.0.0.2$].

    ```bash
    sh ovs-ofctl --protocols=OpenFlow13 add-flow s4 priority=6969,ip,nw_src=10.0.0.4,nw_dst=10.0.0.2,actions=drop 
    ```

- `ovs-ofctl add-flow sw priority=p,dl_src=smac,dl_dst=dmac,actions=act` → Add a flow rule to switch `sw` based on the source MAC `smac` and destination MAC `dmac` addresses. To drop the packet specify the action as `drop`.  
    Adding flow rule to Switch `s3` to **drop** the packets sent from Host `h1` [$00:00:00:00:00:01$] to Host `h11` [$00:00:00:00:00:11$].

    ```bash
    sh ovs-ofctl --protocols=OpenFlow13 add-flow s3 priority=6969,dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:11,actions=drop 
    ```
    ---