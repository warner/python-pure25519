
from pure25519.basic import Element, Scalar, Base
import hashlib, binascii

def H(m):
    return hashlib.sha512(m).digest()

def publickey(seed):
    # turn first half of SHA512(seed) into scalar, then into point
    assert len(seed) == 32
    a = Scalar.clamped_from_bytes(H(seed)[:32])
    A = Base.scalarmult(a)
    return A.to_bytes()

def Hint(m):
    h = H(m)
    return int(binascii.hexlify(h[::-1]), 16)

def signature(m,sk,pk):
    assert len(sk) == 32 # seed
    assert len(pk) == 32
    h = H(sk[:32])
    a_bytes, inter = h[:32], h[32:]
    a = Scalar.clamped_from_bytes(a_bytes)
    r = Hint(inter + m)
    R = Base.scalarmult(r)
    R_bytes = R.to_bytes()
    S = Scalar(r + Hint(R_bytes + pk + m) * a)
    return R_bytes + S.to_bytes()

def checkvalid(s, m, pk):
    if len(s) != 64: raise Exception("signature length is wrong")
    if len(pk) != 32: raise Exception("public-key length is wrong")
    R = Element.from_bytes(s[:32])
    A = Element.from_bytes(pk)
    S = Scalar.from_bytes(s[32:])
    h = Hint(s[:32] + pk + m)
    v1 = Base.scalarmult(S)
    v2 = R.add(A.scalarmult(h))
    return v1==v2

# wrappers

import os

def create_signing_key():
    seed = os.urandom(32)
    return seed
def create_verifying_key(signing_key):
    return publickey(signing_key)

def sign(skbytes, msg):
    """Return just the signature, given the message and just the secret
    key."""
    if len(skbytes) != 32:
        raise ValueError("Bad signing key length %d" % len(skbytes))
    vkbytes = create_verifying_key(skbytes)
    sig = signature(msg, skbytes, vkbytes)
    return sig

def verify(vkbytes, sig, msg):
    if len(vkbytes) != 32:
        raise ValueError("Bad verifying key length %d" % len(vkbytes))
    if len(sig) != 64:
        raise ValueError("Bad signature length %d" % len(sig))
    rc = checkvalid(sig, msg, vkbytes)
    if not rc:
        raise ValueError("rc != 0", rc)
    return True
