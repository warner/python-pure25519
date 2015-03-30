from hashlib import sha256

# a,b random. X=G*a+U*pw. Y=G*b+V*pw. Z1=(Y-V*pw)*a. Z2=(X-U*pw)*b

if False:
    from pure25519.basic import (B, random_scalar, arbitrary_element,
                                 decodepoint, encodepoint, password_to_scalar,
                                 scalarmult_with_extended as scalarmult,
                                 add_affine)
    U = arbitrary_element(b"U")
    V = arbitrary_element(b"V")
    def _start(pw, entropy_f, U):
        a = random_scalar(entropy_f)
        pw_scalar = password_to_scalar(pw)
        X = add_affine(scalarmult(B, a), scalarmult(U, pw_scalar))
        X_s = encodepoint(X)
        return (a, pw_scalar), X_s

    def _finish(start_data, Y_s, V):
        (a, pw_scalar) = start_data
        Y = decodepoint(Y_s)
        Z = scalarmult(add_affine(Y, scalarmult(V, -pw_scalar)), a)
        return encodepoint(Z)

if False:
    from pure25519.basic import (B, random_scalar, arbitrary_element,
                                 decodepoint, encodepoint, password_to_scalar,
                                 xform_affine_to_extended, xform_extended_to_affine,
                                 scalarmult_extended, add_extended,
                                 )
    U = xform_affine_to_extended(arbitrary_element(b"U"))
    V = xform_affine_to_extended(arbitrary_element(b"V"))
    B_e = xform_affine_to_extended(B)
    def _start(pw, entropy_f, U):
        a = random_scalar(entropy_f)
        pw_scalar = password_to_scalar(pw)
        X = add_extended(scalarmult_extended(B_e, a),
                         scalarmult_extended(U, pw_scalar))
        X_s = encodepoint(xform_extended_to_affine(X))
        return (a, pw_scalar), X_s

    def _finish(start_data, Y_s, V):
        (a, pw_scalar) = start_data
        Y = xform_affine_to_extended(decodepoint(Y_s))
        Z = scalarmult_extended(add_extended(Y, scalarmult_extended(V, -pw_scalar)), a)
        return encodepoint(xform_extended_to_affine(Z))

if True:
    from pure25519.basic import (B, random_scalar, arbitrary_element,
                                 decodepoint, encodepoint, password_to_scalar,
                                 xform_affine_to_extended, xform_extended_to_affine,
                                 scalarmult_extended, scalarmult_2_extended, add_extended,
                                 )
    U = arbitrary_element(b"U")
    V = arbitrary_element(b"V")
    def _start(pw, entropy_f, U):
        a = random_scalar(entropy_f)
        pw_scalar = password_to_scalar(pw)
        X = add_extended(scalarmult_2_extended(B, a),
                         scalarmult_2_extended(U, pw_scalar))
        X_s = encodepoint(xform_extended_to_affine(X))
        return (a, pw_scalar), X_s

    def _finish(start_data, Y_s, V):
        (a, pw_scalar) = start_data
        Y = xform_affine_to_extended(decodepoint(Y_s))
        Z = scalarmult_extended(add_extended(Y,
                                             scalarmult_2_extended(V, -pw_scalar)),
                                a)
        return encodepoint(xform_extended_to_affine(Z))

if False:
    from pure25519.basic import (B, random_scalar, arbitrary_element,
                                 decodepoint, encodepoint, password_to_scalar,
                                 xform_affine_to_extended, xform_extended_to_affine,
                                 scalarmult_extended, scalarmult_2_extended, add_extended,
                                 )
    U = arbitrary_element(b"U")
    V = arbitrary_element(b"V")
    def _start(pw, entropy_f, U):
        a = random_scalar(entropy_f)
        pw_scalar = password_to_scalar(pw)
        X = add_extended(scalarmult_2_extended(B, a),
                         scalarmult_2_extended(U, pw_scalar))
        X_s = encodepoint(xform_extended_to_affine(X))
        return (a, pw_scalar), X_s

    def _finish(start_data, Y_s, V):
        (a, pw_scalar) = start_data
        Y = xform_affine_to_extended(decodepoint(Y_s))
        Z = scalarmult_2_extended(xform_extended_to_affine(add_extended(Y,
                                                                      scalarmult_2_extended(V, -pw_scalar))),
                                a)
        return encodepoint(xform_extended_to_affine(Z))


def start_U(pw, entropy_f, idA, idB, U=U, V=V):
    sdata, X_s = _start(pw, entropy_f, U)
    start_data = (sdata, pw, X_s, idA, idB, U, V)
    return start_data, X_s

def finish_U(start_data, Y_s):
    (sdata, pw, X_s, idA, idB, U, V) = start_data
    Z_s = _finish(sdata, Y_s, V)
    transcript = idA + idB + X_s + Y_s + Z_s + pw
    key = sha256(transcript).digest()
    return key


def start_V(pw, entropy_f, idA, idB, U=U, V=V):
    sdata, Y_s = _start(pw, entropy_f, V)
    start_data = (sdata, pw, Y_s, idA, idB, U, V)
    return start_data, Y_s

def finish_V(start_data, X_s):
    (sdata, pw, Y_s, idA, idB, U, V) = start_data
    Z_s = _finish(sdata, X_s, U)
    transcript = idA + idB + X_s + Y_s + Z_s + pw
    key = sha256(transcript).digest()
    return key

