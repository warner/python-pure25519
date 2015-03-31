import binascii

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

b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493

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

# Affine Coordinates

def add_affine(P,Q): # complete
    x1 = P[0]
    y1 = P[1]
    x2 = Q[0]
    y2 = Q[1]
    x3 = (x1*y2+x2*y1) * inv(1+d*x1*x2*y1*y2)
    y3 = (y1*y2+x1*x2) * inv(1-d*x1*x2*y1*y2)
    return (x3 % q,y3 % q)

def scalarmult_affine(P,e):
    e = e % l
    if e == 0: return [0,1]
    Q = scalarmult_affine(P,e/2)
    Q = add_affine(Q,Q)
    if e & 1: Q = add_affine(Q,P)
    return Q

# Extended Coordinates: x=X/Z, y=Y/Z, x*y=T/Z
# http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html

def xform_affine_to_extended(pt):
    (x, y) = pt
    return (x, y, 1, (x*y)%q) # (X,Y,Z,T)

def xform_extended_to_affine(pt):
    (x, y, z, _) = pt
    return ((x*inv(z))%q, (y*inv(z))%q)

def add_extended(pt1, pt2): # add-2008-hwcd-4 : NOT unified, only for pt1!=pt2
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

def double_extended(pt): # dbl-2008-hwcd
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

def scalarmult_extended (pt, n):
    n = n % l
    if n==0: return xform_affine_to_extended((0,1))
    _ = double_extended(scalarmult_extended(pt, n>>1))
    return add_extended(_, pt) if n&1 else _

def scalarmult_with_extended(pt, e):
    e = e % l
    return xform_extended_to_affine(scalarmult_extended(xform_affine_to_extended(pt), e))

def add_extended_z2is1(pt1, pt2): # madd-2008-hwcd-4
    (X1, Y1, Z1, T1) = pt1
    (X2, Y2, Z2, T2) = pt2
    assert Z2 == 1
    A = (Y1-X1)*(Y2+X2) % q
    B = (Y1+X1)*(Y2-X2) % q
    C = Z1*2*T2 % q
    D = 2*T1 % q
    E = D+C % q
    F = B-A % q
    G = B+A % q
    H = D-C % q
    X3 = E*F % q
    Y3 = G*H % q
    T3 = E*H % q
    Z3 = F*G % q
    return (X3, Y3, Z3, T3)

def scalarmult_2_extended(pt, n):
    # takes affine, returns extended
    assert len(pt) == 2 # affine
    n = n % l
    if n==0: return xform_affine_to_extended((0,1))
    xpt = xform_affine_to_extended(pt) # so Z=1
    return scalarmult_2_extended_inner(xpt, n)

def scalarmult_2_extended_inner(xpt, n):
    if n==0: return xform_affine_to_extended((0,1))
    _ = double_extended(scalarmult_2_extended_inner(xpt, n>>1))
    return add_extended_z2is1(_, xpt) if n&1 else _

# encode/decode

# scalars are encoded as 32-bytes little-endian

def encodeint(y):
    assert 0 <= y < 2**256
    return binascii.unhexlify("%064x" % y)[::-1]

def decodeint(s):
    return int(binascii.hexlify(s[:32][::-1]), 16)

# points are encoded as 32-bytes little-endian, b2b1 are 0, b0 is sign

def encodepoint(P):
    x = P[0]
    y = P[1]
    # MSB of output equals x.b0 (=x&1)
    # rest of output is little-endian y
    assert 0 <= y < (1<<255) # always < 0x7fff..ff
    if x & 1:
        y += 1<<255
    return binascii.unhexlify("%064x" % y)[::-1]

def isoncurve(P):
    x = P[0]
    y = P[1]
    return (-x*x + y*y - 1 - d*x*x*y*y) % q == 0

def decodepoint(s):
    unclamped = int(binascii.hexlify(s[:32][::-1]), 16)
    clamp = (1 << 255) - 1
    y = unclamped & clamp # clear MSB
    x = xrecover(y)
    if bool(x & 1) != bool(unclamped & (1<<255)): x = q-x
    P = [x,y]
    if not isoncurve(P): raise Exception("decoding point that is not on curve")
    return P

# utilities

def random_scalar(entropy_f): # 0..l-1 inclusive
    # reduce the bias to a safe level by generating 256 extra bits
    oversized = int(binascii.hexlify(entropy_f(32+32)), 16)
    return oversized % l

import hashlib
def arbitrary_element(seed): # unknown DL
    hseed = hashlib.sha512(seed).digest()
    y = int(binascii.hexlify(hseed), 16) % q
    while True:
        x = xrecover(y)
        P = [x,y]
        P = scalarmult_affine(P, 8) # clear the cofactor
        if isoncurve(P):
            return P
        # I don't understand how to do this properly yet. I expected that the
        # *8 would let any random [xrecover(y),y] be a valid point, but it
        # fails about 50% of the time. This loop is a desperate hack.
        y = (y + 1) % q
    return P

def password_to_scalar(pw):
    oversized = hashlib.sha512(pw).digest()
    return int(binascii.hexlify(oversized), 16) % l
