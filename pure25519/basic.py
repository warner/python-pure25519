
b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493

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

# Affine Coordinates

def add_affine(P,Q): # complete
    x1 = P[0]
    y1 = P[1]
    x2 = Q[0]
    y2 = Q[1]
    x3 = (x1*y2+x2*y1) * inv(1+d*x1*x2*y1*y2)
    y3 = (y1*y2+x1*x2) * inv(1-d*x1*x2*y1*y2)
    return (x3 % q,y3 % q)

def scalarmult_affine(P,e):
    if e == 0: return [0,1]
    Q = scalarmult_affine(P,e/2)
    Q = add_affine(Q,Q)
    if e & 1: Q = add_affine(Q,P)
    return Q

# Extended Coordinates: x=X/Z, y=Y/Z, x*y=T/Z
# http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html

def xform_affine_to_extended(pt):
    (x, y) = pt
    return (x, y, 1, (x*y)%q) # (X,Y,Z,T)

def xform_extended_to_affine(pt):
    (x, y, z, _) = pt
    return ((x*inv(z))%q, (y*inv(z))%q)

def add_extended(pt1, pt2): # add-2008-hwcd-4 : NOT unified, only for pt1!=pt2
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

def double_extended(pt): # dbl-2008-hwcd
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

def xpt_mult (pt, n):
    if n==0: return xform_affine_to_extended((0,1))
    _ = double_extended(xpt_mult(pt, n>>1))
    return add_extended(_, pt) if n&1 else _

def scalarmult_with_extended(pt, e):
    return xform_extended_to_affine(xpt_mult(xform_affine_to_extended(pt), e))
