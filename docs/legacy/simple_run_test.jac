# Simple JAC test file
print("Hello from JAC!");

walker TestWalker {
    def test_method() -> str {
        return "Walker test completed";
    }
}

with entry {
    print("Starting test execution");
    result = TestWalker.test_method();
    print(result);
    print("Test execution finished");
}