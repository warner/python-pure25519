import binascii, hashlib

b = 256
q = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493

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
    return (x%q, y%q, 1, (x*y)%q) # (X,Y,Z,T)

def xform_extended_to_affine(pt):
    (x, y, z, _) = pt
    return ((x*inv(z))%q, (y*inv(z))%q)

def _add_extended_nonunfied(pt1, pt2): # extended->extended
    #return add_extended(pt1,pt2)
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
    # This form only accepts points that are a member of the main 1*L
    # subgroup, and the neutral element Zero. It will give incorrect answers
    # when called with the points of order 2/4/8.
    assert n >= 0
    # to tolerate pt=Zero, we need to use the safe form, because sooner or
    # later we'll be asked to add pt (Zero) to the results of
    # scalarmult_extended() (which will be Zero), and that will violate
    # _add_extended_nonunfied()'s precondition. The affine form of Zero is
    # (x=0,y=1). The extended form has X=0, Y=Z, and Y!=0.
    (X, Y, Z, T) = pt
    Y = Y % q
    Z = Z % q
    if X==0 and Y==Z and Y!=0:
        return scalarmult_extended_safe_slow(pt, n)
    return _scalarmult_extended_internal(pt, n)

def _scalarmult_extended_internal(pt, n):
    if n==0:
        return xform_affine_to_extended((0,1))
    _ = double_extended(_scalarmult_extended_internal(pt, n>>1))
    return _add_extended_nonunfied(_, pt) if n&1 else _

def scalarmult_extended_safe_slow(pt, n):
    # this form is slightly slower, but tolerates arbitrary points, including
    # those which are not in the main 1*L subgroup. This includes points of
    # order 1 (the neutral element Zero), 2, 4, and 8.
    assert n >= 0
    if n==0:
        return xform_affine_to_extended((0,1))
    _ = double_extended(scalarmult_extended_safe_slow(pt, n>>1))
    return add_extended(_, pt) if n&1 else _

# encode/decode

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

class NotOnCurve(Exception):
    pass

def decodepoint(s):
    unclamped = int(binascii.hexlify(s[:32][::-1]), 16)
    clamp = (1 << 255) - 1
    y = unclamped & clamp # clear MSB
    x = xrecover(y)
    if bool(x & 1) != bool(unclamped & (1<<255)): x = q-x
    P = [x,y]
    if not isoncurve(P): raise NotOnCurve("decoding point that is not on curve")
    return P

# Scalar utilities. scalars are encoded as 32-bytes little-endian

def bytes_to_scalar(s):
    assert len(s) == 32, len(s)
    return int(binascii.hexlify(s[::-1]), 16)

def bytes_to_clamped_scalar(s):
    # Ed25519 private keys clamp the scalar to ensure two things:
    #   1: integer value is in L/2 .. L, to avoid small-logarithm
    #      non-wraparaound
    #   2: low-order 3 bits are zero, so a small-subgroup attack won't learn
    #      any information
    # set the top two bits to 01, and the bottom three to 000
    a_unclamped = bytes_to_scalar(s)
    AND_CLAMP = (1<<254) - 1 - 7
    OR_CLAMP = (1<<254)
    a_clamped = (a_unclamped & AND_CLAMP) | OR_CLAMP
    return a_clamped

def random_scalar(entropy_f): # 0..L-1 inclusive
    # reduce the bias to a safe level by generating 256 extra bits
    oversized = int(binascii.hexlify(entropy_f(32+32)), 16)
    return oversized % L

def password_to_scalar(pw):
    oversized = hashlib.sha512(pw).digest()
    return int(binascii.hexlify(oversized), 16) % L

def scalar_to_bytes(y):
    y = y % L
    assert 0 <= y < 2**256
    return binascii.unhexlify("%064x" % y)[::-1]

# Elements, of various orders

def is_extended_zero(XYTZ):
    # catch Zero
    (X, Y, Z, T) = XYTZ
    Y = Y % q
    Z = Z % q
    if X==0 and Y==Z and Y!=0:
        return True
    return False

class ElementOfUnknownGroup:
    # This is used for points of order 2,4,8,2*L,4*L,8*L
    def __init__(self, XYTZ):
        assert isinstance(XYTZ, tuple)
        assert len(XYTZ) == 4
        self.XYTZ = XYTZ


    def add(self, other):
        sum_XYTZ = add_extended(self.XYTZ, other.XYTZ)
        if is_extended_zero(sum_XYTZ):
            return Zero
        return ElementOfUnknownGroup(sum_XYTZ)

    def scalarmult(self, s):
        assert s >= 0
        product = scalarmult_extended_safe_slow(self.XYTZ, s)
        return ElementOfUnknownGroup(product)

    def to_bytes(self):
        return encodepoint(xform_extended_to_affine(self.XYTZ))
    def __eq__(self, other):
        return self.to_bytes() == other.to_bytes()
    def __ne__(self, other):
        return not self == other


