obj Test {
    has name: str;
}

walker BasicWalker {
    can test with Test entry {
        print("Hello");
    }
}

with entry {
    obj = Test(name: "test");
    root ++> obj;
    obj[0] spawn BasicWalker();
}
