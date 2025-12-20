obj TestObject {
    has name: str;
    
    def analyze_patterns() -> dict {
        """
        Test docstring
        """
        patterns = {
            "preferred_study_times": "test",
            "optimal_session_duration": "test"
        };
        return patterns;
    }
}