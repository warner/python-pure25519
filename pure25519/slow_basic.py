
from pure25519.basic import (inv, d, q, l,
                             xform_extended_to_affine,
                             scalarmult_extended,
                             xform_affine_to_extended)

# Affine Coordinates: only here to compare against faster versions

def slow_add_affine(P,Q): # affine->affine
    # Complete: works even when P==Q. Slow: 50x slower than extended
    x1 = P[0]
    y1 = P[1]
    x2 = Q[0]
    y2 = Q[1]
    x3 = (x1*y2+x2*y1) * inv(1+d*x1*x2*y1*y2)
    y3 = (y1*y2+x1*x2) * inv(1-d*x1*x2*y1*y2)
    return (x3 % q,y3 % q)

def slow_scalarmult_affine(P,e): # affine->affine
    e = e % l
    if e == 0: return [0,1]
    Q = slow_scalarmult_affine(P,e//2)
    Q = slow_add_affine(Q,Q)
    if e & 1: Q = slow_add_affine(Q,P)
    return Q

# other functions that are only here for speed comparisons

def scalarmult_affine(pt, e): # affine->affine
    e = e % l
    return xform_extended_to_affine(
            scalarmult_extended(
             xform_affine_to_extended(pt),
            e))
