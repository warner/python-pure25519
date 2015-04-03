from pure25519.basic import Element, Scalar, Base
from hashlib import sha256

# In practice, you should use the Curve25519 function, which is better in
# every way. But this is an example of what Diffie-Hellman looks like.

def dh_start(entropy_f):
    x = Scalar.random(entropy_f)
    X = Base.scalarmult(x)
    return x,X.to_bytes()

def dh_finish(x, Y_s):
    Y = Element.from_bytes(Y_s)
    XY = Y.scalarmult(x)
    return sha256(XY.to_bytes()).digest()
