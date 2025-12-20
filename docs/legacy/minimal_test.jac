obj Test {
    has name: str;
}

walker BasicWalker {
    can test with Test entry {
        print("Hello");
    }
}
