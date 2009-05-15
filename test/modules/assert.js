var assert = exports
 
assert.isTrue = function(assertion, message) {
    if (assertion !== true) {
        message = message ? " : " + message : ""
        throw new AssertionError("Expected true, actually '" + assertion + "'" + message)
    }
}
 
assert.isEqual = function(expected, actual, message) {
    if (expected !== actual) {
        message = message ? " : " + message : ""
        throw new AssertionError("Expected '" + expected + "', actually '" + actual + "'" + message)
    }
}
 
assert.throwsError = function(block, type, message) {
    var threw     = false
    var exception = null
        
    try {
        block()
    } 
    catch (e) {
        threw     = true
        exception = e
    }
    
    message = message ? " : " + message : ""
    
    if (!threw) {
        throw new AssertionError("Expected exception" + message)
    }
    
    if (type !== undefined && !(exception instanceof type)) {
        throw new AssertionError("Expected exception type '" + type + "', actually '" + exception + "'" + message)
    }
}
 
 
assert.AssertionError = function(message) {
    this.name    = "AssertionError"
    this.message = message
}
 
assert.AssertionError.prototype = new Error()

var AssertionError = assert.AssertionError