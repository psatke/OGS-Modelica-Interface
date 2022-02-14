# ============== Libraries ==============

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
import time

# ============== Functions ==============


def initServer():
    PORT = 5050
    HOST = '0.0.0.0'
    ADDR = (HOST, PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    activeConnList = []
    return server, ADDR, activeConnList


def initProtocol():
    # df_SimX = pd.DataFrame(columns=['Paket Code',
    #                                 't',
    #                                 'dt',
    #                                 'n',
    #                                 'kanal1(t)',
    #                                 'kanal1(t-dt)',
    #                                 'kanal2(t)',
    #                                 'kanal2(t-dt)'])
    lSimX = []
    # df_OGS = pd.DataFrame(columns=['Paket Code',
    #                                't',
    #                                'dt',
    #                                'n',
    #                                'kanal1(t)',
    #                                'kanal1(t-dt)',
    #                                'kanal2(t)',
    #                                'kanal2(t-dt)'])
    lOGS = []
    return lSimX, lOGS


def initParameter():
    barrier = threading.Barrier(2, timeout=120.0)
    lock = threading.Lock()
    stepsSimX = -1
    stepsOGS = -1
    t_stopp = 600     # End of simulationtime in s
    waitTotalSimX = 0
    waitTotalOGS = 0
    noBHE = 3
    typeBHE = "2U"
    # Temperature for each pipe + one constant volumeflow for all pipes
    if typeBHE == "1U":
        nop = noBHE+1
    elif typeBHE == "2U":
        nop = 2*noBHE+1

    return barrier, lock, stepsSimX, stepsOGS, t_stopp, waitTotalSimX, waitTotalOGS, nop


def handleClient(conn, addr):

    global stepsOGS, stepsSimX, lSimX, lOGS, waitTotalSimX, waitTotalOGS, nop

    header = conn.recv(20)
    headerUn = struct.unpack('!IdII', header)
    headerSend = struct.pack(
        '!IdII', headerUn[0], headerUn[1], headerUn[3], headerUn[2])
    conn.sendall(headerSend)

    connected = True

    while connected:
        # headerUn[0] = 17 is the identification for SimulationX
        if headerUn[0] == 17:
            dt = headerUn[1]

            # receive results
            datafromSimX = conn.recv(56)
            datafromSimXUn = list(struct.unpack('!IddI4d', datafromSimX))
            with lock:
                lSimX.append(datafromSimXUn)

            # synchronize
            waitStart = time.time()
            try:
                barrier.wait()
            except threading.BrokenBarrierError:
                print('[Server]\t handle_client(SimX): timeout Error')
            finally:
                stepsSimX += 1
            waitStop = time.time()
            waitTotalSimX = waitTotalSimX + (waitStop-waitStart)

            # send results
            with lock:
                package = [16]+lOGS[-1][1:3]+[nop-1]+lOGS[-1][4:-2]
            dataforSimX = struct.pack('!IddI'+(nop-1)*2*'d', *package)
            conn.sendall(dataforSimX)

            barrier.wait()

            if datafromSimXUn[1] > (t_stopp - dt):
                connected = False

        # headerUn[0] = 27 is the identification for OGS
        elif headerUn[0] == 27:

            # receive results
            datafromOGS = conn.recv(24+nop*8)
            datafromOGSUn = struct.unpack('!IddI'+nop*'d', datafromOGS)
            data = []
            if len(lOGS) == 0:
                for i in range(nop):
                    data.append(datafromOGSUn[i+4])
                    data.append(0.0)
            else:
                for i in range(nop):
                    data.append(datafromOGSUn[i+4])
                    data.append(lOGS[-1][i*2+4])
            with lock:
                lOGS.append(
                    [datafromOGSUn[0], datafromOGSUn[1], datafromOGSUn[2], datafromOGSUn[3]]+data)

            # synchronize
            waitStart = time.time()
            try:
                barrier.wait()
            except threading.BrokenBarrierError:
                print('[Server]\t handle_client(OGS): timeout Error')
            finally:
                stepsOGS += 1
            waitStop = time.time()
            waitTotalOGS = waitTotalOGS + (waitStop-waitStart)

            # send results
            with lock:
                package = [26]+lSimX[-1][1:]
            dataforOGS = struct.pack('!IddI4d', *package)
            conn.sendall(dataforOGS)

            connected = False
            barrier.wait()
            print('[Server]\t calculation steps (SimX/OGS): ' +
                  str(stepsSimX) + '/' + str(stepsOGS))
        else:
            print('[Server]\t handle_client(-): unidentified header')
    activeConnList.remove([conn, addr])
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()


def handleServer():
    server.listen()
    print(f"[SERVER]\t is listening on {ADDR}")
    i = 0
    while True:
        conn, addr = server.accept()
        activeConnList.extend([[conn, addr]])
        clientThread = threading.Thread(target=handleClient, args=(
            conn, addr), daemon=True)
        clientThread.setName('Thread [Client ' + str(i) + ']')
        clientThread.start()
        i += 1


def handleSimulationX(xl_id):
    pythoncom.CoInitialize()
    sim = win32com.client.Dispatch(
        pythoncom.CoGetInterfaceAndReleaseStream(xl_id, pythoncom.IID_IDispatch))

    simUninitialized = 0
    simInitBase = 1
    simStopped = 16

    # Wait till SimulationX is initialized
    if sim.InitState == simUninitialized:
        while sim.InitState != simInitBase:
            time.sleep(0.1)

    # Load libraries
    if sim.InitState == simInitBase:
        sim.InitSimEnvironment()
    sim.Visible = True
    sim.Interactive = True
    print("[SIMULATIONX]\t initialized")

    modelPath = os.sep.join(
        [dir, "Modelica-Model", "{}.isx".format(simX_model)])
    doc = sim.Documents.Open(modelPath)
    doc.Reset()
    doc.Start()
    print("[SIMULATIONX]\t running ...")
    while doc.SolutionState != simStopped:
        time.sleep(0.1)
    if doc.SolutionState != 32:
        doc.Save()
        print("[SIMULATIONX]\t calc completed")


def handleOGS():
    # start OGS
    callOGS = r'{}\OGS-Model\ogs.exe -o {}\OGS-Model\results {}\OGS-Model\{}.prj > {}\OGS-Model\results\result.tec'.format(
        dir, dir, dir, OGS_project, dir)
    # subprocess.run(callOGS, shell=True)  # run OGS with Output in terminal
    print('[OGS]\t\t running ...')
    with open(r'{}\OGS-Model\results\out.txt'.format(dir), 'w+') as fout:
        with open(r'{}\OGS-Model\results\err.txt'.format(dir), 'w+') as ferr:
            out = subprocess.call(
                callOGS, cwd=dir, stdout=fout, stderr=ferr, shell=True)
            fout.seek(0)
            output = fout.read()
            ferr.seek(0)
            errors = ferr.read()
    print('[OGS]\t\t calc completed')


# ============== Main ==============
start = time.time()

dir = os.path.dirname(os.path.realpath(__file__))   # Directory of the .py file
simX_model = 'CoSim_Test'
# OGS_project = 'beier_sandbox'
OGS_project = '3BHE_testcase'

server, ADDR, activeConnList = initServer()
lSimX, lOGS = initProtocol()
barrier, lock, stepsSimX, stepsOGS, t_stopp, waitTotalSimX, waitTotalOGS, nop = initParameter()

print("[SERVER]\t is starting ...")
serverThread = threading.Thread(target=handleServer, daemon=True)
serverThread.setName('Thread [SERVER]')
serverThread.start()

try:
    sim = win32com.client.GetActiveObject()
except:
    sim = win32com.client.Dispatch('ESI.SimulationX43')
xl_id = pythoncom.CoMarshalInterThreadInterfaceInStream(
    pythoncom.IID_IDispatch, sim)
simXThread = threading.Thread(
    target=handleSimulationX, kwargs={'xl_id': xl_id})
simXThread.setName('Thread [SimX]')
simXThread.start()

handleOGS()

simXThread.join()

# save communication protocoll
savePathSimX = os.sep.join(
    [dir, "[Server] Com SimX.txt"])
savePathOGS = os.sep.join(
    [dir, "[Server] Com OGS.txt"])

df_SimX = pd.DataFrame(lSimX, columns=[
                       'Paket Code', 't', 'dt', 'n', 'kanal1(t)', 'kanal1(t-dt)', 'kanal2(t)', 'kanal2(t-dt)'])

colOGS = ['Paket Code', 't', 'dt', 'n']
for i in range(len(lOGS)-4):
    colOGS.append('kanal'+str(i+1)+'(t)')
    colOGS.append('kanal'+str(i+1)+'(t-dt)')

df_OGS = pd.DataFrame(lOGS, columns=colOGS)

df_SimX.to_csv(savePathSimX, index=False)
df_OGS.to_csv(savePathOGS, index=False)

end = time.time()

print('[Server]\t OGS had to wait in total for:\t' + str(waitTotalOGS) + 's')
print('[Server]\t SimX had to wait in total for:\t' + str(waitTotalSimX) + 's')
print('[Server]\t Total runtime:\t\t\t' + str(end-start) + 's')
