import blockchain
import transaction


class TxBlock:
    def __init__(self, data=b'', previous_block=None):
        self._block = blockchain.Block(data, previous_block)

    def to_json(self):
        return self._block.to_json()

    @classmethod
    def from_json(cls, json_data):
        tx_block = cls()
        tx_block._block = blockchain.Block.from_json(json_data)
        return tx_block

    def add_tx(self, tx):
        self._block.data += (tx.to_json() + '\n').encode()

    def is_valid(self):
        # all block transactions should be valid.
        txs = [
            transaction.Tx.from_json(tx_json)
            for tx_json in self._block.data.decode().split('\n')
            if tx_json != ''
        ]
        if any(not t.is_valid() for t in txs):
            return False

        # all non-root blocks' previous_hash should match the hash of the previous block.
        is_root = self._block.previous_hash is None
        if not is_root and self.previous_block.hash != self.previous_hash:
            return False

        return True

    @property
    def hash(self):
        return self._block.hash

    @property
    def previous_block(self):
        return self._block.previous_block

    @property
    def previous_hash(self):
        return self._block.previous_hash
