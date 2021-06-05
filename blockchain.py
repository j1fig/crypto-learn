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


def _hash(data, previous_hash):
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data)

    # root block will not have a previous hash.
    if previous_hash is not None:
        digest.update(previous_hash)

    return digest.finalize()
