def sum(n):
    total = 0    
    
    for i in xrange(n+1):
        total += i
        
    return total

ns = [100, 1000, 10000, 100000, 1000000, 10000000, 100000000 ]

for n in ns:
    print "sum(%d): %d" % (n, sum(n))