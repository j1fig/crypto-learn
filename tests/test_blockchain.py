import pytest

import blockchain as bc


@pytest.mark.parametrize('block', [
    bc.Block(b'child', bc.Block(b'root')),
    bc.Block(b'grandchild', bc.Block(b'child', bc.Block(b'root'))),
])
def test_block_hashing(block):
    assert block.previous_block.hash == block.previous_hash


def test_block_tampering():
    root = bc.Block(b'root')
    child = bc.Block(b'child', root)
    grandchild = bc.Block(b'grandchild', child)

    # tamper with data.
    child.data = b'chald'

    # hashes should now differ.
    assert grandchild.previous_block.hash != grandchild.previous_hash
