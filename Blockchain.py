from Block import Block


class Blockchain:
    def __init__(self, id):
        self.clientid = id
        self.last = None
        self.first = None
        self.data = {}

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

    def validateBlock(self):
        pass

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
        pass
