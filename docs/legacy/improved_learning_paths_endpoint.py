"""
Improved Learning Paths Endpoint
Uses proper database relationships and correct field mapping
"""

@router.get("/")
async def get_learning_paths_improved(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get learning paths with accurate progress calculation
    Uses LearningPathConcept association table for precise concept matching
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
            "estimated_hours": path.estimated_hours,
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


@router.get("/with-detailed-progress")
async def get_learning_paths_detailed_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enhanced version with detailed progress breakdown
    Shows individual concept completion status
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
                "status": progress_record.status if progress_record else "not_started",
                "progress_percent": progress_record.progress_percent if progress_record else 0,
                "time_spent": progress_record.time_spent if progress_record else 0,
                "last_accessed": progress_record.last_accessed.isoformat() if progress_record and progress_record.last_accessed else None
            })
        
        # Calculate overall statistics
        total_concepts = len(concepts)
        completed_concepts = sum(1 for cp in concept_progress if cp["status"] == "completed")
        in_progress_concepts = sum(1 for cp in concept_progress if cp["status"] == "in_progress")
        not_started_concepts = sum(1 for cp in concept_progress if cp["status"] == "not_started")
        
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
            "completed_concepts": completed_concepts,
            "in_progress_concepts": in_progress_concepts,
            "not_started_concepts": not_started_concepts,
            
            # Detailed concept breakdown
            "concept_progress": concept_progress,
            
            # Metadata
            "estimated_hours": path.estimated_hours,
            "adaptive": path.adaptive
        })
    
    return response_data