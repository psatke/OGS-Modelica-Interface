###
# Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
# Distributed under a Modified BSD License.
# See accompanying file LICENSE.txt or
# http://www.opengeosys.org/project/license
###

import socket
import struct
import OpenGeoSys

PORT = 5050
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
# Temperature for each pipe + one constant volumeflow for all pipes
noBHE = 3
typeBHE = "2U"
if typeBHE == "1U":
    nop = noBHE
elif typeBHE == "2U":
    nop = 2*noBHE+1


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
        return (0, [284.15]*(nop-1), [284.15]*(nop-1), [0]*(nop-1), [0.0]*(nop-1))
    def serverCommunicationPreTimestep(self, t, dt, Tin_val, Tout_val, flowrate):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        headerSend = struct.pack('!IdII', 27, 60.0, nop, 2)
        client.sendall(headerSend)
        client.recv(20)

        dataOGS = struct.pack('!IddI'+nop*'d',
                              26,
                              t,
                              dt,
                              nop,
                              *Tout_val,
                              sum(flowrate))
        client.sendall(dataOGS)
        dataSimX = client.recv(56)
        dataSimXUn = struct.unpack('!IddI4d', dataSimX)
        client.close()

        flowrate = [dataSimXUn[6]/(nop-1)]*(nop-1)
        Tin_val = [dataSimXUn[4]]*(nop-1)

        return (Tin_val, flowrate)

    # ! Attention: serverCommunication_post is not called at initialization
    def serverCommunicationPostTimestep(self, t, dt, Tin_val, Tout_val, flowrate):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        headerSend = struct.pack('!IdII', 37, 60.0, nop, 2)
        client.sendall(headerSend)
        client.recv(20)

        dataOGS = struct.pack('!IddI'+nop*'d',
                              36,
                              t,
                              dt,
                              nop,
                              *Tout_val,
                              sum(flowrate))
        client.sendall(dataOGS)
        client.close()

        return

# main
bc_bhe = BC()
