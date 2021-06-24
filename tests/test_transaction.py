import os

import sign
import transaction


def test_one_to_one():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    tx = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub2, 1),],
    )
    tx.sign(pvt1)

    # a simple properly signed one to one transaction should be valid.
    assert tx.is_valid()


def test_tampering():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()
    tx = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub2, 1),],
    )
    tx.sign(pvt1)

    # try and deviate funds to a bad actor after signing.
    tx._outputs[transaction._serialize_public_key(pub2)]['pub_key'] = transaction._serialize_public_key(pub3)

    # a tampered with transaction should be invalid.
    assert not tx.is_valid()


def test_negative_input_amount():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    tx = transaction.Tx(
        inputs=[(pub1, -1),],
        outputs=[(pub2, 1),],
    )
    tx.sign(pvt1)

    # a negative input amount should be invalid.
    assert not tx.is_valid()


def test_negative_output_amount():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    tx = transaction.Tx(
        inputs=[(pub1, 0.1),],
        outputs=[(pub2, -0.1),],
    )
    tx.sign(pvt1)

    # a negative output amount should be invalid.
    assert not tx.is_valid()


def test_missing_signature():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()
    tx = transaction.Tx(
        inputs=[(pub1, 1), (pub2, 1)],
        outputs=[(pub3, 1),],
    )
    tx.sign(pvt1)

    # a transaction missing a signature should be invalid.
    assert not tx.is_valid()


def test_wrong_signature():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()
    tx = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub2, 1),],
    )
    tx.sign(pvt3)

    # a badly signed one to one transaction should be invalid.
    assert not tx.is_valid()


def test_output_exceeds_input():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()
    tx = transaction.Tx(
        inputs=[(pub1, 1), (pub2, 1)],
        outputs=[(pub3, 4),],
    )
    tx.sign(pvt1)
    tx.sign(pvt2)

    # a transaction whose output amounts exceed the input amounts should not be valid.
    assert not tx.is_valid()


def test_unsigned_escrow():
    pvt1, pub1 = sign.gen_keys()
    pvt2, pub2 = sign.gen_keys()
    pvt3, pub3 = sign.gen_keys()
    tx = transaction.Tx(
        inputs=[(pub1, 1),],
        outputs=[(pub2, 1),],
        required=[pub3],
    )
    tx.sign(pvt1)

    # a transaction not signed by one of the required party should be invalid.
    assert not tx.is_valid()


def test_serdes():
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
    os.remove('tx.json')

    assert tx.is_valid()
