# The code is subject to Purdue University copyright policies.
# DO NOT SHARE, DISTRIBUTE, OR POST ONLINE
#

import sys
from collections import defaultdict
from router import Router
from packet import Packet
from json import dumps, loads


class DVrouter(Router):
    """Distance vector routing and forwarding implementation"""

    def __init__(self, addr, heartbeatTime, infinity):
        Router.__init__(self, addr, heartbeatTime)  # initialize superclass - don't remove
        self.infinity = infinity
        """add your own class fields and initialization code here"""

        # initialize routing table
        self.table = {}
        self.table[self.addr] = [0,self.addr,0]

        # initialize control packet (routing table)
        content = dumps(self.table)
        self.control = Packet(2, self.addr, 'a', content=content)


    def handlePacket(self, port, packet):
        """process incoming packet"""
        # default implementation sends packet back out the port it arrived
        # you should replace it with your implementation
        
        # if packet received is a data packet - IP forwarding
        if packet.isData():
            if packet.dstAddr in self.table.keys():
                out_port = self.table[packet.dstAddr][2]
                self.send(out_port, packet)
            else:
                return

        # if control packet (routing table of neighbor) update according to case and send routing table to neighbors
        elif packet.isControl():
            table = loads(packet.content)
            cost_to_neighbor = self.links[port].get_cost()
            change = 0
            for d in table.keys():
                if table[d][1] != self.addr:
                    cost_neighbor_d = table[d][0]
                    if d not in self.table.keys():
                        self.table[d] = [cost_neighbor_d + cost_to_neighbor,packet.srcAddr,port]
                        change += 1

                    else:
                        # case 1
                        if self.table[d][2] == port:
                            self.table[d] = [cost_neighbor_d + cost_to_neighbor,packet.srcAddr,port]
                            change += 1

                        # case 2
                        elif self.table[d][1] != packet.srcAddr:
                            if self.table[d][0] > cost_neighbor_d + cost_to_neighbor:
                                self.table[d] = [cost_neighbor_d + cost_to_neighbor,packet.srcAddr,port]
                                change += 1
                
                    # max infinity counter
                    if self.table[d][0] >= self.infinity:
                        self.table[d] = [self.infinity,'',0]

            # if table updated - send it to neighbors
            if change > 0:
                self.control.content = dumps(self.table)
                self.sendtoNeighbors(self.control)
            




    def handleNewLink(self, port, endpoint, cost):
        """a new link has been added to switch port and initialized, or an existing
        link cost has been updated. Implement any routing/forwarding action that
        you might want to take under such a scenario"""

        # add neighbor to the routing table
        self.table[endpoint] = [cost, endpoint, port]
        self.control.content = dumps(self.table)
        self.sendtoNeighbors(self.control)



    def handleRemoveLink(self, port, endpoint):
        """an existing link has been removed from the switch port. Implement any 
        routing/forwarding action that you might want to take under such a scenario"""

        # if link removed update all entries of type (d,cost(X,d),endpoint) in table to (d,infinity,null)
        for d in self.table.keys():
            if self.table[d][1] == endpoint:
                self.table[d] = [self.infinity,'',0]
            


    def handlePeriodicOps(self):
        """handle periodic operations. This method is called every heartbeatTime.
        You can change the value of heartbeatTime in the json file"""
        self.control.content = dumps(self.table)
        self.sendtoNeighbors(self.control)

    def sendtoNeighbors(self, packet):#, port=None):
        for p in self.links.keys():
            #if p != port:
            e2 = self.links[p].get_e2(self.addr)
            packet.dstAddr = e2
            self.send(p, packet)