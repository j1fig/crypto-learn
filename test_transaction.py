import sign
import transaction


def test_valid_one_to_one():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    tx = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub2, 1),],
    )
    tx.sign(pvt1)

    assert tx.is_valid()
