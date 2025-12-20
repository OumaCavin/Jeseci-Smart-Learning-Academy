# Simple standalone JAC test using print
walker test_orchestrator {
    has message: str = "Hello from JAC!";
    
    can test_method with root entry {
        print(self.message);
    }
}

with entry {
    walker = test_orchestrator();
    walker.test_method();
}