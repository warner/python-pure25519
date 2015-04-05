import binascii

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

# Extended Coordinates: x=X/Z, y=Y/Z, x*y=T/Z
# http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html

def xform_affine_to_extended(pt):
    (x, y) = pt
    return (x, y, 1, (x*y)%q) # (X,Y,Z,T)

def xform_extended_to_affine(pt):
    (x, y, z, _) = pt
    return ((x*inv(z))%q, (y*inv(z))%q)

def _add_extended_nonunfied(pt1, pt2): # extended->extended
    # add-2008-hwcd-4 : NOT unified, only for pt1!=pt2. About 10% faster than
    # the (unified) add-2008-hwcd-3, and safe to use inside scalarmult.
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

def double_extended(pt): # extended->extended
    # dbl-2008-hwcd
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

def add_extended(pt1, pt2): # extended->extended
    # add-2008-hwcd-3 . Slightly slower than add-2008-hwcd-4, but -3 is
    # unified, so it's safe for general-purpose addition..
    (X1, Y1, Z1, T1) = pt1
    (X2, Y2, Z2, T2) = pt2
    A = ((Y1-X1)*(Y2-X2)) % q
    B = ((Y1+X1)*(Y2+X2)) % q
    C = T1*(2*d)*T2 % q
    D = Z1*2*Z2 % q
    E = (B-A) % q
    F = (D-C) % q
    G = (D+C) % q
    H = (B+A) % q
    X3 = (E*F) % q
    Y3 = (G*H) % q
    T3 = (E*H) % q
    Z3 = (F*G) % q
    return (X3, Y3, Z3, T3)

def scalarmult_extended (pt, n): # extended->extended
    assert n >= 0
    if n==0:
        return xform_affine_to_extended((0,1))
    # scalarmult(0element, anything) results in both _ and pt being the same
    # thing (the neutral 0element, namely the extended form of (0,1)), which
    # violates _add_extended_nonunfied's precondition. So test for pt=0 and
    # shortcut the operation without using an add. pt=0 means affine
    # coordinates of (x=0,y=1). To get x=0 from extended coordinates, you
    # need either X or Z to be 0. To get y=1, you need Y=Z, Y!=0, Z!=0. So to
    # get pt0, we need X=0, Y=Z, and Y!=0
    (X, Y, Z, T) = pt
    if X==0 and Y==Z and Y!=0:
        return xform_affine_to_extended((0,1))
    _ = double_extended(_scalarmult_extended_internal(pt, n>>1))
    return _add_extended_nonunfied(_, pt) if n&1 else _

def _scalarmult_extended_internal(pt, n): # extended->extended
    if n==0: return xform_affine_to_extended((0,1))
    _ = double_extended(_scalarmult_extended_internal(pt, n>>1))
    return _add_extended_nonunfied(_, pt) if n&1 else _

# encode/decode

# scalars are encoded as 32-bytes little-endian

def encodeint(y):
    assert 0 <= y < 2**256
    return binascii.unhexlify("%064x" % y)[::-1]

def decodeint(s):
    assert len(s) == 32, len(s)
    return int(binascii.hexlify(s[::-1]), 16)

