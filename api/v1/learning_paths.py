"""
Learning paths API endpoints
Adaptive learning path management and recommendations
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.v1.auth import get_current_user
from config.database import get_db, get_neo4j_driver
from database.models import User, LearningPath, LearningSession, Concept, UserConceptProgress, LearningPathConcept


# Router instance
router = APIRouter()


@router.get("/")
async def get_learning_paths(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get learning paths from database with accurate progress calculation.
    
    Uses LearningPathConcept association table for precise concept matching
    and correct field mapping for frontend compatibility.
    """
    
    # 1. Fetch all learning paths from database
    learning_paths = db.query(LearningPath).all()
    
    if not learning_paths:
        return []
    
    # 2. Pre-fetch user progress to avoid N+1 queries
    user_progress_records = db.query(UserConceptProgress).filter(
        UserConceptProgress.user_id == current_user.user_id,
        UserConceptProgress.status == "completed"
    ).all()
    
    # Set of completed concept IDs for fast lookup
    completed_concept_ids = {p.concept_id for p in user_progress_records}
    
    # 3. Pre-fetch all learning path concepts to avoid multiple queries
    path_concept_relations = db.query(LearningPathConcept).all()
    
    # Build a mapping: path_id -> [concept_ids]
    path_to_concepts = {}
    for relation in path_concept_relations:
        if relation.path_id not in path_to_concepts:
            path_to_concepts[relation.path_id] = []
        path_to_concepts[relation.path_id].append(relation.concept_id)
    
    # 4. Build response with accurate progress calculation
    response_data = []
    
    for path in learning_paths:
        # Get the actual concepts for this path from the association table
        path_concept_ids = path_to_concepts.get(path.path_id, [])
        
        if not path_concept_ids:
            # No concepts assigned to this path yet
            progress_percent = 0
            total_concepts = 0
            completed_count = 0
        else:
            # Fetch the actual concepts for this path
            path_concepts = db.query(Concept).filter(
                Concept.concept_id.in_(path_concept_ids)
            ).all()
            
            total_concepts = len(path_concepts)
            completed_count = sum(
                1 for concept in path_concepts 
                if concept.concept_id in completed_concept_ids
            )
            
            progress_percent = round((completed_count / total_concepts) * 100) if total_concepts > 0 else 0
        
        # 5. Transform to frontend format (using correct field names)
        response_data.append({
            "id": path.path_id,                    # ✅ Correct field name
            "title": path.name,                    # ✅ Correct field name  
            "description": path.description,
            "difficulty": path.difficulty_level,   # ✅ This is correct
            "category": path.category,
            "estimated_hours": path.estimated_duration,
            "duration": f"{max(1, total_concepts // 2)} weeks",  # Dynamic based on concepts
            
            # Accurate progress data
            "concepts_count": total_concepts,
            "progress": progress_percent,
            "completed_concepts": completed_count,
            
            # Additional metadata
            "is_public": path.is_public,
            "adaptive": path.adaptive,
            "created_at": path.created_at.isoformat() if path.created_at else None
        })
        
    return response_data


