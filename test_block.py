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
