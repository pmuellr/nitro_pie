// print("Hello", " ", "World", "!")

print("")
print("globals:")
for (var key in this) {
    print("   " + key + ": " + this[key])
}

print("")
print("arguments:")
for (var i=0; i<arguments.length; i++) {
    print("   " + i + ": " + arguments[i])
}

print("")
print("environment:")
for (var key in environment) {
    var val = environment[key]
    print("   " + key + ": " + val)
}