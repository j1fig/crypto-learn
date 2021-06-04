import pytest

import sign


@pytest.fixture
def keys():
    return sign.gen_keys()


@pytest.mark.parametrize('original,tampered,expected', [
    (b"a secret", b"a secret", True),
    (b"a secret", b"o secret", False),
])
def test_verify_msg(original, tampered, expected):
    pvt, pub = sign.gen_keys()
    signature = sign.sign(original, pvt)

    assert sign.verify(tampered, signature, pub) == expected
