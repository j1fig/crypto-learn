from typing import Iterable
import json

from cryptography.hazmat.primitives import serialization

import sign


class Tx:
    def __init__(self, inputs=[], outputs=[], required=[]):
        self._inputs = dict()
        self._outputs = dict()
        self._required = []
        self._signatures = dict()
        for args in inputs:
            self.add_input(*args)
        for args in outputs:
            self.add_output(*args)
        for args in required:
            self.add_required(*args)

    def add_input(self, public_key, amount):
        serialized_key = _serialize_public_key(public_key)
        self._inputs[serialized_key] = {
            'pub_key': serialized_key,
            'amount': amount,
        }

    def add_output(self, public_key, amount):
        serialized_key = _serialize_public_key(public_key)
        self._outputs[serialized_key] = {
            'pub_key': serialized_key,
            'amount': amount,
        }

    def add_required(self, public_key):
        serialized_key = _serialize_public_key(public_key)
        self._required.append(serialized_key)

    def sign(self, private_key):
        self._signatures[private_key] = sign.sign(self._serialize(), private_key)

    def _serialize(self):
        # create a byte-encoded json representation of the transaction.
        return json.dumps(
            list(self._inputs.values()) +
            list(self._outputs.values()) +
            self._required
        ).encode()

    def is_valid(self):
        # all inputs must have signed the transaction.
        signatures_pub_keys = [
            _serialize_public_key(pvt.public_key())
            for pvt in self._signatures
        ]
        if not all(i in signatures_pub_keys for i in self._inputs):
            print('input signature missing')
            return False

        # all required must have signed the transaction.
        if not all(r in signatures_pub_keys for r in self._required):
            print('required signature missing')
            return False

        # negative amount values should be invalid.
        has_negative_input_amount = any(
            v['amount'] < 0 for v in self._inputs.values()
        )
        has_negative_output_amount = any(
            v['amount'] < 0 for v in self._inputs.values()
        )
        if has_negative_input_amount or has_negative_output_amount:
            print('negative amount detected')
            return False

        # all signatures should successfully verify the content.
        message = self._serialize()
        return all(
            sign.verify(message, s, pvt.public_key())
            for pvt, s in self._signatures.items()
        )


def _serialize_public_key(pub):
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1
    )


def _serialize_private_key(pvt):
    return pvt.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1
    )


def _deserialize_private_key(pem_content):
    return serialization.load_pem_private_key(pem_content)
