obj SimpleUser {
    has user_id: str;
    has username: str;
    
    def get_info() -> str {
        return "test";
    }
}