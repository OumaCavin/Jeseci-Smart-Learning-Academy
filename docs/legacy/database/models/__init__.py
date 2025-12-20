"""
Database models for the Jeseci Smart Learning Companion
SQLite-compatible models for development and testing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.database import Base

# Import SQLite-compatible models
from .sqlite_models import *

# Export all models for easy importing throughout the application
__all__ = [
    'Base',
    'User', 
    'UserLearningPreferences',
    'Concept', 
    'ConceptContent',
    'UserConceptProgress',      # Used in learning paths for progress calculation
    'UserContentProgress',      # Used in content management
    'LearningPath', 
    'LearningPathConcept',      # Used in learning paths for concept associations
    'LearningSession',          # Used in learning path tracking
    'UserProgress', 
    'Quiz', 
    'QuizAttempt', 
    'UserAchievement',
    'concept_relations'         # Association table for concept relationships
]