# Simple standalone JAC test
walker test_orchestrator {
    has message: str = "Hello from JAC!";
    
    can test_method with root entry {
        report {"status": "success", "message": self.message};
    }
}

with entry {
    walker = test_orchestrator();
    walker.test_method();
}