# Test JAC Client syntax - Step 2: Add components

# Backend walker
walker test_walker {
    can test with `root entry {
        report {"message": "Backend test"};
    }
}

# Frontend client with multiple components
cl import from react { useState } cl {
    # Simple variable assignment
    appTitle = "Learning Portal";
    
    def app() -> any {
        return <div><h1>{appTitle}</h1></div>;
    }
}

with entry {
    print("Test application ready");
}