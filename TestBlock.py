from Block import Block
from Transaction import Transaction

def testBlock():
    b1 = Block(1)
    t1 = Transaction()
    t1.createTestTransaction()

    t2 = Transaction()
    t2.createTestTransaction()

    b1.addTransaction(t1)
    b1.addTransaction(t2)

    print(b1.mine())
    b1.printTransactions()

def testBlock2():
    b1 = Block(1)
    print(b1.mine())
    b1.printTransactions()

testBlock2()