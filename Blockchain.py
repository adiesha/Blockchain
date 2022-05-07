import pickle
import random
import socket
import logging
import threading

from Block import Block
from Transaction import Transaction


class Blockchain:
    def __init__(self, id):
        self.clientid = id
        self.last = None
        self.first = None
        self.data = {}
        self.map = None
        self.lock = threading.Lock()

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
        self.lock.acquire()
        self.extractData()
        if self.validateBlock(block) and self.validate(block):
            self.addNewBlockToChain(block)
        else:
            print("Random transactions has a conflict try again")
        self.lock.release()
        self.sendMessage()

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

    def validate(self, block):
        # hash the block and check whether it matches with the hash inside it.
        if block.hash == block.gethash():
            print("Block id {0} hash is correct".format(block.id))
        else:
            print("Incorrect hash in the block {0} vs {1}".format(block.hash, block.gethash()))
            return False

        # check the previous hash
        # search the previous block and find it
        prevblock = self.getBlock(block.id - 1)
        if prevblock is None:
            if block.id == 1:
                if block.prevhash == ''.join('0' for i in range(64)):
                    return True
            else:
                print(
                    "block cannot be validated because blockchain does not have its previous block and block is not the initial block")
                print("Block id {0} Block hash {1} block's prev hash {2}".format(block.id, block.hash, block.prevhash))
                return False
        if prevblock.hash == block.prevhash:
            print("Block is validated against its hash and its previous blocks hash")
            return True
        else:
            print("Previous hash is incorrect {0} vs {1}".format(prevblock.hash, block.prevhash))
            return False

    def getBlock(self, id):
        temp = self.last
        if temp is None:
            return None
        else:
            while temp is not None:
                if id == temp.id:
                    return temp
                else:
                    temp = temp.prev
            return None

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
        # print(temp)

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
            # print(data)
            self.data = data
        print(self.data)

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
                amount = random.randint(0, sendersbalance)
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
                temp = []
                end = self.last
                while (end is not None):
                    temp.append(end)
                    end = end.prev
                strReq['list'] = temp

                pickledMessage = pickle.dumps(strReq)
                s.sendall(pickledMessage)
                data = self.receiveWhole(s)
                # print(data)
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

    def receiveMessage(self, message):
        nid = message['id']
        msg = message['msg']
        lst = message['list']
        # check the block id.
        print("Block id {0}".format(msg.id))
        print("Node id {0}".format(nid))
        # if the block id already exist in the bc reject
        currentid = 0 if self.last is None else self.last.id
        if currentid >= msg.id:
            print("New block already exist. current last block {0}: Received block {1}".format(self.last, msg))
            return False, "New block already exist. current last block {0}: Received block {1}".format(self.last, msg)
        # validate the block for double spending else reject
        self.extractData()


        # find the latest block that is common with the list and the bc
        currenttemp = self.last
        filter = []
        while currenttemp is not None:
            filter = [b for b in lst if b.hash == currenttemp.hash]
            if filter:
                break
            else:
                currenttemp = currenttemp.prev

        self.lock.acquire()
        if filter:
            currentBlock = filter[0]
            tempid = currentBlock.id + 1
            self.last = currentBlock
        else:
            self.last = None
            tempid = 1
        while tempid <= msg.id:
            # find the block from the list
            NextBlock = [b for b in lst if b.id == tempid]
            blnew = NextBlock[0]
            self.extractData()
            if not self.validateBlock(blnew):
                print("New block validation failed. Not going to add it to the blockchain Block Id {0}".format(
                    blnew.id))
                return False, "New block validation failed. Not going to add it to the blockchain Block Id {0}".format(
                    blnew.id)
            else:
                # validate the block hashes
                if not self.validate(blnew):
                    print("Block hashes does not match")
                    return False, "Block hashes does not match"
                else:
                    print("validation successful for block {0}".format(blnew))
                    self.addNewBlockToChain(blnew)

            tempid += 1
        self.lock.release()
        pass