class Element(ElementOfUnknownGroup):
    # this only holds elements in the main 1*L subgroup. It never holds Zero,
    # or elements of order 1/2/4/8, or 2*L/4*L/8*L.

    def add(self, other):
        sum_element = ElementOfUnknownGroup.add(self, other)
        if sum_element is Zero:
            return sum_element
        if isinstance(other, Element):
            # adding two subgroup elements results in another subgroup
            # element, or Zero, and we've already excluded Zero
            return Element(sum_element.XYTZ)
        # not necessarily a subgroup member, so assume not
        return sum_element

    def scalarmult(self, s):
        # scalarmult of subgroup members can be done modulo the subgroup
        # order, and using the faster non-unified function.
        s = s % L
        # scalarmult(s=0) gets you Zero
        if s == 0:
            return Zero
        # scalarmult(s=1) gets you self, which is a subgroup member
        # scalarmult(s<grouporder) gets you a different subgroup member
        return Element(scalarmult_extended(self.XYTZ, s))

    # negation and subtraction only make sense for the main subgroup
    def negate(self):
        # slow. Prefer e.scalarmult(-pw) to e.scalarmult(pw).negate()
        return Element(scalarmult_extended(self.XYTZ, L-2))
    def subtract(self, other):
        return self.add(other.negate())

class _ZeroElement(ElementOfUnknownGroup):
    def add(self, other):
        return other # zero+anything = anything
    def scalarmult(self, s):
        return self # zero*anything = zero
    def negate(self):
        return self # -zero = zero
    def subtract(self, other):
        return self.add(other.negate())


Base = Element(xform_affine_to_extended(B))
Zero = _ZeroElement(xform_affine_to_extended((0,1))) # the neutral (identity) element

_zero_bytes = Zero.to_bytes()


def arbitrary_element(seed): # unknown DL
    # TODO: if we don't need uniformity, maybe use just sha256 here?
    hseed = hashlib.sha512(seed).digest()
    y = int(binascii.hexlify(hseed), 16) % q
    while True:
        x = xrecover(y)
        Pa = [x,y] # no attempt to use both "positive" and "negative" X

        # only about 50% of Y coordinates map to valid curve points (I think
        # the other half give you points on the "twist").
        if isoncurve(Pa):
            P = ElementOfUnknownGroup(xform_affine_to_extended(Pa))
            # even if the point is on our curve, it may not be in our
            # particular (order=L) subgroup. The curve has order 8*L, so an
            # arbitrary point could have order 1,2,4,8,1*L,2*L,4*L,8*L
            # (everything which divides the group order).

            # [I MAY BE COMPLETELY WRONG ABOUT THIS, but my brief statistical
            # tests suggest it's not too far off] There are phi(x) points
            # with order x, so:
            #  1 element of order 1: [(x=0,y=1)=Zero]
            #  1 element of order 2 [(x=0,y=-1)]
            #  2 elements of order 4
            #  4 elements of order 8
            #  L-1 elements of order L (including Base)
            #  L-1 elements of order 2*L
            #  2*(L-1) elements of order 4*L
            #  4*(L-1) elements of order 8*L

            # So 50% of random points will have order 8*L, 25% will have
            # order 4*L, 13% order 2*L, and 13% will have our desired order
            # 1*L (and a vanishingly small fraction will have 1/2/4/8). If we
            # multiply any of the 8*L points by 2, we're sure to get an 4*L
            # point (and multiplying a 4*L point by 2 gives us a 2*L point,
            # and so on). Multiplying a 1*L point by 2 gives us a different
            # 1*L point. So multiplying by 8 gets us from almost any point
            # into a uniform point on the correct 1*L subgroup.

            P8 = P.scalarmult(8)

            # if we got really unlucky and picked one of the 8 low-order
            # points, multiplying by 8 will get us to the identity (Zero),
            # which we check for explicitly.
            if is_extended_zero(P8.XYTZ):
                continue

            # Test that we're finally in the right group. We want to
            # scalarmult by L, and we want to *not* use the trick in
            # Group.scalarmult() which does x%L, because that would bypass
            # the check we care about. P is still an _ElementOfUnknownGroup,
            # which doesn't use x%L because that's not correct for points
            # outside the main group.
            assert is_extended_zero(P8.scalarmult(L).XYTZ)

            return Element(P8.XYTZ)
        # increment our Y and try again until we find a valid point
        y = (y + 1) % q
    # never reached

def bytes_to_unknown_group_element(bytes):
    # this accepts all elements, including Zero and wrong-subgroup ones
    if bytes == _zero_bytes:
        return Zero
    XYTZ = xform_affine_to_extended(decodepoint(bytes))
    return ElementOfUnknownGroup(XYTZ)

def bytes_to_element(bytes):
    # this strictly only accepts elements in the right subgroup
    P = bytes_to_unknown_group_element(bytes)
    if P is Zero:
        raise ValueError("element was Zero")
    if not is_extended_zero(P.scalarmult(L).XYTZ):
        raise ValueError("element is not in the right group")
    # the point is in the expected 1*L subgroup, not in the 2/4/8 groups,
    # or in the 2*L/4*L/8*L groups. Promote it to a correct-group Element.
    return Element(P.XYTZ)