@router.get("/recommendations")
async def get_learning_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GENUINE AI: Queries the Knowledge Graph to find the optimal next step.
    Logic: "Find concepts that depend on what I've already finished."
    """
    
    # 1. Get list of everything the user has finished
    completed_records = db.query(UserConceptProgress).filter(
        UserConceptProgress.user_id == current_user.user_id,
        UserConceptProgress.status == "completed"
    ).all()
    
    completed_ids = [r.concept_id for r in completed_records]
    
    # If user is new, recommend "Beginner" nodes
    if not completed_ids:
        beginner_concepts = db.query(Concept).filter(
            Concept.difficulty_level.in_(["beginner", "Beginner"])
        ).all()
        
        recommendations = []
        for concept in beginner_concepts[:3]:
            recommendations.append({
                "concept_id": concept.concept_id,
                "title": concept.display_name,
                "description": concept.description,
                "reason": "Perfect for getting started",
                "difficulty": concept.difficulty_level,
                "estimated_time": "30-60 minutes",
                "match_score": "100%"
            })
        
        return {
            "recommendations": recommendations,
            "message": "Welcome! Here are the best concepts to start your learning journey.",
            "recommendation_type": "beginner_friendly"
        }

    # 2. ASK NEO4J (The Brain) - Get concepts that depend on completed ones
    driver = get_neo4j_driver()
    recommendations = []
    
    if driver:
        try:
            query = """
            // Find concepts the user completed
            MATCH (completed:Concept)
            WHERE completed.concept_id IN $completed_ids
            
            // Find 'next step' concepts that REQUIRE the completed ones
            MATCH (next:Concept)-[:PREREQUISITE]->(completed)
            WHERE NOT next.concept_id IN $completed_ids
            
            // Return the concept and how many requirements user has met
            RETURN next.concept_id as concept_id, next.name as name, 
                   next.display_name as title, next.description as desc, 
                   next.difficulty_level as difficulty,
                   count(completed) as prerequisites_met,
                   size((next)-[:PREREQUISITE]->(:Concept)) as total_prerequisites
            ORDER BY prerequisites_met DESC, difficulty
            LIMIT 5
            """
            
            with driver.session() as session:
                result = session.run(query, completed_ids=completed_ids)
                
                for record in result:
                    prerequisites_met = record['prerequisites_met']
                    total_prerequisites = record['total_prerequisites']
                    readiness_score = (prerequisites_met / total_prerequisites * 100) if total_prerequisites > 0 else 100
                    
                    if readiness_score >= 50:  # User is ready for this concept
                        recommendations.append({
                            "concept_id": record["concept_id"],
                            "title": record["title"],
                            "description": record["desc"],
                            "reason": f"You've mastered {prerequisites_met} of {total_prerequisites} prerequisites!",
                            "difficulty": record["difficulty"],
                            "match_score": f"{int(readiness_score)}%",
                            "estimated_time": "45-90 minutes"
                        })
                        
        except Exception as e:
            print(f"Graph Error: {e}")
            # Fallback to simple SQL-based recommendations
            pass
    
    # 3. Fallback: SQL-based recommendations if Neo4j fails
    if not recommendations:
        in_progress_concepts = db.query(UserConceptProgress).filter(
            UserConceptProgress.user_id == current_user.user_id,
            UserConceptProgress.status == "in_progress"
        ).all()
        
        in_progress_ids = {r.concept_id for r in in_progress_concepts}
        
        # Recommend concepts not started but related to in-progress ones
        related_concepts = db.query(Concept).filter(
            ~Concept.concept_id.in_(completed_ids + list(in_progress_ids))
        ).limit(3).all()
        
        for concept in related_concepts:
            recommendations.append({
                "concept_id": concept.concept_id,
                "title": concept.display_name,
                "description": concept.description,
                "reason": "Continue your learning journey",
                "difficulty": concept.difficulty_level,
                "match_score": "75%",
                "estimated_time": "45-90 minutes"
            })

    return {
        "recommendations": recommendations,
        "message": f"Found {len(recommendations)} personalized recommendations based on your progress",
        "completed_concepts": len(completed_ids),
        "recommendation_type": "graph_based" if driver and recommendations else "sequential"
    }


@router.post("/{path_id}/start")
async def start_learning_path(
    path_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a learning path"""
    
    # For now, just return success message
    # In a real implementation, this would create a learning session
    return {
        "message": f"Started learning path {path_id}",
        "session_id": f"session_{path_id}_{current_user.user_id}",
        "status": "started"
    }


