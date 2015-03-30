# python-pure25519

This contains a collection of pure-python functions to implement
Curve25519-based cryptography, including:

* Curve25519 Diffie-Hellman Key Agreement
* Ed25519 digital signatures
* SPAKE2 Password Authenticated Key Agreement

This code is mostly for research purposes: you almost certainly don't want to
use it for production. Use pynacl or python-ed25519 instead, which are python
bindings to djb's C implementations of Curve25519/Ed25519 (and the rest of
the NaCl suite).

Bad things about this module:

* much much slower than C
* not written by djb, so probably horribly buggy and insecure
* not constant-time

Good things about this module:

* can be used without a C compiler

## Sources


Adapted from https://bitbucket.org/dholth/ed25519ll

Based on http://ed25519.cr.yp.to/python/ed25519.py

See also http://ed25519.cr.yp.to/software.html

Adapted by Ron Garret

Sped up considerably using coordinate transforms found on:

http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html

Specifically add-2008-hwcd-4 and dbl-2008-hwcd
