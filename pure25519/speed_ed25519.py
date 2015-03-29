import timeit

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

def run():
    S1 = "from pure25519 import ed25519_oop; msg=b'hello world'"
    S2 = "sk,vk = ed25519_oop.create_keypair()"
    S3 = "sig = sk.sign(msg)"
    S4 = "vk.verify(sig, msg)"

    p("generate", [S1], S2)
    p("sign", [S1, S2], S3)
    p("verify", [S1, S2, S3], S4)

    S1 = "from pure25519 import ed25519 as P"
    S2 = "h=P.Hint(b'')"

    p("Hint", [S1], S2)