def clamped_decodeint(s):
    # clamp the scalar to ensure two things:
    #   1: integer value is in l/2 .. l, to avoid small-logarithm
    #      non-wraparaound
    #   2: low-order 3 bits are zero, so a small-subgroup attack won't learn
    #      any information
    # set the top two bits to 01, and the bottom three to 000
    a_unclamped = decodeint(s)
    AND_CLAMP = (1<<254) - 1 - 7
    OR_CLAMP = (1<<254)
    a_clamped = (a_unclamped & AND_CLAMP) | OR_CLAMP
    return a_clamped

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
        P = [x,y] # no attempt to use both "positive" and "negative" X

        # only about 50% of Y coordinates map to valid curve points (I think
        # the other half give you points on the "twist").
        if isoncurve(P):
            P = Element(xform_affine_to_extended(P))
            # even if the point is on our curve, it may not be in our
            # particular (order=l) subgroup. The curve has order 8*l, so an
            # arbitrary point could have order 1,2,4,8,1*l,2*l,4*l,8*l
            # (everything which divides the group order). There are phi(x)
            # points with order x, so:
            #  1 element of order 1: [(x=0,y=1)=Zero]
            #  1 element of order 2 [(x=0,y=-1)]
            #  2 elements of order 4
            #  4 elements of order 8
            #  l-1 elements of order l (including Base)
            #  l-1 elements of order 2*l
            #  2*(l-1) elements of order 4*l
            #  4*(l-1) elements of order 8*l

            # So 50% of random points will have order 8*l, 25% will have
            # order 4*l, 13% order 2*l, and 13% will have our desired order
            # 1*l (and a vanishingly small fraction will have 1/2/4/8). If we
            # multiply any of the 8*l points by 2, we're sure to get an 4*l
            # point (and multiplying a 4*l point by 2 gives us a 2*l point,
            # and so on). Multiplying a 1*l point by 2 gives us a different
            # 1*l point. So multiplying by 8 gets us from almost any point
            # into a uniform point on the correct 1*l subgroup.

            P = P.scalarmult(8)

            # if we got really unlucky and picked one of the 8 low-order
            # points, multiplying by 8 will get us to the identity (Zero),
            # which we check for explicitly.
            if P == Zero:
                continue

            # Test that we're finally in the right group. We use
            # _scalarmult_raw() because the normal scalarmult(x) does x%l,
            # and that would bypass the check we care about
            assert P._scalarmult_raw(l) == Zero

            return xform_extended_to_affine(P.XYTZ)
        # increment our Y and try again until we find a valid point
        y = (y + 1) % q
    return P

def password_to_scalar(pw):
    oversized = hashlib.sha512(pw).digest()
    return int(binascii.hexlify(oversized), 16) % l


INT_TYPE = type(1<<256) # 'long' on py2, 'int' on py3

class Scalar(INT_TYPE):
    def __new__(klass, val):
        return INT_TYPE.__new__(klass, val % l)
    def __neg__(self):
        return INT_TYPE.__neg__(self) % l
    def __add__(self, other):
        return self.__add__(self, other) % l
    def __sub__(self, other):
        return self.__sub__(self, other) % l
    def __mul__(self, other):
        return self.__mul__(self, other) % l
    def __div__(self, other):
        raise TypeError("Scalars cannot be divided, only +/-/*")
    def __divmod__(self, other):
        raise TypeError("Scalars cannot be divided, only +/-/*")

    def to_bytes(self):
        return encodeint(self % l)

    @classmethod
    def random(klass, entropy_f):
        return klass(random_scalar(entropy_f))
    @classmethod
    def from_bytes(klass, bytes):
        return decodeint(bytes)
    @classmethod
    def from_password(klass, pw):
        return klass(password_to_scalar(pw))
    @classmethod
    def clamped_from_bytes(klass, bytes):
        return klass(clamped_decodeint(bytes))

class Element:
    def __init__(self, XYTZ):
        assert isinstance(XYTZ, tuple)
        assert len(XYTZ) == 4
        self.XYTZ = XYTZ
    def add(self, other):
        return Element(add_extended(self.XYTZ, other.XYTZ))
    def negate(self):
        # slow. Prefer e.scalarmult(-pw) to e.scalarmult(pw).negate()
        return Element(scalarmult_extended(self.XYTZ, l-2))
    def subtract(self, other):
        return self.add(self.negate(other))
    def scalarmult(self, s):
        return Element(scalarmult_extended(self.XYTZ, int(s) % l))
    def _scalarmult_raw(self, s):
        return Element(scalarmult_extended(self.XYTZ, int(s))) # no %l
    def to_bytes(self):
        return encodepoint(xform_extended_to_affine(self.XYTZ))
    def __eq__(self, other):
        return self.to_bytes() == other.to_bytes()

    @classmethod
    def from_bytes(klass, bytes):
        return klass(xform_affine_to_extended(decodepoint(bytes)))
    @classmethod
    def arbitrary(klass, seed):
        return klass(xform_affine_to_extended(arbitrary_element(seed)))

Base = Element(xform_affine_to_extended(B))
Zero = Base.scalarmult(0) # the neutral (identity) element
