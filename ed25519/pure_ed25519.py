
# single-file pure-python ed25519 digital signatures, rearranged to minimize
# the namespace pollution so this can be embedded in another file. Adapted
# from https://bitbucket.org/dholth/ed25519ll


# Ed25519 digital signatures
# Based on http://ed25519.cr.yp.to/python/ed25519.py
# See also http://ed25519.cr.yp.to/software.html
# Adapted by Ron Garret
# Sped up considerably using coordinate transforms found on:
# http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html
# Specifically add-2008-hwcd-4 and dbl-2008-hwcd

# Can probably get some extra speedup here by replacing this with
# an extended-euclidean, but performance seems OK without that


import os

def create_signing_key():
    seed = os.urandom(32)
    return seed
def create_verifying_key(signing_key):
    return publickey(signing_key)

def sign(skbytes, msg):
    """Return just the signature, given the message and just the secret
    key."""
    if len(skbytes) != 32:
        raise ValueError("Bad signing key length %d" % len(skbytes))
    vkbytes = create_verifying_key(skbytes)
    sig = signature(msg, skbytes, vkbytes)
    return sig

def verify(vkbytes, sig, msg):
    if len(vkbytes) != 32:
        raise ValueError("Bad verifying key length %d" % len(vkbytes))
    if len(sig) != 64:
        raise ValueError("Bad signature length %d" % len(sig))
    rc = checkvalid(sig, msg, vkbytes)
    if not rc:
        raise ValueError("rc != 0", rc)
    return True

ed25519_create_signing_key = create_signing_key
ed25519_create_verifying_key = create_verifying_key
ed25519_sign = sign
ed25519_verify = verify

## sk = ed25519_create_signing_key()
## msg = "hello world"
## sig = ed25519_sign(sk, msg)
## assert len(sig) == 64
## vk = ed25519_create_verifying_key(sk)
## ed25519_verify(vk, sig, msg)
## print "ok"

