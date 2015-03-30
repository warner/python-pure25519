import os, unittest
from binascii import hexlify
from pure25519.spake2 import start_U, finish_U, start_V, finish_V

class SPAKE2(unittest.TestCase):
    def assertBytesEqual(self, e1, e2):
        self.assertEqual(hexlify(e1), hexlify(e2))

    def test_success(self):
        print
        pw = b"password"
        sd_U,X = start_U(pw, os.urandom, b"idA", b"idB")
        sd_V,Y = start_V(pw, os.urandom, b"idA", b"idB")
        K1 = finish_U(sd_U,Y)
        K2 = finish_V(sd_V,X)
        self.assertBytesEqual(K1, K2)

    def test_failure(self):
        sd_U,X = start_U(b"password", os.urandom, b"idA", b"idB")
        sd_V,Y = start_V(b"wrong", os.urandom, b"idA", b"idB")
        K1 = finish_U(sd_U,Y)
        K2 = finish_V(sd_V,X)
        self.assertNotEqual(hexlify(K1), hexlify(K2))
