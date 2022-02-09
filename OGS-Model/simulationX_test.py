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
        # BHE 1U: len(Tin) = len(Tout) = len(Tout_node_id) = len(flowrate) = numberOfBHE
        # BHE 1U: Tin[0] = Input Temperature of first BHE
        # BHE 1U: Tin[1] = Input Temperature of second BHE
        # BHE 2U: len(Tin) = len(Tout) = len(Tout_node_id) = len(flowrate) = numberOfBHE*2
        # BHE 2U: Tin[0] = Input Temperature of first pipe of first BHE
        # BHE 2U: Tin[1] = Input Temperature of second pipe of first BHE
        return (0, [295.15]*6, [295.15]*6, [0]*6, [2.0E-04]*6)

    def serverCommunication(self, t, dt, Tin_val, Tout_val, flowrate):
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

        # TODO: return multiple values in flowrate and Tin_val
        # ! flowrate = [a, b, c] results in solver failure
        flowrate = [dataSimXUn[4]]*6
        Tin_val = [dataSimXUn[6]-10, dataSimXUn[6]-5, dataSimXUn[6],
                   dataSimXUn[6]+5, dataSimXUn[6]+10, dataSimXUn[6]+15]

        return (Tin_val, flowrate)


# main
bc_bhe = BC()
