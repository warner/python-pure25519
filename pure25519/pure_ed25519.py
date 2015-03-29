
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

