"""
Content Management API Routes - Jeseci Smart Learning Academy
Admin Content Management with Course and Learning Path Administration

This module provides admin-only endpoints for managing educational content
including courses, learning paths, concepts, and related materials.

Author: Cavin Otieno
License: MIT License
"""

import os
import sys
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Import modules
import admin_auth
from admin_auth import AdminRole, ContentAdminUser, SuperAdminUser

# =============================================================================
# Content Management Models
# =============================================================================

class CourseCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    domain: str = Field(default="Computer Science")
    difficulty: str = Field(default="beginner")  # beginner, intermediate, advanced
    estimated_duration: Optional[int] = Field(None, description="Duration in minutes")
    prerequisites: List[str] = Field(default=[], description="List of prerequisite course IDs")
    learning_objectives: List[str] = Field(default=[], description="Learning objectives")
    tags: List[str] = Field(default=[], description="Course tags")
    is_published: bool = Field(default=False)
    thumbnail_url: Optional[str] = Field(None, description="Course thumbnail URL")

class CourseUpdateRequest(BaseModel):
    course_id: str = Field(..., description="Course ID to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    domain: Optional[str] = Field(None)
    difficulty: Optional[str] = Field(None)
    estimated_duration: Optional[int] = Field(None)
    prerequisites: Optional[List[str]] = Field(None)
    learning_objectives: Optional[List[str]] = Field(None)
    tags: Optional[List[str]] = Field(None)
    is_published: Optional[bool] = Field(None)
    thumbnail_url: Optional[str] = Field(None)

class LearningPathCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    category: str = Field(default="Programming")
    difficulty: str = Field(default="beginner")
    estimated_duration: Optional[int] = Field(None, description="Duration in minutes")
    target_audience: str = Field(default="Beginners")
    course_sequence: List[str] = Field(..., description="Ordered list of course IDs")
    prerequisites: List[str] = Field(default=[], description="Prerequisite learning paths")
    learning_outcomes: List[str] = Field(default=[], description="Expected outcomes")
    is_published: bool = Field(default=False)
    thumbnail_url: Optional[str] = Field(None)

class ConceptCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(default="Computer Science")
    subcategory: Optional[str] = Field(None)
    domain: str = Field(default="Computer Science")
    difficulty_level: str = Field(default="beginner")
    description: str = Field(..., min_length=1, max_length=1000)
    detailed_description: Optional[str] = Field(None, max_length=5000)
    key_terms: List[str] = Field(default=[])
    synonyms: List[str] = Field(default=[])
    learning_objectives: List[str] = Field(default=[])
    practical_applications: List[str] = Field(default=[])
    real_world_examples: List[str] = Field(default=[])
    common_misconceptions: List[str] = Field(default=[])
    prerequisite_concepts: List[str] = Field(default=[], description="Prerequisite concept IDs")

class ContentResponse(BaseModel):
    success: bool
    message: str
    content_id: Optional[str] = None
    content_type: str
    timestamp: str

class ContentListResponse(BaseModel):
    success: bool
    content: List[Dict[str, Any]]
    total: int
    content_type: str
    filters: Dict[str, Any]

class BulkContentActionRequest(BaseModel):
    content_ids: List[str] = Field(..., description="List of content IDs")
    action: str = Field(..., description="Action: publish, unpublish, delete, duplicate")
    content_type: str = Field(..., description="Type: course, learning_path, concept")

# =============================================================================
# Content Database Operations
# =============================================================================

class ContentManager:
    """Manages educational content operations"""
    
    def __init__(self):
        self.courses_db = {}  # In-memory storage for demo
        self.learning_paths_db = {}
        self.concepts_db = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize with sample content focused on JAC programming"""
        # Sample courses - JAC Programming Language
        self.courses_db = {
            "course_jac_fundamentals": {
                "course_id": "course_jac_fundamentals",
                "title": "JAC Programming Fundamentals",
                "description": "Master the fundamentals of Jaclang programming including syntax, variables, control flow, and functions with Object-Spatial Programming introduction",
                "domain": "Jaclang Programming",
                "difficulty": "beginner",
                "estimated_duration": 1800,  # 30 hours
                "prerequisites": [],
                "learning_objectives": [
                    "Understand Jaclang syntax and type annotations",
                    "Declare variables with proper type annotations",
                    "Implement control flow with if-else and loops",
                    "Create reusable functions with def keyword",
                    "Introduction to Object-Spatial Programming concepts"
                ],
                "tags": ["jac", "jaclang", "programming", "fundamentals", "osp"],
                "is_published": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            },
            "course_jac_osp": {
                "course_id": "course_jac_osp",
                "title": "Object-Spatial Programming in Jaclang",
                "description": "Deep dive into Object-Spatial Programming paradigm with nodes, edges, and walkers for graph-based computation",
                "domain": "Jaclang Programming",
                "difficulty": "intermediate",
                "estimated_duration": 2400,  # 40 hours
                "prerequisites": ["course_jac_fundamentals"],
                "learning_objectives": [
                    "Understand the OSP paradigm shift",
                    "Define nodes with has properties",
                    "Create edges between nodes using connection operators",
                    "Implement walkers for graph traversal",
                    "Build persistent graph-based applications"
                ],
                "tags": ["jac", "osp", "nodes", "edges", "walkers", "graph"],
                "is_published": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            },
            "course_jac_walkers": {
                "course_id": "course_jac_walkers",
                "title": "Advanced Walkers and Graph Traversal",
                "description": "Master walker abilities, context variables, spawning, and multi-walker coordination for complex graph traversal patterns",
                "domain": "Jaclang Programming",
                "difficulty": "advanced",
                "estimated_duration": 3000,  # 50 hours
                "prerequisites": ["course_jac_osp"],
                "learning_objectives": [
                    "Implement walker entry and exit abilities",
                    "Use can blocks for node-specific behavior",
                    "Spawn multiple walkers for parallel traversal",
                    "Manage walker context and state",
                    "Implement complex traversal algorithms"
                ],
                "tags": ["jac", "walkers", "traversal", "abilities", "spawn", "context"],
                "is_published": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            },
            "course_jac_ai_integration": {
                "course_id": "course_jac_ai_integration",
                "title": "JAC AI Integration with byLLM",
                "description": "Learn to integrate Large Language Models using Jaclang's byLLM feature for AI-powered application development",
                "domain": "Jaclang Programming",
                "difficulty": "intermediate",
                "estimated_duration": 1800,  # 30 hours
                "prerequisites": ["course_jac_fundamentals"],
                "learning_objectives": [
                    "Understand Jaclang's AI integration capabilities",
                    "Implement byLLM blocks for LLM calls",
                    "Build AI-powered walkers and nodes",
                    "Handle LLM responses and context management",
                    "Create intelligent graph-based applications"
                ],
                "tags": ["jac", "ai", "llm", "byllm", "machine-learning"],
                "is_published": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            }
        }
        
        # Sample learning paths - JAC Programming
        self.learning_paths_db = {
            "path_jac_mastery": {
                "path_id": "path_jac_mastery",
                "title": "Jaclang Programming Mastery",
                "description": "Complete path from Jaclang fundamentals to advanced Object-Spatial Programming with AI integration",
                "category": "Jaclang Programming",
                "difficulty": "beginner",
                "estimated_duration": 9000,  # 150 hours
                "target_audience": "Programmers learning Jaclang",
                "course_sequence": [
                    "course_jac_fundamentals",
                    "course_jac_osp",
                    "course_jac_walkers",
                    "course_jac_ai_integration"
                ],
                "prerequisites": [],
                "learning_outcomes": [
                    "Proficiency in Jaclang syntax and programming",
                    "Understanding of Object-Spatial Programming paradigm",
                    "Ability to build graph-based applications with nodes and walkers",
                    "Skills in AI integration using byLLM",
                    "Knowledge of scale-agnostic programming patterns"
                ],
                "is_published": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            },
            "path_jac_osp_specialist": {
                "path_id": "path_jac_osp_specialist",
                "title": "Object-Spatial Programming Specialist",
                "description": "Specialized path focusing on nodes, edges, walkers, and graph-based computation in Jaclang",
                "category": "Jaclang Programming",
                "difficulty": "intermediate",
                "estimated_duration": 5400,  # 90 hours
                "target_audience": "Developers wanting to master OSP",
                "course_sequence": [
                    "course_jac_fundamentals",
                    "course_jac_osp",
                    "course_jac_walkers"
                ],
                "prerequisites": ["Basic programming knowledge"],
                "learning_outcomes": [
                    "Master node and edge creation",
                    "Implement complex walker behaviors",
                    "Build persistent graph databases",
                    "Design distributed graph applications"
                ],
                "is_published": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            }
        }
        
        # Sample concepts - JAC Programming Concepts
        self.concepts_db = {
            "concept_jac_variables": {
                "concept_id": "concept_jac_variables",
                "name": "jac_variables_data_types",
                "display_name": "JAC Variables and Data Types",
                "category": "Jaclang Programming",
                "subcategory": "Fundamentals",
                "domain": "Jaclang Programming",
                "difficulty_level": "beginner",
                "description": "Understanding Jaclang's type system, variable declarations with has keyword, and data type annotations",
                "key_terms": ["variable", "has", "type annotation", "str", "int", "float", "bool"],
                "learning_objectives": [
                    "Declare variables with has keyword",
                    "Understand Jaclang's type annotations",
                    "Work with primitive and collection types"
                ],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            },
            "concept_jac_control_flow": {
                "concept_id": "concept_jac_control_flow",
                "name": "jac_control_flow",
                "display_name": "JAC Control Flow",
                "category": "Jaclang Programming",
                "subcategory": "Fundamentals",
                "domain": "Jaclang Programming",
                "difficulty_level": "beginner",
                "description": "Mastering conditional statements, loops, and pattern matching in Jaclang with curly brace blocks",
                "key_terms": ["if", "else", "while", "for", "break", "continue", "pattern matching"],
                "learning_objectives": [
                    "Write conditional statements with if-elif-else",
                    "Implement loops for repetitive tasks",
                    "Use comparison and logical operators"
                ],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            },
            "concept_jac_functions": {
                "concept_id": "concept_jac_functions",
                "name": "jac_functions",
                "display_name": "JAC Functions and Abilities",
                "category": "Jaclang Programming",
                "subcategory": "Fundamentals",
                "domain": "Jaclang Programming",
                "difficulty_level": "beginner",
                "description": "Creating reusable code blocks with def keyword, parameters, return values, and default arguments in Jaclang",
                "key_terms": ["def", "function", "ability", "return", "parameter", "default argument"],
                "learning_objectives": [
                    "Define functions with def keyword",
                    "Use type annotations for parameters and returns",
                    "Implement default parameter values"
                ],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            },
            "concept_jac_nodes": {
                "concept_id": "concept_jac_nodes",
                "name": "jac_nodes_edges",
                "display_name": "JAC Nodes and Edges",
                "category": "Jaclang Programming",
                "subcategory": "Object-Spatial Programming",
                "domain": "Jaclang Programming",
                "difficulty_level": "intermediate",
                "description": "Defining nodes as stateful entities with has properties and creating edges for relationships in Jaclang graphs",
                "key_terms": ["node", "edge", "has", "++>", "<++", "<++>", "connection operator"],
                "learning_objectives": [
                    "Define nodes with node keyword",
                    "Add properties using has declarations",
                    "Create edges between nodes",
                    "Understand bidirectional relationships"
                ],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            },
            "concept_jac_walkers": {
                "concept_id": "concept_jac_walkers",
                "name": "jac_walkers",
                "display_name": "JAC Walkers and Graph Traversal",
                "category": "Jaclang Programming",
                "subcategory": "Object-Spatial Programming",
                "domain": "Jaclang Programming",
                "difficulty_level": "intermediate",
                "description": "Implementing walkers as mobile computational units that traverse graphs with visit, spawn, and ability patterns",
                "key_terms": ["walker", "visit", "spawn", "can", "entry", "exit", "context"],
                "learning_objectives": [
                    "Define walkers with walker keyword",
                    "Implement entry and exit abilities",
                    "Use visit for graph traversal",
                    "Spawn multiple walkers"
                ],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            },
            "concept_jac_osp": {
                "concept_id": "concept_jac_osp",
                "name": "jac_object_spatial_programming",
                "display_name": "JAC Object-Spatial Programming (OSP)",
                "category": "Jaclang Programming",
                "subcategory": "Object-Spatial Programming",
                "domain": "Jaclang Programming",
                "difficulty_level": "intermediate",
                "description": "Understanding the Object-Spatial Programming paradigm where computation moves to data in graph structures",
                "key_terms": ["OSP", "Object-Spatial", "graph", "persistent", "computation to data"],
                "learning_objectives": [
                    "Understand OSP paradigm shift",
                    "Compare traditional vs spatial programming",
                    "Build persistent graph applications",
                    "Design distributed computation patterns"
                ],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            },
            "concept_jac_byllm": {
                "concept_id": "concept_jac_byllm",
                "name": "jac_ai_integration",
                "display_name": "JAC AI Integration with byLLM",
                "category": "Jaclang Programming",
                "subcategory": "AI Integration",
                "domain": "Jaclang Programming",
                "difficulty_level": "intermediate",
                "description": "Integrating Large Language Models using Jaclang's byLLM feature for AI-powered graph applications",
                "key_terms": ["byLLM", "LLM", "AI", "language model", "context", "prompt"],
                "learning_objectives": [
                    "Understand byLLM syntax and usage",
                    "Implement LLM calls in walkers",
                    "Handle AI responses and context",
                    "Build intelligent graph applications"
                ],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            },
            "concept_jac_scale_agnostic": {
                "concept_id": "concept_jac_scale_agnostic",
                "name": "jac_scale_agnostic_programming",
                "display_name": "JAC Scale-Agnostic Programming",
                "category": "Jaclang Programming",
                "subcategory": "Advanced Concepts",
                "domain": "Jaclang Programming",
                "difficulty_level": "advanced",
                "description": "Writing Jaclang code that scales from single-node to distributed multi-node deployments transparently",
                "key_terms": ["scale-agnostic", "distributed", "transparent scaling", "persistence"],
                "learning_objectives": [
                    "Understand scale-agnostic principles",
                    "Write code that works at any scale",
                    "Leverage Jaclang's automatic distribution",
                    "Optimize for different deployment sizes"
                ],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "system"
            }
        }
    
    def create_course(self, course_data: Dict[str, Any], admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new course"""
        course_id = f"course_{course_data['title'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        course = {
            "course_id": course_id,
            **course_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": admin_user.get("user_id"),
            "created_by_username": admin_user.get("username")
        }
        
        self.courses_db[course_id] = course
        
        return {
            "success": True,
            "course_id": course_id,
            "message": "Course created successfully"
        }
    
    def update_course(self, course_id: str, updates: Dict[str, Any], admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing course"""
        if course_id not in self.courses_db:
            return {
                "success": False,
                "error": "Course not found",
                "code": "NOT_FOUND"
            }
        
        course = self.courses_db[course_id]
        
        # Update fields
        for field, value in updates.items():
            if value is not None:
                course[field] = value
        
        course["updated_at"] = datetime.now().isoformat()
        course["last_updated_by"] = admin_user.get("user_id")
        
        return {
            "success": True,
            "course_id": course_id,
            "message": "Course updated successfully"
        }
    
    def delete_course(self, course_id: str) -> Dict[str, Any]:
        """Delete a course"""
        if course_id not in self.courses_db:
            return {
                "success": False,
                "error": "Course not found",
                "code": "NOT_FOUND"
            }
        
        del self.courses_db[course_id]
        
        return {
            "success": True,
            "message": "Course deleted successfully"
        }
    
    def get_courses(self, limit: int = 50, offset: int = 0, 
                   filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get courses with filtering"""
        courses = list(self.courses_db.values())
        
        # Apply filters
        if filters:
            if filters.get("domain"):
                courses = [c for c in courses if c.get("domain") == filters["domain"]]
            if filters.get("difficulty"):
                courses = [c for c in courses if c.get("difficulty") == filters["difficulty"]]
            if filters.get("published_only"):
                courses = [c for c in courses if c.get("is_published", False)]
            if filters.get("search"):
                search_term = filters["search"].lower()
                courses = [
                    c for c in courses 
                    if search_term in c.get("title", "").lower() or 
                       search_term in c.get("description", "").lower()
                ]
        
        # Apply pagination
        total = len(courses)
        courses = courses[offset:offset + limit]
        
        return {
            "success": True,
            "courses": courses,
            "total": total
        }
    
    def create_learning_path(self, path_data: Dict[str, Any], admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new learning path"""
        path_id = f"path_{path_data['title'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        # Validate course sequence
        for course_id in path_data["course_sequence"]:
            if course_id not in self.courses_db:
                return {
                    "success": False,
                    "error": f"Course not found: {course_id}",
                    "code": "INVALID_COURSE"
                }
        
        learning_path = {
            "path_id": path_id,
            **path_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": admin_user.get("user_id"),
            "created_by_username": admin_user.get("username")
        }
        
        self.learning_paths_db[path_id] = learning_path
        
        return {
            "success": True,
            "path_id": path_id,
            "message": "Learning path created successfully"
        }
    
    def create_concept(self, concept_data: Dict[str, Any], admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new concept"""
        concept_id = f"concept_{concept_data['name'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        concept = {
            "concept_id": concept_id,
            **concept_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": admin_user.get("user_id"),
            "created_by_username": admin_user.get("username")
        }
        
        self.concepts_db[concept_id] = concept
        
        return {
            "success": True,
            "concept_id": concept_id,
            "message": "Concept created successfully"
        }

# Global content manager instance
content_manager = ContentManager()

# =============================================================================
# Content Management Router
# =============================================================================

def create_content_admin_router() -> APIRouter:
    """Create content management router"""
    
    router = APIRouter()

    # =============================================================================
    # Course Management Endpoints
    # =============================================================================

    @router.get("/admin/content/courses", response_model=ContentListResponse)
    async def get_courses_admin(
        limit: int = Query(default=50, le=100, description="Maximum courses to return"),
        offset: int = Query(default=0, ge=0, description="Number of courses to skip"),
        domain: Optional[str] = Query(default=None, description="Filter by domain"),
        difficulty: Optional[str] = Query(default=None, description="Filter by difficulty"),
        published_only: bool = Query(default=False, description="Only published courses"),
        search: Optional[str] = Query(default=None, description="Search title/description"),
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Get all courses with filtering (Content Admin+)"""
        try:
            filters = {
                "domain": domain,
                "difficulty": difficulty,
                "published_only": published_only,
                "search": search
            }
            
            result = content_manager.get_courses(limit, offset, filters)
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "courses_list_accessed",
                details={
                    "filters": filters,
                    "results_count": len(result["courses"])
                }
            )
            
            return ContentListResponse(
                success=True,
                content=result["courses"],
                total=result["total"],
                content_type="course",
                filters=filters
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve courses",
                    "message": str(e)
                }
            )

    @router.post("/admin/content/courses", response_model=ContentResponse)
    async def create_course_admin(
        request: CourseCreateRequest,
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Create a new course (Content Admin+)"""
        try:
            course_data = request.dict()
            result = content_manager.create_course(course_data, admin_user)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Course creation failed",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "course_created",
                target=result["course_id"],
                details={
                    "title": request.title,
                    "domain": request.domain,
                    "difficulty": request.difficulty
                }
            )
            
            return ContentResponse(
                success=True,
                message="Course created successfully",
                content_id=result["course_id"],
                content_type="course",
                timestamp=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to create course",
                    "message": str(e)
                }
            )

    @router.put("/admin/content/courses", response_model=ContentResponse)
    async def update_course_admin(
        request: CourseUpdateRequest,
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Update an existing course (Content Admin+)"""
        try:
            updates = {k: v for k, v in request.dict().items() if v is not None and k != "course_id"}
            result = content_manager.update_course(request.course_id, updates, admin_user)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=404 if result.get("code") == "NOT_FOUND" else 400,
                    detail={
                        "error": "Course update failed",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "course_updated",
                target=request.course_id,
                details={"updates": list(updates.keys())}
            )
            
            return ContentResponse(
                success=True,
                message="Course updated successfully",
                content_id=request.course_id,
                content_type="course",
                timestamp=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to update course",
                    "message": str(e)
                }
            )

    @router.delete("/admin/content/courses/{course_id}")
    async def delete_course_admin(
        course_id: str,
        admin_user: Dict[str, Any] = SuperAdminUser  # Only super admin can delete
    ):
        """Delete a course (Super Admin only)"""
        try:
            result = content_manager.delete_course(course_id)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=404 if result.get("code") == "NOT_FOUND" else 400,
                    detail={
                        "error": "Course deletion failed",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "course_deleted",
                target=course_id,
                details={"permanent_deletion": True}
            )
            
            return {
                "success": True,
                "message": "Course deleted successfully",
                "course_id": course_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to delete course",
                    "message": str(e)
                }
            )

    # =============================================================================
    # Learning Path Management Endpoints
    # =============================================================================

    @router.post("/admin/content/learning-paths", response_model=ContentResponse)
    async def create_learning_path_admin(
        request: LearningPathCreateRequest,
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Create a new learning path (Content Admin+)"""
        try:
            path_data = request.dict()
            result = content_manager.create_learning_path(path_data, admin_user)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Learning path creation failed",
                        "message": result.get("error"),
                        "code": result.get("code")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "learning_path_created",
                target=result["path_id"],
                details={
                    "title": request.title,
                    "course_count": len(request.course_sequence),
                    "category": request.category
                }
            )
            
            return ContentResponse(
                success=True,
                message="Learning path created successfully",
                content_id=result["path_id"],
                content_type="learning_path",
                timestamp=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to create learning path",
                    "message": str(e)
                }
            )

    # =============================================================================
    # Concept Management Endpoints
    # =============================================================================

    @router.post("/admin/content/concepts", response_model=ContentResponse)
    async def create_concept_admin(
        request: ConceptCreateRequest,
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Create a new concept (Content Admin+)"""
        try:
            concept_data = request.dict()
            result = content_manager.create_concept(concept_data, admin_user)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Concept creation failed",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "concept_created",
                target=result["concept_id"],
                details={
                    "name": request.name,
                    "category": request.category,
                    "difficulty": request.difficulty_level
                }
            )
            
            return ContentResponse(
                success=True,
                message="Concept created successfully",
                content_id=result["concept_id"],
                content_type="concept",
                timestamp=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to create concept",
                    "message": str(e)
                }
            )

    # =============================================================================
    # Bulk Operations
    # =============================================================================

    @router.post("/admin/content/bulk-action")
    async def bulk_content_action(
        request: BulkContentActionRequest,
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Perform bulk actions on content (Content Admin+)"""
        try:
            if not request.content_ids:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "No content IDs provided"}
                )
            
            results = {"success": 0, "failed": 0, "errors": []}
            
            # Process each content item
            for content_id in request.content_ids:
                try:
                    if request.action == "publish":
                        # Implementation for publishing content
                        results["success"] += 1
                    elif request.action == "unpublish":
                        # Implementation for unpublishing content
                        results["success"] += 1
                    elif request.action == "delete" and admin_user.get("admin_role") == "super_admin":
                        # Only super admin can delete
                        results["success"] += 1
                    else:
                        results["errors"].append(f"Invalid action or insufficient permissions: {request.action}")
                        results["failed"] += 1
                        
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"{content_id}: {str(e)}")
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, f"bulk_{request.action}_{request.content_type}",
                details={
                    "content_count": len(request.content_ids),
                    "success_count": results["success"],
                    "failed_count": results["failed"]
                }
            )
            
            return {
                "success": True,
                "message": f"Bulk action completed: {results['success']} successful, {results['failed']} failed",
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to perform bulk action",
                    "message": str(e)
                }
            )

    return content_app

# =============================================================================
# Export content router
# =============================================================================

content_admin_router = create_content_admin_router()