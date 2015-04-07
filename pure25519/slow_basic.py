
from pure25519.basic import (inv, d, q, L,
                             xform_extended_to_affine,
                             scalarmult_extended,
                             xform_affine_to_extended,
                             double_extended, _add_extended_nonunfied)

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
    e = e % L
    if e == 0: return [0,1]
    Q = slow_scalarmult_affine(P,e//2)
    Q = slow_add_affine(Q,Q)
    if e & 1: Q = slow_add_affine(Q,P)
    return Q

# other functions that are only here for speed comparisons

def scalarmult_affine(pt, e): # affine->affine
    e = e % L
    return xform_extended_to_affine(
            scalarmult_extended(
             xform_affine_to_extended(pt),
            e))

def scalarmult_affine_to_extended(pt, n): # affine->extended
    assert len(pt) == 2 # affine
    n = n % L
    if n==0: return xform_affine_to_extended((0,1))
    xpt = xform_affine_to_extended(pt) # so Z=1
    return _scalarmult_affine_to_extended_inner(xpt, n)

def _scalarmult_affine_to_extended_inner(xpt, n):
    if n==0: return xform_affine_to_extended((0,1))
    _ = double_extended(_scalarmult_affine_to_extended_inner(xpt, n>>1))
    return _add_extended_nonunfied(_, xpt) if n&1 else _
