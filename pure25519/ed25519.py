
from pure25519.basic import (b,B,l,
                             encodepoint, encodeint, decodepoint, decodeint,
                             scalarmult_with_extended as scalarmult,
                             add_affine as add)
import hashlib, binascii

try: # pragma nocover
    unicode
    PY3 = False
    def asbytes(b):
        """Convert array of integers to byte string"""
        return ''.join(chr(x) for x in b)
    def joinbytes(b):
        """Convert array of bytes to byte string"""
        return ''.join(b)
    def bit(h, i):
        """Return i'th bit of bytestring h"""
        return (ord(h[i//8]) >> (i%8)) & 1

except NameError: # pragma nocover
    PY3 = True
    asbytes = bytes
    joinbytes = bytes
    def bit(h, i):
        return (h[i//8] >> (i%8)) & 1

def H(m):
    return hashlib.sha512(m).digest()

def publickey(sk):
    h = H(sk)
    a = 2**(b-2) + sum(2**i * bit(h,i) for i in range(3,b-2))
    A = scalarmult(B,a)
    return encodepoint(A)

def Hint(m):
    h = H(m)
    return int(binascii.hexlify(h[::-1]), 16)

def signature(m,sk,pk):
    sk = sk[:32]
    h = H(sk)
    a = 2**(b-2) + sum(2**i * bit(h,i) for i in range(3,b-2))
    inter = joinbytes([h[i] for i in range(b//8,b//4)])
    r = Hint(inter + m)
    R = scalarmult(B,r)
    S = (r + Hint(encodepoint(R) + pk + m) * a) % l
    return encodepoint(R) + encodeint(S)

def checkvalid(s, m, pk):
    if len(s) != b//4: raise Exception("signature length is wrong")
    if len(pk) != b//8: raise Exception("public-key length is wrong")
    R = decodepoint(s[0:b//8]) # 32
    A = decodepoint(pk)
    S = decodeint(s[b//8:b//4]) # 32
    h = Hint(encodepoint(R) + pk + m)
    v1 = scalarmult(B,S)
    v2 = add(R,scalarmult(A,h))
    #Ah_xpt = xpt_mult(pt_xform(A), h)
    #R_Ah_xpt = xpt_add(pt_xform(R), Ah_xpt)
    #v2 = pt_unxform(R_Ah_xpt)
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
