
# single-file pure-python ed25519 digital signatures, rearranged to minimize
# the namespace pollution so this can be embedded in another file. Adapted
# from https://bitbucket.org/dholth/ed25519ll


# Ed25519 digital signatures
# Based on http://ed25519.cr.yp.to/python/ed25519.py
# See also http://ed25519.cr.yp.to/software.html
# Adapted by Ron Garret
# Sped up considerably using coordinate transforms found on:
# http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html
# Specifically add-2008-hwcd-4 and dbl-2008-hwcd

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

import hashlib, binascii

b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493

def H(m):
    return hashlib.sha512(m).digest()

# Can probably get some extra speedup here by replacing this with
# an extended-euclidean, but performance seems OK without that
def inv(x):
    return pow(x, q-2, q)

d = -121665 * inv(121666)
I = pow(2,(q-1)//4,q)

def xrecover(y):
    xx = (y*y-1) * inv(d*y*y+1)
    x = pow(xx,(q+3)//8,q)
    if (x*x - xx) % q != 0: x = (x*I) % q
    if x % 2 != 0: x = q-x
    return x

By = 4 * inv(5)
Bx = xrecover(By)
B = [Bx % q,By % q]

#def edwards(P,Q):
#    x1 = P[0]
#    y1 = P[1]
#    x2 = Q[0]
#    y2 = Q[1]
#    x3 = (x1*y2+x2*y1) * inv(1+d*x1*x2*y1*y2)
#    y3 = (y1*y2+x1*x2) * inv(1-d*x1*x2*y1*y2)
#    return (x3 % q,y3 % q)

#def scalarmult(P,e):
#    if e == 0: return [0,1]
#    Q = scalarmult(P,e/2)
#    Q = edwards(Q,Q)
#    if e & 1: Q = edwards(Q,P)
#    return Q

# Faster (!) version based on:
# http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html

def xpt_add(pt1, pt2):
    (X1, Y1, Z1, T1) = pt1
    (X2, Y2, Z2, T2) = pt2
    A = ((Y1-X1)*(Y2+X2)) % q
    B = ((Y1+X1)*(Y2-X2)) % q
    C = (Z1*2*T2) % q
    D = (T1*2*Z2) % q
    E = (D+C) % q
    F = (B-A) % q
    G = (B+A) % q
    H = (D-C) % q
    X3 = (E*F) % q
    Y3 = (G*H) % q
    Z3 = (F*G) % q
    T3 = (E*H) % q
    return (X3, Y3, Z3, T3)

def xpt_double (pt):
    (X1, Y1, Z1, _) = pt
    A = (X1*X1)
    B = (Y1*Y1)
    C = (2*Z1*Z1)
    D = (-A) % q
    J = (X1+Y1) % q
    E = (J*J-A-B) % q
    G = (D+B) % q
    F = (G-C) % q
    H = (D-B) % q
    X3 = (E*F) % q
    Y3 = (G*H) % q
    Z3 = (F*G) % q
    T3 = (E*H) % q
    return (X3, Y3, Z3, T3)

def pt_xform (pt):
    (x, y) = pt
    return (x, y, 1, (x*y)%q)

def pt_unxform (pt):
    (x, y, z, _) = pt
    return ((x*inv(z))%q, (y*inv(z))%q)

def xpt_mult (pt, n):
    if n==0: return pt_xform((0,1))
    _ = xpt_double(xpt_mult(pt, n>>1))
    return xpt_add(_, pt) if n&1 else _

def scalarmult(pt, e):
    return pt_unxform(xpt_mult(pt_xform(pt), e))

def encodeint(y):
    bits = [(y >> i) & 1 for i in range(b)]
    e = [(sum([bits[i * 8 + j] << j for j in range(8)]))
                                    for i in range(b//8)]
    return asbytes(e)

def encodepoint(P):
    x = P[0]
    y = P[1]
    bits = [(y >> i) & 1 for i in range(b - 1)] + [x & 1]
    e = [(sum([bits[i * 8 + j] << j for j in range(8)]))
                                    for i in range(b//8)]
    return asbytes(e)

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

def isoncurve(P):
    x = P[0]
    y = P[1]
    return (-x*x + y*y - 1 - d*x*x*y*y) % q == 0

def decodeint(s):
    return int(binascii.hexlify(s[:32][::-1]), 16)

def decodepoint(s):
    unclamped = int(binascii.hexlify(s[:32][::-1]), 16)
    clamp = (1 << 255) - 1
    y = unclamped & clamp
    x = xrecover(y)
    if x & 1 != bit(s,b-1): x = q-x
    P = [x,y]
    if not isoncurve(P): raise Exception("decoding point that is not on curve")
    return P

def checkvalid(s, m, pk):
    if len(s) != b//4: raise Exception("signature length is wrong")
    if len(pk) != b//8: raise Exception("public-key length is wrong")
    R = decodepoint(s[0:b//8]) # 32
    A = decodepoint(pk)
    S = decodeint(s[b//8:b//4]) # 32
    h = Hint(encodepoint(R) + pk + m)
    v1 = scalarmult(B,S)
#  v2 = edwards(R,scalarmult(A,h))
    v2 = pt_unxform(xpt_add(pt_xform(R), pt_xform(scalarmult(A, h))))
    return v1==v2


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

ed25519_create_signing_key = create_signing_key
ed25519_create_verifying_key = create_verifying_key
ed25519_sign = sign
ed25519_verify = verify

## sk = ed25519_create_signing_key()
## msg = "hello world"
## sig = ed25519_sign(sk, msg)
## assert len(sig) == 64
## vk = ed25519_create_verifying_key(sk)
## ed25519_verify(vk, sig, msg)
## print "ok"

