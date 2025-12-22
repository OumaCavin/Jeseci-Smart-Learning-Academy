"""
Test to verify the concepts API fix
Tests the database query logic without starting the full server
"""

import sys
import os
sys.path.append('.')

def test_concepts_query_logic():
    """Test the concepts query logic without the web server"""
    print("🔧 Testing Concepts API Query Logic")
    print("=" * 50)
    
    try:
        # Import required modules
        from config.database import SessionLocal
        from database.models.sqlite_models import Concept
        
        # Create a database session
        db = SessionLocal()
        
        try:
            # Test basic query (this was failing before)
            print("📋 Testing basic concepts query...")
            concepts = db.query(Concept).limit(5).all()
            
            if concepts:
                print(f"✅ Found {len(concepts)} concepts")
                for concept in concepts:
                    print(f"   • {concept.name} ({concept.category})")
            else:
                print("⚠️  No concepts found in database")
            
            # Test search query (this was the problematic one)
            print("\n🔍 Testing search query logic...")
            search_query = "variables"
            
            # This should work now without the .any() method
            filtered_concepts = db.query(Concept).filter(
                Concept.name.ilike(f"%{search_query}%")
            ).all()
            
            print(f"✅ Search query worked! Found {len(filtered_concepts)} concepts")
            
            # Test JSON field access
            print("\n📊 Testing JSON field access...")
            if concepts:
                concept = concepts[0]
                print(f"   • Key terms: {type(concept.key_terms)} - {concept.key_terms}")
                print(f"   • Synonyms: {type(concept.synonyms)} - {concept.synonyms}")
                print("✅ JSON fields accessible")
            
            print("\n🎉 All database queries working correctly!")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_concepts_import():
    """Test importing the concepts module"""
    print("📦 Testing Concepts Module Import")
    print("=" * 50)
    
    try:
        # Try to import the concepts module
        from api.v1.concepts import router
        print("✅ Concepts module imported successfully")
        
        # Check if the problematic line is removed
        import inspect
        source = inspect.getsource(router.routes[0].endpoint)
        
        if ".any(" in source:
            print("❌ Still contains .any() method - fix not applied")
            return False
        else:
            print("✅ .any() method removed from query logic")
            
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Concepts API Fix")
    print("=" * 60)
    
    # Test imports
    import_success = test_concepts_import()
    
    # Test database logic
    db_success = test_concepts_query_logic()
    
    print("\n" + "=" * 60)
    print("📋 Test Results:")
    print(f"   • Module Import: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   • Database Logic: {'✅ PASS' if db_success else '❌ FAIL'}")
    
    if import_success and db_success:
        print("\n🎉 All tests passed! The fix should resolve the Internal Server Error.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")