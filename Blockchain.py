import pickle
import random
import socket
import logging

from Block import Block
from Transaction import Transaction


class Blockchain:
    def __init__(self, id):
        self.clientid = id
        self.last = None
        self.first = None
        self.data = {}
        self.map = None

    def __str__(self):
        return "Data {0}".format(self.data)

    def createAblock(self, transactions):
        newblockid = self.getLastBlockId() + 1
        block = Block(newblockid)
        block.addTransactions(transactions)
        # add prev block hash
        if self.last is not None:
            block.prevhash = self.last.hash
        block.coinbase = (self.clientid, 100)
        block.mine()
        self.addNewBlockToChain(block)

    def getLastBlockId(self):
        if self.last is None:
            return 0
        else:
            return self.last.id

    def validateBlock(self, block, data=None):
        if data is None:
            data = self.data

        for tr in block.transactions:
            sender = tr.sender
            receiver = tr.recipient
            amount = tr.amount
            if sender in data:
                if data[sender] >= amount:
                    pass
                else:
                    print("Does not have enough balance in sender {0} Amount:{1}".format(sender, data[sender]))
                    return False
            else:
                print("Sender not in the block chain {0}".format(sender))
                return False
        return True

    def addNewBlockToChain(self, block):
        temp = self.last
        if temp is not None:
            temp.next = block
        self.last = block
        self.last.prev = temp

        if self.first is None:
            self.first = self.last

    def printChain(self):
        temp = self.last
        while (True):
            if temp is None:
                return
            else:
                print(temp)
                temp = temp.prev

    def extractData(self):
        temp = []
        block = self.last
        while block is not None:
            temp.append(block)
            block = block.prev
        print(temp)

        data = {}
        while temp:
            bl = temp.pop()
            coinbase = bl.coinbase
            if coinbase[0] is not None:
                if coinbase[0] in data:
                    data[coinbase[0]] = data[coinbase[0]] + coinbase[1]
                else:
                    data[coinbase[0]] = coinbase[1]

            for tr in bl.transactions:
                sender = tr.sender
                receiver = tr.recipient
                amount = tr.amount
                if sender in data:
                    data[sender] = data[sender] - amount
                else:
                    print("Error: No sender in the data")
                    return None
                if receiver in data:
                    data[receiver] = data[receiver] + amount
                else:
                    data[receiver] = amount
            print(data)
            self.data = data

    def createSetOfTransacations(self):
        temptr = []
        if self.data is None:
            return []
        else:
            noOftransactions = random.randint(1, 10)
            print("Selected transaction amount {0}".format(noOftransactions))
            keys = list(self.data.keys())
            while (noOftransactions > 0 and keys):
                choice = random.choice(keys)
                keys.remove(choice)
                sendersbalance = self.data[choice]
                amount = random.randint(1, sendersbalance)
                tr = Transaction()
                tr.sender = choice
                tr.recipient = random.randint(0, 10)
                tr.amount = amount
                noOftransactions -= 1
                temptr.append(tr)

            return temptr

    def sendMessage(self):
        for k, v in self.map.items():
            if k != self.clientid:
                self.sendViaSocket(k, self.last)

    def sendViaSocket(self, k, m):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.map[k][0], int(self.map[k][1])))

                strReq = {}
                strReq['id'] = self.clientid
                strReq['msg'] = m

                pickledMessage = pickle.dumps(strReq)
                s.sendall(pickledMessage)
                data = self.receiveWhole(s)
                print(data)
                print(pickle.loads(data))
            except ConnectionRefusedError:
                print("Connection cannot be established to node {0}".format(k))
                logging.error("Connection cannot be established to node {0}".format(k))

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
