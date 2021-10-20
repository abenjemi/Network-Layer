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


    def handlePacket(self, port, packet):
        """process incoming packet"""
        # default implementation sends packet back out the port it arrived
        # you should replace it with your implementation
        self.send(port, packet)


    def handleNewLink(self, port, endpoint, cost):
        """a new link has been added to switch port and initialized, or an existing
        link cost has been updated. Implement any routing/forwarding action that
        you might want to take under such a scenario"""
        pass


    def handleRemoveLink(self, port, endpoint):
        """an existing link has been removed from the switch port. Implement any 
        routing/forwarding action that you might want to take under such a scenario"""
        pass


    def handlePeriodicOps(self):
        """handle periodic operations. This method is called every heartbeatTime.
        You can change the value of heartbeatTime in the json file"""
        pass
