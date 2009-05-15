assert = require("assert.js")
runner = require("jsunit.js")

if (!this.exports) {
    suite = require("jsunit_sample.js")
    runner.run(suite)
    exports = {}
}

exports.setUp = function() {
    print("in setUp()")
}

exports.tearDown = function() {
    print("in tearDown()")
}

exports.test_p = function() {
    assert.isTrue(true)
}

exports.test_f = function() {
    assert.isTrue(false)
}

exports.test_e = function() {
    throw "oops"
}

