# The code is subject to Purdue University copyright policies.
# DO NOT SHARE, DISTRIBUTE, OR POST ONLINE
#

import sys
from collections import defaultdict
from router import Router
from packet import Packet
from json import dumps, loads
from heapq import heappush, heappop, heapify


class PQEntry:

    def __init__(self, addr, cost, next_hop):
        self.addr = addr
        self.cost = cost
        self.next_hop = next_hop

    def __lt__(self, other):
         return (self.cost < other.cost)

    def __eq__(self, other):
         return (self.cost == other.cost)


class LSrouter(Router):
    """Link state routing and forwarding implementation"""

    def __init__(self, addr, heartbeatTime):
        Router.__init__(self, addr, heartbeatTime)  # initialize superclass - don't remove
        self.graph = {} # A dictionary with KEY = router
                        # VALUE = a list of lists of all its neighbor routers/clients and the cost to each neighbor
                        # {router: [[neighbor_router_or_client, cost]]}
        self.graph[self.addr] = []
        
        self.control = Packet(2, self.addr, 'a', content='[]')
        lst = loads(self.control.content)

        self.table = {}
        """add your own class fields and initialization code here"""


    def handlePacket(self, port, packet):
        """process incoming packet"""






        
        # if packet received is a data packet
        if packet.isData():
            if packet.dstAddr in self.table.keys():
                out_port = self.table[packet.dstAddr][2]
                self.send(out_port, packet)
            else:
                return


        # if packet received is control packet (LSA)
        elif packet.isControl():

            # each router adds its neighbors and cost to neighbors to graph

            LSA = []
            for link in self.links.values():
                #print(self.addr, '    ', link.e1, ' ', link.e2, ' ', link.cost)
                neighbor = [link.get_e2(self.addr), link.get_cost()]
                # print(self.addr, ' ' , neighbor)
                LSA.append(neighbor)

            self.graph[self.addr] = LSA

            # update control packet
            content = dumps(LSA)
            self.control.content = content


            #old_graph = self.graph
            LSA = loads(packet.content)
            self.graph[packet.srcAddr] = LSA
            self.sendtoNeighbors(port=port)
            # if old_graph != self.graph:
            finishedQ = self.dijkstra()
            for i in range(len(finishedQ)):
                out_port = self.getPort(finishedQ[i].next_hop)
                lst = [finishedQ[i].cost,finishedQ[i].next_hop,out_port]
                self.table[finishedQ[i].addr] = lst

    def handleNewLink(self, port, endpoint, cost):
        """a new link has been added to switch port and initialized, or an existing
        link cost has been updated. Implement any routing/forwarding action that
        you might want to take under such a scenario"""
        for neighbor in self.graph[self.addr]:
            if neighbor[0] == endpoint:
                self.graph[self.addr].remove(neighbor)
        self.graph[self.addr].append([endpoint,cost])


    def handleRemoveLink(self, port, endpoint):
        """an existing link has been removed from the switch port. Implement any 
        routing/forwarding action that you might want to take under such a scenario"""
        for neighbor in self.graph[self.addr]:
            if neighbor[0] == endpoint:
                self.graph[self.addr].remove(neighbor)


    def handlePeriodicOps(self):
        """handle periodic operations. This method is called every heartbeatTime.
        You can change the value of heartbeatTime in the json file"""

        # if self.control.content == '[]':
        
        # print("control packet of ", self.addr,"content = ", content)
        self.sendtoNeighbors()

    def sendtoNeighbors(self, port=None):
        for p in self.links.keys():
            if p != port:
                e2 = self.links[p].get_e2(self.addr)
                self.control.dstAddr = e2
                self.send(p, self.control)
                
    def getPort(self, e2):
        for p in self.links.keys():
            if self.links[p].get_e2(self.addr) == e2:
                return p


    def dijkstra(self):
        """An implementation of Dijkstra's shortest path algorithm.
        Operates on self.graph datastructure and returns the cost and next hop to
        each destination router in the graph as a List (finishedQ) of type PQEntry"""
        priorityQ = []
        finishedQ = [PQEntry(self.addr, 0, self.addr)]
        for neighbor in self.graph[self.addr]:
            heappush(priorityQ, PQEntry(neighbor[0], neighbor[1], neighbor[0]))

        while len(priorityQ) > 0:
            dst = heappop(priorityQ)
            finishedQ.append(dst)
            if not(dst.addr in self.graph.keys()):
                continue
            for neighbor in self.graph[dst.addr]:
                #neighbor already exists in finnishedQ
                found = False
                for e in finishedQ:
                    if e.addr == neighbor[0]:
                        found = True
                        break
                if found:
                    continue
                newCost = dst.cost + neighbor[1]
                #neighbor already exists in priorityQ
                found = False
                for e in priorityQ:
                    if e.addr == neighbor[0]:
                        found = True
                        if newCost < e.cost:
                            del e
                            heapify(priorityQ)
                            heappush(priorityQ, PQEntry(neighbor[0], newCost, dst.next_hop))
                        break
                if not found:
                    heappush(priorityQ, PQEntry(neighbor[0], newCost, dst.next_hop))

        return finishedQ

