exports.run = function(objectOrModule, context) {
    
    if (typeof objectOrModule === "string")
        objectOrModule = require(objectOrModule);
 
    if (!objectOrModule) throw "Nothing to run";
 
    var localContext = context || { passed : 0, failed : 0, error : 0 };

    var methodSetUp    = function() {}
    var methodTearDown = function() {}
    
    if (typeof objectOrModule.setUp === "function") {
        methodSetUp = objectOrModule.setUp
    }
    
    if (typeof objectOrModule.tearDown === "function") {
        methodTearDown = objectOrModule.tearDown
    }
    
    for (var property in objectOrModule) {
        
        if (property.match(/^test/)) {
            if (typeof objectOrModule[property] != "function") {
                exports.run(objectOrModule[property], localContext);
                continue
            }

            var methodTest = objectOrModule[property]
            
            var testObject = {}
            testObject["setUp"]    = methodSetUp
            testObject["tearDown"] = methodTearDown
            testObject[property]   = methodTest
            
            testObject.setUp()
            
            try {
                testObject[property]()
                localContext.passed++
            }
            catch (e) {
                if (e.name === "AssertionError") {
                    print("Assertion Failed in " + property + ": " + e)
                    localContext.failed++
                }
                else {
                    print("Exception in " + property + ": " + e)
                    localContext.error++
                }
            }
            finally {
                testObject.tearDown()
            }
       }
    }
    
    if (context === undefined) {
        print("Passed " + localContext.passed + "; Failed " + localContext.failed + "; Error " + localContext.error+";");
    }
}