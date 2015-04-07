import unittest
from binascii import hexlify
from pure25519.basic import Zero, _ElementOfUnknownGroup
from pure25519.basic import xform_affine_to_extended, l

ORDERS = {1: "1", 2: "2", 4: "4", 8: "8",
          1*l: "1*L", 2*l: "2*L", 4*l: "4*L", 8*l: "8*L"}
def get_order(e):
    for o in sorted(ORDERS):
        if e._scalarmult_raw(o) == Zero:
            return o

class Orders(unittest.TestCase):
    def assertElementsEqual(self, e1, e2, msg=None):
        self.assertEqual(hexlify(e1.to_bytes()), hexlify(e2.to_bytes()),
                         msg)

    def collect(self, e):
        values = set()
        for i in range(400):
            values.add(e.scalarmult(i).to_bytes())
        return values

    def test_orders(self):
        # all points should have an order that's listed in ORDERS. Test some
        # specific points.

        p0 = Zero
        values = self.collect(p0)
        self.assertEqual(len(values), 1)
        self.assertEqual(values, set([Zero.to_bytes()]))

        # (0,-1) should be order 2
        p1 = _ElementOfUnknownGroup(xform_affine_to_extended((0,-1)))
        values = self.collect(p1)
        self.assertEqual(len(values), 2)
        self.assertEqual(values, set([Zero.to_bytes(), p1.to_bytes()]))

