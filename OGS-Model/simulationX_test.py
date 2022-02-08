###
# Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
# Distributed under a Modified BSD License.
# See accompanying file LICENSE.txt or
# http://www.opengeosys.org/project/license
###

import sys
import socket
import struct
import OpenGeoSys

PORT = 5050
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)


class BC(OpenGeoSys.BHENetwork):
    def initializeDataContainer(self):
        # initialize network and get data from the network
        # (initial time, Tin, Tout, Tout_node_id, flowrate)
        return (0, [295.15], [295.15], [0], [2.0E-04])

    def serverCommunication(self, t, dt, Tin_val, Tout_val, flowrate):
        # TODO: Code for SimualtionX simulation
        # with t; only take the last results for each time point
        # TODO: say SimulationX the next time point from OGS

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        headerSend = struct.pack('!IdII', 27, 60.0, 2, 2)
        client.sendall(headerSend)
        client.recv(20)

        dataOGS = struct.pack('!IddIdd', 26, t, dt, 2,
                              flowrate[0], Tout_val[0])
        client.sendall(dataOGS)
        dataSimX = client.recv(56)
        dataSimXUn = struct.unpack('!IddI4d', dataSimX)
        client.close()

        flowrate = [dataSimXUn[4]*3]
        Tin_val = [dataSimXUn[6]*3]

        return (Tin_val, flowrate)


# main
bc_bhe = BC()
