obj SimpleObject {
    has name: str = "test";
    has value: int = 42;
    
    def greet() -> str {
        return f"Hello {self.name}";
    }
}

walker SimpleWalker {
    has message: str = "Hello World";
    
    can visit_simple with SimpleObject entry {
        print(f"Walker visited object: {here.name}");
        print(f"Walker message: {self.message}");
        print(f"Object value: {here.value}");
    }
}

with entry {
    # Create a simple graph
    obj = SimpleObject(name: "TestObject");
    root ++> obj;
    
    # Spawn walker
    walker = SimpleWalker(message: "Testing Jac");
    obj[0] spawn walker;
}
