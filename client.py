# echo-client.py
import json
import logging
import os
import pickle
import random
import socket
import sys
import threading
import time

from Blockchain import Blockchain


class Client():

    def __init__(self, host="127.0.0.1", clientip="127.0.0.1", serverport=65431, hb=20, toggleHB=False):
        self.HOST = host  # The server's hostname or IP address
        self.SERVER_PORT = serverport  # The port used by the server
        self.clientip = clientip
        self.clientPort = None
        self.seq = None
        self.map = None
        self.bc = None
        self.heartbeatInterval = hb
        self.togglehb = toggleHB
        self.clientmutex = threading.Lock()
        self.txservcflag = False

    def createJSONReq(self, typeReq, nodes=None, slot=None):
        # Initialize node
        if typeReq == 1:
            request = {"req": "1"}
            return request
        # Send port info
        elif typeReq == 2:
            request = {"req": "2", "seq": str(self.seq), "port": str(self.clientPort)}
            return request
        # Get map data
        elif typeReq == 3:
            request = {"req": "3", "seq": str(self.seq)}
            return request
        else:
            return ""

    def receiveWhole(self, s):
        BUFF_SIZE = 4096  # 4 KiB
        data = b''
        while True:
            part = s.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                # either 0 or end of data
                break
        return data

    def getJsonObj(self, input):
        jr = json.loads(input)
        return jr

    def initializeTheNode(self):
        # establish connection with server and give info about the client port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HOST, self.SERVER_PORT))
            strReq = self.createJSONReq(1)
            jsonReq = json.dumps(strReq)

            s.sendall(str.encode(jsonReq))

            data = self.receiveWhole(s)
            resp = self.getJsonObj(data.decode("utf-8"))

            self.seq = int(resp['seq'])
            print("sequence: " + str(self.seq))
            s.close()
        currrent_dir = os.getcwd()
        finallogdir = os.path.join(currrent_dir, 'log')
        if not os.path.exists(finallogdir):
            os.mkdir(finallogdir)
        logging.basicConfig(filename="log/{0}.log".format(self.seq), level=logging.DEBUG, filemode='w')

    def sendNodePort(self):
        # establish connection with server and give info about the client port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HOST, self.SERVER_PORT))
            strReq = self.createJSONReq(2)
            jsonReq = json.dumps(strReq)

            s.sendall(str.encode(jsonReq))

            data = self.receiveWhole(s)
            resp = self.getJsonObj(data.decode("utf-8"))

            print(resp['response'])
            s.close()

    def downloadNodeMap(self):
        # establish connection with server and give info about the client port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HOST, self.SERVER_PORT))
            strReq = self.createJSONReq(3)
            jsonReq = json.dumps(strReq)

            s.sendall(str.encode(jsonReq))

            data = self.receiveWhole(s)
            resp = self.getJsonObj(data.decode("utf-8"))

            print(resp)
            s.close()
            return resp

    def getMapData(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HOST, self.SERVER_PORT))
            strReq = self.createJSONReq(3)
            jsonReq = json.dumps(strReq)

            s.sendall(str.encode(jsonReq))

            data = self.receiveWhole(s)
            resp = self.getJsonObj(data.decode("utf-8"))
            resp2 = {}
            for k, v in resp.items():
                resp2[int(k)] = (v[0], int(v[1]))

            print(resp2)
            s.close()
            return resp2

    def process(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, int(self.clientPort)))
            while (True):
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    time.sleep(2)
                    while True:
                        data = self.receiveWhole(conn)
                        if data == b'':
                            break
                        message = self.getJsonObj(data.decode("utf-8"))
                        if list(message.keys())[0] == "req":
                            event = message
                            print("Message received: ", message)
                        else:
                            self.map = message
                            print("Updated Map: ", self.map)

    def createThreadToListen(self):
        thread = threading.Thread(target=self.ReceiveMessageFunct)
        thread.daemon = True
        thread.start()
        return thread

    def createTxServiceThread(self):
        thread = threading.Thread(target=self.txservice)
        thread.daemon = True
        thread.start()
        return thread

    def txservice(self):
        while True:
            time.sleep(15)
            if self.txservcflag:
                print("Transaction Service invoked. Trying to create a new block in node {0}".format(self.seq))
                self.bc.createAblock(self.bc.createSetOfTransacations())

    #
    # def createThreadToBroadcast(self, event, nodes, slot):
    #     thread = threading.Thread(target=self.broadcast(event, nodes, slot))
    #     thread.daemon = True
    #     thread.start()
    #
    # def createHeartBeatThread(self):
    #     thread = threading.Thread(target=self.heartbeat)
    #     thread.daemon = True
    #     thread.start()

    def ReceiveMessageFunct(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Started listening to clientip {0} port {1}".format(self.clientip, self.clientPort))
            s.bind((self.clientip, self.clientPort))
            while True:
                s.listen()
                conn, addr = s.accept()
                with conn:
                    # print(f"Connected by {addr}")
                    logging.debug(f"Connected by {addr}")
                    while True:
                        data = self.receiveWhole(conn)
                        self.clientmutex.acquire()
                        if data == b'':
                            break
                        unpickledRequest = pickle.loads(data)
                        # print(unpickledRequest)
                        logging.debug(unpickledRequest)
                        if isinstance(unpickledRequest, dict):
                            # join the partial log
                            # np = unpickledRequest['pl']
                            # mtx = unpickledRequest['mtx']
                            # nid = unpickledRequest['nodeid']
                            print(unpickledRequest)
                            nid = unpickledRequest['id']
                            msg = unpickledRequest['msg']
                            lst = unpickledRequest['list']
                            print(nid, msg, lst)
                            self.bc.receiveMessage(unpickledRequest)

                            # self.bc.receiveMessage((np, mtx, nid))

                            # conflicts = self.dd.checkConflictingAppnmts()
                            # for c in conflicts:
                            #     self.dd.cancelAppointment((c.timeslot, c))

                            # create message receive event
                            # send the message success request
                            response = {"response": "Success"}
                            # the_encoding = chardet.detect(pickle.dumps(response))['encoding']
                            # response['encoding'] = the_encoding
                            pickledMessage = pickle.dumps(response)
                            try:
                                conn.sendall(pickledMessage)
                            except:
                                print("Problem occurred while sending the reply to node {0}".format("jhgjy"))
                        else:
                            response = {"response": "Failed", "error": "Request should be a dictionary"}
                            # the_encoding = chardet.detect(pickle.dumps(response))['encoding']
                            # response['encoding'] = the_encoding
                            pickledMessage = pickle.dumps(response)
                            conn.sendall(pickledMessage)
                        self.clientmutex.release()
                        break


    def menu(self, bc):
        while True:
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            print("Display Blockchain\t[d]")
            print("Display Last Block\t[l]")
            print("Create new block\t[b]")
            print("Display specific block\t[g]")
            print("Display summary of the blockchain\t[e]")
            print("Press t to Toggle the transaction service\t [t]")
            print("Quit    \t[q]")
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

            resp = input("Choice: ").lower().split()
            if len(resp) < 1:
                print("Not a correct input")
                continue
            if resp[0] == 'd':
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print("Display Blockchain")
                bc.printChain()
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            elif resp[0] == 'l':
                print("====================")
                print(bc.last)
                print("====================")
            elif resp[0] == 'b':
                print("*******************************************")
                self.bc.createAblock(bc.createSetOfTransacations())
                print("*******************************************")
            elif resp[0] == 's':
                self.bc.sendMessage()
            elif resp[0] == 'q':
                print("Quitting")
                break
            elif resp[0] == 'e':
                print("####################################")
                self.bc.extractData()
                print("####################################")
            elif resp[0] == 'g':
                print("====================")
                blockid = int(input("input the block id: "))
                print(self.bc.getBlock(blockid))
                print("====================")
            elif resp[0] == 't':
                self.txservcflag = not self.txservcflag
                print("----------------------------------------------------")
                print("Toggling txservice flag->{0}".format(self.txservcflag))
                print("::::::::::::::::::::::::::::::::::::::::::::::::::::")

    def main(self):
        print('Number of arguments:', len(sys.argv), 'arguments.')
        print('Argument List:', str(sys.argv))

        if len(sys.argv) > 1:
            print("Server ip is {0}".format(sys.argv[1]))
            self.HOST = sys.argv[1]
            print("Server Ip updated")

        if len(sys.argv) > 2:
            print("Client's ip is {0}".format(sys.argv[2]))
            self.clientip = sys.argv[2]

        else:
            print("User did not choose a client ip default is 127.0.0.1")
            self.clientip = "127.0.0.1"

        if len(sys.argv) > 3:
            print("user inputted client port {0}".format(sys.argv[3]))
            self.clientPort = int(sys.argv[3])
        else:
            print("User did not choose a port for the node. Random port between 55000-63000 will be selected")
            port = random.randint(55000, 63000)
            print("Random port {0} selected".format(port))
            self.clientPort = port

        self.initializeTheNode()
        self.sendNodePort()
        # need to put following inside the menu
        # self.createThreadToListen()
        print("Ready to start the Calendar. Please wait until all the nodes are ready to continue. Then press Enter")
        if input() == "":
            print("Started Creating the Distributed Calendar")
            self.map = self.getMapData()
            blockchain = Blockchain(self.seq)
            blockchain.map = self.map
            self.bc = blockchain
            # self.createThreadToListen()
            # self.createHeartBeatThread()
            self.createThreadToListen()
            self.createTxServiceThread()
            self.menu(blockchain)


if __name__ == '__main__':
    client = Client()
    client.main()
