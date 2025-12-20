#!/usr/bin/env python3
"""
Link JAC concepts to JAC learning paths
Creates the missing relationships between concepts and learning paths
"""

from sqlalchemy.orm import Session
from config.database import SessionLocal
from database.models.sqlite_models import Concept, LearningPath, LearningPathConcept

def link_jac_concepts_to_paths():
    """Link JAC concepts to JAC learning paths"""
    db = SessionLocal()
    
    try:
        print("🔗 Linking JAC Concepts to Learning Paths...")
        
        # Get JAC concepts and paths
        concepts = db.query(Concept).filter(Concept.category == "JAC Programming").all()
        paths = db.query(LearningPath).filter(LearningPath.category == "JAC Programming").all()
        
        print(f"Found {len(concepts)} concepts and {len(paths)} paths")
        
        # Define the relationships based on difficulty and learning progression
        path_concept_mappings = {
            "JAC Programming Fundamentals Journey": [
                ("jac_programming_fundamentals", 1, 10),
                ("jac_variables_data_types", 2, 10),
                ("jac_control_flow", 3, 8),
                ("jac_functions", 4, 8)
            ],
            "JAC Object-Oriented and Collections Mastery": [
                ("jac_collections", 1, 18),
                ("jac_oop", 2, 17)
            ],
            "JAC Object-Spatial Programming Expert": [
                ("jac_object_spatial_programming", 1, 17),
                ("jac_nodes_edges", 2, 17),
                ("jac_walkers", 3, 16)
            ],
            "JAC AI Integration and Expert Level": [
                ("jac_ai_integration", 1, 23),
                ("jac_scale_agnostic_programming", 2, 22)
            ]
        }
        
        links_created = 0
        
        # Create relationships
        for path_name, concept_mappings in path_concept_mappings.items():
            path = next((p for p in paths if p.name == path_name), None)
            if not path:
                print(f"❌ Path not found: {path_name}")
                continue
                
            print(f"\n📚 Linking concepts to: {path_name}")
            
            for concept_name, order, duration in concept_mappings:
                concept = next((c for c in concepts if c.name == concept_name), None)
                if not concept:
                    print(f"❌ Concept not found: {concept_name}")
                    continue
                
                # Check if relationship already exists
                existing = db.query(LearningPathConcept).filter(
                    LearningPathConcept.path_id == path.path_id,
                    LearningPathConcept.concept_id == concept.concept_id
                ).first()
                
                if existing:
                    print(f"  ⚠️  Relationship already exists: {concept.display_name}")
                    continue
                
                # Create new relationship
                link = LearningPathConcept(
                    path_id=path.path_id,
                    concept_id=concept.concept_id,
                    sequence_order=order,
                    estimated_duration=duration,
                    required_mastery_level=0.0 if order == 1 else (0.7 if path.difficulty_level == "intermediate" else (0.8 if path.difficulty_level == "advanced" else 0.9)),
                    adaptive_difficulty=True
                )
                db.add(link)
                links_created += 1
                print(f"  ✅ Linked: {concept.display_name} (Order: {order}, Duration: {duration}h)")
        
        # Commit all changes
        db.commit()
        
        # Verify relationships
        relationships = db.query(LearningPathConcept).join(
            LearningPath, LearningPathConcept.path_id == LearningPath.path_id
        ).filter(LearningPath.category == "JAC Programming").all()
        
        print(f"\n🎉 Successfully created {links_created} new relationships!")
        print(f"📊 Total JAC concept-path relationships: {len(relationships)}")
        
        # Show summary by path
        print(f"\n📈 Relationships by Learning Path:")
        for path in paths:
            path_rels = [r for r in relationships if r.path_id == path.path_id]
            print(f"  • {path.name}: {len(path_rels)} concepts")
        
    except Exception as e:
        print(f"❌ Error linking concepts to paths: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    link_jac_concepts_to_paths()