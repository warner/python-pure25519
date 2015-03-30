from pure25519.basic import (B, random_scalar, decodepoint, encodepoint,
                             scalarmult_with_extended as scalarmult)
from hashlib import sha256

# In practice, you should use the Curve25519 function, which is better in
# every way. But this is an example of what Diffie-Hellman looks like.

def dh_start(entropy_f):
    x = random_scalar(entropy_f)
    X = scalarmult(B, x)
    return x,encodepoint(X)

def dh_finish(x, Y_s):
    Y = decodepoint(Y_s)
    XY = scalarmult(Y, x)
    return sha256(encodepoint(XY)).digest()
