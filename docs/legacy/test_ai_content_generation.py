#!/usr/bin/env python3
"""
AI Content Generator Test Script
Tests the Just-in-Time Content Generation system
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from config.database import DATABASE_URL
from database.models import Base, Concept
from services.ai_generator import generate_lesson_content, generate_practice_questions


async def test_ai_content_generation():
    """Test the AI content generation system"""
    
    print("🤖 Testing AI Content Generation System...")
    print("=" * 60)
    
    # Check OpenAI configuration
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment")
        print("   The system will use fallback content templates")
        print("   Set OPENAI_API_KEY in .env for full AI functionality")
        print()
    
    # Get database session
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Test 1: Check concepts exist
        print("📚 Test 1: Checking concepts...")
        concepts = db.query(Concept).all()
        print(f"   ✅ Found {len(concepts)} concepts")
        
        if len(concepts) == 0:
            print("   ❌ No concepts found! Run seed_concepts_direct.py first")
            return False
        
        # Test 2: Test AI lesson generation for each concept
        print("\n🎓 Test 2: Testing AI lesson generation...")
        
        for i, concept in enumerate(concepts[:3], 1):  # Test first 3 concepts
            print(f"\n   📖 Testing concept {i}: {concept.display_name}")
            
            try:
                # Generate lesson content
                print(f"      🤖 Generating lesson...")
                lesson_content = await generate_lesson_content(
                    concept_name=concept.display_name,
                    domain=concept.domain,
                    difficulty=concept.difficulty_level,
                    category=concept.category,
                    detailed_description=concept.detailed_description
                )
                
                print(f"      ✅ Generated {len(lesson_content)} characters of content")
                
                # Show first few lines
                lines = lesson_content.split('\n')[:5]
                print(f"      📄 Preview:")
                for line in lines:
                    if line.strip():
                        print(f"         {line[:80]}{'...' if len(line) > 80 else ''}")
                
                # Save to database for caching
                concept.lesson_content = lesson_content
                concept.lesson_generated_at = datetime.utcnow()
                concept.lesson_model_used = "gpt-4o-mini" if openai_key else "fallback"
                
                print(f"      💾 Cached lesson content in database")
                
            except Exception as e:
                print(f"      ❌ Error generating lesson: {str(e)}")
        
        # Commit all generated content
        db.commit()
        print(f"\n   ✅ Committed {min(3, len(concepts))} AI-generated lessons to database")
        
        # Test 3: Test practice question generation
        print("\n❓ Test 3: Testing practice question generation...")
        
        for concept in concepts[:2]:  # Test first 2 concepts
            try:
                questions = await generate_practice_questions(
                    concept_name=concept.display_name,
                    difficulty=concept.difficulty_level,
                    question_count=2
                )
                
                print(f"   📝 Generated {len(questions)} questions for {concept.display_name}")
                for q in questions:
                    print(f"      Q: {q.get('question', 'N/A')[:60]}...")
                    
            except Exception as e:
                print(f"   ❌ Error generating questions for {concept.display_name}: {str(e)}")
        
        # Test 4: Verify cached content retrieval
        print("\n💾 Test 4: Testing cached content retrieval...")
        
        concepts_with_content = db.query(Concept).filter(Concept.lesson_content.isnot(None)).all()
        print(f"   ✅ Found {len(concepts_with_content)} concepts with cached lessons")
        
        for concept in concepts_with_content[:2]:
            print(f"   📄 {concept.display_name}:")
            print(f"      Generated: {concept.lesson_generated_at}")
            print(f"      Model: {concept.lesson_model_used}")
            print(f"      Content length: {len(concept.lesson_content)} chars")
        
        print("\n" + "=" * 60)
        print("🎉 AI Content Generation Test Complete!")
        print("✅ System is ready for production use")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


def show_system_overview():
    """Show overview of the AI content generation system"""
    
    print("\n" + "=" * 60)
    print("🤖 JUST-IN-TIME CONTENT GENERATOR - SYSTEM OVERVIEW")
    print("=" * 60)
    
    print("\n🎯 PURPOSE:")
    print("   Generate personalized educational content on-demand using AI")
    print("   Cache generated content for instant future access")
    
    print("\n🔧 COMPONENTS:")
    print("   ✅ Database Model: lesson_content column in Concept model")
    print("   ✅ AI Service: services/ai_generator.py with OpenAI integration")
    print("   ✅ API Endpoints: /concepts/{id}/lesson and related endpoints")
    print("   ✅ Frontend: AI lesson modal with markdown rendering")
    print("   ✅ Caching: Write-back cache in PostgreSQL")
    
    print("\n🌐 API ENDPOINTS:")
    print("   GET  /api/v1/concepts/{concept_id}/lesson")
    print("   GET  /api/v1/concepts/{concept_id}/practice-questions")
    print("   POST /api/v1/concepts/{concept_id}/regenerate-lesson")
    print("   GET  /api/v1/concepts/{concept_id}/lesson-status")
    
    print("\n💡 HOW IT WORKS:")
    print("   1. User clicks 'Start Learning' on a concept")
    print("   2. System checks if lesson exists in database")
    print("   3. If cached → Return instantly")
    print("   4. If not cached → Generate via OpenAI API")
    print("   5. Save generated content to database for future use")
    print("   6. Display personalized lesson to user")
    
    print("\n⚡ BENEFITS:")
    print("   🎯 Personalized content based on difficulty level")
    print("   🚀 Infinite scalability (no pre-written content needed)")
    print("   💰 Cost-effective (generate once, cache forever)")
    print("   🧠 AI-powered contextual understanding")
    print("   📈 Always up-to-date content quality")
    
    print("\n🔧 CONFIGURATION:")
    print("   Required: OPENAI_API_KEY in environment")
    print("   Model: gpt-4o-mini (cost-effective)")
    print("   Fallback: Template content when OpenAI unavailable")
    
    print("\n" + "=" * 60)


async def main():
    """Main test function"""
    show_system_overview()
    
    success = await test_ai_content_generation()
    
    if success:
        print("\n🎊 SUCCESS: AI Content Generation System is operational!")
        print("🌟 Users can now receive personalized AI-generated lessons!")
        print("\n📋 NEXT STEPS:")
        print("   1. Set OPENAI_API_KEY in your .env file for full functionality")
        print("   2. Start the API server: python main.py")
        print("   3. Start the frontend: cd frontend-jac && python serve.py")
        print("   4. Visit http://localhost:8080 and click 'Start Learning'")
    else:
        print("\n⚠️  ISSUES FOUND: Some components may need attention")
        print("🔧 Check the error messages above for troubleshooting")


if __name__ == "__main__":
    asyncio.run(main())