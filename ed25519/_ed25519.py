from . import pure_ed25519 as _raw

class BadSignatureError(Exception):
    pass

SECRETKEYBYTES = 64
PUBLICKEYBYTES = 32
SIGNATUREKEYBYTES = 64

def publickey(seed32):
    assert len(seed32) == 32
    vk32 = _raw.ed25519_create_verifying_key(seed32)
    return vk32, seed32+vk32
def sign(msg, skvk):
    assert len(skvk) == 64
    sk = skvk[:32]
    sig = _raw.ed25519_sign(sk, msg)
    return sig+msg
def open(sigmsg, vk):
    assert len(vk) == 32
    sig = sigmsg[:64]
    msg = sigmsg[64:]
    try:
        _raw.ed25519_verify(vk, sig, msg)
    except ValueError as e:
        raise BadSignatureError(e)
    except Exception as e:
        if str(e) == "decoding point that is not on curve":
            raise BadSignatureError(e)
        raise
    return msg