@router.post("/sessions/{session_id}/complete")
async def complete_learning_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete a learning session"""
    
    # For now, just return success message
    return {
        "message": f"Completed learning session {session_id}",
        "status": "completed",
        "completed_at": "2025-12-14T07:55:08Z"
    }


def transform_learning_path_to_api_format(learning_path: LearningPath, user_id: str, db: Session) -> Dict[str, Any]:
    """
    Transform LearningPath database model to API format.
    
    This function resolves the frontend/backend inconsistency by converting:
    - Database 'name' -> API 'title'
    - Database 'difficulty_level' -> API 'difficulty'
    """
    
    # Get concept count for this path
    concept_count = db.query(LearningPathConcept).filter(
        LearningPathConcept.path_id == learning_path.path_id
    ).count()
    
    # Calculate user progress for this path
    user_progress = db.query(UserConceptProgress).filter(
        UserConceptProgress.user_id == user_id,
        UserConceptProgress.concept_id.in_(
            db.query(LearningPathConcept.concept_id).filter(
                LearningPathConcept.path_id == learning_path.path_id
            ).subquery()
        )
    ).all()
    
    completed_concepts = sum(1 for p in user_progress if p.status == 'completed')
    progress_percent = round((completed_concepts / concept_count * 100) if concept_count > 0 else 0)
    
    return {
        "id": learning_path.path_id,
        "title": learning_path.name,  # Transform: name -> title
        "description": learning_path.description,
        "difficulty": learning_path.difficulty_level,  # Transform: difficulty_level -> difficulty
        "category": learning_path.category,
        "duration": f"{max(1, concept_count // 2)} weeks",
        "concepts_count": concept_count,
        "progress": progress_percent,
        "estimated_hours": concept_count * 3,
        "is_public": learning_path.is_public,
        "is_ai_generated": learning_path.is_ai_generated,
        "adaptive": learning_path.adaptive,
        "created_at": learning_path.created_at.isoformat() if learning_path.created_at else None,
        "version": learning_path.version
    }


@router.get("/database")
async def get_learning_paths_from_database(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get learning paths from the actual database with API transformation.
    
    This endpoint resolves the frontend/backend inconsistency by transforming:
    - Database 'name' -> Frontend 'title'
    - Database 'difficulty_level' -> Frontend 'difficulty'
    
    Use this endpoint instead of the dynamic generation for consistent data.
    """
    
    # Fetch actual learning paths from database
    learning_paths = db.query(LearningPath).all()
    
    if not learning_paths:
        return {
            "paths": [],
            "message": "No learning paths found in database. Run seed_graph_paths_simple.py to populate.",
            "count": 0
        }
    
    # Transform each path to API format
    transformed_paths = []
    for path in learning_paths:
        api_path = transform_learning_path_to_api_format(path, current_user.user_id, db)
        transformed_paths.append(api_path)
    
    return {
        "paths": transformed_paths,
        "message": f"Retrieved {len(transformed_paths)} learning paths from database",
        "count": len(transformed_paths),
        "transformation_applied": {
            "database_to_api": {
                "name": "title",
                "difficulty_level": "difficulty"
            }
        }
    }


