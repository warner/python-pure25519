
Q = 53 # = 4*13+1
# 29

def span(n):
    reached = []
    i = 1
    while True:
        if i in reached:
            return reached
        reached.append(i)
        i = (i * n) % Q

from collections import defaultdict
counts = defaultdict(set)
for n in range(1,Q):
    s = span(n)
    print "%2d (%2d): %s" % (n, len(s), s)
    counts[len(s)].add(n)

for size in sorted(counts):
    print "order=%d: %d elements" % (size, len(counts[size]))
    #if size == Q-1: print "(nevermind)"; continue
    for n in sorted(counts[size]):
        print " ", n, sorted(span(n)), (n*n)%Q

#for base in sorted(counts[13]):
#    print base, sorted(span(base))


# for any given size, there is exactly one subgroup of that size
