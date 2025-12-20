"""
Pages Index
Export all page components
"""

# Import all pages
import "./dashboard" as dashboard;
import "./concepts" as concepts;
import "./learning_paths" as learning_paths;
import "./progress" as progress;

# Export page components
DashboardPage = dashboard.DashboardPage;
ConceptsPage = concepts.ConceptsPage;
LearningPathsPage = learning_paths.LearningPathsPage;
ProgressPage = progress.ProgressPage;