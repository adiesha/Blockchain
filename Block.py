import hashlib
import time


class Block:
    def __init__(self, id):
        self.id = id
        self.nonce = 0
        self.transactions = []
        self.prev = ''.join('0' for i in range(64))
        self.hash = None
        self.maxNonce = 50000000
        self.difficultySize = 5
        self.difficultyprefix = ''.join('0' for i in range(self.difficultySize))
        self.trasactionstring = None

    def mine(self):
        start = time.perf_counter()
        for i in range(self.maxNonce):
            self.nonce = i
            text = self.gethashablestring()
            encodedText = text.encode()
            temphash = hashlib.sha256(encodedText).hexdigest()
            if temphash[0:self.difficultySize] == self.difficultyprefix:
                print("hash mined {0}".format(temphash))
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
        transactiondata = self.getTransactionsStringFromcache()
        prev = self.prev
        result = blockid + nonceString + transactiondata + prev
        return result

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

    def printTransactions(self):
        for t in self.transactions:
            print(t)