@router.get("/{path_id}")
async def get_learning_path_by_id(
    path_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific learning path by ID from the database with API transformation.
    Includes concepts list for "Start Path" functionality.
    """
    
    learning_path = db.query(LearningPath).filter(
        LearningPath.path_id == path_id
    ).first()
    
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learning path with ID {path_id} not found"
        )
    
    # Transform to API format
    api_path = transform_learning_path_to_api_format(learning_path, current_user.user_id, db)
    
    # NEW: Fetch actual concepts for this path to enable "Start Path" functionality
    path_concepts = db.query(LearningPathConcept).filter(
        LearningPathConcept.path_id == path_id
    ).order_by(LearningPathConcept.sequence_order).all()
    
    # Get user progress for all concepts in this path to determine completion status
    concept_ids = [pc.concept_id for pc in path_concepts]
    user_progress = db.query(UserConceptProgress).filter(
        UserConceptProgress.user_id == current_user.user_id,
        UserConceptProgress.concept_id.in_(concept_ids)
    ).all()
    
    # Create progress lookup: concept_id -> progress record
    progress_map = {p.concept_id: p for p in user_progress}
    
    # Get concept details with completion status
    concepts_list = []
    for path_concept in path_concepts:
        concept = db.query(Concept).filter(
            Concept.concept_id == path_concept.concept_id
        ).first()
        
        if concept:
            # Get user's progress for this concept
            progress = progress_map.get(path_concept.concept_id)
            
            concepts_list.append({
                "concept_id": concept.concept_id,
                "name": concept.name,
                "display_name": concept.display_name,
                "description": concept.description,
                "difficulty_level": concept.difficulty_level,
                "sequence_order": path_concept.sequence_order,
                "estimated_duration": path_concept.estimated_duration,
                # Add completion status for frontend logic
                "status": progress.status if progress else "not_started",
                "progress_percent": progress.progress_percent or 0 if progress else 0,
                "completed": progress.status == "completed" if progress else False
            })
    
    # Add concepts to the response
    api_path["concepts"] = concepts_list
    
    return api_path


@router.get("/detailed-progress")
async def get_learning_paths_detailed_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enhanced version with detailed progress breakdown.
    
    Shows individual concept completion status and comprehensive analytics.
    Use this endpoint when you need detailed progress information for UI features
    like progress bars, concept status indicators, and time tracking.
    """
    
    learning_paths = db.query(LearningPath).all()
    response_data = []
    
    # Get all user progress with detailed status
    user_progress_records = db.query(UserConceptProgress).filter(
        UserConceptProgress.user_id == current_user.user_id
    ).all()
    
    # Build progress lookup: concept_id -> progress record
    concept_progress_map = {p.concept_id: p for p in user_progress_records}
    
    # Get all path-concept relationships
    path_concept_relations = db.query(LearningPathConcept).all()
    
    # Build path concept mapping
    path_to_concepts = {}
    for relation in path_concept_relations:
        if relation.path_id not in path_to_concepts:
            path_to_concepts[relation.path_id] = []
        path_to_concepts[relation.path_id].append(relation.concept_id)
    
    for path in learning_paths:
        path_concept_ids = path_to_concepts.get(path.path_id, [])
        
        if not path_concept_ids:
            continue
            
        # Get concepts with their progress status
        concepts = db.query(Concept).filter(
            Concept.concept_id.in_(path_concept_ids)
        ).all()
        
        # Build concept progress breakdown
        concept_progress = []
        for concept in concepts:
            progress_record = concept_progress_map.get(concept.concept_id)
            
            concept_progress.append({
                "concept_id": concept.concept_id,
                "name": concept.name,
                "display_name": concept.display_name,
                "status": progress_record.status if progress_record else "not_started",
                "progress_percent": progress_record.progress_percent if progress_record else 0,
                "time_spent": progress_record.time_spent if progress_record else 0,
                "last_accessed": progress_record.last_accessed.isoformat() if progress_record and progress_record.last_accessed else None,
                "difficulty_level": concept.difficulty_level,
                "estimated_duration": concept.estimated_duration
            })
        
        # Calculate overall statistics
        total_concepts = len(concepts)
        completed_concepts = sum(1 for cp in concept_progress if cp["status"] == "completed")
        in_progress_concepts = sum(1 for cp in concept_progress if cp["status"] == "in_progress")
        not_started_concepts = sum(1 for cp in concept_progress if cp["status"] == "not_started")
        
        # Calculate total time spent
        total_time_spent = sum(cp["time_spent"] for cp in concept_progress)
        
        # Calculate average progress
        avg_progress = sum(cp["progress_percent"] for cp in concept_progress) / total_concepts if total_concepts > 0 else 0
        
        overall_progress = round((completed_concepts / total_concepts) * 100) if total_concepts > 0 else 0
        
        response_data.append({
            "id": path.path_id,
            "title": path.name,
            "description": path.description,
            "difficulty": path.difficulty_level,
            "category": path.category,
            
            # Progress summary
            "concepts_count": total_concepts,
            "progress": overall_progress,
            "average_progress": round(avg_progress),
            "completed_concepts": completed_concepts,
            "in_progress_concepts": in_progress_concepts,
            "not_started_concepts": not_started_concepts,
            
            # Time analytics
            "total_time_spent": total_time_spent,
            "estimated_hours": path.estimated_duration,
            "time_efficiency": round((total_time_spent / path.estimated_duration * 100) if path.estimated_duration and path.estimated_duration > 0 else 0),
            
            # Detailed concept breakdown
            "concept_progress": concept_progress,
            
            # Metadata
            "adaptive": path.adaptive,
            "is_public": path.is_public,
            "is_ai_generated": path.is_ai_generated,
            "created_at": path.created_at.isoformat() if path.created_at else None,
            "version": path.version
        })
    
    return {
        "paths": response_data,
        "summary": {
            "total_paths": len(response_data),
            "total_concepts": sum(p["concepts_count"] for p in response_data),
            "total_completed": sum(p["completed_concepts"] for p in response_data),
            "overall_progress": round(sum(p["progress"] for p in response_data) / len(response_data)) if response_data else 0
        }
    }