"""
Direct Database Concept Seeding Script
Populates the database with concepts directly (no API required)
"""

import sys
import os
from datetime import datetime
import uuid

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from config.database import DATABASE_URL
from database.models import Base, Concept


def create_sample_concepts():
    """Create sample concepts for the learning platform"""
    
    concepts_data = [
        {
            "name": "variables",
            "display_name": "Variables and Data Types",
            "description": "Understanding variables as containers for storing data values, including different data types like strings, numbers, and booleans.",
            "detailed_description": "Variables are fundamental building blocks in programming. They act as named containers that store different types of data. Understanding variables and data types is essential for any programming journey, as they form the basis for data manipulation and program logic.",
            "category": "Programming Fundamentals",
            "subcategory": "Data Types",
            "domain": "Computer Science",
            "difficulty_level": "beginner",
            "complexity_score": 2.0,
            "cognitive_load": 2.5,
            "key_terms": ["variable", "string", "number", "boolean", "data type", "declaration", "assignment", "naming conventions"],
            "synonyms": ["Data Storage", "Program Variables", "Value Containers"],
            "learning_objectives": [
                "Understand what variables are and why they're used",
                "Learn different data types and when to use them",
                "Practice variable naming conventions",
                "Master variable declaration and assignment"
            ],
            "practical_applications": [
                "Storing user input in forms",
                "Calculating mathematical expressions",
                "Managing application state",
                "Processing database records"
            ],
            "real_world_examples": [
                "Shopping cart totals in e-commerce",
                "User profile information in social media",
                "Temperature readings in weather apps",
                "Score tracking in games"
            ],
            "common_misconceptions": [
                "Variables are the same as constants",
                "All data types behave the same way",
                "Variable names don't matter",
                "You can't change variable values after declaration"
            ]
        },
        {
            "name": "arrays",
            "display_name": "Arrays and Lists",
            "description": "Ordered collections of elements that can be accessed by their index position, fundamental for organizing multiple related values.",
            "detailed_description": "Arrays and lists are essential data structures that allow you to store multiple values in a single variable. They're perfect for managing collections of related data like lists of names, numbers, or objects. Understanding arrays is crucial for data manipulation and algorithm implementation.",
            "category": "Programming Fundamentals",
            "subcategory": "Data Structures",
            "domain": "Computer Science",
            "difficulty_level": "beginner",
            "complexity_score": 3.5,
            "cognitive_load": 4.0,
            "key_terms": ["array", "list", "index", "element", "length", "iteration", "sorting", "searching", "multidimensional"],
            "synonyms": ["Ordered Collections", "Data Lists", "Indexed Arrays"],
            "learning_objectives": [
                "Understand what arrays and lists are",
                "Learn about indexing and element access",
                "Practice array operations and manipulation",
                "Apply arrays to real-world problems"
            ],
            "practical_applications": [
                "Managing shopping cart items",
                "Storing student grades",
                "Processing form submissions",
                "Building contact lists"
            ],
            "real_world_examples": [
                "Spotify playlists of songs",
                "Instagram photo galleries",
                "Email inbox message lists",
                "Restaurant menu items"
            ],
            "common_misconceptions": [
                "Arrays can only contain one data type",
                "Array size is fixed at creation",
                "Arrays always start indexing at 1",
                "Arrays are slower than individual variables"
            ]
        },
        {
            "name": "html_basics",
            "display_name": "HTML Fundamentals",
            "description": "The standard markup language for creating web pages, providing structure and content organization for websites.",
            "detailed_description": "HTML (HyperText Markup Language) is the backbone of web development. It provides the structure and semantic meaning to web content using elements and tags. Every web page you've ever visited uses HTML to define its layout, headings, paragraphs, links, and multimedia content.",
            "category": "Web Development",
            "subcategory": "Front-end Technologies",
            "domain": "Computer Science",
            "difficulty_level": "beginner",
            "complexity_score": 3.0,
            "cognitive_load": 3.5,
            "key_terms": ["HTML", "elements", "tags", "attributes", "semantic", "headings", "paragraphs", "links", "images", "lists"],
            "synonyms": ["Web Markup", "HTML Structure", "Hypertext"],
            "learning_objectives": [
                "Understand HTML's role in web development",
                "Learn essential HTML elements and their purposes",
                "Practice creating structured web documents",
                "Apply semantic HTML principles"
            ],
            "practical_applications": [
                "Creating personal websites",
                "Building landing pages",
                "Structuring blog content",
                "Developing web forms"
            ],
            "real_world_examples": [
                "Company About pages",
                "News article layouts",
                "E-commerce product pages",
                "Social media post structures"
            ],
            "common_misconceptions": [
                "HTML is a programming language",
                "More tags always mean better code",
                "HTML handles styling and behavior",
                "All HTML elements display the same way"
            ]
        },
        {
            "name": "linear_equations",
            "display_name": "Linear Equations",
            "description": "Mathematical equations that create straight lines when graphed, fundamental to algebra and problem-solving.",
            "detailed_description": "Linear equations are mathematical expressions that show a straight line relationship between variables. They're the simplest type of equations and form the foundation for more advanced mathematics. Understanding linear equations is crucial for algebra, calculus, and many real-world applications in science, engineering, and economics.",
            "category": "Mathematics",
            "subcategory": "Algebra",
            "domain": "Mathematics",
            "difficulty_level": "intermediate",
            "complexity_score": 5.0,
            "cognitive_load": 5.5,
            "key_terms": ["linear", "equation", "slope", "y-intercept", "variable", "constant", "graph", "solution", "coefficient"],
            "synonyms": ["Straight Line Equations", "First-Degree Equations", "Linear Functions"],
            "learning_objectives": [
                "Understand the concept of linear relationships",
                "Learn to solve linear equations step-by-step",
                "Practice graphing linear equations",
                "Apply linear equations to real-world problems"
            ],
            "practical_applications": [
                "Calculating business profits",
                "Predicting temperature changes",
                "Determining travel distances",
                "Budget planning and forecasting"
            ],
            "real_world_examples": [
                "Taxi fare calculations",
                "Cell phone plan pricing",
                "Gas mileage calculations",
                "Currency exchange rates"
            ],
            "common_misconceptions": [
                "Linear equations always have one solution",
                "Linear means the equation is simple",
                "You can only solve equations with one variable",
                "Linear equations only work with positive numbers"
            ]
        },
        {
            "name": "photosynthesis",
            "display_name": "Photosynthesis",
            "description": "The process by which plants convert light energy into chemical energy, producing glucose and oxygen from carbon dioxide and water.",
            "detailed_description": "Photosynthesis is one of the most important biological processes on Earth. It's how green plants, algae, and some bacteria convert sunlight, carbon dioxide, and water into glucose (food) and oxygen. This process is fundamental to life as we know it, providing the oxygen we breathe and forming the base of most food chains.",
            "category": "Biology",
            "subcategory": "Plant Biology",
            "domain": "Life Sciences",
            "difficulty_level": "intermediate",
            "complexity_score": 6.0,
            "cognitive_load": 6.5,
            "key_terms": ["photosynthesis", "chlorophyll", "chloroplast", "glucose", "oxygen", "carbon dioxide", "light energy", "stomata", " Calvin cycle"],
            "synonyms": ["Plant Food Production", "Light Synthesis", "Biochemical Energy Conversion"],
            "learning_objectives": [
                "Understand the process and importance of photosynthesis",
                "Learn the two main stages of photosynthesis",
                "Identify factors that affect photosynthesis rate",
                "Apply knowledge of photosynthesis to ecological concepts"
            ],
            "practical_applications": [
                "Optimizing crop yields in agriculture",
                "Understanding forest ecosystem health",
                "Climate change impact assessment",
                "Developing sustainable farming practices"
            ],
            "real_world_examples": [
                "Greenhouse plant cultivation",
                "Forest carbon sequestration",
                "Algae biofuel production",
                "Indoor air purification systems"
            ],
            "common_misconceptions": [
                "Plants only photosynthesize during the day",
                "All plant parts can photosynthesize",
                "Photosynthesis produces only oxygen",
                "More light always means better photosynthesis"
            ]
        }
    ]
    
    return concepts_data


