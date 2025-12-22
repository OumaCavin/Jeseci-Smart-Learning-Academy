obj SimpleUser {
    has user_id: str;
    has username: str;
    
    def get_info() -> str {
        return f"User {self.username} with ID {self.user_id}";
    }
}

export { SimpleUser };