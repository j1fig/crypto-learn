import sign
import transaction


def test_block_serdes():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()

    tx = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub2, 1),],
    )
    tx.sign(pvt1)

    with open('tx.json', 'w') as f:
        f.write(tx.to_json())

    with open('tx.json', 'r') as f:
        tx = transaction.Tx.from_json(f.read())

    assert tx.is_valid()
