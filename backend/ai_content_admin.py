"""
AI Content Management System - Jeseci Smart Learning Academy
AI-Generated Content Review, Quality Control, and Management

This module provides admin endpoints for managing AI-generated content,
including review workflows, quality scoring, and content approval processes.

Author: Cavin Otieno
License: MIT License
"""

import os
import sys
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import uuid
import json
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Import modules
import admin_auth
from admin_auth import AdminRole, ContentAdminUser, SuperAdminUser

# =============================================================================
# AI Content Management Models
# =============================================================================

class ContentStatus(str, Enum):
    GENERATED = "generated"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    PUBLISHED = "published"

class ContentQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

class AIContentType(str, Enum):
    LESSON = "lesson"
    QUIZ = "quiz"
    EXPLANATION = "explanation"
    EXAMPLE = "example"
    EXERCISE = "exercise"

class AIContentReviewRequest(BaseModel):
    content_id: str = Field(..., description="AI content ID to review")
    status: ContentStatus = Field(..., description="New status for the content")
    quality_score: Optional[float] = Field(None, ge=0, le=10, description="Quality score 0-10")
    quality_rating: Optional[ContentQuality] = Field(None, description="Quality rating")
    reviewer_feedback: str = Field(..., min_length=1, description="Reviewer feedback/comments")
    requires_revision: bool = Field(default=False, description="Whether content needs revision")
    revision_notes: Optional[str] = Field(None, description="Specific revision requirements")

class AIContentGenerateRequest(BaseModel):
    content_type: AIContentType = Field(..., description="Type of content to generate")
    concept_name: str = Field(..., min_length=1, description="Concept or topic name")
    domain: Optional[str] = Field(None, description="Subject domain (optional - will be auto-detected from concept)")
    difficulty: str = Field(default="beginner", description="Difficulty level")
    target_audience: str = Field(default="students", description="Target audience")
    learning_objectives: List[str] = Field(default=[], description="Specific learning objectives")
    context: Optional[str] = Field(None, description="Additional context for generation")
    style_preferences: Optional[Dict[str, Any]] = Field(None, description="Style preferences")

class AIContentResponse(BaseModel):
    success: bool
    content_id: Optional[str] = None
    content_type: str
    status: str
    message: str
    timestamp: str

class AIContentListResponse(BaseModel):
    success: bool
    content: List[Dict[str, Any]]
    total: int
    filters: Dict[str, Any]
    statistics: Dict[str, Any]

class AIUsageStatsResponse(BaseModel):
    success: bool
    period: str
    usage_statistics: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    performance_metrics: Dict[str, Any]

class AvailableDomainsResponse(BaseModel):
    success: bool
    domains: List[str]
    source: str
    message: str

# =============================================================================
# AI Content Database Manager
# =============================================================================

