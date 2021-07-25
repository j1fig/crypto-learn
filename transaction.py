from decimal import Decimal, ROUND_DOWN
import base64
import json

from cryptography.hazmat.primitives import serialization

import sign


MINING_REWARD = 25

"""
Tx represents a transaction and it's properties.

Tx inner data is stored as str and not bytes, decoding as late as the calling interfaces allows it to.
In cases where a non UTF-8 byte-encoding is used, binary data is base64 encoded before converting to str.
This makes serialization/deserialization easier at some expense of serdes code to convert to/from Python objects leaking into the business logic. This can be greatly improved upon.
"""
class Tx:
    def __init__(self, inputs=[], outputs=[], required=[]):
        """
        `inputs` are the sources from which the transaction originates. these are specified by a list of public key and amount tuples. TODO make that a type.
        `outputs` are the destinations to which the transaction goes to. these are specified by a list of public key and amount tuples.
        `required` are the third parties that are required to sign the transaction. these are specified as a list of public keys expected to have signed the transaction.
        """
        self._inputs = dict()
        self._outputs = dict()
        self._required = []
        self._signatures = dict()
        for args in inputs:
            self.add_input(*args)
        for args in outputs:
            self.add_output(*args)
        for args in required:
            self.add_required(args)

    def to_json(self):
        return json.dumps({
            'inputs': self._inputs,
            'outputs': self._outputs,
            'required': self._required,
            'signatures': self._signatures,
        })

    @classmethod
    def from_json(cls, json_data):
        tx = cls()
        tx_data = json.loads(json_data)
        tx._inputs = tx_data['inputs']
        tx._outputs = tx_data['outputs']
        tx._required = tx_data['required']
        tx._signatures = tx_data['signatures']
        return tx

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
        serialized_key = _serialize_public_key(private_key.public_key())
        self._signatures[serialized_key] = base64.b64encode(
            sign.sign(self._serialize_payload(), private_key)
        ).decode()

    def _serialize_payload(self):
        # create a byte-encoded json representation of the transaction main payload.
        return json.dumps(
            list(self._inputs.values()) +
            list(self._outputs.values()) +
            self._required
        ).encode()

    def is_valid(self):
        # all inputs must have signed the transaction.
        if not all(i in self._signatures for i in self._inputs):
            print('input signature missing')
            return False

        # all required must have signed the transaction.
        if not all(r in self._signatures for r in self._required):
            print('required signature missing')
            return False

        # negative amount values should be invalid.
        has_negative_input_amount = any(
            v['amount'] < 0 for v in self._inputs.values()
        )
        has_negative_output_amount = any(
            v['amount'] < 0 for v in self._outputs.values()
        )
        if has_negative_input_amount or has_negative_output_amount:
            print('negative amount detected')
            return False

        # TODO Move this to a block level consistency check.
        # output amount must not exceed the inputs' amount with the mining reward.
        # input_amount = Decimal(sum(v['amount'] for v in self._inputs.values())).quantize(Decimal('0.0000000000001'), rounding=ROUND_DOWN)
        # output_amount = Decimal(sum(v['amount'] for v in self._outputs.values())).quantize(Decimal('0.0000000000001'), rounding=ROUND_DOWN)
        # if output_amount > input_amount + Decimal(MINING_REWARD):
        #     print('output amount exceeds the input amount')
        #     print(output_amount)
        #     print(input_amount + Decimal(MINING_REWARD))
        #     return False

        # all signatures should successfully verify the content.
        message = self._serialize_payload()
        return all(
            sign.verify(
                message,
                base64.b64decode(sig.encode()),
                _deserialize_public_key(pub_key.encode())
            )
            for pub_key, sig in self._signatures.items()
        )


def _serialize_public_key(pub):
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1
    ).decode()


def _deserialize_public_key(pem_content):
    return serialization.load_pem_public_key(pem_content)
