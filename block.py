import blockchain


class TxBlock:
    def __init__(self, data, previous_block=None):
        self._block = blockchain.Block(data, previous_block)

    def add_tx(self, tx):
        pass

    def is_valid(self):
        return False
