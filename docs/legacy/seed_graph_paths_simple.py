"""
Seed Graph Learning Paths (Simplified)
Syncs learning paths directly to SQLite database without Neo4j dependency
"""

import sys
sys.path.append('.')

from config.database import SessionLocal
from database.models.sqlite_models import Concept, LearningPath, LearningPathConcept

# Define Paths and their Concepts (Updated to match our current database)
GRAPH_PATHS = [
    {
        "title": "Programming Fundamentals Journey",
        "difficulty": "Beginner",
        "category": "Computer Science",
        "contains": ["variables", "arrays"]
    },
    {
        "title": "Web Development Essentials",
        "difficulty": "Beginner", 
        "category": "Computer Science",
        "contains": ["html_basics", "variables"]
    },
    {
        "title": "Mathematics for Programming",
        "difficulty": "Intermediate",
        "category": "Mathematics",
        "contains": ["linear_equations", "variables"]
    },
    {
        "title": "Science & Technology Integration",
        "difficulty": "Intermediate",
        "category": "Life Sciences",
        "contains": ["photosynthesis", "linear_equations"]
    }
]

def seed_graph_paths_simple():
    print("🚀 Syncing Learning Paths to SQLite Database...")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 1. Get all concepts from database
        print("🔍 Resolving concept IDs from database...")
        all_concepts = db.query(Concept).all()
        concept_map = {c.name.lower().replace(' ', '_'): c for c in all_concepts}
        
        print(f"📚 Found {len(concept_map)} concepts in database:")
        for name, concept in concept_map.items():
            print(f"   • {concept.name}: {concept.concept_id[:8]}...")
        
        # 2. Create Learning Paths
        print(f"\n📦 Creating {len(GRAPH_PATHS)} Learning Paths...")
        
        created_paths = 0
        total_relationships = 0
        
        for path in GRAPH_PATHS:
            print(f"\n📦 Creating Path: {path['title']}")
            
            # Check if path already exists
            existing_path = db.query(LearningPath).filter(
                LearningPath.name == path['title']
            ).first()
            
            if existing_path:
                print(f"   ⚠️  Learning Path already exists, skipping...")
                continue
            
            # Create new learning path
            learning_path = LearningPath(
                name=path['title'],
                difficulty_level=path['difficulty'],
                category=path['category'],
                description=f"Comprehensive learning path covering {path['category']} concepts"
            )
            
            db.add(learning_path)
            db.flush()  # Get the ID
            
            created_paths += 1
            print(f"   ✅ Created Learning Path: {learning_path.name}")
            
            # 3. Link concepts to path
            linked_concepts = 0
            for concept_name in path['contains']:
                # Try different name variations
                concept_variations = [
                    concept_name.lower(),
                    concept_name.lower().replace('_', ' '),
                    concept_name.title(),
                    concept_name.title().replace('_', ' ')
                ]
                
                concept = None
                for variation in concept_variations:
                    if variation in concept_map:
                        concept = concept_map[variation]
                        break
                
                if concept:
                    # Check if relationship already exists
                    existing_rel = db.query(LearningPathConcept).filter(
                        LearningPathConcept.path_id == learning_path.path_id,
                        LearningPathConcept.concept_id == concept.concept_id
                    ).first()
                    
                    if not existing_rel:
                        # Create relationship
                        path_concept = LearningPathConcept(
                            path_id=learning_path.path_id,
                            concept_id=concept.concept_id,
                            sequence_order=len(path['contains']) - path['contains'].index(concept_name)
                        )
                        db.add(path_concept)
                        linked_concepts += 1
                        print(f"   🔗 Linked -> {concept.name}")
                    else:
                        print(f"   ⚠️  Relationship already exists: {concept.name}")
                else:
                    print(f"   ⚠️  Concept not found: {concept_name}")
            
            total_relationships += linked_concepts
            print(f"      📊 Linked {linked_concepts} concepts to this path")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ Learning Paths Synced Successfully!")
        print(f"🎯 Created {created_paths} new learning paths")
        print(f"🔗 Created {total_relationships} path-concept relationships")
        
        # Show summary
        all_paths = db.query(LearningPath).all()
        print(f"\n📊 Total Learning Paths in Database: {len(all_paths)}")
        for path in all_paths:
            concept_count = db.query(LearningPathConcept).filter(
                LearningPathConcept.path_id == path.path_id
            ).count()
            print(f"   • {path.name} ({concept_count} concepts)")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = seed_graph_paths_simple()
    if success:
        print("\n🌟 Learning Paths are now available in the database!")
        print("💡 Note: This is a simplified version using SQLite only")
        print("💡 For full graph functionality, Neo4j server would be needed")
    else:
        print("\n⚠️  Seeding incomplete. Check errors above.")