from __future__ import print_function
import sys
import unittest
from binascii import hexlify, unhexlify
import hashlib

if sys.version_info[0] == 2:
    def bit(h, i):
        """Return i'th bit of bytestring h"""
        return (ord(h[i//8]) >> (i%8)) & 1
else:
    def bit(h, i):
        return (h[i//8] >> (i%8)) & 1

b = 256
def H(m):
    return hashlib.sha512(m).digest()

class Compare(unittest.TestCase):
    # I want to replace some very manual (and slow) loops with builtins.
    # These tests are to ensure that the replacements work the same way

    # Hint turns bytes into a 512-bit integer, little-endian (the first byte
    # of H(m) is used for the low-order 8 bits of the integer, with the LSB
    # of H(m)[0] used as the LSB of the integer).
    def orig_Hint(self, m):
        h = H(m)
        return sum(2**i * bit(h,i) for i in range(2*b))
    def new_Hint(self, m):
        h = H(m)
        return int(hexlify(h[::-1]), 16)
    def test_Hint(self):
        for i in range(200):
            m = str(i).encode("ascii")
            self.assertEqual(self.orig_Hint(m), self.new_Hint(m))
