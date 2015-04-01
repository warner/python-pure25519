import unittest
from binascii import hexlify
from pure25519.basic import (l, B, arbitrary_element, encodepoint,
                             password_to_scalar,
                             add_affine,
                             scalarmult_affine, scalarmult_affine_2,
                             scalarmult_affine_to_extended,
                             xform_extended_to_affine)

class Basic(unittest.TestCase):
    def assertElementsEqual(self, e1, e2, msg=None):
        self.assertEqual(hexlify(encodepoint(e1)), hexlify(encodepoint(e2)),
                         msg)
    def assertBytesEqual(self, e1, e2, msg=None):
        self.assertEqual(hexlify(e1), hexlify(e2), msg)

    def test_arbitrary_element(self):
        for i in range(20):
            seed = str(i).encode("ascii")
            e = arbitrary_element(seed)
            e2 = arbitrary_element(seed)
            self.assertElementsEqual(e, e2)

    def test_password_to_scalar(self):
        for i in range(20):
            seed = str(i).encode("ascii")
            s = password_to_scalar(seed)
            s2 = password_to_scalar(seed)
            self.assertEqual(s, s2)

    def test_scalarmult(self):
        add = add_affine
        sm1 = scalarmult_affine
        sm2 = scalarmult_affine_2
        e0 = sm1(B, 0)
        self.assertElementsEqual(add(e0,e0), e0)
        e1 = sm1(B,1)
        self.assertElementsEqual(e1, B)
        self.assertElementsEqual(add(e0,e1), e1)
        self.assertElementsEqual(sm1(B, -5), sm1(B, -5 % l))
        self.assertElementsEqual(sm1(e0, 5), e0)
        e2 = sm1(B,2)
        self.assertElementsEqual(add(e1,e1), e2)
        e5 = sm1(B, 5)
        e10 = sm1(B, 10)
        e15 = sm1(B, 15)
        self.assertElementsEqual(add(e5, e5), e10)
        self.assertElementsEqual(add(e5, e10), e15)
        self.assertElementsEqual(sm1(e2, 5), e10)
        em5 = sm1(B, -5)
        self.assertElementsEqual(add(e15, em5), e10)
        self.assertElementsEqual(add(e5, em5), e0)

        e = {}
        for i in range(-50, 100):
            e[i] = sm1(B, i)
            self.assertElementsEqual(sm2(B, i), e[i])
            self.assertElementsEqual(xform_extended_to_affine(scalarmult_affine_to_extended(B, i)),
                                     e[i])

        for i in range(20,30):
            for j in range(-10,10):
                x1 = add(e[i], e[j])
                x2 = sm1(B, i+j)
                self.assertElementsEqual(x1, x2, (x1,x2,i,j))
                x3 = sm2(B, i+j)
                self.assertElementsEqual(x1, x3, (x1,x3,i,j))
