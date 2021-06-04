from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def gen_keys():
    pvt = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    pub = pvt.public_key()
    return pvt, pub


def sign(msg, private_key):
    return private_key.sign(
        msg, 
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )


def verify(msg, signature, public_key):
    try:
        public_key.verify(
            signature,
            msg,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False
