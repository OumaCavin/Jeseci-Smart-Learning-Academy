"""
Assessment Agent - Quiz Generation and Evaluation
Jeseci Smart Learning Academy - Sophisticated Multi-Agent Learning Platform

This module implements the Assessment Agent, which provides dynamic quiz generation,
answer evaluation, difficulty calibration, and knowledge gap identification.
"""

import asyncio
import json
import random
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from backend.agents.base_agent import BaseAgent, AgentMessage, AgentTask, AgentState, MessageType, Priority

# Import centralized logging configuration
from logger_config import logger


@dataclass
class QuizQuestion:
    """Represents a quiz question"""
    hints: List[str] = field(default_factory=list)
    question_id: str
    question_type: str  # multiple_choice, true_false, short_answer, code
    question: str
    options: List[str]
    correct_answer: Any
    explanation: str
    difficulty: str
    topic: str
    points: int


@dataclass
class Quiz:
    """Represents a complete quiz"""
    quiz_id: str
    title: str
    description: str
    topic: str
    difficulty: str
    questions: List[QuizQuestion]
    time_limit_minutes: int
    passing_score: float
    created_at: str


@dataclass
class QuizAttempt:
    """Represents a quiz attempt by a user"""
    attempt_id: str
    quiz_id: str
    user_id: str
    answers: Dict[str, Any]
    score: float
    started_at: str
    completed_at: str
    time_spent_seconds: int


