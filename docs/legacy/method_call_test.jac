obj TestObject {
    has name: str;
    
    def test_method() -> str {
        return "test";
    }
    
    def test_dict() -> dict {
        patterns = {
            "result": self.test_method()
        };
        return patterns;
    }
}