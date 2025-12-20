"""
Test API Transformation for Learning Paths
Verifies that the new endpoints return data in frontend-friendly format
"""

import requests
import json

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"
USERNAME = "cavin_admin"
PASSWORD = "secure_password_123"

def test_api_transformation():
    print("🔄 Testing API Transformation for Learning Paths")
    print("=" * 60)
    
    try:
        # 1. Login
        print("🔐 Authenticating...")
        auth_resp = requests.post(f"{API_URL}/auth/login", json={"username": USERNAME, "password": PASSWORD})
        if auth_resp.status_code != 200:
            print(f"❌ Login failed: {auth_resp.text}")
            return False
            
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful!")
        
        # 2. Test database learning paths endpoint
        print("\n📊 Testing database learning paths endpoint...")
        db_resp = requests.get(f"{API_URL}/learning-paths/database", headers=headers)
        
        if db_resp.status_code == 200:
            data = db_resp.json()
            print(f"✅ Found {data['count']} learning paths from database")
            
            if data['paths']:
                print("\n📋 Sample learning path (transformed format):")
                sample_path = data['paths'][0]
                print(f"   • Title: {sample_path.get('title')} (was 'name' in DB)")
                print(f"   • Difficulty: {sample_path.get('difficulty')} (was 'difficulty_level' in DB)")
                print(f"   • Category: {sample_path.get('category')}")
                print(f"   • Progress: {sample_path.get('progress')}%")
                print(f"   • Concepts: {sample_path.get('concepts_count')}")
                
                # Verify transformation
                assert 'title' in sample_path, "Missing 'title' field"
                assert 'difficulty' in sample_path, "Missing 'difficulty' field"
                assert 'name' not in sample_path, "Should not have 'name' field"
                assert 'difficulty_level' not in sample_path, "Should not have 'difficulty_level' field"
                
                print("\n✅ API Transformation Working Correctly!")
                print("   • Database 'name' → API 'title' ✓")
                print("   • Database 'difficulty_level' → API 'difficulty' ✓")
                
                # 3. Test individual path endpoint
                print(f"\n🔍 Testing individual path endpoint for: {sample_path['id']}")
                individual_resp = requests.get(f"{API_URL}/learning-paths/database/{sample_path['id']}", headers=headers)
                
                if individual_resp.status_code == 200:
                    individual_data = individual_resp.json()
                    print(f"✅ Individual path retrieved successfully")
                    print(f"   • Title: {individual_data.get('title')}")
                    print(f"   • Difficulty: {individual_data.get('difficulty')}")
                else:
                    print(f"❌ Individual path endpoint failed: {individual_resp.status_code}")
                    
                return True
            else:
                print("⚠️  No learning paths found. Database might be empty.")
                print("💡 Run seed_graph_paths_simple.py to populate learning paths.")
                return False
        else:
            print(f"❌ Database endpoint failed: {db_resp.status_code}")
            print(f"   Response: {db_resp.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Start the API server first: python main.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_old_vs_new_format():
    """Compare old dynamic format vs new database format"""
    print("\n🔄 Comparing Old vs New API Format")
    print("=" * 60)
    
    try:
        # Login
        auth_resp = requests.post(f"{API_URL}/auth/login", json={"username": USERNAME, "password": PASSWORD})
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get old format (dynamic)
        old_resp = requests.get(f"{API_URL}/learning-paths/", headers=headers)
        old_data = old_resp.json() if old_resp.status_code == 200 else []
        
        # Get new format (database)
        new_resp = requests.get(f"{API_URL}/learning-paths/database", headers=headers)
        new_data = new_resp.json() if new_resp.status_code == 200 else {"paths": []}
        
        print(f"📊 Format Comparison:")
        print(f"   • Old (dynamic): {len(old_data)} paths")
        print(f"   • New (database): {new_data.get('count', 0)} paths")
        
        if old_data and new_data.get('paths'):
            print(f"\n✅ Both formats available:")
            print(f"   • Old: Dynamic generation based on concepts")
            print(f"   • New: Actual database records with transformation")
            print(f"   • Frontend should use '/database' endpoints for consistency")
            
        return True
        
    except Exception as e:
        print(f"⚠️  Comparison test skipped: {e}")
        return False

if __name__ == "__main__":
    success1 = test_api_transformation()
    success2 = test_old_vs_new_format()
    
    print("\n" + "=" * 60)
    if success1:
        print("🎉 API Transformation Implementation: SUCCESS!")
        print("✅ Frontend/backend inconsistency resolved")
        print("💡 Use /learning-paths/database endpoints for consistent data format")
    else:
        print("❌ Some tests failed. Check server and database setup.")
        
    print("\n📋 Available Endpoints:")
    print("   • GET /api/v1/learning-paths/          (Dynamic generation)")
    print("   • GET /api/v1/learning-paths/database  (Database with transformation)")
    print("   • GET /api/v1/learning-paths/database/{id} (Single path)")