class AssessmentAgent(BaseAgent):
    """
    Assessment Agent for quiz generation and evaluation
    
    The Assessment Agent provides:
    - Dynamic quiz generation based on topics and difficulty
    - Answer evaluation and scoring
    - Difficulty calibration based on performance
    - Knowledge gap identification
    - Adaptive testing
    - Progress assessment
    
    Attributes:
        question_bank: Repository of quiz questions
        quiz_templates: Templates for quiz generation
        active_attempts: Currently active quiz attempts
        attempt_history: History of all quiz attempts
    """
    
    def __init__(self, agent_id: str = "assessment_agent",
                 agent_name: str = "Assessment Engine",
                 message_bus = None):
        """
        Initialize the Assessment Agent
        
        Args:
            agent_id: Unique identifier
            agent_name: Human-readable name
            message_bus: Optional message bus instance
        """
        super().__init__(agent_id, agent_name, "Assessment")
        
        # Question management
        self.question_bank: List[QuizQuestion] = []
        self.quiz_templates: Dict[str, Dict] = {}
        self.active_attempts: Dict[str, QuizAttempt] = {}
        self.attempt_history: List[QuizAttempt] = []
        
        # Initialize question bank
        self._initialize_question_bank()
        self._initialize_quiz_templates()
        
        self.logger.info("Assessment Agent initialized")
    
    def _register_capabilities(self):
        """Register the capabilities of the Assessment Agent"""
        self.capabilities = [
            "quiz_generation",
            "answer_evaluation",
            "difficulty_calibration",
            "knowledge_gap_identification",
            "adaptive_testing",
            "progress_assessment",
            "question_management",
            "scoring_and_feedback"
        ]
    
    def _initialize_question_bank(self):
        """Initialize the question bank with sample questions"""
        questions = [
            # OSP Basics
            QuizQuestion(
                question_id="osp_001",
                question_type="multiple_choice",
                question="What is the primary purpose of nodes in Object-Spatial Programming?",
                options=[
                    "To define function behaviors",
                    "To represent data entities in a graph",
                    "To handle network connections",
                    "To manage database connections"
                ],
                correct_answer=1,
                explanation="Nodes are the fundamental building blocks in OSP that represent data entities. They are connected through edges to form graph structures.",
                difficulty="beginner",
                topic="osp_basics",
                points=10,
                hints=[
                    "Think about what nodes represent in a graph structure",
                    "Nodes are the 'things' in your data model"
                ]
            ),
            QuizQuestion(
                question_id="osp_002",
                question_type="multiple_choice",
                question="What is the role of walkers in OSP?",
                options=[
                    "To store data persistently",
                    "To navigate and perform actions on the graph",
                    "To compile the application",
                    "To handle user authentication"
                ],
                correct_answer=1,
                explanation="Walkers are agents that navigate through the graph, visiting nodes and performing actions. They are the 'actors' in OSP.",
                difficulty="beginner",
                topic="osp_basics",
                points=10,
                hints=[
                    "Walkers 'walk' through the graph",
                    "They perform actions on nodes"
                ]
            ),
            QuizQuestion(
                question_id="osp_003",
                question_type="true_false",
                question="In OSP, edges can only represent one type of relationship between nodes.",
                options=["True", "False"],
                correct_answer=1,
                explanation="Edges in OSP can represent multiple types of relationships, including directional and weighted connections.",
                difficulty="intermediate",
                topic="osp_basics",
                points=5
            ),
            
            # byLLM Basics
            QuizQuestion(
                question_id="byllm_001",
                question_type="multiple_choice",
                question="What does the @can by llm() decorator enable in Jaclang?",
                options=[
                    "Database connection management",
                    "AI-powered code generation and analysis",
                    "Network socket creation",
                    "File system operations"
                ],
                correct_answer=1,
                explanation="The @can by llm() decorator enables methods to leverage large language models for intelligent code generation and analysis tasks.",
                difficulty="intermediate",
                topic="byllm_basics",
                points=15,
                hints=[
                    "Think about what LLM stands for",
                    "This decorator involves AI capabilities"
                ]
            ),
            QuizQuestion(
                question_id="byllm_002",
                question_type="multiple_choice",
                question="When using byLLM for content generation, what factor most affects output quality?",
                options=[
                    "The color scheme of the IDE",
                    "The quality and specificity of prompts",
                    "The computer's processor speed",
                    "The operating system version"
                ],
                correct_answer=1,
                explanation="The quality of LLM-generated content heavily depends on how well-crafted your prompts are. Clear, specific prompts yield better results.",
                difficulty="beginner",
                topic="byllm_basics",
                points=10
            ),
            
            # Programming Fundamentals
            QuizQuestion(
                question_id="prog_001",
                question_type="multiple_choice",
                question="Which of the following is NOT a primitive data type in most programming languages?",
                options=["Integer", "Boolean", "Class", "Float"],
                correct_answer=2,
                explanation="A Class is a composite/user-defined type, not a primitive. Primitives are basic types built into the language.",
                difficulty="beginner",
                topic="programming_fundamentals",
                points=10
            ),
            QuizQuestion(
                question_id="prog_002",
                question_type="true_false",
                question="Recursion always requires a base case to prevent infinite loops.",
                options=["True", "False"],
                correct_answer=0,
                explanation="A base case is essential in recursion to provide a termination condition. Without it, the function would call itself indefinitely.",
                difficulty="intermediate",
                topic="programming_fundamentals",
                points=10
            ),
            QuizQuestion(
                question_id="prog_003",
                question_type="short_answer",
                question="What is the time complexity of binary search?",
                options=[],
                correct_answer="O(log n)",
                explanation="Binary search has O(log n) complexity because it halves the search space with each comparison.",
                difficulty="intermediate",
                topic="programming_fundamentals",
                points=20
            ),
            
            # Data Structures
            QuizQuestion(
                question_id="ds_001",
                question_type="multiple_choice",
                question="Which data structure follows the Last-In-First-Out (LIFO) principle?",
                options=["Queue", "Stack", "Array", "Linked List"],
                correct_answer=1,
                explanation="A Stack follows LIFO - the last element added is the first one removed. Think of a stack of plates.",
                difficulty="beginner",
                topic="data_structures",
                points=10
            ),
            QuizQuestion(
                question_id="ds_002",
                question_type="multiple_choice",
                question="What is the primary advantage of a hash table over other data structures for lookups?",
                options=[
                    "Maintains insertion order",
                    "O(1) average-case lookup time",
                    "Automatically sorts elements",
                    "Uses less memory than arrays"
                ],
                correct_answer=1,
                explanation="Hash tables provide O(1) average-case time complexity for insertions, deletions, and lookups when the hash function distributes keys uniformly.",
                difficulty="intermediate",
                topic="data_structures",
                points=15
            ),
            
            # Advanced Concepts
            QuizQuestion(
                question_id="adv_001",
                question_type="multiple_choice",
                question="What is polymorphism in object-oriented programming?",
                options=[
                    "The ability to hide internal details",
                    "The ability of objects to take many forms",
                    "The process of creating multiple threads",
                    "A type of database relationship"
                ],
                correct_answer=1,
                explanation="Polymorphism allows objects of different classes to be treated as objects of a common superclass. It enables one interface to be used for a general class of actions.",
                difficulty="advanced",
                topic="oop_concepts",
                points=20
            ),
            QuizQuestion(
                question_id="adv_002",
                question_type="multiple_choice",
                question="What is the purpose of dependency injection in software design?",
                options=[
                    "To increase code complexity",
                    "To decouple components and improve testability",
                    "To speed up compilation",
                    "To handle memory management"
                ],
                correct_answer=1,
                explanation="Dependency injection helps achieve loose coupling by providing dependencies from external sources rather than creating them internally, making code more testable and maintainable.",
                difficulty="advanced",
                topic="software_design",
                points=20
            )
        ]
        
        self.question_bank = questions
    
    def _initialize_quiz_templates(self):
        """Initialize quiz templates for different scenarios"""
        self.quiz_templates = {
            "concept_check": {
                "name": "Concept Check",
                "description": "Quick assessment of understanding",
                "question_count": 5,
                "time_limit": 10,
                "passing_score": 0.6,
                "difficulty_range": ["beginner"]
            },
            "comprehensive": {
                "name": "Comprehensive Quiz",
                "description": "Thorough assessment covering multiple topics",
                "question_count": 15,
                "time_limit": 30,
                "passing_score": 0.7,
                "difficulty_range": ["beginner", "intermediate"]
            },
            "advanced": {
                "name": "Advanced Assessment",
                "description": "Challenging assessment for experienced learners",
                "question_count": 10,
                "time_limit": 25,
                "passing_score": 0.65,
                "difficulty_range": ["intermediate", "advanced"]
            },
            "adaptive": {
                "name": "Adaptive Quiz",
                "description": "Difficulty adjusts based on performance",
                "question_count": 20,
                "time_limit": 40,
                "passing_score": 0.7,
                "difficulty_range": ["beginner", "intermediate", "advanced"]
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
        
        if action == "generate_quiz":
            return await self._generate_quiz(content)
        elif action == "start_quiz":
            return await self._start_quiz(content)
        elif action == "submit_answer":
            return await self._submit_answer(content)
        elif action == "complete_quiz":
            return await self._complete_quiz(content)
        elif action == "evaluate_answer":
            return self._evaluate_answer(content)
        elif action == "identify_knowledge_gaps":
            return self._identify_knowledge_gaps(content)
        elif action == "calibrate_difficulty":
            return self._calibrate_difficulty(content)
        elif action == "get_question":
            return self._get_question(content)
        elif action == "get_quiz_result":
            return self._get_quiz_result(content)
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
        
        if command == "create_custom_quiz":
            return await self._create_custom_quiz(task.parameters)
        elif command == "analyze_performance":
            return self._analyze_performance(task.parameters)
        elif command == "generate_report":
            return await self._generate_assessment_report(task.parameters)
        elif command == "get_statistics":
            return self._get_assessment_statistics(task.parameters)
        else:
            return {"error": f"Unknown command: {command}"}
    
    # Quiz Generation Methods
    
    async def _generate_quiz(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a quiz based on parameters
        
        Args:
            content: Quiz generation parameters
            
        Returns:
            Generated quiz
        """
        topic = content.get("topic", "general")
        difficulty = content.get("difficulty", "mixed")
        question_count = content.get("question_count", 10)
        quiz_type = content.get("type", "comprehensive")
        
        # Filter questions by topic and difficulty
        filtered_questions = self._filter_questions(topic, difficulty, question_count)
        
        if len(filtered_questions) < question_count:
            # Add more questions from related topics
            related = self._get_related_questions(topic, question_count - len(filtered_questions))
            filtered_questions.extend(related)
        
        # Shuffle and select
        random.shuffle(filtered_questions)
        selected_questions = filtered_questions[:question_count]
        
        import uuid
        
        quiz_id = f"quiz_{uuid.uuid4().hex[:8]}"
        template = self.quiz_templates.get(quiz_type, self.quiz_templates["comprehensive"])
        
        quiz = Quiz(
            quiz_id=quiz_id,
            title=f"{topic.title()} Assessment",
            description=f"Test your knowledge of {topic}",
            topic=topic,
            difficulty=difficulty,
            questions=selected_questions,
            time_limit_minutes=template["time_limit"],
            passing_score=template["passing_score"],
            created_at=datetime.now().isoformat()
        )
        
        self.logger.info(f"Quiz generated: {quiz_id} with {len(selected_questions)} questions")
        
        return {
            "success": True,
            "quiz": {
                "quiz_id": quiz.quiz_id,
                "title": quiz.title,
                "description": quiz.description,
                "topic": quiz.topic,
                "difficulty": quiz.difficulty,
                "question_count": len(quiz.questions),
                "time_limit_minutes": quiz.time_limit_minutes,
                "passing_score": quiz.passing_score,
                "questions": [
                    {
                        "question_id": q.question_id,
                        "question": q.question,
                        "question_type": q.question_type,
                        "options": q.options,
                        "points": q.points,
                        "hints": q.hints[:2] if q.hints else []
                    }
                    for q in quiz.questions
                ]
            }
        }
    
    def _filter_questions(self, topic: str, difficulty: str, 
                         count: int) -> List[QuizQuestion]:
        """
        Filter questions by topic and difficulty
        
        Args:
            topic: Topic to filter by
            difficulty: Difficulty level
            count: Number of questions needed
            
        Returns:
            Filtered questions
        """
        filtered = []
        
        for q in self.question_bank:
            # Match topic
            topic_match = topic == "general" or q.topic == topic
            
            # Match difficulty
            if difficulty == "mixed":
                diff_match = True
            elif difficulty == "adaptive":
                diff_match = q.difficulty in ["beginner", "intermediate"]
            else:
                diff_match = q.difficulty == difficulty
            
            if topic_match and diff_match:
                filtered.append(q)
        
        return filtered
    
    def _get_related_questions(self, topic: str, count: int) -> List[QuizQuestion]:
        """Get questions from related topics"""
        related_topics = {
            "osp_basics": ["programming_fundamentals", "data_structures"],
            "byllm_basics": ["programming_fundamentals", "software_design"],
            "programming_fundamentals": ["osp_basics", "data_structures"],
            "data_structures": ["programming_fundamentals", "oop_concepts"],
            "oop_concepts": ["software_design", "programming_fundamentals"]
        }
        
        topics = related_topics.get(topic, ["general"])
        related = []
        
        for t in topics:
            related.extend([q for q in self.question_bank if q.topic == t])
        
        random.shuffle(related)
        return related[:count]
    
    async def _create_custom_quiz(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a custom quiz with specific parameters
        
        Args:
            params: Custom quiz parameters
            
        Returns:
            Created quiz
        """
        topics = params.get("topics", ["general"])
        difficulty = params.get("difficulty", "mixed")
        question_count = params.get("question_count", 10)
        include_types = params.get("question_types", ["multiple_choice", "true_false", "short_answer"])
        
        # Collect questions from specified topics
        all_questions = []
        for topic in topics:
            all_questions.extend(self._filter_questions(topic, difficulty, 50))
        
        # Filter by question type
        if include_types != ["all"]:
            all_questions = [q for q in all_questions if q.question_type in include_types]
        
        # Select questions
        random.shuffle(all_questions)
        selected = all_questions[:question_count]
        
        import uuid
        
        return {
            "success": True,
            "quiz": {
                "quiz_id": f"quiz_{uuid.uuid4().hex[:8]}",
                "topics": topics,
                "difficulty": difficulty,
                "question_count": len(selected),
                "questions": [q.question_id for q in selected]
            }
        }
    
    # Quiz Session Methods
    
    async def _start_quiz(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a quiz attempt
        
        Args:
            content: Start parameters
            
        Returns:
            Quiz attempt information
        """
        import uuid
        
        quiz_id = content.get("quiz_id")
        user_id = content.get("user_id")
        
        attempt_id = f"attempt_{uuid.uuid4().hex[:8]}"
        
        attempt = QuizAttempt(
            attempt_id=attempt_id,
            quiz_id=quiz_id,
            user_id=user_id,
            answers={},
            score=0.0,
            started_at=datetime.now().isoformat(),
            completed_at="",
            time_spent_seconds=0
        )
        
        self.active_attempts[attempt_id] = attempt
        
        self.logger.info(f"Quiz started: attempt {attempt_id} for quiz {quiz_id}")
        
        return {
            "success": True,
            "attempt_id": attempt_id,
            "started_at": attempt.started_at,
            "message": "Quiz started. Good luck!"
        }
    
    async def _submit_answer(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit an answer for a question
        
        Args:
            content: Answer submission
            
        Returns:
            Evaluation result
        """
        attempt_id = content.get("attempt_id")
        question_id = content.get("question_id")
        answer = content.get("answer")
        
        if attempt_id not in self.active_attempts:
            return {"error": "Invalid attempt ID"}
        
        attempt = self.active_attempts[attempt_id]
        
        # Find the question
        question = next((q for q in self.question_bank if q.question_id == question_id), None)
        
        if not question:
            return {"error": "Invalid question ID"}
        
        # Evaluate the answer
        is_correct = self._check_answer(question, answer)
        
        # Record the answer
        attempt.answers[question_id] = {
            "answer": answer,
            "correct": is_correct,
            "points": question.points if is_correct else 0
        }
        
        # Calculate current score
        total_points = sum(q.points for q in self.question_bank if q.question_id in attempt.answers)
        earned_points = sum(a["points"] for a in attempt.answers.values())
        attempt.score = earned_points / max(total_points, 1) if total_points > 0 else 0
        
        return {
            "success": True,
            "correct": is_correct,
            "explanation": question.explanation,
            "current_score": round(attempt.score * 100, 1),
            "hints": question.hints[:1] if not is_correct and question.hints else []
        }
    
    async def _complete_quiz(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete a quiz attempt
        
        Args:
            content: Completion parameters
            
        Returns:
            Final quiz results
        """
        attempt_id = content.get("attempt_id")
        
        if attempt_id not in self.active_attempts:
            return {"error": "Invalid attempt ID"}
        
        attempt = self.active_attempts[attempt_id]
        
        # Calculate final score
        attempt.completed_at = datetime.now().isoformat()
        attempt.time_spent_seconds = self._calculate_time_spent(attempt.started_at, attempt.completed_at)
        
        # Move to history
        self.attempt_history.append(attempt)
        del self.active_attempts[attempt_id]
        
        # Determine pass/fail
        passed = attempt.score >= 0.7  # Default passing score
        
        # Get performance breakdown
        breakdown = self._get_performance_breakdown(attempt)
        
        self.logger.info(f"Quiz completed: attempt {attempt_id}, score: {attempt.score * 100}%")
        
        return {
            "success": True,
            "results": {
                "attempt_id": attempt_id,
                "score": round(attempt.score * 100, 1),
                "passed": passed,
                "time_spent_seconds": attempt.time_spent_seconds,
                "questions_answered": len(attempt.answers),
                "correct_answers": breakdown["correct"],
                "incorrect_answers": breakdown["incorrect"],
                "breakdown": breakdown["by_topic"],
                "feedback": self._generate_quiz_feedback(attempt.score, breakdown)
            }
        }
    
    # Answer Evaluation Methods
    
    def _evaluate_answer(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single answer
        
        Args:
            content: Answer to evaluate
            
        Returns:
            Evaluation result
        """
        question_id = content.get("question_id")
        answer = content.get("answer")
        
        question = next((q for q in self.question_bank if q.question_id == question_id), None)
        
        if not question:
            return {"error": "Invalid question ID"}
        
        is_correct = self._check_answer(question, answer)
        
        return {
            "success": True,
            "correct": is_correct,
            "explanation": question.explanation,
            "points_earned": question.points if is_correct else 0,
            "hints": question.hints if not is_correct else []
        }
    
    def _check_answer(self, question: QuizQuestion, answer: Any) -> bool:
        """
        Check if an answer is correct
        
        Args:
            question: The question
            answer: The answer to check
            
        Returns:
            True if correct
        """
        correct = question.correct_answer
        
        # Handle different question types
        if question.question_type == "multiple_choice" or question.question_type == "true_false":
            return int(answer) == int(correct)
        elif question.question_type == "short_answer":
            # Case-insensitive string comparison
            if isinstance(answer, str) and isinstance(correct, str):
                return answer.lower().strip() == correct.lower().strip()
            return str(answer).lower().strip() == str(correct).lower().strip()
        elif question.question_type == "code":
            # For code questions, basic check (in production, use execution)
            return str(answer).strip() == str(correct).strip()
        
        return False
    
    def _get_performance_breakdown(self, attempt: QuizAttempt) -> Dict[str, Any]:
        """
        Get performance breakdown by topic
        
        Args:
            attempt: The quiz attempt
            
        Returns:
            Performance breakdown
        """
        correct = 0
        incorrect = 0
        by_topic = {}
        
        for question_id, answer_data in attempt.answers.items():
            question = next((q for q in self.question_bank if q.question_id == question_id), None)
            
            if question:
                if answer_data["correct"]:
                    correct += 1
                else:
                    incorrect += 1
                
                topic = question.topic
                if topic not in by_topic:
                    by_topic[topic] = {"correct": 0, "incorrect": 0}
                
                if answer_data["correct"]:
                    by_topic[topic]["correct"] += 1
                else:
                    by_topic[topic]["incorrect"] += 1
        
        return {
            "correct": correct,
            "incorrect": incorrect,
            "by_topic": by_topic
        }
    
    def _generate_quiz_feedback(self, score: float, 
                                breakdown: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive feedback for quiz results"""
        if score >= 0.9:
            level = "Excellent"
            message = "Outstanding performance! You've demonstrated mastery of this topic."
        elif score >= 0.75:
            level = "Great"
            message = "Great job! You have a strong understanding of the material."
        elif score >= 0.6:
            level = "Good"
            message = "Good work! Keep practicing to strengthen your knowledge."
        elif score >= 0.4:
            level = "Needs Improvement"
            message = "You're making progress. Review the topics where you missed questions."
        else:
            level = "Keep Learning"
            message = "Don't give up! Review the material and try again."
        
        # Identify areas for improvement
        weak_topics = [
            topic for topic, data in breakdown["by_topic"].items()
            if data["incorrect"] > data["correct"]
        ]
        
        return {
            "level": level,
            "message": message,
            "score_category": "Pass" if score >= 0.7 else "Needs Work",
            "strong_areas": [
                topic for topic, data in breakdown["by_topic"].items()
                if data["correct"] >= data["incorrect"]
            ],
            "weak_areas": weak_topics,
            "recommendations": [
                f"Review {topic.replace('_', ' ')} concepts" for topic in weak_topics[:3]
            ]
        }
    
    # Knowledge Gap Methods
    
    def _identify_knowledge_gaps(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify knowledge gaps based on quiz performance
        
        Args:
            content: Request parameters
            
        Returns:
            Knowledge gap analysis
        """
        user_id = content.get("user_id")
        
        # Get user's quiz history
        user_attempts = [a for a in self.attempt_history if a.user_id == user_id]
        
        # Analyze incorrect answers
        incorrect_by_topic = {}
        incorrect_by_difficulty = {}
        
        for attempt in user_attempts:
            for question_id, answer_data in attempt.answers.items():
                if not answer_data["correct"]:
                    question = next((q for q in self.question_bank 
                                   if q.question_id == question_id), None)
                    
                    if question:
                        # Track by topic
                        if question.topic not in incorrect_by_topic:
                            incorrect_by_topic[question.topic] = []
                        incorrect_by_topic[question.topic].append(question_id)
                        
                        # Track by difficulty
                        if question.difficulty not in incorrect_by_difficulty:
                            incorrect_by_difficulty[question.difficulty] = 0
                        incorrect_by_difficulty[question.difficulty] += 1
        
        # Generate gap analysis
        knowledge_gaps = []
        for topic, questions in incorrect_by_topic.items():
            knowledge_gaps.append({
                "topic": topic,
                "questions_missed": len(questions),
                "priority": "high" if len(questions) > 3 else "medium",
                "recommended_action": f"Review {topic.replace('_', ' ')} fundamentals"
            })
        
        return {
            "success": True,
            "analysis": {
                "total_gaps_identified": len(knowledge_gaps),
                "gaps": sorted(knowledge_gaps, key=lambda x: len(x["questions_missed"]), reverse=True),
                "difficulty_patterns": incorrect_by_difficulty,
                "recommendations": [
                    "Focus on topics with most incorrect answers",
                    "Practice more questions at your current level before advancing",
                    "Review explanations for missed questions"
                ]
            }
        }
    
    # Difficulty Calibration Methods
    
    def _calibrate_difficulty(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calibrate difficulty based on performance
        
        Args:
            content: Calibration parameters
            
        Returns:
            Calibrated difficulty recommendation
        """
        user_id = content.get("user_id")
        current_difficulty = content.get("current_difficulty", "beginner")
        recent_score = content.get("recent_score", 0.5)
        
        # Determine recommended difficulty
        if recent_score >= 0.85:
            recommended = self._increase_difficulty(current_difficulty)
            reason = "Strong performance - ready for more challenging content"
        elif recent_score < 0.5:
            recommended = self._decrease_difficulty(current_difficulty)
            reason = "Additional practice needed at current level"
        else:
            recommended = current_difficulty
            reason = "Good progress - continue with current level"
        
        return {
            "success": True,
            "calibration": {
                "current_difficulty": current_difficulty,
                "recommended_difficulty": recommended,
                "reason": reason,
                "adjustment": "increase" if recommended != current_difficulty else "maintain"
            }
        }
    
    def _increase_difficulty(self, current: str) -> str:
        """Increase difficulty level"""
        levels = ["beginner", "intermediate", "advanced"]
        try:
            idx = levels.index(current)
            return levels[min(idx + 1, len(levels) - 1)]
        except ValueError:
            return "intermediate"
    
    def _decrease_difficulty(self, current: str) -> str:
        """Decrease difficulty level"""
        levels = ["beginner", "intermediate", "advanced"]
        try:
            idx = levels.index(current)
            return levels[max(idx - 1, 0)]
        except ValueError:
            return "beginner"
    
    # Question Access Methods
    
    def _get_question(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a specific question
        
        Args:
            content: Request parameters
            
        Returns:
            Question data
        """
        question_id = content.get("question_id")
        
        question = next((q for q in self.question_bank if q.question_id == question_id), None)
        
        if not question:
            return {"error": "Question not found"}
        
        return {
            "success": True,
            "question": {
                "question_id": question.question_id,
                "question": question.question,
                "question_type": question.question_type,
                "options": question.options,
                "points": question.points,
                "difficulty": question.difficulty,
                "topic": question.topic
            }
        }
    
    # Result Methods
    
    def _get_quiz_result(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get quiz results for an attempt
        
        Args:
            content: Request parameters
            
        Returns:
            Quiz results
        """
        attempt_id = content.get("attempt_id")
        
        attempt = next((a for a in self.attempt_history if a.attempt_id == attempt_id), None)
        
        if not attempt:
            return {"error": "Attempt not found"}
        
        breakdown = self._get_performance_breakdown(attempt)
        
        return {
            "success": True,
            "results": {
                "attempt_id": attempt.attempt_id,
                "quiz_id": attempt.quiz_id,
                "score": round(attempt.score * 100, 1),
                "completed_at": attempt.completed_at,
                "time_spent_seconds": attempt.time_spent_seconds,
                "breakdown": breakdown,
                "feedback": self._generate_quiz_feedback(attempt.score, breakdown)
            }
        }
    
    # Analytics Methods
    
    def _analyze_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze quiz performance for a user
        
        Args:
            params: Analysis parameters
            
        Returns:
            Performance analysis
        """
        user_id = params.get("user_id")
        
        user_attempts = [a for a in self.attempt_history if a.user_id == user_id]
        
        if not user_attempts:
            return {
                "success": True,
                "analysis": {
                    "message": "No quiz attempts yet",
                    "recommendations": ["Take a quiz to start tracking your progress"]
                }
            }
        
        scores = [a.score for a in user_attempts]
        avg_score = sum(scores) / len(scores)
        
        # Performance by topic
        topic_performance = {}
        for attempt in user_attempts:
            for question_id, answer_data in attempt.answers.items():
                question = next((q for q in self.question_bank 
                               if q.question_id == question_id), None)
                if question:
                    topic = question.topic
                    if topic not in topic_performance:
                        topic_performance[topic] = []
                    topic_performance[topic].append(1 if answer_data["correct"] else 0)
        
        topic_averages = {
            topic: round(sum(scores) / len(scores), 2)
            for topic, scores in topic_performance.items()
        }
        
        return {
            "success": True,
            "analysis": {
                "total_quizzes": len(user_attempts),
                "average_score": round(avg_score * 100, 1),
                "highest_score": round(max(scores) * 100, 1),
                "lowest_score": round(min(scores) * 100, 1),
                "recent_trend": "improving" if len(scores) >= 2 and scores[-1] > scores[-2] else "stable",
                "topic_performance": topic_averages
            }
        }
    
    async def _generate_assessment_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an assessment report
        
        Args:
            params: Report parameters
            
        Returns:
            Assessment report
        """
        user_id = params.get("user_id")
        
        analysis = self._analyze_performance({"user_id": user_id})
        
        gaps = self._identify_knowledge_gaps({"user_id": user_id})
        
        report = {
            "report_id": f"assessment_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),
            "summary": analysis["analysis"],
            "knowledge_gaps": gaps["analysis"],
            "recommendations": [
                "Focus on weak areas identified in the analysis",
                "Take quizzes regularly to track improvement",
                "Review explanations for incorrect answers"
            ]
        }
        
        return {
            "success": True,
            "report": report
        }
    
    def _get_assessment_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get assessment statistics
        
        Args:
            params: Request parameters
            
        Returns:
            Assessment statistics
        """
        return {
            "success": True,
            "statistics": {
                "total_questions": len(self.question_bank),
                "questions_by_topic": self._count_by_topic(),
                "questions_by_difficulty": self._count_by_difficulty(),
                "total_attempts": len(self.attempt_history),
                "average_score": round(sum(a.score for a in self.attempt_history) / max(len(self.attempt_history), 1) * 100, 1) if self.attempt_history else 0
            }
        }
    
    def _count_by_topic(self) -> Dict[str, int]:
        """Count questions by topic"""
        counts = {}
        for q in self.question_bank:
            counts[q.topic] = counts.get(q.topic, 0) + 1
        return counts
    
    def _count_by_difficulty(self) -> Dict[str, int]:
        """Count questions by difficulty"""
        counts = {}
        for q in self.question_bank:
            counts[q.difficulty] = counts.get(q.difficulty, 0) + 1
        return counts
    
    def _calculate_time_spent(self, start: str, end: str) -> int:
        """Calculate time spent in seconds"""
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            return int((end_dt - start_dt).total_seconds())
        except:
            return 0