class AIContentManager:
    """Manages AI-generated content and review processes"""

    # Domain mapping for dynamic domain detection based on concept keywords
    DOMAIN_KEYWORDS = {
        "jac": "Jac Programming",
        "node": "Jac Programming",
        "walker": "Jac Programming",
        "edge": "Jac Programming",
        "osp": "Jac Programming",
        "graph": "Jac Programming",
        "python": "Jac Programming",
        "programming": "Jac Programming",
        "algorithm": "Jac Programming",
        "software": "Jac Programming",
        "computer": "Jac Programming",
    }

    def __init__(self):
        self.ai_content_db = {}  # In-memory storage for demo
        self.ai_usage_stats = {}
        self._init_sample_data()

    def get_domain_for_concept(self, concept_name: str, provided_domain: Optional[str] = None) -> str:
        """
        Dynamically determine the domain for a concept.
        If domain is provided, use it. Otherwise, detect from concept name.
        Falls back to Jac Programming as default since this is a Jac-focused platform.
        """
        if provided_domain:
            return provided_domain

        # Normalize concept name for matching
        concept_lower = concept_name.lower()

        # Check keyword mappings
        for keyword, domain in self.DOMAIN_KEYWORDS.items():
            if keyword in concept_lower:
                return domain

        # Default to Jac Programming platform domain
        return "Jac Programming"

    def get_available_domains(self) -> List[str]:
        """Get list of available domains from the system"""
        # Return domains that are available in the system
        # This could be extended to query the actual database
        return list(set(self.DOMAIN_KEYWORDS.values())) + ["Jac Programming"]

    def _init_sample_data(self):
        """Initialize with sample AI content for Jac programming curriculum"""
        now = datetime.now()

        # Sample AI-generated content for Jaclang concepts
        sample_content = {
            "ai_content_001": {
                "content_id": "ai_content_001",
                "content_type": "lesson",
                "concept_name": "Jac Nodes",
                "domain": "Jac Programming",
                "difficulty": "beginner",
                "status": "pending_review",
                "quality_score": None,
                "quality_rating": None,
                "generated_at": now.isoformat(),
                "reviewed_at": None,
                "reviewer_id": None,
                "reviewer_feedback": None,
                "content_data": {
                    "title": "Understanding Jac Nodes",
                    "content": "Nodes are the fundamental building blocks in Jaclang, representing entities with attributes and behaviors. Each node can contain data fields and capabilities that define its characteristics and interactions within the graph.",
                    "examples": [
                        "node person { has name: str, age: int; }",
                        "node document { has title: str, content: str, author: person; }",
                        "node machine { has status: str, uptime: float; }"
                    ],
                    "key_points": [
                        "Nodes represent entities in the object-spatial programming model",
                        "Each node can have typed attributes using 'has' declarations",
                        "Nodes can reference other nodes as attributes, enabling graph structures",
                        "Node definitions serve as blueprints for creating node instances"
                    ]
                },
                "ai_model": "gpt-4",
                "generation_cost": 0.045,
                "word_count": 350,
                "estimated_reading_time": 2
            },
            "ai_content_002": {
                "content_id": "ai_content_002",
                "content_type": "quiz",
                "concept_name": "Jac Walkers",
                "domain": "Jac Programming",
                "difficulty": "intermediate",
                "status": "approved",
                "quality_score": 8.5,
                "quality_rating": "good",
                "generated_at": (now - timedelta(days=2)).isoformat(),
                "reviewed_at": (now - timedelta(days=1)).isoformat(),
                "reviewer_id": "admin_reviewer_001",
                "reviewer_feedback": "Well-structured quiz with clear questions and good coverage of Jac walker concepts.",
                "content_data": {
                    "title": "Jac Walkers Assessment",
                    "questions": [
                        {
                            "question": "What is the primary purpose of a walker in Jaclang?",
                            "options": [
                                "To store data persistently",
                                "To traverse and perform actions on node graphs",
                                "To compile Jac code to Python",
                                "To define user interface elements"
                            ],
                            "correct_answer": 1
                        },
                        {
                            "question": "Which keyword is used to spawn a new walker instance in Jac?",
                            "options": ["create", "spawn", "new", "init"],
                            "correct_answer": 1
                        },
                        {
                            "question": "Walkers can only traverse nodes in a single direction along edges.",
                            "options": ["True", "False"],
                            "correct_answer": 1
                        }
                    ]
                },
                "ai_model": "gpt-4",
                "generation_cost": 0.032,
                "word_count": 250
            },
            "ai_content_003": {
                "content_id": "ai_content_003",
                "content_type": "exercise",
                "concept_name": "Jac Edges",
                "domain": "Jac Programming",
                "difficulty": "beginner",
                "status": "approved",
                "quality_score": 9.0,
                "quality_rating": "excellent",
                "generated_at": (now - timedelta(days=5)).isoformat(),
                "reviewed_at": (now - timedelta(days=4)).isoformat(),
                "reviewer_id": "admin_reviewer_002",
                "reviewer_feedback": "Excellent exercise that clearly demonstrates edge creation and traversal.",
                "content_data": {
                    "title": "Jac Edge Creation Exercise",
                    "content": "Create edges to establish relationships between nodes and enable walker traversal.",
                    "exercises": [
                        {
                            "task": "Create an edge 'knows' connecting two person nodes",
                            "hint": "Use the 'edge' keyword with 'connects' to define the relationship",
                            "solution": "edge knows { connects person, person; }"
                        },
                        {
                            "task": "Write a walker that traverses the 'knows' edge",
                            "hint": "Use 'traverse' or 'walk' with the edge name",
                            "solution": "walker find_connections { take [knows]; }"
                        }
                    ],
                    "key_points": [
                        "Edges define relationships between nodes in the graph",
                        "Edges can be directed or undirected depending on use case",
                        "Walkers traverse edges to navigate between connected nodes",
                        "Edge definitions specify which node types they connect"
                    ]
                },
                "ai_model": "gpt-4",
                "generation_cost": 0.038,
                "word_count": 280
            }
        }

        self.ai_content_db = sample_content

        # Sample usage statistics - these would be calculated from AI content database in production
        self.ai_usage_stats = {
            "daily": {},  # Dynamic: Aggregate from daily content generation logs
            "monthly": {}  # Dynamic: Aggregate from monthly content generation logs
        }

    def calculate_ai_usage_stats(self, period: str = "monthly") -> Dict[str, Any]:
        """
        Calculate AI usage statistics dynamically from actual content generation data.
        In production, this would query the AI content database.
        """
        # Get all AI-generated content
        all_content = list(self.ai_content_db.values())

        if not all_content:
            return {
                "daily": {},
                "monthly": {}
            }

        # Calculate statistics from actual content
        now = datetime.now()
        approved_count = len([c for c in all_content if c.get("status") == ContentStatus.APPROVED.value])
        total_quality = sum(c.get("quality_score", 0) for c in all_content if c.get("quality_score"))
        quality_count = len([c for c in all_content if c.get("quality_score")])
        avg_quality = total_quality / quality_count if quality_count > 0 else 0.0
        approval_rate = approved_count / len(all_content) if all_content else 0.0

        # Calculate daily stats
        today = str(now.date())
        daily_stats = {
            today: {
                "content_generated": len(all_content),
                "total_cost": sum(c.get("generation_cost", 0) for c in all_content),
                "avg_quality_score": round(avg_quality, 1),
                "approval_rate": round(approval_rate, 2)
            }
        }

        # Calculate monthly stats
        month_key = f"{now.year}-{now.month:02d}"
        monthly_stats = {
            month_key: {
                "content_generated": len(all_content),
                "total_cost": round(sum(c.get("generation_cost", 0) for c in all_content), 2),
                "avg_quality_score": round(avg_quality, 1),
                "approval_rate": round(approval_rate, 2)
            }
        }

        return {
            "daily": daily_stats,
            "monthly": monthly_stats
        }

    def refresh_ai_usage_stats(self) -> Dict[str, Any]:
        """Refresh AI usage statistics from actual data"""
        self.ai_usage_stats = self.calculate_ai_usage_stats()
        return {
            "success": True,
            "stats": self.ai_usage_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_content(self, request_data: Dict[str, Any], admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """Generate new AI content with dynamic domain detection"""
        content_id = f"ai_content_{uuid.uuid4().hex[:12]}"

        # Dynamically determine domain from concept name
        domain = self.get_domain_for_concept(
            request_data.get('concept_name', ''),
            request_data.get('domain')
        )

        # Simulate AI content generation
        content_data = {
            "title": f"AI Generated: {request_data['concept_name']}",
            "content": f"AI-generated content about {request_data['concept_name']} at {request_data['difficulty']} level...",
            "generated_for_audience": request_data.get('target_audience', 'students'),
            "learning_objectives": request_data.get('learning_objectives', [])
        }
        
        # Create content record
        ai_content = {
            "content_id": content_id,
            "content_type": request_data['content_type'],
            "concept_name": request_data['concept_name'],
            "domain": domain,  # Use dynamically determined domain
            "difficulty": request_data['difficulty'],
            "status": ContentStatus.PENDING_REVIEW,
            "quality_score": None,
            "quality_rating": None,
            "generated_at": datetime.now().isoformat(),
            "generated_by": admin_user.get("user_id"),
            "reviewer_id": None,
            "reviewer_feedback": None,
            "content_data": content_data,
            "ai_model": "gpt-4",  # Simulated
            "generation_cost": 0.035,  # Simulated
            "word_count": len(content_data['content']),
            "target_audience": request_data.get('target_audience'),
            "context": request_data.get('context')
        }
        
        self.ai_content_db[content_id] = ai_content
        
        return {
            "success": True,
            "content_id": content_id,
            "status": ContentStatus.PENDING_REVIEW,
            "message": "AI content generated successfully and is pending review"
        }
    
    def review_content(self, content_id: str, review_data: Dict[str, Any], reviewer: Dict[str, Any]) -> Dict[str, Any]:
        """Review AI-generated content"""
        if content_id not in self.ai_content_db:
            return {
                "success": False,
                "error": "AI content not found",
                "code": "NOT_FOUND"
            }
        
        content = self.ai_content_db[content_id]
        
        # Update content with review data
        content.update({
            "status": review_data['status'],
            "quality_score": review_data.get('quality_score'),
            "quality_rating": review_data.get('quality_rating'),
            "reviewed_at": datetime.now().isoformat(),
            "reviewer_id": reviewer.get("user_id"),
            "reviewer_feedback": review_data['reviewer_feedback'],
            "requires_revision": review_data.get('requires_revision', False),
            "revision_notes": review_data.get('revision_notes')
        })
        
        return {
            "success": True,
            "content_id": content_id,
            "new_status": review_data['status'],
            "message": "Content review completed successfully"
        }
    
    def get_ai_content(self, limit: int = 50, offset: int = 0, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get AI content with filtering"""
        content_list = list(self.ai_content_db.values())
        
        # Apply filters
        if filters:
            if filters.get("status"):
                content_list = [c for c in content_list if c.get("status") == filters["status"]]
            if filters.get("content_type"):
                content_list = [c for c in content_list if c.get("content_type") == filters["content_type"]]
            if filters.get("quality_rating"):
                content_list = [c for c in content_list if c.get("quality_rating") == filters["quality_rating"]]
            if filters.get("needs_review"):
                content_list = [c for c in content_list if c.get("status") == "pending_review"]
        
        # Sort by generation date (newest first)
        content_list.sort(key=lambda x: x.get("generated_at", ""), reverse=True)
        
        # Statistics
        total = len(content_list)
        status_counts = {}
        quality_counts = {}
        
        for content in content_list:
            status = content.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            
            quality = content.get("quality_rating")
            if quality:
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        # Apply pagination
        paginated_content = content_list[offset:offset + limit]
        
        return {
            "success": True,
            "content": paginated_content,
            "total": total,
            "statistics": {
                "status_distribution": status_counts,
                "quality_distribution": quality_counts,
                "avg_quality_score": sum(c.get("quality_score", 0) for c in content_list if c.get("quality_score")) / max(len([c for c in content_list if c.get("quality_score")]), 1)
            }
        }
    
    def get_usage_statistics(self, period: str = "monthly") -> Dict[str, Any]:
        """Get AI usage statistics and cost analysis"""
        stats_data = self.ai_usage_stats.get(period, {})
        
        if not stats_data:
            return {
                "success": False,
                "error": f"No statistics available for period: {period}"
            }
        
        # Calculate aggregated metrics
        total_content = sum(data.get("content_generated", 0) for data in stats_data.values())
        total_cost = sum(data.get("total_cost", 0) for data in stats_data.values())
        avg_quality = sum(data.get("avg_quality_score", 0) for data in stats_data.values()) / max(len(stats_data), 1)
        avg_approval = sum(data.get("approval_rate", 0) for data in stats_data.values()) / max(len(stats_data), 1)
        
        return {
            "success": True,
            "period": period,
            "usage_statistics": {
                "total_content_generated": total_content,
                "average_daily_generation": total_content / max(len(stats_data), 1),
                "content_types_breakdown": {
                    "lessons": int(total_content * 0.4),
                    "quizzes": int(total_content * 0.3),
                    "explanations": int(total_content * 0.2),
                    "examples": int(total_content * 0.1)
                }
            },
            "cost_analysis": {
                "total_cost": round(total_cost, 2),
                "average_cost_per_content": round(total_cost / max(total_content, 1), 4),
                "projected_monthly_cost": round(total_cost * 30 / max(len(stats_data), 1), 2)
            },
            "performance_metrics": {
                "average_quality_score": round(avg_quality, 2),
                "approval_rate": round(avg_approval * 100, 1),
                "content_efficiency": "high" if avg_quality > 7.5 and avg_approval > 0.8 else "medium"
            }
        }

# Global AI content manager instance
ai_content_manager = AIContentManager()

# =============================================================================
# AI Content Management Router
# =============================================================================

def create_ai_content_router() -> APIRouter:
    """Create AI content management router"""
    
    router = APIRouter()

    # =============================================================================
    # AI Content Generation & Management
    # =============================================================================

    @router.get("/admin/ai/content", response_model=AIContentListResponse)
    async def get_ai_content_admin(
        limit: int = Query(default=50, le=100, description="Maximum content items to return"),
        offset: int = Query(default=0, ge=0, description="Number of items to skip"),
        status: Optional[ContentStatus] = Query(default=None, description="Filter by status"),
        content_type: Optional[AIContentType] = Query(default=None, description="Filter by content type"),
        quality_rating: Optional[ContentQuality] = Query(default=None, description="Filter by quality"),
        needs_review: bool = Query(default=False, description="Only content needing review"),
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Get AI-generated content with filtering (Content Admin+)"""
        try:
            filters = {
                "status": status,
                "content_type": content_type,
                "quality_rating": quality_rating,
                "needs_review": needs_review
            }
            
            result = ai_content_manager.get_ai_content(limit, offset, filters)
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "ai_content_list_accessed",
                details={
                    "filters": {k: v for k, v in filters.items() if v is not None},
                    "results_count": len(result["content"])
                }
            )
            
            return AIContentListResponse(
                success=True,
                content=result["content"],
                total=result["total"],
                filters=filters,
                statistics=result["statistics"]
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve AI content",
                    "message": str(e)
                }
            )

    @router.post("/admin/ai/generate", response_model=AIContentResponse)
    async def generate_ai_content_admin(
        request: AIContentGenerateRequest,
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Generate new AI content (Content Admin+)"""
        try:
            request_data = request.dict()
            result = ai_content_manager.generate_content(request_data, admin_user)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "AI content generation failed",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "ai_content_generated",
                target=result["content_id"],
                details={
                    "content_type": request.content_type,
                    "concept": request.concept_name,
                    "difficulty": request.difficulty
                }
            )
            
            return AIContentResponse(
                success=True,
                content_id=result["content_id"],
                content_type=request.content_type,
                status=result["status"],
                message="AI content generated successfully",
                timestamp=datetime.now().isoformat()
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to generate AI content",
                    "message": str(e)
                }
            )

    @router.post("/admin/ai/stats/refresh", response_model=AIUsageStatsResponse)
    async def refresh_ai_usage_stats_admin(
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Refresh AI usage statistics by recalculating from actual data (Content Admin+)"""
        try:
            refresh_result = ai_content_manager.refresh_ai_usage_stats()

            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "ai_stats_refreshed",
                details={"timestamp": refresh_result["timestamp"]}
            )

            # Get the refreshed statistics
            result = ai_content_manager.get_usage_statistics("monthly")

            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Failed to retrieve statistics",
                        "message": result.get("error")
                    }
                )

            return AIUsageStatsResponse(
                success=True,
                period="monthly",
                usage_statistics=result["usage_statistics"],
                cost_analysis=result["cost_analysis"],
                performance_metrics=result["performance_metrics"]
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to refresh AI usage statistics",
                    "message": str(e)
                }
            )

    @router.get("/admin/ai/domains", response_model=AvailableDomainsResponse)
    async def get_available_domains(
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Get list of available domains for AI content generation (Content Admin+)"""
        try:
            domains = ai_content_manager.get_available_domains()

            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "domains_list_accessed",
                details={"domains_count": len(domains)}
            )

            return AvailableDomainsResponse(
                success=True,
                domains=domains,
                source="dynamic_keyword_mapping",
                message="Domains are dynamically determined based on concept names. This list represents available domain categories."
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve domains",
                    "message": str(e)
                }
            )

    @router.put("/admin/ai/review", response_model=AIContentResponse)
    async def review_ai_content_admin(
        request: AIContentReviewRequest,
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Review AI-generated content (Content Admin+)"""
        try:
            review_data = request.dict()
            result = ai_content_manager.review_content(request.content_id, review_data, admin_user)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=404 if result.get("code") == "NOT_FOUND" else 400,
                    detail={
                        "error": "Content review failed",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "ai_content_reviewed",
                target=request.content_id,
                details={
                    "new_status": request.status,
                    "quality_score": request.quality_score,
                    "quality_rating": request.quality_rating,
                    "requires_revision": request.requires_revision
                }
            )
            
            return AIContentResponse(
                success=True,
                content_id=request.content_id,
                content_type="ai_content",
                status=result["new_status"],
                message="Content review completed successfully",
                timestamp=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to review AI content",
                    "message": str(e)
                }
            )

    # =============================================================================
    # AI Usage Analytics
    # =============================================================================

    @router.get("/admin/ai/analytics", response_model=AIUsageStatsResponse)
    async def get_ai_usage_stats(
        period: str = Query(default="monthly", description="Statistics period: daily, weekly, monthly"),
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Get AI usage statistics and cost analysis (Content Admin+)"""
        try:
            result = ai_content_manager.get_usage_statistics(period)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Failed to retrieve statistics",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "ai_analytics_accessed",
                details={"period": period}
            )
            
            return AIUsageStatsResponse(
                success=True,
                period=period,
                usage_statistics=result["usage_statistics"],
                cost_analysis=result["cost_analysis"],
                performance_metrics=result["performance_metrics"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve AI usage statistics",
                    "message": str(e)
                }
            )

    return ai_app

# =============================================================================
# Export AI content router
# =============================================================================

ai_content_router = create_ai_content_router()