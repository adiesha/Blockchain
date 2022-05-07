import hashlib
import time


class Block:
    def __init__(self, id):
        self.id = id
        self.nonce = 0
        self.transactions = []
        self.prev = None
        self.next = None
        self.prevhash = ''.join('0' for i in range(64))
        self.hash = None
        self.maxNonce = 50000000
        self.difficultySize = 4
        self.difficultyprefix = ''.join('0' for i in range(self.difficultySize))
        self.trasactionstring = None
        self.coinbase = (None, 0)

    def gethash(self):
        text = self.gethashablestring()
        encodedText = text.encode()
        temphash = hashlib.sha256(encodedText).hexdigest()
        return temphash

    def mine(self):
        start = time.perf_counter()
        for i in range(self.maxNonce):
            self.nonce = i
            text = self.gethashablestring()
            encodedText = text.encode()
            temphash = hashlib.sha256(encodedText).hexdigest()
            if temphash[0:self.difficultySize] == self.difficultyprefix:
                print("hash mined {0}".format(temphash))
                self.hash = temphash
                end = time.perf_counter()
                return temphash, self.nonce, end - start
            else:
                # print(temphash)
                continue
        print("Could not mine the hash with existing nonce. Increase the max Nonce size")
        return None, self.nonce, self

    def gethashablestring(self):
        blockid = str(self.id)
        nonceString = str(self.nonce)
        coinbase = str(self.coinbase)
        transactiondata = self.getTransactionsStringFromcache()
        prev = self.prevhash
        result = blockid + nonceString + coinbase + transactiondata + prev
        return result

    def getHash(self):
        text = self.gethashablestring()
        encodedText = text.encode()
        temphash = hashlib.sha256(encodedText).hexdigest()
        return temphash

    def getTransactionsStringFromcache(self):
        if self.trasactionstring is None:
            self.trasactionstring = self.createTransactionDataString()
            return self.trasactionstring
        else:
            return self.trasactionstring

    def createTransactionDataString(self):
        transactiondata = ''
        for t in self.transactions:
            transactiondata = transactiondata + str(t)
        return transactiondata

    def addTransaction(self, tr):
        self.transactions.append(tr)

    def addTransactions(self, trarray):
        self.transactions = trarray

    def printTransactions(self):
        print("Coin base: {0} -> {1}".format(self.coinbase[1], self.coinbase[0]))
        for t in self.transactions:
            print(t)

    def __str__(self):
        return "BlockID: {0} Nonce: {1} CoindBase: {2} Tr: {3} PreviousHash : {4} Hash:{5}".format(self.id, self.nonce,
                                                                                                   self.coinbase,
                                                                                                   self.transactions,
                                                                                                   self.prevhash,
                                                                                                   self.hash)
