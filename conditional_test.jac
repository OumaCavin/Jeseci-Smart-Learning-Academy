obj SimpleUser {
    has user_id: str;
    has username: str;
    has age: int;
    
    def get_status() -> str {
        if self.age >= 18 {
            return "adult";
        } else {
            return "minor";
        }
    }
}