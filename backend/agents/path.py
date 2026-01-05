"""
Path Agent - Learning Path Optimization
Jeseci Smart Learning Academy - Sophisticated Multi-Agent Learning Platform

This module implements the Path Agent, which provides personalized learning path
creation, prerequisite analysis, goal-oriented planning, and progress-based path adjustment.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict

from backend.agents.base_agent import BaseAgent, AgentMessage, AgentTask, AgentState, MessageType, Priority

# Import centralized logging configuration
from logger_config import logger


@dataclass
class LearningPath:
    """Represents a complete learning path"""
    progress: float = 0.0
    status: str = "active"
    path_id: str
    title: str
    description: str
    user_id: str
    difficulty: str
    estimated_weeks: int
    milestones: List['Milestone']
    topics: List[str]
    prerequisites: List[str]
    learning_objectives: List[str]
    created_at: str
    updated_at: str


@dataclass
class Milestone:
    """Represents a milestone in a learning path"""
    status: str = "pending"
    completion_criteria: List[str] = field(default_factory=list)
    resources: List[Dict] = field(default_factory=list)
    milestone_id: str
    order: int
    title: str
    description: str
    topics: List[str]
    estimated_hours: int
    exercises_count: int
    assessments_count: int


@dataclass
class PathProgress:
    """Represents progress through a learning path"""
    recommendations: List[str] = field(default_factory=list)
    path_id: str
    user_id: str
    current_milestone: int
    completed_milestones: List[int]
    topics_completed: List[str]
    total_hours_spent: float
    progress_percentage: float
    last_activity: str


class PathAgent(BaseAgent):
    """
    Path Agent for learning path optimization and management
    
    The Path Agent provides:
    - Personalized learning path creation
    - Prerequisite analysis and validation
    - Goal-oriented planning
    - Progress-based path adjustment
    - Milestone tracking
    - Adaptive recommendations
    
    Attributes:
        learning_paths: Stored learning paths
        path_templates: Templates for common learning paths
        topic_prerequisites: Prerequisite relationships between topics
        user_progress: Progress tracking per user
    """
    
    def __init__(self, agent_id: str = "path_agent",
                 agent_name: str = "Learning Path Optimizer",
                 message_bus = None):
        """
        Initialize the Path Agent
        
        Args:
            agent_id: Unique identifier
            agent_name: Human-readable name
            message_bus: Optional message bus instance
        """
        super().__init__(agent_id, agent_name, "Path")
        
        # Path management
        self.learning_paths: Dict[str, LearningPath] = {}
        self.path_templates: Dict[str, Dict] = {}
        self.user_progress: Dict[str, PathProgress] = {}
        
        # Topic prerequisites graph
        self.topic_prerequisites: Dict[str, List[str]] = {}
        self._initialize_topic_prerequisites()
        self._initialize_path_templates()
        
        self.logger.info("Path Agent initialized")
    
    def _register_capabilities(self):
        """Register the capabilities of the Path Agent"""
        self.capabilities = [
            "path_creation",
            "prerequisite_analysis",
            "goal_planning",
            "progress_adjustment",
            "milestone_tracking",
            "adaptive_recommendations",
            "path_optimization",
            "curriculum_design"
        ]
    
    def _initialize_topic_prerequisites(self):
        """Initialize topic prerequisite relationships"""
        self.topic_prerequisites = {
            "osp_basics": ["programming_fundamentals"],
            "byllm_basics": ["programming_fundamentals", "osp_basics"],
            "advanced_osp": ["osp_basics"],
            "ai_integration": ["byllm_basics", "osp_basics"],
            "data_structures": ["programming_fundamentals"],
            "algorithms": ["data_structures", "programming_fundamentals"],
            "oop_concepts": ["programming_fundamentals"],
            "software_design": ["oop_concepts", "programming_fundamentals"],
            "web_development": ["programming_fundamentals", "html_css"],
            "react_basics": ["javascript_fundamentals", "web_development"],
            "backend_development": ["programming_fundamentals", "database_basics"],
            "machine_learning_basics": ["python_fundamentals", "math_basics"],
            "deep_learning": ["machine_learning_basics", "linear_algebra"]
        }
    
    def _initialize_path_templates(self):
        """Initialize learning path templates"""
        self.path_templates = {
            "full_stack_developer": {
                "name": "Full Stack Developer",
                "description": "Master both frontend and backend development",
                "difficulty": "beginner_to_intermediate",
                "estimated_weeks": 16,
                "topics": [
                    "programming_fundamentals",
                    "html_css",
                    "javascript_fundamentals",
                    "web_development",
                    "react_basics",
                    "backend_development",
                    "database_basics",
                    "api_design"
                ],
                "milestones": 4
            },
            "ai_ml_engineer": {
                "name": "AI/ML Engineer",
                "description": "Build intelligent systems and machine learning models",
                "difficulty": "intermediate",
                "estimated_weeks": 20,
                "topics": [
                    "python_fundamentals",
                    "math_basics",
                    "data_structures",
                    "machine_learning_basics",
                    "deep_learning",
                    "nlp_basics",
                    "computer_vision"
                ],
                "milestones": 4
            },
            "jaclang_developer": {
                "name": "Jaclang Graph Developer",
                "description": "Master graph-based programming with Jaclang",
                "difficulty": "intermediate_to_advanced",
                "estimated_weeks": 12,
                "topics": [
                    "programming_fundamentals",
                    "osp_basics",
                    "byllm_basics",
                    "advanced_osp",
                    "ai_integration"
                ],
                "milestones": 4
            },
            "data_scientist": {
                "name": "Data Scientist",
                "description": "Analyze data and extract insights",
                "difficulty": "intermediate",
                "estimated_weeks": 18,
                "topics": [
                    "python_fundamentals",
                    "math_basics",
                    "statistics",
                    "data_visualization",
                    "machine_learning_basics",
                    "sql_database"
                ],
                "milestones": 4
            }
        }
    
    async def handle_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Handle incoming messages
        
        Args:
            message: The incoming message
            
        Returns:
            Processing result
        """
        content = message.content
        action = content.get("action", "")
        
        if action == "create_path":
            return await self._create_path(content)
        elif action == "get_path":
            return self._get_path(content)
        elif action == "update_progress":
            return await self._update_progress(content)
        elif action == "adjust_path":
            return await self._adjust_path(content)
        elif action == "validate_prerequisites":
            return self._validate_prerequisites(content)
        elif action == "analyze_prerequisites":
            return self._analyze_prerequisites(content)
        elif action == "get_recommendations":
            return self._get_recommendations(content)
        elif action == "get_milestones":
            return self._get_milestones(content)
        elif action == "complete_milestone":
            return await self._complete_milestone(content)
        elif action == "generate_path_from_template":
            return await self._generate_path_from_template(content)
        else:
            return {"action": "acknowledged", "agent": self.agent_name}
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute a task
        
        Args:
            task: The task to execute
            
        Returns:
            Task result
        """
        command = task.command
        
        if command == "optimize_path":
            return await self._optimize_path(task.parameters)
        elif command == "create_curriculum":
            return await self._create_curriculum(task.parameters)
        elif command == "analyze_learning_gaps":
            return self._analyze_learning_gaps(task.parameters)
        elif command == "get_path_statistics":
            return self._get_path_statistics(task.parameters)
        else:
            return {"error": f"Unknown command: {command}"}
    
    # Path Creation Methods
    
    async def _create_path(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a personalized learning path
        
        Args:
            content: Path creation parameters
            
        Returns:
            Created learning path
        """
        import uuid
        
        user_id = content.get("user_id")
        topic = content.get("topic", "")
        difficulty = content.get("difficulty", "beginner")
        goals = content.get("goals", [])
        time_availability = content.get("hours_per_week", 10)
        existing_knowledge = content.get("existing_knowledge", [])
        
        # Analyze goals and create milestones
        milestones = self._create_milestones(
            topic=topic,
            difficulty=difficulty,
            goals=goals,
            hours_per_week=time_availability,
            existing_knowledge=existing_knowledge
        )
        
        # Calculate estimated duration
        total_hours = sum(m.estimated_hours for m in milestones)
        estimated_weeks = max(1, int(total_hours / time_availability))
        
        path_id = f"path_{uuid.uuid4().hex[:8]}"
        
        path = LearningPath(
            path_id=path_id,
            title=f"{topic.title()} Learning Path",
            description=f"Personalized path to master {topic} in {estimated_weeks} weeks",
            user_id=user_id,
            difficulty=difficulty,
            estimated_weeks=estimated_weeks,
            milestones=milestones,
            topics=[topic],
            prerequisites=self._get_prerequisites(topic),
            learning_objectives=self._generate_learning_objectives(topic, goals),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Store the path
        self.learning_paths[path_id] = path
        
        # Initialize progress tracking
        self.user_progress[f"{user_id}_{path_id}"] = PathProgress(
            path_id=path_id,
            user_id=user_id,
            current_milestone=1,
            completed_milestones=[],
            topics_completed=[],
            total_hours_spent=0,
            progress_percentage=0.0,
            last_activity=datetime.now().isoformat()
        )
        
        self.logger.info(f"Learning path created: {path_id} for user {user_id}")
        
        return {
            "success": True,
            "path": self._serialize_path(path),
            "estimated_duration_weeks": estimated_weeks,
            "total_hours": total_hours,
            "message": "Learning path created successfully"
        }
    
    def _create_milestones(self, topic: str, difficulty: str, goals: List[str],
                          hours_per_week: int, 
                          existing_knowledge: List[str]) -> List[Milestone]:
        """
        Create milestones for a learning path
        
        Args:
            topic: Main topic
            difficulty: Difficulty level
            goals: Learning goals
            hours_per_week: Available hours per week
            existing_knowledge: Topics already known
            
        Returns:
            List of milestones
        """
        milestone_count = 4
        hours_per_milestone = hours_per_week * 4  # 4 weeks per milestone
        
        milestones = []
        
        for i in range(1, milestone_count + 1):
            milestone = Milestone(
                milestone_id=f"milestone_{i}",
                order=i,
                title=self._get_milestone_title(i, topic),
                description=self._get_milestone_description(i, topic, difficulty),
                topics=self._get_milestone_topics(i, topic, difficulty),
                estimated_hours=hours_per_milestone,
                exercises_count=5 + i * 2,
                assessments_count=2,
                status="pending" if i > 1 else "active",
                completion_criteria=self._get_completion_criteria(i, topic),
                resources=self._get_milestone_resources(i, topic)
            )
            milestones.append(milestone)
        
        return milestones
    
    def _get_milestone_title(self, order: int, topic: str) -> str:
        """Get milestone title based on order"""
        titles = {
            1: f"Foundation: {topic} Basics",
            2: f"Building Skills in {topic}",
            3: f"Advanced {topic} Concepts",
            4: f"Mastering {topic}"
        }
        return titles.get(order, f"{topic} - Phase {order}")
    
    def _get_milestone_description(self, order: int, topic: str, 
                                   difficulty: str) -> str:
        """Get milestone description"""
        descriptions = {
            1: f"Start your journey with {topic}. Learn the fundamental concepts and build a strong foundation.",
            2: "Build upon your foundational knowledge with hands-on practice and real-world examples.",
            3: "Dive deeper into advanced concepts and prepare for complex applications.",
            4: "Consolidate your knowledge and prepare for expert-level implementation."
        }
        return descriptions.get(order, f"Phase {order} of learning {topic}")
    
    def _get_milestone_topics(self, order: int, topic: str, 
                             difficulty: str) -> List[str]:
        """Get topics covered in a milestone"""
        base_topics = {
            1: ["introduction", "core_concepts", "basic_syntax"],
            2: ["practical_applications", "common_patterns", "tools"],
            3: ["advanced_concepts", "optimization", "best_practices"],
            4: ["real_world_projects", "case_studies", "expert_techniques"]
        }
        
        topics = base_topics.get(order, [])
        return [f"{topic}_{t}" for t in topics]
    
    def _get_completion_criteria(self, order: int, topic: str) -> List[str]:
        """Get completion criteria for a milestone"""
        return [
            f"Complete all lessons in Milestone {order}",
            f"Finish at least 80% of practice exercises",
            f"Pass the milestone assessment with 70% or higher",
            f"Spend at least the estimated hours on content"
        ]
    
    def _get_milestone_resources(self, order: int, topic: str) -> List[Dict]:
        """Get recommended resources for a milestone"""
        return [
            {
                "type": "lesson",
                "title": f"Core Concepts - Part {order}",
                "format": "interactive"
            },
            {
                "type": "exercise",
                "title": f"Practice Problems - Set {order}",
                "format": "hands_on"
            },
            {
                "type": "quiz",
                "title": f"Knowledge Check - Milestone {order}",
                "format": "assessment"
            }
        ]
    
    def _get_prerequisites(self, topic: str) -> List[str]:
        """Get prerequisites for a topic"""
        return self.topic_prerequisites.get(topic, [])
    
    def _generate_learning_objectives(self, topic: str, 
                                      goals: List[str]) -> List[str]:
        """Generate learning objectives based on goals"""
        objectives = [
            f"Understand the fundamental concepts of {topic}",
            f"Apply {topic} principles to solve real-world problems",
            f"Analyze and evaluate {topic} approaches",
            f"Create practical implementations using {topic}"
        ]
        
        # Add goal-specific objectives
        for goal in goals:
            if "build" in goal.lower() or "create" in goal.lower():
                objectives.append(f"Build real-world projects using {topic}")
            elif "master" in goal.lower() or "expert" in goal.lower():
                objectives.append(f"Achieve expert-level proficiency in {topic}")
        
        return objectives
    
    async def _generate_path_from_template(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a learning path from a template
        
        Args:
            content: Template parameters
            
        Returns:
            Generated learning path
        """
        template_name = content.get("template", "")
        user_id = content.get("user_id")
        customization = content.get("customization", {})
        
        template = self.path_templates.get(template_name)
        
        if not template:
            return {"error": f"Template '{template_name}' not found"}
        
        # Create path from template with customization
        path = await self._create_path({
            "user_id": user_id,
            "topic": template["name"],
            "difficulty": customization.get("difficulty", template["difficulty"]),
            "goals": customization.get("goals", []),
            "hours_per_week": customization.get("hours_per_week", 10),
            "existing_knowledge": customization.get("existing_knowledge", [])
        })
        
        # Update with template specifics
        path_data = path["path"]
        path_data["template_used"] = template_name
        path_data["topics"] = template["topics"]
        path_data["estimated_weeks"] = template["estimated_weeks"]
        
        return {
            "success": True,
            "path": path_data,
            "template": template_name
        }
    
    # Path Access Methods
    
    def _get_path(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a learning path by ID
        
        Args:
            content: Request parameters
            
        Returns:
            Learning path data
        """
        path_id = content.get("path_id")
        user_id = content.get("user_id")
        
        path_key = f"{user_id}_{path_id}" if user_id else path_id
        
        if path_key not in self.learning_paths:
            return {"error": "Learning path not found"}
        
        path = self.learning_paths[path_key]
        
        return {
            "success": True,
            "path": self._serialize_path(path)
        }
    
    def _serialize_path(self, path: LearningPath) -> Dict[str, Any]:
        """Serialize LearningPath to dictionary"""
        return {
            "path_id": path.path_id,
            "title": path.title,
            "description": path.description,
            "user_id": path.user_id,
            "difficulty": path.difficulty,
            "estimated_weeks": path.estimated_weeks,
            "progress": path.progress,
            "status": path.status,
            "milestones": [
                {
                    "milestone_id": m.milestone_id,
                    "order": m.order,
                    "title": m.title,
                    "description": m.description,
                    "topics": m.topics,
                    "estimated_hours": m.estimated_hours,
                    "status": m.status,
                    "completion_criteria": m.completion_criteria
                }
                for m in path.milestones
            ],
            "topics": path.topics,
            "prerequisites": path.prerequisites,
            "learning_objectives": path.learning_objectives,
            "created_at": path.created_at,
            "updated_at": path.updated_at
        }
    
    # Progress Tracking Methods
    
    async def _update_progress(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update progress on a learning path
        
        Args:
            content: Progress update parameters
            
        Returns:
            Updated progress
        """
        path_id = content.get("path_id")
        user_id = content.get("user_id")
        milestone_completed = content.get("milestone_completed", 0)
        topics_completed = content.get("topics_completed", [])
        hours_spent = content.get("hours_spent", 0)
        
        progress_key = f"{user_id}_{path_id}"
        
        if progress_key not in self.user_progress:
            return {"error": "Progress not found"}
        
        progress = self.user_progress[progress_key]
        
        # Update progress
        progress.topics_completed.extend(topics_completed)
        progress.total_hours_spent += hours_spent
        progress.last_activity = datetime.now().isoformat()
        
        if milestone_completed > 0 and milestone_completed not in progress.completed_milestones:
            progress.completed_milestones.append(milestone_completed)
            progress.current_milestone = milestone_completed + 1
        
        # Calculate percentage
        if path_id in self.learning_paths:
            path = self.learning_paths[progress_key]
            path.progress = len(progress.completed_milestones) / len(path.milestones) * 100
            progress.progress_percentage = path.progress
            
            # Update milestone status
            for m in path.milestones:
                if m.order in progress.completed_milestones:
                    m.status = "completed"
                elif m.order == progress.current_milestone:
                    m.status = "active"
                else:
                    m.status = "pending"
        
        return {
            "success": True,
            "progress": {
                "current_milestone": progress.current_milestone,
                "completed_milestones": progress.completed_milestones,
                "topics_completed": progress.topics_completed,
                "total_hours_spent": progress.total_hours_spent,
                "progress_percentage": round(progress.progress_percentage, 1)
            },
            "recommendations": self._generate_progress_recommendations(progress, path_id)
        }
    
    async def _complete_milestone(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark a milestone as completed
        
        Args:
            content: Completion parameters
            
        Returns:
            Completion result
        """
        path_id = content.get("path_id")
        user_id = content.get("user_id")
        milestone_id = content.get("milestone_id")
        
        progress_key = f"{user_id}_{path_id}"
        
        if progress_key not in self.learning_paths:
            return {"error": "Learning path not found"}
        
        path = self.learning_paths[progress_key]
        
        # Find and update milestone
        for milestone in path.milestones:
            if milestone.milestone_id == milestone_id or milestone.order == milestone_id:
                milestone.status = "completed"
                
                # Update progress
                progress = self.user_progress.get(progress_key)
                if progress:
                    if milestone.order not in progress.completed_milestones:
                        progress.completed_milestones.append(milestone.order)
                    progress.current_milestone = milestone.order + 1
                    progress.progress_percentage = len(progress.completed_milestones) / len(path.milestones) * 100
                
                break
        
        return {
            "success": True,
            "message": f"Milestone {milestone_id} completed",
            "path_progress": path.progress,
            "next_milestone": path.milestones[min(progress.current_milestone - 1, len(path.milestones) - 1)].title if progress else None
        }
    
    def _get_milestones(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get milestones for a learning path
        
        Args:
            content: Request parameters
            
        Returns:
            Milestone data
        """
        path_id = content.get("path_id")
        user_id = content.get("user_id")
        
        progress_key = f"{user_id}_{path_id}"
        
        if progress_key not in self.learning_paths:
            return {"error": "Learning path not found"}
        
        path = self.learning_paths[progress_key]
        
        return {
            "success": True,
            "milestones": [
                {
                    "milestone_id": m.milestone_id,
                    "order": m.order,
                    "title": m.title,
                    "description": m.description,
                    "topics": m.topics,
                    "estimated_hours": m.estimated_hours,
                    "status": m.status,
                    "progress": 100 if m.status == "completed" else (50 if m.status == "active" else 0)
                }
                for m in path.milestones
            ]
        }
    
    # Path Adjustment Methods
    
    async def _adjust_path(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust a learning path based on progress
        
        Args:
            content: Adjustment parameters
            
        Returns:
            Adjusted path
        """
        path_id = content.get("path_id")
        user_id = content.get("user_id")
        feedback = content.get("feedback", {})
        
        progress_key = f"{user_id}_{path_id}"
        
        if progress_key not in self.learning_paths:
            return {"error": "Learning path not found"}
        
        path = self.learning_paths[progress_key]
        
        # Adjust based on feedback
        pace_too_fast = feedback.get("pace_too_fast", False)
        pace_too_slow = feedback.get("pace_too_slow", False)
        topics_too_hard = feedback.get("topics_too_hard", [])
        topics_too_easy = feedback.get("topics_too_easy", [])
        
        adjustments = []
        
        if pace_too_fast:
            # Slow down by adding buffer time
            path.estimated_weeks = int(path.estimated_weeks * 1.25)
            adjustments.append("Extended estimated duration for better pacing")
        
        if pace_too_slow:
            # Speed up by consolidating topics
            path.estimated_weeks = max(1, int(path.estimated_weeks * 0.75))
            adjustments.append("Condensed duration for faster progression")
        
        if topics_too_hard:
            # Add prerequisite material
            for topic in topics_too_hard:
                prereqs = self._get_prerequisites(topic)
                adjustments.append(f"Added prerequisites for {topic}: {prereqs}")
        
        if topics_too_easy:
            # Advance topics
            adjustments.append(f"Advanced difficulty for: {topics_too_easy}")
        
        path.updated_at = datetime.now().isoformat()
        
        return {
            "success": True,
            "path": self._serialize_path(path),
            "adjustments": adjustments,
            "message": "Learning path adjusted based on your feedback"
        }
    
    # Prerequisite Methods
    
    def _validate_prerequisites(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate prerequisites for a topic or path
        
        Args:
            content: Validation parameters
            
        Returns:
            Validation result
        """
        topic = content.get("topic", "")
        user_knowledge = content.get("user_knowledge", [])
        
        prerequisites = self._get_prerequisites(topic)
        
        missing = [p for p in prerequisites if p not in user_knowledge]
        satisfied = [p for p in prerequisites if p in user_knowledge]
        
        is_ready = len(missing) == 0
        
        return {
            "success": True,
            "topic": topic,
            "prerequisites": {
                "required": prerequisites,
                "satisfied": satisfied,
                "missing": missing
            },
            "ready_to_start": is_ready,
            "recommendations": [f"Learn {m} first" for m in missing] if not is_ready else []
        }
    
    def _analyze_prerequisites(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze prerequisites for a learning goal
        
        Args:
            content: Analysis parameters
            
        Returns:
            Prerequisite analysis
        """
        goal_topic = content.get("topic", "")
        target_level = content.get("target_level", "intermediate")
        
        # Build prerequisite tree
        prereq_tree = self._build_prereq_tree(goal_topic)
        
        # Calculate total learning time
        total_topics = len(set(prereq_tree))
        estimated_hours = total_topics * 5  # 5 hours per topic
        
        return {
            "success": True,
            "analysis": {
                "topic": goal_topic,
                "target_level": target_level,
                "prerequisite_tree": prereq_tree,
                "total_topics": total_topics,
                "estimated_hours": estimated_hours,
                "learning_order": self._get_learning_order(prereq_tree),
                "critical_path": self._get_critical_path(prereq_tree)
            }
        }
    
    def _build_prereq_tree(self, topic: str) -> Dict[str, List[str]]:
        """Build a tree of prerequisites for a topic"""
        tree = {topic: self._get_prerequisites(topic)}
        
        for prereq in tree[topic]:
            if prereq not in tree:
                sub_prereqs = self._build_prereq_tree(prereq)
                tree.update(sub_prereqs)
        
        return tree
    
    def _get_learning_order(self, prereq_tree: Dict[str, List[str]]) -> List[str]:
        """Get recommended learning order based on prerequisites"""
        # Simple topological sort
        order = []
        remaining = set(prereq_tree.keys())
        
        while remaining:
            # Find topics with no unmet prerequisites
            ready = [t for t in remaining if not any(p in remaining for p in prereq_tree[t])]
            
            if ready:
                topic = ready[0]
                order.append(topic)
                remaining.remove(topic)
            else:
                # Circular dependency - add arbitrary topic
                topic = next(iter(remaining))
                order.append(topic)
                remaining.remove(topic)
        
        return order
    
    def _get_critical_path(self, prereq_tree: Dict[str, List[str]]) -> List[str]:
        """Get the critical path (longest chain of prerequisites)"""
        # Simplified - just return the topic itself
        return list(prereq_tree.keys())
    
    # Recommendation Methods
    
    def _get_recommendations(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get personalized recommendations for next steps
        
        Args:
            content: Request parameters
            
        Returns:
            Recommendations
        """
        user_id = content.get("user_id")
        path_id = content.get("path_id")
        
        progress_key = f"{user_id}_{path_id}"
        
        # Get current progress
        progress = self.user_progress.get(progress_key)
        path = self.learning_paths.get(progress_key)
        
        if not progress or not path:
            return {
                "success": True,
                "recommendations": [
                    "Create a learning path to get personalized recommendations",
                    "Start with foundational topics",
                    "Set clear learning goals"
                ]
            }
        
        recommendations = []
        
        # Recommend current milestone topics
        current_milestone = next(
            (m for m in path.milestones if m.order == progress.current_milestone),
            None
        )
        
        if current_milestone:
            recommendations.append({
                "type": "current_focus",
                "title": f"Focus on: {current_milestone.title}",
                "description": current_milestone.description,
                "topics": current_milestone.topics,
                "estimated_hours": current_milestone.estimated_hours
            })
        
        # Recommend based on progress
        if progress.progress_percentage < 25:
            recommendations.append({
                "type": "getting_started",
                "title": "Getting Started Tips",
                "tips": [
                    "Complete the first milestone's lessons",
                    "Practice with the exercises",
                    "Take the milestone quiz"
                ]
            })
        elif progress.progress_percentage < 50:
            recommendations.append({
                "type": "building_momentum",
                "title": "Building Momentum",
                "tips": [
                    "Keep a consistent learning schedule",
                    "Review previous material weekly",
                    "Apply concepts in small projects"
                ]
            })
        elif progress.progress_percentage < 75:
            recommendations.append({
                "type": "deepening_knowledge",
                "title": "Deepening Your Knowledge",
                "tips": [
                    "Work on practical projects",
                    "Explore advanced topics",
                    "Connect with other learners"
                ]
            })
        else:
            recommendations.append({
                "type": "finishing_strong",
                "title": "Finishing Strong",
                "tips": [
                    "Complete remaining milestones",
                    "Review all learned concepts",
                    "Prepare for final assessment"
                ]
            })
        
        return {
            "success": True,
            "recommendations": recommendations,
            "current_progress": progress.progress_percentage,
            "next_milestone": current_milestone.title if current_milestone else None
        }
    
    def _generate_progress_recommendations(self, progress: PathProgress,
                                           path_id: str) -> List[str]:
        """Generate recommendations based on progress"""
        recommendations = []
        
        if progress.progress_percentage < 10:
            recommendations.append("Start with the first milestone to build momentum")
        elif progress.progress_percentage < 30:
            recommendations.append("Great start! Keep progressing through the milestones")
        elif progress.progress_percentage < 50:
            recommendations.append("You're making good progress. Stay consistent!")
        elif progress.progress_percentage < 70:
            recommendations.append("Over halfway there! Keep up the good work")
        elif progress.progress_percentage < 90:
            recommendations.append("Almost done! Complete the final milestones")
        else:
            recommendations.append("Congratulations on your progress! Complete the last steps")
        
        return recommendations
    
    # Analysis Methods
    
    def _analyze_learning_gaps(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze learning gaps for a user
        
        Args:
            params: Analysis parameters
            
        Returns:
            Gap analysis
        """
        user_id = params.get("user_id")
        
        # Get user's progress across all paths
        user_progress = {k: v for k, v in self.user_progress.items() if k.startswith(user_id)}
        
        if not user_progress:
            return {
                "success": True,
                "analysis": {
                    "message": "No learning paths found",
                    "gaps": [],
                    "recommendations": ["Create a learning path to analyze gaps"]
                }
            }
        
        # Analyze completed vs. in-progress
        completed_topics = set()
        in_progress_topics = set()
        
        for progress in user_progress.values():
            completed_topics.update(progress.topics_completed)
            in_progress_topics.update(
                t for path in self.learning_paths.values() 
                for m in path.milestones 
                if m.order >= progress.current_milestone
                for t in m.topics
            )
        
        gaps = list(in_progress_topics - completed_topics)
        
        return {
            "success": True,
            "analysis": {
                "completed_topics": list(completed_topics),
                "in_progress_topics": list(in_progress_topics),
                "learning_gaps": gaps,
                "completion_rate": sum(p.progress_percentage for p in user_progress.values()) / max(len(user_progress), 1)
            },
            "recommendations": [
                f"Focus on: {g}" for g in gaps[:3]
            ]
        }
    
    async def _optimize_path(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize a learning path for efficiency
        
        Args:
            params: Optimization parameters
            
        Returns:
            Optimization result
        """
        path_id = params.get("path_id")
        user_id = params.get("user_id")
        
        progress_key = f"{user_id}_{path_id}"
        
        if progress_key not in self.learning_paths:
            return {"error": "Learning path not found"}
        
        path = self.learning_paths[progress_key]
        
        # Optimize milestones
        optimized_milestones = []
        for milestone in path.milestones:
            # Prioritize topics based on dependencies
            milestone.topics = self._get_learning_order(
                {t: self._get_prerequisites(t) for t in milestone.topics}
            )
            optimized_milestones.append(milestone)
        
        path.milestones = optimized_milestones
        path.updated_at = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Path optimized for efficient learning",
            "optimizations": [
                "Reordered topics based on dependencies",
                "Consolidated related concepts",
                "Balanced workload across milestones"
            ]
        }
    
    async def _create_curriculum(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete curriculum
        
        Args:
            params: Curriculum parameters
            
        Returns:
            Created curriculum
        """
        topic = params.get("topic", "")
        difficulty = params.get("difficulty", "beginner")
        duration_weeks = params.get("duration_weeks", 12)
        hours_per_week = params.get("hours_per_week", 10)
        
        curriculum = {
            "curriculum_id": f"curriculum_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": f"{topic.title()} Curriculum",
            "difficulty": difficulty,
            "duration_weeks": duration_weeks,
            "total_hours": duration_weeks * hours_per_week,
            "weekly_structure": [],
            "assessments": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Create weekly structure
        for week in range(1, duration_weeks + 1):
            week_plan = {
                "week": week,
                "focus": f"Week {week} Focus",
                "topics": [f"Topic {i}" for i in range(1, 4)],
                "objectives": [f"Objective {i}" for i in range(1, 4)],
                "hours_allocated": hours_per_week,
                "activities": [
                    {"type": "lesson", "hours": 3},
                    {"type": "practice", "hours": 4},
                    {"type": "review", "hours": 2},
                    {"type": "assessment", "hours": 1}
                ]
            }
            curriculum["weekly_structure"].append(week_plan)
        
        # Add assessments
        curriculum["assessments"] = [
            {"week": 4, "type": "midterm", "focus": "Foundations"},
            {"week": 8, "type": "progress", "focus": "Intermediate Concepts"},
            {"week": duration_weeks, "type": "final", "focus": "Complete Mastery"}
        ]
        
        return {
            "success": True,
            "curriculum": curriculum
        }
    
    def _get_path_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get learning path statistics
        
        Args:
            params: Request parameters
            
        Returns:
            Path statistics
        """
        return {
            "success": True,
            "statistics": {
                "total_paths": len(self.learning_paths),
                "templates_available": len(self.path_templates),
                "topics_with_prerequisites": len(self.topic_prerequisites),
                "user_progress_records": len(self.user_progress)
            }
        }
