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

b = 256 # =32*8
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

    def orig_decodepoint_sum(self, s):
        # the original. 802us.
        y = sum(2**i * bit(s,i) for i in range(0,b-1))
        #print("%064x" % y)
        return y

    def new_decodepoint_sum_1(self, s):
        # the range(0,b-1) means we don't use the MSB of the last byte, so
        # the high-order bit of the int will be zero. In this form, we clamp
        # the int. 337us
        unclamped = int(hexlify(s[:32][::-1]), 16)
        clamp = (1 << 255) - 1
        clamped = unclamped & clamp
        return clamped

    def new_decodepoint_sum_2(self, s):
        # In this form, we remap the last byte before conversion. 340us
        s = s[:32]
        clamped_byte = unhexlify("%02x" % (int(hexlify(s[-2:]), 16) & 0x7f))
        clamped_s = s[:-1] + clamped_byte
        clamped = int(hexlify(clamped_s[::-1]), 16)
        #print("%064x" % clamped)
        return clamped

    def test_decodepoint_sum(self):
        for i in range(200):
            #print()
            s = H(str(i).encode("ascii"))[:32]
            self.assertEqual(self.orig_decodepoint_sum(s),
                             self.new_decodepoint_sum_1(s))
            self.assertEqual(self.new_decodepoint_sum_1(s),
                             self.new_decodepoint_sum_2(s))

    def orig_decodeint(self, s):
        return sum(2**i * bit(s,i) for i in range(0,b))
    def new_decodeint(self, s):
        return int(hexlify(s[:32][::-1]), 16)

    def test_decodeint(self):
        for i in range(200):
            s = H(str(i).encode("ascii"))[:32]
            self.assertEqual(self.orig_decodeint(s),
                             self.new_decodeint(s))
