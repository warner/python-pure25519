import timeit

def do(setup_statements, statement):
    # extracted from timeit.py
    t = timeit.Timer(stmt=statement,
                     setup="\n".join(setup_statements))
    # determine number so that 0.2 <= total time < 2.0
    for i in range(1, 10):
        number = 10**i
        x = t.timeit(number)
        if x >= 0.5:
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
    S1 = "import os; from pure25519 import spake2; pw=b'pw'; A=b'idA'; B=b'idB'"
    S2 = "sdata_U,X_s = spake2.start_U(pw, os.urandom, A, B)"
    S3 = "sdata_V,Y_s = spake2.start_V(pw, os.urandom, A, B)"
    S4 = "k = spake2.finish_U(sdata_U,Y_s)"

    print("speed_spake2")
    p("start", [S1], S2)
    p("finish", [S1, S2, S3], S4)

    S1 = "import os; from pure25519 import spake2; pw=b'pw'"
    S2v1 = "sdata,X_s = spake2._start_v1(pw, os.urandom, spake2.U)"
    S2v2 = "sdata,X_s = spake2._start_v2(pw, os.urandom, spake2.U)"
    S2v3 = "sdata,X_s = spake2._start_v3(pw, os.urandom, spake2.U)"
    S2v4 = "sdata,X_s = spake2._start_v4(pw, os.urandom, spake2.U_e)"
    S3 = "sdata2,Y_s = spake2._start_v1(pw, os.urandom, spake2.V)"
    S4v1 = "Z = spake2._finish_v1(sdata, Y_s, spake2.V)"
    S4v2 = "Z = spake2._finish_v2(sdata, Y_s, spake2.V)"
    S4v3 = "Z = spake2._finish_v3(sdata, Y_s, spake2.V)"
    S4v4 = "Z = spake2._finish_v4(sdata, Y_s, spake2.V_e)"

    p("_start_v1", [S1], S2v1)
    p("_start_v2", [S1], S2v2)
    p("_start_v3", [S1], S2v3)
    p("_start_v4", [S1], S2v4)
    p("_finish_v1", [S1,S2v1,S3], S4v1)
    p("_finish_v2", [S1,S2v1,S3], S4v2)
    p("_finish_v3", [S1,S2v1,S3], S4v3)
    p("_finish_v4", [S1,S2v1,S3], S4v4)
