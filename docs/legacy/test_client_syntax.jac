# Test JAC Client syntax

# Backend walker
walker test_walker {
    can test with `root entry {
        report {"message": "Backend test"};
    }
}

# Frontend client
cl import from react { useState } cl {
    def app() -> any {
        return <div><h1>Hello from JAC Client!</h1></div>;
    }
}

with entry {
    print("Test application ready");
}