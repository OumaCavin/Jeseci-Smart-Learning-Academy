obj SimpleUser {
    has user_id: str;
    has username: str;
    has age: int;
    has completed_modules: list;
    
    def check_access(module_id: str) -> bool {
        # Test various syntax patterns
        if self.age >= 18 {
            return true;
        }
        
        # Test list operations
        for item in self.completed_modules {
            if item == module_id {
                return true;
            }
        }
        
        return false;
    }
}