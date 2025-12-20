"""
Simple JAC Learning Portal Example
Basic demonstration of JAC serve functionality
"""

# Basic node definition
node LearningConcept {
    has concept_id: str;
    has title: str;
    has description: str;
    has difficulty_level: int = 1;
    
    def get_info {
        return {
            "id": self.concept_id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty_level
        };
    }
}

# Simple walker for API endpoints
walker hello_world {
    can hello with root entry {
        report {
            "message": "Welcome to Jeseci Smart Learning Academy!",
            "status": "success",
            "timestamp": "2025-12-20T22:37:55Z"
        };
    }
}

# Get learning concepts
walker get_concepts {
    can get_concepts with root entry {
        concepts = [];
        
        # Create sample concepts
        basic_concept = LearningConcept(
            concept_id="jac_basics",
            title="JAC Language Basics",
            description="Introduction to JAC programming",
            difficulty_level=1
        );
        
        advanced_concept = LearningConcept(
            concept_id="jac_advanced",
            title="Advanced JAC Programming",
            description="Complex JAC concepts and patterns",
            difficulty_level=3
        );
        
        root ++> basic_concept;
        root ++> advanced_concept;
        
        # Get all concepts from graph (simplified for now)
        # all_concepts = [root --> (?LearningConcept)];
        
        # For demonstration, use the concepts we created
        concepts.append(basic_concept.get_info());
        concepts.append(advanced_concept.get_info());
        
        report {
            "concepts": concepts,
            "total_count": len(concepts),
            "status": "success"
        };
    }
}

# Health check endpoint
walker health_check {
    can health_check with root entry {
        report {
            "service": "Jeseci Smart Learning Academy",
            "status": "healthy",
            "version": "1.0.0",
            "architecture": "Pure JAC",
            "timestamp": "2025-12-20T22:37:55Z"
        };
    }
}