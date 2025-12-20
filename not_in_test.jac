obj TestModule {
    has module_id: str;
    has prerequisites: list;
    
    def check_prerequisites(completed_modules: list) -> bool {
        for prereq in self.prerequisites {
            # This is the exact syntax that was failing
            if prereq not in completed_modules {
                return false;
            }
        }
        return true;
    }
}