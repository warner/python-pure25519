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
        test = unittest.defaultTestLoader.loadTestsFromName("ed25519.test_ed25519")
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
                if x >= 0.2:
                    break
            return x / number

        def abbrev(t):
            if t > 1.0:
                return "%.3fs" % t
            if t > 1e-3:
                return "%.2fms" % (t*1e3)
            return "%.2fus" % (t*1e6)

        S1 = "import ed25519; msg=b'hello world'"
        S2 = "sk,vk = ed25519.create_keypair()"
        S3 = "sig = sk.sign(msg)"
        S4 = "vk.verify(sig, msg)"

        generate = do([S1], S2)
        sign = do([S1, S2], S3)
        verify = do([S1, S2, S3], S4)

        print("generate: %s" % abbrev(generate))
        print("sign: %s" % abbrev(sign))
        print("verify: %s" % abbrev(verify))

setup(name="pure25519",
      version="0", # not for publication
      description="pure-python curve25519/ed25519 routines",
      author="Brian Warner",
      author_email="warner-python-pure25519@lothar.com",
      license="MIT",
      url="https://github.com/warner/python-pure25519",
      packages=["ed25519"],
      package_dir={"ed25519": "ed25519"},
      cmdclass={"test": Test, "speed": Speed},
      )
