import unittest
import random
from binascii import hexlify
from pure25519.basic import (q, l, B, _ElementOfUnknownGroup,
                             _add_extended_nonunfied, add_extended, encodepoint,
                             xform_extended_to_affine, xform_affine_to_extended)
from pure25519.basic import Scalar, Base, Element, Zero
from pure25519.slow_basic import (slow_add_affine, scalarmult_affine,
                                  scalarmult_affine_to_extended)

class Basic(unittest.TestCase):
    def assertElementsEqual(self, e1, e2, msg=None):
        self.assertEqual(hexlify(e1.to_bytes()), hexlify(e2.to_bytes()),
                         msg)
    def assertBytesEqual(self, e1, e2, msg=None):
        self.assertEqual(hexlify(e1), hexlify(e2), msg)

    def test_arbitrary_element(self):
        for i in range(20):
            seed = str(i).encode("ascii")
            e = Element.arbitrary(seed)
            e2 = Element.arbitrary(seed)
            self.assertElementsEqual(e, e2)

    def test_password_to_scalar(self):
        for i in range(20):
            seed = str(i).encode("ascii")
            s = Scalar.from_password(seed)
            s2 = Scalar.from_password(seed)
            self.assertEqual(s, s2)

    def test_scalarmult(self):
        Bsm = Base.scalarmult
        e0 = Bsm(0)
        e1 = Bsm(1)
        e2 = Bsm(2)
        e5 = Bsm(5)
        e10 = Bsm(10)
        e15 = Bsm(15)
        em5 = Bsm(-5)
        self.assertElementsEqual(e0.add(e0), e0)
        self.assertElementsEqual(e1, Base)
        self.assertElementsEqual(e0.add(e1), e1)
        self.assertElementsEqual(Bsm(-5), Bsm(-5 % l))
        # there was a bug, due to the add inside scalarmult being
        # non-unified, which caused e0.scalarmult(N) to not equal e0
        self.assertElementsEqual(e0.scalarmult(5), e0)
        self.assertElementsEqual(e2.scalarmult(0), e0)
        self.assertElementsEqual(e1.add(e1), e2)
        self.assertElementsEqual(e5.add(e5), e10)
        self.assertElementsEqual(e5.add(e10), e15)
        self.assertElementsEqual(e2.scalarmult(5), e10)
        self.assertElementsEqual(e15.add(em5), e10)
        self.assertElementsEqual(e5.add(em5), e0)

        sm2 = scalarmult_affine
        e = {}
        for i in range(-50, 100):
            e[i] = Bsm(i)
            self.assertElementsEqual(Element(xform_affine_to_extended(sm2(B, i))), e[i])
            self.assertElementsEqual(Element(scalarmult_affine_to_extended(B, i)),
                                     e[i])

        for i in range(20,30):
            for j in range(-10,10):
                x1 = e[i].add(e[j])
                x2 = Bsm(i+j)
                self.assertElementsEqual(x1, x2, (x1,x2,i,j))
                x3 = Element(xform_affine_to_extended(sm2(B, i+j)))
                self.assertElementsEqual(x1, x3, (x1,x3,i,j))

    def test_orders(self):
        # the point (0,1) is the identity, and has order 1
        p0 = xform_affine_to_extended((0,1))
        # p0+p0=p0
        # p0+anything=anything

        # The point (0,-1) has order 2
        p2 = xform_affine_to_extended((0,-1))
        p3 = add_extended(p2, p2) # p3=p2+p2=p0
        p4 = add_extended(p3, p2) # p4=p3+p2=p2
        p5 = add_extended(p4, p2) # p5=p4+p2=p0
        self.assertBytesEqual(encodepoint(xform_extended_to_affine(p3)),
                              encodepoint(xform_extended_to_affine(p0)))
        self.assertBytesEqual(encodepoint(xform_extended_to_affine(p4)),
                              encodepoint(xform_extended_to_affine(p2)))
        self.assertBytesEqual(encodepoint(xform_extended_to_affine(p5)),
                              encodepoint(xform_extended_to_affine(p0)))

        # now same thing, but with Element
        p0 = _ElementOfUnknownGroup(xform_affine_to_extended((0,1)))
        self.assertElementsEqual(p0, Zero)
        p2 = _ElementOfUnknownGroup(xform_affine_to_extended((0,-1)))
        p3 = p2.add(p2)
        p4 = p3.add(p2)
        p5 = p4.add(p2)
        self.assertElementsEqual(p3, p0)
        self.assertElementsEqual(p4, p2)
        self.assertElementsEqual(p5, p0)

        # and again, with .scalarmult instead of .add
        p3 = p2._scalarmult_raw(2) # p3=2*p2=p0
        p4 = p2._scalarmult_raw(3) # p4=3*p2=p2
        p5 = p2._scalarmult_raw(4) # p5=4*p2=p0
        self.assertElementsEqual(p3, p0) # TODO: failing
        self.assertElementsEqual(p4, p2)
        self.assertElementsEqual(p5, p0)

    def test_add(self):
        e = []
        for i in range(100):
            seed = str(i).encode("ascii")
            s = Scalar.from_password(seed)
            e.append(Base.scalarmult(s))
        for i in range(100):
            x = random.choice(e)
            y = random.choice(e)

            sum1 = element_from_affine(
                slow_add_affine(xform_extended_to_affine(x.XYTZ),
                                xform_extended_to_affine(y.XYTZ)))
            sum2 = x.add(y)
            self.assertElementsEqual(sum1, sum2)
            if x != y:
                sum3 = Element(_add_extended_nonunfied(x.XYTZ, y.XYTZ))
                self.assertElementsEqual(sum1, sum3)

    def test_bad_group(self):
        b = encodepoint((0,-1%q)) # order 2
        self.assertRaises(ValueError, Element.from_bytes, b)

def element_from_affine(P):
    return Element(xform_affine_to_extended(P))
