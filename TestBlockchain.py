from Blockchain import Blockchain
from Transaction import Transaction


def testBlockchain():
    t1 = Transaction()
    t1.createTestTransaction()

    t2 = Transaction()
    t2.createTestTransaction()
    tr = [t1, t2]
    bc = Blockchain(1)
    bc.createAblock([])
    bc.createAblock([])
    bc.createAblock(tr)
    print(bc)
    bc.printChain()

testBlockchain()