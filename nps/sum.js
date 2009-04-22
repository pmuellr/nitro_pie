function sum(n) {
    total = 0    
    
    for (var i=0; i<n+1; i++) {
        total += i
    }
        
    return total
}

ns = [100, 1000, 10000, 100000, 1000000, 10000000, 100000000 ]

for (var i=0; i<ns.length; i++) {
    print("sum(", ns[i], "): ", sum(ns[i]))
}