def seed_concepts_to_database():
    """Seed concepts directly to the database"""
    
    # Get database session
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Check if concepts already exist
        existing_count = db.query(Concept).count()
        print(f"📊 Found {existing_count} existing concepts in database")
        
        # Create sample concepts data
        concepts_data = create_sample_concepts()
        
        created_count = 0
        
        for concept_data in concepts_data:
            # Check if concept already exists
            existing_concept = db.query(Concept).filter(Concept.name == concept_data["name"]).first()
            
            if existing_concept:
                print(f"   ✓ Concept '{concept_data['display_name']}' already exists, skipping...")
                continue
            
            # Create new concept
            concept = Concept(
                name=concept_data["name"],
                display_name=concept_data["display_name"],
                description=concept_data["description"],
                detailed_description=concept_data["detailed_description"],
                category=concept_data["category"],
                subcategory=concept_data["subcategory"],
                domain=concept_data["domain"],
                difficulty_level=concept_data["difficulty_level"],
                complexity_score=concept_data["complexity_score"],
                cognitive_load=concept_data["cognitive_load"],
                key_terms=concept_data["key_terms"],
                synonyms=concept_data["synonyms"],
                learning_objectives=concept_data["learning_objectives"],
                practical_applications=concept_data["practical_applications"],
                real_world_examples=concept_data["real_world_examples"],
                common_misconceptions=concept_data["common_misconceptions"]
            )
            
            db.add(concept)
            created_count += 1
            print(f"   ✅ Created: {concept_data['display_name']} ({concept_data['domain']})")
        
        # Commit all changes
        db.commit()
        print(f"\n🎉 Successfully seeded {created_count} concepts!")
        
        # Show final count
        final_count = db.query(Concept).count()
        print(f"📈 Total concepts in database: {final_count}")
        
        # Show summary by domain
        print("\n📊 Concepts by Domain:")
        domains = db.query(Concept.domain, db.func.count(Concept.concept_id)).group_by(Concept.domain).all()
        for domain, count in domains:
            print(f"   • {domain}: {count} concepts")
        
        # Show summary by difficulty
        print("\n📊 Concepts by Difficulty:")
        difficulties = db.query(Concept.difficulty_level, db.func.count(Concept.concept_id)).group_by(Concept.difficulty_level).all()
        for difficulty, count in difficulties:
            print(f"   • {difficulty.title()}: {count} concepts")
        
    except Exception as e:
        print(f"❌ Error seeding concepts: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Starting direct concept seeding...")
    seed_concepts_to_database()
    print("✅ Concept seeding completed!")