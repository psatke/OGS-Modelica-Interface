###
# Copyright (c) 2012-2021, OpenGeoSys Community (http://www.opengeosys.org)
# Distributed under a Modified BSD License.
# See accompanying file LICENSE.txt or
# http://www.opengeosys.org/project/license
###

import sys
import socket
import struct
from pandas import read_csv
import OpenGeoSys

PORT = 5050
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)

# df_server = read_csv("initial.csv", delimiter=";", index_col=[
#                      0], dtype={"data_index": str})


def get_Tin(t):
    df_readfile = read_csv("readfile.txt", delimiter=";")
    time_list = df_readfile["time"].tolist()  # prepare the time adjustment
    # !!!makes simulation much slower!!! - time adjustment to nearest value in list in case time value isn't in the list (happens in Beier test)
    t = min(time_list, key=lambda x: abs(x-t))
    return [float(df_readfile.Tin[df_readfile.time == t])]


# OGS setting
# Dirichlet BCs
class BC(OpenGeoSys.BHENetwork):
    def initializeDataContainer(self):
        # initialize network and get data from the network
        # convert dataframe to column list
        t = 0  # 'initial time'
        # 'Tin_val'; option: give array directly
        # data_col_1 = df_server["Tin_val"].tolist()
        # data_col_2 = df_server["Tout_val"].tolist()  # 'Tout_val'
        # data_col_3 = df_server["Tout_node_id"].astype(
        #     int).tolist()  # 'Tout_node_id'
        # data_col_4 = df_server["flowrate"].tolist()  # 'BHE flow rate'
        # return (t, data_col_1, data_col_2, data_col_3, data_col_4)
        return (t, [295.36], [295.13], [0], [2.0E-04])

    def serverCommunication(self, t, dt, Tin_val, Tout_val, flowrate):
        # TODO: Code for SimualtionX simulation
        # with t; only take the last results for each time point
        # TODO: say SimulationX the next time point from OGS

        # dt_file = open("_dt.txt", "a")
        # dt_file.write("tada tada" + "\n")
        # dt_file.close()

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

        flowrate = [dataSimXUn[4]]
        Tin_val = [dataSimXUn[6]]

        # Tin_val = get_Tin(t)
        # tin_file = open("_T_in.txt", "a")
        # tin_file.write(str(t) + str(Tin_val) + "\n")
        # tin_file.close()

        # tout_file = open("_T_out.txt", "a")
        # tout_file.write(str(t) + str(Tout_val) + "\n")
        # tout_file.close()

        # flowrate_file = open("_flowrate.txt", "a")
        # flowrate_file.write(str(t) + str(flowrate) + "\n")
        # flowrate_file.close()

        # dt_file = open("_dt.txt", "a")
        # dt_file.write(str(t) + ';' + str(dt) + "\n")
        # dt_file.close()

        return (Tin_val, flowrate)


# main
bc_bhe = BC()
