import os

import block
import sign
import transaction


def test_single_block():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()

    root = block.TxBlock()
    tx = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub2, 1),],
    )
    tx.sign(pvt1)
    root.add_tx(tx)

    tx2 = transaction.Tx(
        inputs=[(pub3, 1),],
        outputs=[(pub1, 1),],
    )
    tx2.sign(pvt3)
    root.add_tx(tx2)

    assert root.is_valid()


def test_mining():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()
    pvt4, pub4 = sign.gen_keys()

    root = block.TxBlock()
    tx = transaction.Tx(
        inputs=[(pub1, 1.1),],
        outputs=[(pub2, 1),],
    )
    tx.sign(pvt1)
    root.add_tx(tx)

    # miner reward transaction.
    tx2 = transaction.Tx(
        outputs=[(pub4, 25.1),],
    )
    tx2.sign(pvt3)
    root.add_tx(tx2)

    assert root.is_valid()


def test_bad_block():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()

    root = block.TxBlock()
    tx = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub2, 100),],  # this makes the transaction invalid.
    )
    tx.sign(pvt1)
    root.add_tx(tx)

    tx2 = transaction.Tx(
        inputs=[(pub3, 1),],
        outputs=[(pub1, 1),],
    )
    tx2.sign(pvt3)
    root.add_tx(tx2)

    assert not root.is_valid()


def test_block_serdes():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()

    root = block.TxBlock()
    tx = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub2, 1),],
    )
    tx.sign(pvt1)
    root.add_tx(tx)

    tx2 = transaction.Tx(
        inputs=[(pub3, 1),],
        outputs=[(pub1, 1),],
    )
    tx2.sign(pvt3)
    root.add_tx(tx2)

    with open('block.json', 'w') as f:
        f.write(root.to_json())
    with open('block.json', 'r') as f:
        root = block.TxBlock.from_json(f.read())
    os.remove('block.json')

    assert root.is_valid()


def test_multiple_blocks():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()

    # root block and its transactions.
    root = block.TxBlock()
    tx = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub2, 1),],
    )
    tx.sign(pvt1)
    root.add_tx(tx)

    tx2 = transaction.Tx(
        inputs=[(pub3, 1),],
        outputs=[(pub1, 1),],
    )
    tx2.sign(pvt3)
    root.add_tx(tx2)

    # child block and its transactions.
    child = block.TxBlock(previous_block=root)
    tx3 = transaction.Tx(
        inputs=[(pub2, 1),],
        outputs=[(pub3, 1),],
    )
    tx3.sign(pvt2)
    child.add_tx(tx3)

    tx4 = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub3, 1),],
        required=[pub2],
    )
    tx4.sign(pvt1)
    tx4.sign(pvt2)
    child.add_tx(tx4)

    assert child.is_valid()
    assert root.is_valid()


def test_block_tampering():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()

    # root block and its transactions.
    root = block.TxBlock()
    tx = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub2, 1),],
    )
    tx.sign(pvt1)
    root.add_tx(tx)

    tx2 = transaction.Tx(
        inputs=[(pub3, 1),],
        outputs=[(pub1, 1),],
    )
    tx2.sign(pvt3)
    root.add_tx(tx2)

    # child block and its transactions.
    child = block.TxBlock(previous_block=root)
    tx3 = transaction.Tx(
        inputs=[(pub2, 1),],
        outputs=[(pub3, 1),],
    )
    tx3.sign(pvt2)
    child.add_tx(tx3)

    tx4 = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub3, 1),],
        required=[pub2],
    )
    tx4.sign(pvt1)
    tx4.sign(pvt2)
    child.add_tx(tx4)

    # tamper the child by adding an extra transaction.
    child.previous_block.add_tx(tx4)

    assert not child.is_valid()
    assert root.is_valid()
