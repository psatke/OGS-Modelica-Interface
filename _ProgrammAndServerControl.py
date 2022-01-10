# ======= Libraries =======
import socket
import threading
import struct
import pandas as pd
import numpy as np
import os
import time
import win32com.client
import pythoncom
import subprocess

# ======= Parameters =======
dir = os.path.dirname(os.path.realpath(__file__))   # Directory of the .py file
PORT = 5050
HOST = '0.0.0.0'
ADDR = (HOST, PORT)
t_stopp = 600     # End of simulationtime in s
simX_model = 'CoSim_Test'
OGS_project = 'beier_sandbox'


# ======= Initialization ======
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
activeConnList = []

df_SimX = pd.DataFrame(columns=['Paket Code', 't', 'dt', 'n',
                                'kanal1(t)', 'kanal1(t-dt)', 'kanal2(t)', 'kanal2(t-dt)'])
df_OGS = pd.DataFrame(columns=['Paket Code', 't', 'dt', 'n',
                               'kanal1(t)', 'kanal1(t-dt)', 'kanal2(t)', 'kanal2(t-dt)'])
# OGS will conntect after the first calculationstep. The initialization is added manually.
df_OGS = df_OGS.append({'Paket Code': 26, 't': 0.0, 'dt': 60.0, 'n': 2, 'kanal1(t)': 0.0002,
                        'kanal1(t-dt)': 0.0002, 'kanal2(t)': 295.36, 'kanal2(t-dt)': 295.36}, ignore_index=True)

stepsSimX = 0
stepsOGS = 1

# ======= Functions =======


def handle_client(conn, addr):

    global stepsOGS
    global stepsSimX
    global df_SimX
    global df_OGS

    print(f"[SEVER] {addr} connected.")
    header = conn.recv(20)
    headerUn = struct.unpack('!IdII', header)
    dt = headerUn[1]
    conn.sendall(header)

    connected = True
    while connected:
        # headerUn[0] = 17 is the identification for SimulationX
        if headerUn[0] == 17:
            # receive results
            dataSimX = conn.recv(56)
            dataSimXUn = struct.unpack('!IddI4d', dataSimX)
            df_SimX = df_SimX.append({'Paket Code': dataSimXUn[0], 't': dataSimXUn[1], 'dt': dataSimXUn[2], 'n': dataSimXUn[3], 'kanal1(t)': dataSimXUn[4],
                                      'kanal1(t-dt)': dataSimXUn[5], 'kanal2(t)': dataSimXUn[6], 'kanal2(t-dt)': dataSimXUn[7]}, ignore_index=True)
            stepsSimX += 1
            # wait for counterpart
            while stepsOGS != stepsSimX:
                time.sleep(0.1)
            # send results
            dataOGS = struct.pack('!IddI4d', 16, df_OGS['t'].tail(1), df_OGS['dt'].tail(1), 2, df_OGS['kanal1(t)'].tail(
                1), df_OGS['kanal1(t-dt)'].tail(1), df_OGS['kanal2(t)'].tail(1), df_OGS['kanal2(t-dt)'].tail(1))
            conn.sendall(dataOGS)
            if dataSimXUn[1] > (t_stopp - dt):
                connected = False

        # headerUn[0] = 27 is the identification for OGS
        elif headerUn[0] == 27:
            # receive results
            dataOGS = conn.recv(40)
            dataOGSUn = struct.unpack('!IddIdd', dataOGS)
            df_OGS = df_OGS.append({'Paket Code': dataOGSUn[0], 't': dataOGSUn[1], 'dt': dataOGSUn[2], 'n': dataOGSUn[3], 'kanal1(t)': dataOGSUn[4],
                                    'kanal1(t-dt)': df_OGS.iat[-1, 4], 'kanal2(t)': dataOGSUn[5], 'kanal2(t-dt)': df_OGS.iat[-1, 6]}, ignore_index=True)
            stepsOGS += 1
            # wait for counterpart
            while stepsOGS != stepsSimX:
                time.sleep(0.1)
            # send results
            dataSimX = struct.pack('!IddI4d', 26, df_SimX['t'].tail(1), df_SimX['dt'].tail(1), 2, df_SimX['kanal1(t)'].tail(
                1), df_SimX['kanal1(t-dt)'].tail(1), df_SimX['kanal2(t)'].tail(1), df_SimX['kanal2(t-dt)'].tail(1))
            conn.sendall(dataSimX)
            connected = False
    print(f"[SERVER] {addr} disconnected.")
    activeConnList.remove([conn, addr])
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()


def startServer():
    server.listen()
    print(f"[SERVER] is listening on {ADDR}")
    while True:
        conn, addr = server.accept()
        activeConnList.extend([[conn, addr]])
        clientThread = threading.Thread(target=handle_client, args=(
            conn, addr), daemon=True)
        clientThread.start()
        # print(f"[SERVER] active connections: {threading.activeCount() - 3}")


def startSimulationX(xl_id):
    pythoncom.CoInitialize()
    sim = win32com.client.Dispatch(
        pythoncom.CoGetInterfaceAndReleaseStream(xl_id, pythoncom.IID_IDispatch))
    # Wait till SimulationX is initialized
    if sim.InitState == simUninitialized:
        while sim.InitState != simInitBase:
            time.sleep(0.1)
    # Load libraries
    if sim.InitState == simInitBase:
        sim.InitSimEnvironment()
    sim.Visible = True
    sim.Interactive = True
    print("[SIMULATIONX] initialized")
    modelPath = os.sep.join(
        [dir, "Modelica-Model", "{}.isx".format(simX_model)])
    doc = sim.Documents.Open(modelPath)
    doc.Reset()
    doc.Start()
    print("[SIMULATIONX] running ...")
    while doc.SolutionState != simStopped:
        time.sleep(0.1)
    print("[SIMULATIONX] calc completed")


# ===== Main =====
print("[STARTING] server is starting ...")
serverThread = threading.Thread(target=startServer, daemon=True)
serverThread.start()

# initialization SimulationX
simUninitialized = 0
simInitBase = 1
simStopped = 16
SimulationX_COM_AppId = 'ESI.SimulationX42'
try:
    sim = win32com.client.GetActiveObject()
except:
    sim = win32com.client.Dispatch(SimulationX_COM_AppId)
xl_id = pythoncom.CoMarshalInterThreadInterfaceInStream(
    pythoncom.IID_IDispatch, sim)
simXThread = threading.Thread(target=startSimulationX, kwargs={'xl_id': xl_id})
simXThread.start()

# start OGS
callOGS = dir + r'\OGS-Model' + r'\ogs.exe ' + \
    dir + r'\OGS-Model' + r'\{}.prj'.format(OGS_project)
# subprocess.call(callOGS, cwd=dir) # run OGS with Output
print('[OGS] running ...')
with open('out.txt', 'w+') as fout:
    with open('err.txt', 'w+') as ferr:
        out = subprocess.call(callOGS, cwd=dir, stdout=fout, stderr=ferr)
        fout.seek(0)
        output = fout.read()
        ferr.seek(0)
        errors = ferr.read()

print('[OGS] calc completed')

savePathSimX = os.sep.join(
    [dir, "[Server] Com SimX.txt"])
savePathOGS = os.sep.join(
    [dir, "[Server] Com OGS.txt"])
df_SimX.to_csv(savePathSimX, index=False)
df_OGS.to_csv(savePathOGS, index=False)
