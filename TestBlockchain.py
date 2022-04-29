from Blockchain import Blockchain


def testBlockchain():
    # t1 = Transaction()
    # t1.createTestTransaction(1)
    #
    # t2 = Transaction()
    # t2.createTestTransaction(1)
    #
    # t3 = Transaction()
    # t3.createTestTransaction(1)
    #
    # t4 = Transaction()
    # t4.createTestTransaction()

    # tr = [t1, t2]
    bc = Blockchain(1)
    bc.extractData()
    bc.createAblock(bc.createSetOfTransacations())
    print(bc.validateBlock(bc.last))
    bc.extractData()
    bc.createAblock(bc.createSetOfTransacations())
    print(bc.validateBlock(bc.last))
    bc.extractData()
    bc.createAblock(bc.createSetOfTransacations())
    print(bc.validateBlock(bc.last))
    bc.extractData()
    print(bc.validateBlock(bc.last))
    bc.createAblock([])
    print(bc.validateBlock(bc.last))
    bc.createAblock(bc.createSetOfTransacations())
    print(bc.validateBlock(bc.last))
    print(bc)
    bc.printChain()
    bc.extractData()


testBlockchain()
