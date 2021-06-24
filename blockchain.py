import json

from cryptography.hazmat.primitives import hashes


class Block:
    data = None
    previous_block = None
    previous_hash = None

    def __init__(self, data, previous_block=None):
        self.data = data
        self._hash = None
        self.previous_block = previous_block
        self.previous_hash = previous_block.hash if previous_block else None

    @property
    def hash(self):
        return _hash(self.data, self.previous_hash)

    def to_json(self):
        return json.dumps({
            'data': self.data.decode() if self.data is not None else None,
            'previous_block': self.previous_block.to_json() if self.previous_block is not None else None,
            'previous_hash': self.previous_hash.decode() if self.previous_hash is not None else None,
        })

    @classmethod
    def from_json(cls, json_data):
        block = cls(data=None)
        bd = json.loads(json_data)
        block.data = bd['data'].encode() if bd['data'] is not None else None
        block.previous_hash = bd['previous_hash'].encode() if bd['previous_hash'] is not None else None
        block.previous_block = Block.from_json(bd['previous_block']) if bd['previous_block'] is not None else None
        return block


def _hash(data, previous_hash):
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data)

    # root block will not have a previous hash.
    if previous_hash is not None:
        digest.update(previous_hash)

    return digest.finalize()
