#!/usr/bin/env python

from __future__ import print_function
import sys, unittest, timeit
from distutils.core import setup, Command

class Test(Command):
    description = "run tests"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        test = unittest.defaultTestLoader.discover("ed25519")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(test)
        sys.exit(not result.wasSuccessful())

class KnownAnswerTest(Test):
    description = "run known-answer-tests"
    def run(self):
        test = unittest.defaultTestLoader.loadTestsFromName("ed25519.do_ed25519_kat")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(test)
        sys.exit(not result.wasSuccessful())

class Speed(Test):
    description = "run benchmark suite"
    def run(self):
        def do(setup_statements, statement):
            # extracted from timeit.py
            t = timeit.Timer(stmt=statement,
                             setup="\n".join(setup_statements))
            # determine number so that 0.2 <= total time < 2.0
            for i in range(1, 10):
                number = 10**i
                x = t.timeit(number)
                if x >= 1.0:
                    break
            return x / number

        def abbrev(t):
            if t > 1.0:
                return "%.3fs" % t
            if t > 1e-3:
                return "%.2fms" % (t*1e3)
            return "%.2fus" % (t*1e6)

        def p(name, setup_statements, statements):
            t = sorted([do(setup_statements, statements) for i in range(3)])
            print("%12s: %s (%s)" % (name,
                                     abbrev(min(t)),
                                     " ".join([abbrev(s) for s in t])))

        S1 = "import ed25519; msg=b'hello world'"
        S2 = "sk,vk = ed25519.create_keypair()"
        S3 = "sig = sk.sign(msg)"
        S4 = "vk.verify(sig, msg)"

        p("generate", [S1], S2)
        p("sign", [S1, S2], S3)
        p("verify", [S1, S2, S3], S4)

        # speedup opportunities:
        #  bits-to-int (implemented with sum(2**i*bit(h,i) for in in range())
        #    0.5ms for range(b), 1.0ms for range(2*b)
        #    replace with int("%x"%bits,16)
        #    plus/minus some bitshifts
        #    maybe save 3ms here
        #  redundant xform
        #    R+Ah calc does pt_xform(scalarmult(A,h))
        #    but scalarmult = pt_unxform(xpt_mult(pt_xform(pt),e))
        #    can remove the pt_xform(pt_unxform()) pair
        #    save 1ms here
        #  v1==v2 works on untransformed values
        #    can we leave them transformed? 2ms to save
        #    probably not: Z will be different
        #    maybe there's a way to compare extended coords quickly
        #    can you add the points together and compare to 0?
        #  expmod() should be pow()
        #    reduces xrecover() from 1.9ms to 0.33
        #    reduces decodepoint from 2.35 to 0.8
        #    reduces pt_unxform from 1.03 to 0.040, via inv()
        #    reduces scalarmult from 6.67 to 5.5, via pt_unxform()
        #    probably 6.2ms just with this
        #
        # so 6.2m from expmod->pow, 2ms from bits2int
        # should improve verf from 21.8 to ~15.6
        # Actually yields 12.1ms, sweet.

        # sign: 14.46ms
        # verify: 21.78ms
        #  decodepoint  2.35  ms (0.48 bits2int, 1.93 xrecover, <.002 oncurve)
        #  decodepoint  2.35  ms
        #  decodeint    0.468
        #  encodepoint  0.168
        #  Hint()       1.08  (0.019 is the hash, rest is bits2int)
        #  scalarmult   6.67
        #  R+Ah:        7.71
        #   scalarmult   6.67
        #   pt_xform     0.00082
        #   pt_xform     0.00082
        #   xpt_add      0.00357
        #   pt_unxform   1.03
        #
        # xrecover: 1.90 ms

        # as of 5f98321, xrecover takes 326us
        #  of which 160us is the inv()
        #  and another 160us is the pow()
        #  so the next step to reduce that is to implement the
        #  extended-euclidean algorithm suggested in the comment
        #  used once in xrecover, twice in pt_unxform
        #  so 5 total, maybe 900us on the table

        # remaining sum():
        #  encodeint()
        #  encodepoint()
        #  publickey()
        #  signature()

        S1 = "from ed25519.pure_ed25519 import export"
        S2 = "s=export['publickey'](b'')"
        S3 = "p=export['decodepoint'](s)"
        S4 = r"i = b'\xff'*32"
        S5 = "si=export['decodeint'](i)"
        S6 = "h=export['Hint'](b'')"
        S7 = "Ah=export['scalarmult'](p,h)"
        S8 = "Ahx=export['pt_xform'](Ah)"
        S9 = "export['xpt_add'](Ahx,Ahx)"
        S10 = "export['pt_unxform'](Ahx)"
        S11 = "S=export['encodepoint'](p)"
        S12 = "export['xrecover'](export['Bx'])"
        S13 = "export['isoncurve'](p)"
        S14 = "export['encodeint'](si)"

        p("decodepoint", [S1, S2], S3)
        p("decodeint", [S1, S4], S5)
        p("scalarmult", [S1,S2,S3,S6], S7)
        p("pt_xform", [S1,S2,S3,S6,S7], S8)
        p("xpt_add", [S1,S2,S3,S6,S7,S8], S9)
        p("pt_unxform", [S1,S2,S3,S6,S7,S8], S10)
        p("encodepoint", [S1,S2,S3], S11)
        p("encodeint", [S1,S4,S5], S14)
        p("Hint", [S1], S6)
        p("xrecover", [S1], S12)
        p("isoncurve", [S1, S2, S3], S13)

setup(name="pure25519",
      version="0", # not for publication
      description="pure-python curve25519/ed25519 routines",
      author="Brian Warner",
      author_email="warner-python-pure25519@lothar.com",
      license="MIT",
      url="https://github.com/warner/python-pure25519",
      packages=["ed25519"],
      package_dir={"ed25519": "ed25519"},
      cmdclass={"test": Test, "speed": Speed, "test_kat": KnownAnswerTest},
      )
