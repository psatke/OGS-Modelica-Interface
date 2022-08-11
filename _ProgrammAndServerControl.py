'''This programm manages the Co-Simulation of OpenGeoSys (OGS) and Modelica.

The execution of this file will start Modelica in the simulation environment SimulationX and OGS.
While both programs are running they will connect as clients to the server, that is started in the main part of this program.
Multiple threads are responsible to manage Modelica, OGS and their communication. The communictaion is mainly determined by the
Modelica component used for communictation (in this case from the SimulationX library GenericInterfaces.CoSimulation.Coupling).
The communication with OGS on the other hand is defined in the file OGS-Model\PreAndPostTimestep.py'''

# ============== Libraries ==============

import socket
import threading
import struct
import pandas as pd
import os
import time
import win32com.client
import pythoncom
import subprocess
import time

# ============== Functions ==============


def handleClient(conn: str, addr: int) -> None:
    '''Handles the communication to the clients Modelica and OGS'''

    # header = [Package Code,
    #       Communication Step Size,
    #       Transmitted Channels,
    #       Received Channels]
    header = conn.recv(20)
    headerUn = struct.unpack('!IdII', header)
    headerSend = struct.pack(
        '!IdII', headerUn[0], headerUn[1], headerUn[3], headerUn[2])
    conn.sendall(headerSend)

    connected = True
    
    # special case initialization: 
    if trackingDict['currentStepOGS'] == -1 and headerUn[0] == 27:
        # receive OGS initialization
        datafromOGS = conn.recv(24+headerUn[2]*8)
        datafromOGSUn = struct.unpack('!IddI'+headerUn[2]*'d', datafromOGS)
        data = []
        if len(lOGS) == 0:
            for i in range(headerUn[2]):
                data.append(datafromOGSUn[i+4])
                data.append(0.0)
        else:
            for i in range(headerUn[2]):
                data.append(datafromOGSUn[i+4])
                data.append(lOGS[-1][i*2+4])
        with lock:
            lOGS.append(list(datafromOGSUn[0:4])+data)

        synchronizeWithCount('OGS')

        # send initialization back to OGS
        with lock:
            package = [26]+lSimX[-1][1:-2]
        dataforOGS = struct.pack('!IddI4d', *package)
        conn.sendall(dataforOGS)

        synchronize('OGS')
        

    # headerUn[0] = 17 is the identification for SimulationX
    elif headerUn[0] == 17:
        # SimulationX maintains the connection for the whole simulation
        # receive SimX initialization
        datafromSimX = conn.recv(24+headerUn[2]*2*8)
        datafromSimXUn = list(struct.unpack(
            '!IddI'+headerUn[2]*2*'d', datafromSimX))
        with lock:
            lSimX.append(datafromSimXUn)
        
        synchronizeWithCount('SimX')

        # send results initialization
        with lock:
            package = [16]+lOGS[-1][1:3] + \
                [(len(lOGS[0])-6)//2]+lOGS[-1][4:-2]
        dataforSimX = struct.pack('!IddI'+(len(lOGS[0])-6)*'d', *package)
        conn.sendall(dataforSimX)

        synchronize('SimX')

        print('[Server]\t initialization completed (SimX/OGS): ' +
              str(trackingDict['currentStepSimX']) + '/' + str(trackingDict['currentStepOGS']))

        while connected:
            # receive results
            datafromSimX = conn.recv(24+headerUn[2]*2*8)
            datafromSimXUn = list(struct.unpack(
                '!IddI'+headerUn[2]*2*'d', datafromSimX))

            with lock:
                lSimX.append(datafromSimXUn)

            waitStart = time.time()
            try:
                barrier.wait()
            except threading.BrokenBarrierError:
                print('[Server]\t handle_client(SimX): timeout Error')
                quickSave()
            finally:
                trackingDict['currentStepSimX'] += 1
            
            synchronize('SimX')

            waitStop = time.time()
            trackingDict['waitTotalSimX'] += (waitStop-waitStart)

            # send results
            with lock:
                package = [16]+lOGS[-1][1:3] + \
                    [(len(lOGS[0])-6)//2]+lOGS[-1][4:-2]
            dataforSimX = struct.pack('!IddI'+(len(lOGS[0])-6)*'d', *package)
            conn.sendall(dataforSimX)

            synchronize('SimX')

            if datafromSimXUn[1] == simTimeFinalStep:
                connected = False

    # headerUn[0] = 27 is the identification for OGS-Pre
    elif headerUn[0] == 27:
        # receive results
        datafromOGS = conn.recv(24+headerUn[2]*8)
        datafromOGSUn = struct.unpack('!IddI'+headerUn[2]*'d', datafromOGS)
        data = []
        if len(lOGS) == 0:
            for i in range(headerUn[2]):
                data.append(datafromOGSUn[i+4])
                data.append(0.0)
        else:
            for i in range(headerUn[2]):
                data.append(datafromOGSUn[i+4])
                data.append(lOGS[-1][i*2+4])
        with lock:
            lOGS.append(list(datafromOGSUn[0:4])+data)
        waitStart = time.time()
        
        synchronize('OGS')

        waitStop = time.time()
        with lock:
            trackingDict['waitTotalOGS'] += (waitStop-waitStart)
        # send results
        with lock:
            package = [26]+lSimX[-1][1:-2]
        dataforOGS = struct.pack('!IddI4d', *package)
        conn.sendall(dataforOGS)

    # headerUn[0] = 37 is the identification for OGS-Post
    elif headerUn[0] == 37:
        datafromOGS = conn.recv(24+headerUn[2]*8)
        datafromOGSUn = struct.unpack('!IddI'+headerUn[2]*'d', datafromOGS)
        data = []
        if len(lOGS) == 0:
            for i in range(headerUn[2]):
                data.append(datafromOGSUn[i+4])
                data.append(0.0)
        else:
            for i in range(headerUn[2]):
                data.append(datafromOGSUn[i+4])
                data.append(lOGS[-1][i*2+4])
        with lock:
            lOGS.append(list(datafromOGSUn[0:4])+data)

        synchronizeWithCount('OGS')

        synchronize('OGS')
        
        print('[Server]\t calculation steps (SimX/OGS): ' +
              str(trackingDict['currentStepSimX']) + '/' + str(trackingDict['currentStepOGS']))
    else:
        print('[Server]\t handle_client(-): unknown header')
    activeConnList.remove([conn, addr])
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()


def synchronizeWithCount(client: str) -> None:
    '''Synchronizes different threads for communication and increases the current Timestep'''
    waitStart = time.time()
    try:
        barrier.wait()
    except threading.BrokenBarrierError:
        print('[Server]\t handle_client({}): timeout Error'.format(client))
        quickSave()
    finally:
        with lock:
            trackingDict['currentStep{}'.format(client)] += 1
    waitStop = time.time()
    with lock:
        trackingDict['waitTotal{}'.format(client)] += (waitStop-waitStart)


def synchronize(client: str) -> None:
    '''Synchronizes different threads for communication'''
    try:
        barrier.wait()
    except threading.BrokenBarrierError:
        print('[Server]\t handle_client({}}): timeout Error'.format(client))
        quickSave()


def handleServer() -> None:
    '''Starts new threads for each client that trys to communicate'''
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


def handleSimulationX(xl_id) -> None:
    '''Starts SimulationX'''
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


def quickSave() -> None:
    '''Saves the communication protocoll up this timestep'''
    savePathSimX = os.sep.join(
        [dir, "[Server] Com SimX.txt"])
    savePathOGS = os.sep.join(
        [dir, "[Server] Com OGS.txt"])

    df_SimX = pd.DataFrame(lSimX, columns=[
                        'Paket Code', 
                        't', 
                        'dt', 
                        'n', 
                        'kanal1(t)', 
                        'kanal1(t-dt)', 
                        'kanal2(t)', 
                        'kanal2(t-dt)', 
                        'kanal3(t)', 
                        'kanal3(t-dt)'])

    colOGS = ['Paket Code', 't', 'dt', 'n']
    for i in range((len(lOGS[0])-4)//2):
        colOGS.append('kanal'+str(i+1)+'(t)')
        colOGS.append('kanal'+str(i+1)+'(t-dt)')

    df_OGS = pd.DataFrame(lOGS, columns=colOGS)

    df_SimX.to_csv(savePathSimX, index=False)
    df_OGS.to_csv(savePathOGS, index=False)

    file = open('[Server] runtime.txt', 'w+')
    file.write('OGS had to wait in total for:\t' + str(trackingDict["waitTotalOGS"]) + ' s\n' +'SimX had to wait in total for:\t' + str(trackingDict["waitTotalSimX"]) + ' s\n')
    file.close()


# ============== Main ==============

# ______________ Initializaiton ______________

start = time.time()

dir = os.path.dirname(os.path.realpath(__file__))   # Directory of the .py file
simX_model = 'Validierung'
OGS_project = '3BHE'

PORT = 5050
HOST = '0.0.0.0'
ADDR = (HOST, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
activeConnList = []

# init Data Storage as lists
# lSimX = [[Package Code,
#           SimulationTime t,
#           SimulationTimestep dt,
#           NumberOfChannels,
#           Channel1 at t,
#           Channel1 at t-dt,
#           ...
#           Channel3 at t,
#           Channel3 at t-dt],
#           [following Timesteps],
#           ...]
lSimX = []
# lOGS = [[Package Code,
#           SimulationTime t,
#           SimulationTimestep dt,
#           NumberOfChannels,
#           Channel1 at t,
#           Channel1 at t-dt,
#           ...
#           Channel(NumberOfParameters) at t,
#           Channel(NumberOfParameters) at t-dt],
#           [following Timesteps],
#           ...]
lOGS = []

barrier = threading.Barrier(2, timeout=120.0)
lock = threading.Lock()
simTimeFinalStep = 60*60*10
trackingDict = {"currentStepSimX": -1, 
    "currentStepOGS": -1,
    "waitTotalSimX": 0,
    "waitTotalOGS": 0}


# ______________ Start Calculation ______________

print("[SERVER]\t is starting ...")
serverThread = threading.Thread(target=handleServer, daemon=True)
serverThread.setName('Thread [SERVER]')
serverThread.start()

try:
    sim = win32com.client.GetActiveObject()
except:
    sim = win32com.client.Dispatch('ESI.SimulationX43')
xl_id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, sim)
# help(type(xl_id))
# print(isinstance(xl_id, pythoncom.PyIStream))
simXThread = threading.Thread(target=handleSimulationX, kwargs={'xl_id': xl_id})
simXThread.setName('Thread [SimX]')
simXThread.start()

callOGS = r'OGS-Model\ogs.exe -o OGS-Model\results OGS-Model\{}.prj > OGS-Model\results\result.tec'.format(OGS_project)
# subprocess.run(r'OGS-Model\ogs.exe OGS-Model\3BHE.prj > result.tec &', shell=True) # run OGS with Output in terminal
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

simXThread.join()


# ______________ Save Results ______________

savePathSimX = os.sep.join([dir, "[Server] Com SimX.txt"])
savePathOGS = os.sep.join([dir, "[Server] Com OGS.txt"])

df_SimX = pd.DataFrame(lSimX, columns=[
                        'Paket Code',
                        't',
                        'dt',
                        'n',
                        'kanal1(t)',
                        'kanal1(t-dt)', 
                        'kanal2(t)', 
                        'kanal2(t-dt)', 
                        'kanal3(t)', 
                        'kanal3(t-dt)'])

colOGS = ['Paket Code', 't', 'dt', 'n']
for i in range((len(lOGS[0])-4)//2):
    colOGS.append('kanal'+str(i+1)+'(t)')
    colOGS.append('kanal'+str(i+1)+'(t-dt)')

df_OGS = pd.DataFrame(lOGS, columns=colOGS)

df_SimX.to_csv(savePathSimX, index=False)
df_OGS.to_csv(savePathOGS, index=False)

end = time.time()

file = open('[Server] runtime.txt', 'w+')
file.write('OGS had to wait in total for:\t' + str(trackingDict['waitTotalOGS']) + ' s\n' +
           'SimX had to wait in total for:\t' + str(trackingDict['waitTotalSimX']) + ' s\n' +
           'Total runtime:\t\t\t' + str(end-start) + ' s')
file.close()

print('[Server]\t OGS had to wait in total for:\t' + str(trackingDict['waitTotalOGS']) + 's')
print('[Server]\t SimX had to wait in total for:\t' + str(trackingDict['waitTotalSimX']) + 's')
print('[Server]\t Total runtime:\t\t\t' + str(end-start) + 's')
