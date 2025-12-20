import requests
import sys
from datetime import datetime

# Config
API_URL = "http://127.0.0.1:8000/api/v1"
CREDENTIALS = {"username": "cavin_admin", "password": "secure_password_123"}

def check_status():
    print("🔍 JESECI ECOSYSTEM STATUS CHECK")
    print("==================================================")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Backend Health
    try:
        health = requests.get("http://127.0.0.1:8000/health")
        if health.status_code == 200:
            print("1️⃣  Backend Health Check")
            print("   ✅ Backend is running and healthy")
        else:
            print("1️⃣  Backend Health Check")
            print(f"   ❌ Backend returned status {health.status_code}")
            sys.exit(1)
    except:
        print("1️⃣  Backend Health Check")
        print("   ❌ Backend is DOWN. Start it with: uvicorn main:app --reload")
        sys.exit(1)

    # 2. Authentication
    token = None
    try:
        auth = requests.post(f"{API_URL}/auth/login", json=CREDENTIALS)
        if auth.status_code == 200:
            token = auth.json()["access_token"]
            print("\n2️⃣  Authentication Test")
            print("   ✅ Authentication working")
        else:
            print("\n2️⃣  Authentication Test")
            print(f"   ❌ Login failed: {auth.text}")
            return
    except Exception as e:
        print(f"   ❌ Auth Error: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Knowledge Base (Concepts)
    print("\n3️⃣  Knowledge Base Status")
    try:
        c_resp = requests.get(f"{API_URL}/concepts/", headers=headers)
        if c_resp.status_code == 200:
            c_data = c_resp.json()
            
            # Robust check for List vs Dict responses
            if isinstance(c_data, list):
                count = len(c_data)
            elif isinstance(c_data, dict):
                count = len(c_data.get('data', []))
            else:
                count = 0
                
            if count > 0:
                print(f"   ✅ Concepts found: {count}")
            else:
                print("   ⚠️  No concepts found (Database is empty)")
        else:
            print(f"   ❌ API Error: {c_resp.status_code} - {c_resp.text}")
    except Exception as e:
        print(f"   ❌ Concepts check failed: {e}")

    # 4. Progress Tracking
    print("\n4️⃣  Progress Tracking Status")
    try:
        p_resp = requests.get(f"{API_URL}/progress/", headers=headers)
        if p_resp.status_code == 200:
            p_data = p_resp.json()
            stats = p_data.get("overall_stats", {})
            print("   ✅ Progress tracking active")
            print("   📊 Statistics:")
            print(f"      • Concepts learned: {stats.get('total_concepts_learned', 0)}")
            print(f"      • Time spent: {stats.get('total_time_spent', 0)} hours")
            print(f"      • Completion rate: {stats.get('completion_rate', 0)}%")
        else:
            print(f"   ❌ Progress API error: {p_resp.status_code} (Likely DB Schema Mismatch)")
    except Exception as e:
        print(f"   ❌ Progress check failed: {e}")

    # 5. Learning Paths (Added back)
    print("\n5️⃣  Learning Paths Status")
    try:
        # Note: Adjust URL if your router prefix is different (e.g. /learning-paths vs /learning-paths/)
        lp_resp = requests.get(f"{API_URL}/learning-paths/", headers=headers) 
        if lp_resp.status_code == 200:
            lp_data = lp_resp.json()
            print(f"   ✅ {len(lp_data)} learning paths found")
            if len(lp_data) > 0:
                print("   🛤️  Sample paths:")
                for path in lp_data[:3]:
                    print(f"      • {path.get('title')} ({path.get('difficulty')}) - {path.get('progress')}% complete")
        else:
            print(f"   ⚠️  Learning Paths endpoint returned {lp_resp.status_code}")
    except Exception as e:
        print(f"   ❌ Learning Paths check failed: {e}")

    print("\n==================================================")

if __name__ == "__main__":
    check_status()