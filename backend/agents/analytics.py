"""
Analytics Agent - Learning Metrics and Insights
Jeseci Smart Learning Academy - Sophisticated Multi-Agent Learning Platform

This module implements the Analytics Agent, which provides real-time progress
tracking, mastery metrics, learning pattern analysis, and performance reporting.
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
class MasteryRecord:
    """Record of mastery for a specific concept"""
    concept_id: str
    user_id: str
    mastery_score: float
    attempts: int
    last_attempt: str
    time_spent_minutes: int
    strength_areas: List[str]
    weak_areas: List[str]


@dataclass
class LearningMetric:
    """A single learning metric"""
    metric_id: str
    user_id: str
    metric_type: str
    value: float
    unit: str
    timestamp: str
    context: Dict[str, Any] = field(default_factory=dict)


class AnalyticsAgent(BaseAgent):
    """
    Analytics Agent for learning metrics and insights
    
    The Analytics Agent provides:
    - Real-time progress tracking
    - Mastery score calculation
    - Learning pattern analysis
    - Predictive analytics
    - Performance reporting
    - Trend identification
    
    Attributes:
        user_metrics: Stored metrics per user
        mastery_records: Mastery data per concept
        learning_sessions: Learning session data
        aggregated_stats: System-wide statistics
    """
    
    def __init__(self, agent_id: str = "analytics_agent",
                 agent_name: str = "Learning Analytics",
                 message_bus = None):
        """
        Initialize the Analytics Agent
        
        Args:
            agent_id: Unique identifier
            agent_name: Human-readable name
            message_bus: Optional message bus instance
        """
        super().__init__(agent_id, agent_name, "Analytics")
        
        # Data storage
        self.user_metrics: Dict[str, List[LearningMetric]] = defaultdict(list)
        self.mastery_records: Dict[str, Dict[str, MasteryRecord]] = defaultdict(dict)
        self.learning_sessions: List[Dict] = []
        self.achievements: Dict[str, List[Dict]] = defaultdict(list)
        
        # Aggregated statistics
        self.system_stats = {
            "total_users": 0,
            "total_sessions": 0,
            "total_content_consumed": 0,
            "average_completion_rate": 0.0,
            "popular_topics": [],
            "difficulty_distribution": {}
        }
        
        self.logger.info("Analytics Agent initialized")
    
    def _register_capabilities(self):
        """Register the capabilities of the Analytics Agent"""
        self.capabilities = [
            "progress_tracking",
            "mastery_calculation",
            "pattern_analysis",
            "predictive_analytics",
            "performance_reporting",
            "trend_identification",
            "achievement_tracking",
            "recommendation_generation"
        ]
    
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
        
        if action == "track_progress":
            return await self._track_progress(content)
        elif action == "calculate_mastery":
            return self._calculate_mastery(content)
        elif action == "get_user_analytics":
            return await self._get_user_analytics(content)
        elif action == "generate_report":
            return await self._generate_report(content)
        elif action == "identify_trends":
            return self._identify_trends(content)
        elif action == "check_achievements":
            return self._check_achievements(content)
        elif action == "get_recommendations":
            return self._get_recommendations(content)
        elif action == "log_session":
            return await self._log_session(content)
        elif action == "get_dashboard":
            return self._get_dashboard(content)
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
        
        if command == "analyze_learning_path":
            return await self._analyze_learning_path(task.parameters)
        elif command == "predict_performance":
            return self._predict_performance(task.parameters)
        elif command == "aggregate_statistics":
            return self._aggregate_statistics(task.parameters)
        elif command == "generate_insights":
            return await self._generate_insights(task.parameters)
        else:
            return {"error": f"Unknown command: {command}"}
    
    # Progress Tracking Methods
    
    async def _track_progress(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track progress for a user
        
        Args:
            content: Progress data
            
        Returns:
            Tracking result
        """
        user_id = content.get("user_id")
        metric_type = content.get("metric_type", "progress")
        value = content.get("value", 0)
        unit = content.get("unit", "%")
        context = content.get("context", {})
        
        import uuid
        
        metric = LearningMetric(
            metric_id=f"metric_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.now().isoformat(),
            context=context
        )
        
        self.user_metrics[user_id].append(metric)
        
        # Update mastery if applicable
        if metric_type == "concept_completed":
            await self._update_concept_mastery(user_id, context.get("concept_id"), value)
        
        # Update system stats
        self.system_stats["total_content_consumed"] += 1
        
        self.logger.debug(f"Progress tracked for {user_id}: {metric_type} = {value}")
        
        return {
            "success": True,
            "metric_id": metric.metric_id,
            "message": "Progress tracked successfully"
        }
    
    async def _update_concept_mastery(self, user_id: str, concept_id: str, 
                                       score: float):
        """
        Update mastery record for a concept
        
        Args:
            user_id: User identifier
            concept_id: Concept identifier
            score: Achievement score
        """
        record_key = f"{user_id}_{concept_id}"
        
        if record_key in self.mastery_records[user_id]:
            record = self.mastery_records[user_id][concept_id]
            record.mastery_score = (record.mastery_score + score) / 2
            record.attempts += 1
            record.last_attempt = datetime.now().isoformat()
        else:
            record = MasteryRecord(
                concept_id=concept_id,
                user_id=user_id,
                mastery_score=score,
                attempts=1,
                last_attempt=datetime.now().isoformat(),
                time_spent_minutes=0,
                strength_areas=[],
                weak_areas=[]
            )
            self.mastery_records[user_id][concept_id] = record
    
    # Mastery Calculation Methods
    
    def _calculate_mastery(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate mastery score for a concept
        
        Args:
            content: Calculation parameters
            
        Returns:
            Mastery calculation result
        """
        user_id = content.get("user_id")
        concept_id = content.get("concept_id")
        
        record_key = f"{user_id}_{concept_id}"
        
        if record_key not in self.mastery_records.get(user_id, {}):
            return {
                "success": True,
                "mastery": {
                    "concept_id": concept_id,
                    "score": 0.0,
                    "level": "not_started",
                    "message": "No learning activity recorded yet"
                }
            }
        
        record = self.mastery_records[user_id][concept_id]
        
        # Calculate mastery level
        score = record.mastery_score
        
        if score >= 0.9:
            level = "mastered"
        elif score >= 0.75:
            level = "advanced"
        elif score >= 0.5:
            level = "intermediate"
        elif score >= 0.25:
            level = "beginner"
        else:
            level = "introduced"
        
        # Calculate projected time to mastery
        if score < 0.9 and record.attempts > 0:
            remaining = 0.9 - score
            rate = score / record.attempts
            projected_sessions = max(1, int(remaining / rate))
        else:
            projected_sessions = 0
        
        return {
            "success": True,
            "mastery": {
                "concept_id": concept_id,
                "score": round(score, 2),
                "level": level,
                "attempts": record.attempts,
                "time_spent_minutes": record.time_spent_minutes,
                "projected_sessions_to_mastery": projected_sessions,
                "strength_areas": record.strength_areas,
                "weak_areas": record.weak_areas,
                "last_attempt": record.last_attempt
            }
        }
    
    # Analytics Methods
    
    async def _get_user_analytics(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a user
        
        Args:
            content: Request parameters
            
        Returns:
            User analytics
        """
        user_id = content.get("user_id")
        time_range = content.get("time_range", "all")
        
        metrics = self.user_metrics.get(user_id, [])
        
        # Filter by time range if specified
        if time_range != "all":
            cutoff = self._get_time_cutoff(time_range)
            metrics = [m for m in metrics if m.timestamp >= cutoff]
        
        # Calculate analytics
        total_sessions = len(set(m.session_id for m in metrics if hasattr(m, 'session_id')))
        avg_progress = sum(m.value for m in metrics if m.metric_type == "progress") / max(len([m for m in metrics if m.metric_type == "progress"]), 1)
        total_time = sum(m.value for m in metrics if m.metric_type == "time_spent")
        
        # Get mastery summary
        mastery_summary = self._get_mastery_summary(user_id)
        
        # Get achievements
        achievements = self.achievements.get(user_id, [])
        
        return {
            "success": True,
            "analytics": {
                "user_id": user_id,
                "time_range": time_range,
                "overview": {
                    "total_sessions": total_sessions,
                    "total_time_minutes": total_time,
                    "average_progress": round(avg_progress, 2),
                    "concepts_completed": mastery_summary["mastered"] + mastery_summary["advanced"]
                },
                "mastery": mastery_summary,
                "achievements": {
                    "earned": len([a for a in achievements if a.get("earned")]),
                    "recent": achievements[-5:] if achievements else []
                },
                "trends": self._calculate_trends(metrics),
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def _get_mastery_summary(self, user_id: str) -> Dict[str, int]:
        """
        Get summary of mastery levels for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Mastery level counts
        """
        records = self.mastery_records.get(user_id, {}).values()
        
        summary = {
            "mastered": 0,
            "advanced": 0,
            "intermediate": 0,
            "beginner": 0,
            "introduced": 0
        }
        
        for record in records:
            score = record.mastery_score
            
            if score >= 0.9:
                summary["mastered"] += 1
            elif score >= 0.75:
                summary["advanced"] += 1
            elif score >= 0.5:
                summary["intermediate"] += 1
            elif score >= 0.25:
                summary["beginner"] += 1
            else:
                summary["introduced"] += 1
        
        return summary
    
    def _calculate_trends(self, metrics: List[LearningMetric]) -> Dict[str, Any]:
        """
        Calculate trends from metrics
        
        Args:
            metrics: List of metrics
            
        Returns:
            Trend analysis
        """
        if not metrics:
            return {"trend": "no_data", "message": "Insufficient data for trend analysis"}
        
        # Group by metric type
        by_type = defaultdict(list)
        for m in metrics:
            by_type[m.metric_type].append(m)
        
        trends = {}
        
        for metric_type, type_metrics in by_type.items():
            if len(type_metrics) >= 2:
                sorted_metrics = sorted(type_metrics, key=lambda m: m.timestamp)
                
                first_half_avg = sum(m.value for m in sorted_metrics[:len(sorted_metrics)//2]) / max(len(sorted_metrics)//2, 1)
                second_half_avg = sum(m.value for m in sorted_metrics[len(sorted_metrics)//2:]) / max(len(sorted_metrics) - len(sorted_metrics)//2, 1)
                
                if second_half_avg > first_half_avg * 1.1:
                    trend = "improving"
                elif second_half_avg < first_half_avg * 0.9:
                    trend = "declining"
                else:
                    trend = "stable"
                
                trends[metric_type] = {
                    "trend": trend,
                    "change_percent": round((second_half_avg - first_half_avg) / max(first_half_avg, 0.01) * 100, 1)
                }
        
        return trends
    
    # Reporting Methods
    
    async def _generate_report(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a learning report
        
        Args:
            content: Report parameters
            
        Returns:
            Generated report
        """
        user_id = content.get("user_id")
        report_type = content.get("type", "weekly")
        start_date = content.get("start_date")
        end_date = content.get("end_date")
        
        # Get analytics data
        analytics = await self._get_user_analytics({
            "user_id": user_id,
            "time_range": report_type
        })
        
        # Generate report sections
        sections = []
        
        # Overview section
        overview = analytics["analytics"]["overview"]
        sections.append({
            "title": "Learning Overview",
            "content": f"""
            During this period, you completed {overview['concepts_completed']} concepts 
            across {overview['total_sessions']} learning sessions, spending approximately 
            {overview['total_time_minutes']} minutes learning.
            
            Your average progress was {overview['average_progress']}%.
            """.strip()
        })
        
        # Mastery section
        mastery = analytics["analytics"]["mastery"]
        sections.append({
            "title": "Concept Mastery",
            "content": f"""
            Current mastery breakdown:
            - Mastered: {mastery['mastered']} concepts
            - Advanced: {mastery['advanced']} concepts
            - Intermediate: {mastery['intermediate']} concepts
            - Beginner: {mastery['beginner']} concepts
            - Introduced: {mastery['introduced']} concepts
            """.strip()
        })
        
        # Trends section
        trends = analytics["analytics"]["trends"]
        if trends:
            sections.append({
                "title": "Learning Trends",
                "content": "Your learning progress is showing the following trends:\n" +
                          "\n".join(f"- {k}: {v['trend']} ({v['change_percent']}%)" 
                                   for k, v in trends.items())
            })
        
        report = {
            "report_id": f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": user_id,
            "type": report_type,
            "period": {
                "start": start_date or "Beginning",
                "end": end_date or datetime.now().isoformat()
            },
            "sections": sections,
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "report": report
        }
    
    def _identify_trends(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify trends in learning data
        
        Args:
            content: Request parameters
            
        Returns:
            Trend analysis
        """
        user_id = content.get("user_id")
        metrics_type = content.get("metrics_type", "all")
        
        metrics = self.user_metrics.get(user_id, [])
        
        if metrics_type != "all":
            metrics = [m for m in metrics if m.metric_type == metrics_type]
        
        return {
            "success": True,
            "trends": self._calculate_trends(metrics),
            "insights": self._generate_trend_insights(metrics)
        }
    
    def _generate_trend_insights(self, metrics: List[LearningMetric]) -> List[str]:
        """Generate insights from trend data"""
        insights = []
        
        if not metrics:
            return ["Start learning to generate insights"]
        
        trends = self._calculate_trends(metrics)
        
        for metric_type, trend_data in trends.items():
            if trend_data["trend"] == "improving":
                insights.append(f"Your {metric_type} is improving by {trend_data['change_percent']}%")
            elif trend_data["trend"] == "declining":
                insights.append(f"Attention needed: Your {metric_type} is declining")
        
        return insights
    
    # Achievement Methods
    
    def _check_achievements(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check and award achievements
        
        Args:
            content: Request parameters
            
        Returns:
            Achievement status
        """
        user_id = content.get("user_id")
        
        achievements = self.achievements.get(user_id, [])
        
        # Define achievement criteria
        criteria = [
            {
                "id": "first_lesson",
                "name": "First Steps",
                "description": "Complete your first lesson",
                "check": lambda: self._check_criteria(user_id, "lessons_completed", 1)
            },
            {
                "id": "five_lessons",
                "name": "Knowledge Seeker",
                "description": "Complete 5 lessons",
                "check": lambda: self._check_criteria(user_id, "lessons_completed", 5)
            },
            {
                "id": "week_streak",
                "name": "Consistent Learner",
                "description": "Maintain a 7-day learning streak",
                "check": lambda: self._check_criteria(user_id, "streak_days", 7)
            },
            {
                "id": "perfect_quiz",
                "name": "Quiz Master",
                "description": "Score 100% on a quiz",
                "check": lambda: self._check_criteria(user_id, "perfect_quiz", 1)
            }
        ]
        
        # Check criteria and award achievements
        earned = []
        for crit in criteria:
            earned_now = crit["check"]()
            
            if earned_now:
                achievement = {
                    "id": crit["id"],
                    "name": crit["name"],
                    "description": crit["description"],
                    "earned": True,
                    "earned_at": datetime.now().isoformat()
                }
                
                # Check if already earned
                already_earned = any(
                    a.get("id") == crit["id"] for a in achievements
                )
                
                if not already_earned:
                    achievements.append(achievement)
                    earned.append(achievement)
        
        self.achievements[user_id] = achievements
        
        return {
            "success": True,
            "achievements": {
                "total": len(achievements),
                "earned_now": earned,
                "all_achievements": achievements
            }
        }
    
    def _check_criteria(self, user_id: str, criteria_type: str, 
                        threshold: float) -> bool:
        """
        Check if user meets achievement criteria
        
        Args:
            user_id: User identifier
            criteria_type: Type of criteria
            threshold: Threshold value
            
        Returns:
            True if criteria met
        """
        metrics = self.user_metrics.get(user_id, [])
        
        # Get latest value for criteria type
        value = 0
        for m in reversed(metrics):
            if m.metric_type == criteria_type:
                value = m.value
                break
        
        return value >= threshold
    
    # Recommendation Methods
    
    def _get_recommendations(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get personalized recommendations
        
        Args:
            content: Request parameters
            
        Returns:
            Recommendations
        """
        user_id = content.get("user_id")
        
        # Get user analytics
        analytics = self.user_metrics.get(user_id, [])
        
        recommendations = []
        
        # Analyze learning patterns
        if not analytics:
            recommendations.append("Start your learning journey by exploring available courses")
        else:
            # Check mastery levels
            mastery = self._get_mastery_summary(user_id)
            
            if mastery["beginner"] > mastery["mastered"]:
                recommendations.append("Focus on completing beginner courses before advancing")
            
            if mastery["mastered"] >= 3:
                recommendations.append("You're doing great! Consider helping other learners")
            
            # Check for declining trends
            trends = self._calculate_trends(analytics)
            for metric_type, trend_data in trends.items():
                if trend_data["trend"] == "declining":
                    recommendations.append(f"Your {metric_type} needs attention. Try reviewing previous material")
        
        # Time-based recommendations
        recent_sessions = [m for m in analytics 
                          if hasattr(m, 'session_id') 
                          and self._is_recent(m.timestamp, hours=24)]
        
        if not recent_sessions:
            recommendations.append("Start learning today to maintain your progress!")
        
        return {
            "success": True,
            "recommendations": recommendations,
            "personalized_tips": [
                "Break your learning into 25-minute focused sessions",
                "Review material before starting new topics",
                "Practice with hands-on exercises"
            ]
        }
    
    # Session Methods
    
    async def _log_session(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log a learning session
        
        Args:
            content: Session data
            
        Returns:
            Log result
        """
        session_data = {
            "session_id": content.get("session_id"),
            "user_id": content.get("user_id"),
            "start_time": content.get("start_time"),
            "end_time": content.get("end_time"),
            "duration_minutes": content.get("duration_minutes", 0),
            "topics_covered": content.get("topics_covered", []),
            "progress_change": content.get("progress_change", 0),
            "engagement_score": content.get("engagement_score", 0.5),
            "logged_at": datetime.now().isoformat()
        }
        
        self.learning_sessions.append(session_data)
        
        # Update system stats
        self.system_stats["total_sessions"] += 1
        
        return {
            "success": True,
            "session_logged": session_data["session_id"]
        }
    
    # Dashboard Methods
    
    def _get_dashboard(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get dashboard data
        
        Args:
            content: Request parameters
            
        Returns:
            Dashboard data
        """
        user_id = content.get("user_id")
        
        metrics = self.user_metrics.get(user_id, [])
        mastery = self._get_mastery_summary(user_id)
        achievements = self.achievements.get(user_id, [])
        
        # Calculate quick stats
        today_metrics = [m for m in metrics if self._is_recent(m.timestamp, hours=24)]
        today_time = sum(m.value for m in today_metrics if m.metric_type == "time_spent")
        
        return {
            "success": True,
            "dashboard": {
                "quick_stats": {
                    "today_learning_minutes": today_time,
                    "current_streak": self._calculate_streak(user_id),
                    "weekly_goal_progress": self._calculate_weekly_progress(user_id)
                },
                "mastery_overview": {
                    "total_concepts": sum(mastery.values()),
                    "mastered": mastery["mastered"],
                    "in_progress": mastery["beginner"] + mastery["intermediate"]
                },
                "recent_achievements": [a for a in achievements if a.get("earned")][-3:],
                "quick_actions": [
                    {"action": "continue_learning", "label": "Continue Learning"},
                    {"action": "review", "label": "Review Previous Material"},
                    {"action": "new_topic", "label": "Explore New Topic"}
                ]
            }
        }
    
    def _calculate_streak(self, user_id: str) -> int:
        """
        Calculate learning streak for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of consecutive days
        """
        sessions = self.learning_sessions
        user_sessions = [s for s in sessions if s.get("user_id") == user_id]
        
        if not user_sessions:
            return 0
        
        # Sort by date and calculate streak
        dates = set()
        for s in user_sessions:
            session_date = s.get("start_time", "")[:10]
            if session_date:
                dates.add(session_date)
        
        # Count consecutive days from today
        streak = 0
        current = datetime.now().date()
        
        while True:
            date_str = current.strftime("%Y-%m-%d")
            if date_str in dates:
                streak += 1
                current -= timedelta(days=1)
            elif date_str < datetime.now().strftime("%Y-%m-%d"):
                break
            else:
                current -= timedelta(days=1)
        
        return streak
    
    def _calculate_weekly_progress(self, user_id: str) -> float:
        """
        Calculate weekly progress toward goal
        
        Args:
            user_id: User identifier
            
        Returns:
            Progress percentage (0-1)
        """
        goal_minutes = 300  # 5 hours per week
        
        # Get this week's learning time
        this_week = [m for m in self.user_metrics.get(user_id, []) 
                    if self._is_recent(m.timestamp, days=7)
                    and m.metric_type == "time_spent"]
        
        total_time = sum(m.value for m in this_week)
        
        return min(1.0, total_time / goal_minutes)
    
    # Helper Methods
    
    def _get_time_cutoff(self, time_range: str) -> str:
        """Get datetime cutoff for time range filtering"""
        now = datetime.now()
        
        if time_range == "day":
            cutoff = now - timedelta(days=1)
        elif time_range == "week":
            cutoff = now - timedelta(weeks=1)
        elif time_range == "month":
            cutoff = now - timedelta(days=30)
        elif time_range == "quarter":
            cutoff = now - timedelta(days=90)
        else:
            return "1970-01-01"
        
        return cutoff.isoformat()
    
    def _is_recent(self, timestamp: str, 
                   hours: int = 0, days: int = 0) -> bool:
        """Check if a timestamp is recent"""
        try:
            dt = datetime.fromisoformat(timestamp)
            now = datetime.now()
            delta = now - dt
            
            if hours > 0:
                return delta.total_seconds() < hours * 3600
            elif days > 0:
                return delta.days < days
            
            return False
        except:
            return False
    
    async def _analyze_learning_path(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a learning path for effectiveness
        
        Args:
            params: Analysis parameters
            
        Returns:
            Analysis result
        """
        path = params.get("path", [])
        user_id = params.get("user_id")
        
        if not path:
            return {
                "success": True,
                "analysis": {
                    "effectiveness": "unknown",
                    "message": "No path data to analyze"
                }
            }
        
        # Analyze completion rates
        completed = sum(1 for item in path if item.get("status") == "completed")
        total = len(path)
        
        effectiveness = "high" if completed / max(total, 1) > 0.7 else "medium" if completed / max(total, 1) > 0.4 else "low"
        
        return {
            "success": True,
            "analysis": {
                "effectiveness": effectiveness,
                "completion_rate": round(completed / max(total, 1) * 100, 1),
                "suggestions": self._generate_path_suggestions(path)
            }
        }
    
    def _generate_path_suggestions(self, path: List[Dict]) -> List[str]:
        """Generate suggestions for improving learning path"""
        suggestions = []
        
        completed = sum(1 for item in path if item.get("status") == "completed")
        
        if completed == 0:
            suggestions.append("Start with the first module to build momentum")
        elif completed < len(path) * 0.3:
            suggestions.append("Focus on completing the current module before moving on")
        
        return suggestions
    
    def _predict_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict future performance based on patterns
        
        Args:
            params: Prediction parameters
            
        Returns:
            Prediction result
        """
        user_id = params.get("user_id")
        target_topic = params.get("topic")
        
        # Get historical data
        metrics = self.user_metrics.get(user_id, [])
        
        if not metrics:
            return {
                "success": True,
                "prediction": {
                    "confidence": "low",
                    "estimated_score": 0.5,
                    "message": "Insufficient data for prediction"
                }
            }
        
        # Simple prediction based on historical performance
        avg_performance = sum(m.value for m in metrics 
                            if m.metric_type == "progress") / max(len([m for m in metrics if m.metric_type == "progress"]), 1)
        
        predicted_score = min(1.0, avg_performance + 0.1)  # Slight optimistic bias
        
        return {
            "success": True,
            "prediction": {
                "confidence": "medium",
                "estimated_score": round(predicted_score, 2),
                "recommended_study_time": "30 minutes",
                "suggested_difficulty": "intermediate" if avg_performance > 0.6 else "beginner"
            }
        }
    
    def _aggregate_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate system-wide statistics
        
        Args:
            params: Request parameters
            
        Returns:
            Aggregated statistics
        """
        return {
            "success": True,
            "statistics": {
                **self.system_stats,
                "user_count": len(self.user_metrics),
                "session_count": len(self.learning_sessions),
                "aggregated_at": datetime.now().isoformat()
            }
        }
    
    async def _generate_insights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate learning insights
        
        Args:
            params: Request parameters
            
        Returns:
            Generated insights
        """
        user_id = params.get("user_id")
        
        insights = []
        
        # Analyze recent activity
        recent_metrics = [m for m in self.user_metrics.get(user_id, []) 
                         if self._is_recent(m.timestamp, days=7)]
        
        if len(recent_metrics) < 5:
            insights.append("Learning consistently helps improve retention")
        
        # Analyze mastery distribution
        mastery = self._get_mastery_summary(user_id)
        if mastery["beginner"] > mastery["mastered"]:
            insights.append("Completing more beginner courses will help build a strong foundation")
        
        # Time-based insights
        today_metrics = [m for m in recent_metrics if self._is_recent(m.timestamp, hours=24)]
        if not today_metrics:
            insights.append("Start learning today to maintain your progress!")
        
        return {
            "success": True,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
