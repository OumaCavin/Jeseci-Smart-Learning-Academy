# Simple test to verify JAC runtime works

print("Hello from JAC!");

obj SimpleTest {
    has message: str = "Test message";
    
    def get_message() -> str {
        return self.message;
    }
}

walker TestWalker {
    can test with SimpleTest entry {
        print(f"Walker message: {here.get_message()}");
    }
}

with entry {
    print("Starting JAC execution");
    test_obj = SimpleTest();
    root ++> test_obj;
    test_obj[0] spawn TestWalker();
    print("JAC execution completed");
}