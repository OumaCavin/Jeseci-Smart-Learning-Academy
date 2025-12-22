"""
Jeseci Smart Learning Academy - Architecture Information
========================================================

This module contains architecture metadata and configuration information
for the Jeseci Smart Learning Academy platform.

Architecture: Object-Spatial Programming with JSX
Version: 5.0.0
Author: Cavin Otieno
Date: December 22, 2025

Framework: Jaclang 0.9.3
Backend: Pure Jaclang with OpenAI Integration
Frontend: Native JSX implementation (no external React dependencies)
"""

# Architecture Configuration
ARCHITECTURE_CONFIG = {
    "name": "Jeseci Smart Learning Academy",
    "version": "5.0.0",
    "architecture": "Object-Spatial Programming with JSX",
    "framework": "Jaclang 0.9.3",
    "backend_type": "Pure Jaclang with OpenAI Integration",
    "frontend_type": "Native JSX (no external React)",
    "author": "Cavin Otieno",
    "created_date": "2025-12-22"
}

# Architecture Benefits
ARCHITECTURE_BENEFITS = [
    "Single language (Jaclang)",
    "No external React dependencies",
    "Native JSX implementation",
    "Built-in authentication",
    "Native backend communication",
    "Zero configuration build"
]

# Technology Stack
TECHNOLOGY_STACK = {
    "language": "Jaclang",
    "framework_version": "0.9.3",
    "programming_paradigm": "Object-Spatial Programming",
    "frontend_rendering": "Native JSX",
    "ai_integration": "OpenAI"
}

def get_architecture_info() -> dict:
    """
    Returns comprehensive architecture information.
    
    Returns:
        Dictionary containing architecture metadata
    """
    return {
        "config": ARCHITECTURE_CONFIG,
        "benefits": ARCHITECTURE_BENEFITS,
        "technology_stack": TECHNOLOGY_STACK
    }

def get_version_info() -> dict:
    """
    Returns version and framework information.
    
    Returns:
        Dictionary containing version details
    """
    return {
        "version": ARCHITECTURE_CONFIG["version"],
        "framework": ARCHITECTURE_CONFIG["framework"],
        "architecture": ARCHITECTURE_CONFIG["architecture"]
    }
