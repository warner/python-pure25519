
from .basic import (b,B,l,d,q,xrecover,
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
    v2 = add(R,scalarmult(A,h))
    #Ah_xpt = xpt_mult(pt_xform(A), h)
    #R_Ah_xpt = xpt_add(pt_xform(R), Ah_xpt)
    #v2 = pt_unxform(R_Ah_xpt)
    return v1==v2
