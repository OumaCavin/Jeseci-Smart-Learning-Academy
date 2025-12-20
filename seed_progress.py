import requests
import random

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"
USERNAME = "cavin_admin"
PASSWORD = "secure_password_123"

def seed_user_progress():
    print("🚀 Simulating User Learning Progress...")

    # 1. Login
    try:
        auth_resp = requests.post(f"{API_URL}/auth/login", json={"username": USERNAME, "password": PASSWORD})
        if auth_resp.status_code != 200:
            print(f"❌ Login failed: {auth_resp.text}")
            return
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # 2. Get Concepts (Fixing the 'list' object error)
    print("📚 Fetching concepts...")
    try:
        resp = requests.get(f"{API_URL}/concepts/", headers=headers)
        if resp.status_code != 200:
            print(f"❌ Failed to fetch concepts: {resp.text}")
            return
            
        concepts_data = resp.json()
        
        # 🛠️ FIX: Handle both List and Dictionary responses
        if isinstance(concepts_data, dict):
            concepts = concepts_data.get("data", []) or concepts_data.get("items", [])
        elif isinstance(concepts_data, list):
            concepts = concepts_data
        else:
            concepts = []

    except Exception as e:
        print(f"❌ Error parsing concepts: {e}")
        return
    
    if not concepts:
        print("❌ No concepts found. Run seed_concepts.py first!")
        return

    # 3. Simulate Learning
    print(f"✅ Found {len(concepts)} concepts. Simulating study session...")
    
    success_count = 0
    for concept in concepts:
        # Randomly decide if we've started this concept
        if random.random() > 0.3: # 70% chance we touched it
            
            # Random progress stats
            is_complete = random.random() > 0.5
            progress_pct = 100 if is_complete else random.randint(10, 90)
            status = "completed" if is_complete else "in_progress"
            minutes = random.randint(30, 180) 
            
            try:
                # Use the correct ID field
                c_id = concept.get('concept_id') or concept.get('id')
                c_name = concept.get('display_name') or concept.get('name')
                
                requests.post(
                    f"{API_URL}/progress/concepts/{c_id}/update",
                    params={ 
                        "time_spent": minutes,
                        "progress_percent": progress_pct,
                        "status": status
                    },
                    headers=headers
                )
                print(f"   📝 Updated: {c_name} ({progress_pct}%)")
                success_count += 1
            except Exception as e:
                print(f"   ⚠️ Failed to update {c_name}: {e}")

    print(f"\n✅ Dashboard data populated! ({success_count} records updated)")

if __name__ == "__main__":
    seed_user_progress()