from pure25519.basic import l, Element, Zero
import os, collections

ORDERS = {1: "1", 2: "2", 4: "4", 8: "8",
          1*l: "1*L", 2*l: "2*L", 4*l: "4*L", 8*l: "8*L"}
def get_order(e):
    for o in sorted(ORDERS):
        if e._scalarmult_raw(o) == Zero:
            return o

TRIALS = 1000
orderbins = collections.defaultdict(int)
def test(multipler):
    count = 0
    for i in range(TRIALS):
        e = Element.arbitrary(os.urandom(8))
        orderbins[get_order(e)] += 1
        f = e.scalarmult(multipler)
        if f._scalarmult_raw(l) == Zero:
            count += 1
    return 1.0 * count / TRIALS

print "fraction of good-order points after multiplier"
print 1, test(1) # 13%
print 2, test(2) # 25%
print 4, test(4) # 50%
print 8, test(8) # 100%

print "bins:"
for o in sorted(orderbins):
    print ORDERS[o], orderbins[o]


# over 4000 trials, we see about 500 elements of order 1*L, 500 of 2*L, 1000
# of 4*L, and 2000 of 8*L
