# Simple standalone JAC test using print
walker test_orchestrator {
    has message: str = "Hello from JAC!";
    
    can test_method with root entry {
        print(self.message);
    }
}

with entry {
    print("Starting test");
    print("Test completed");
}