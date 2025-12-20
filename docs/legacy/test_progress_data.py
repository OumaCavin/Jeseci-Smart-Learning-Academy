#!/usr/bin/env python3
"""
Test Progress Data Population Script
This script populates the database with sample progress data for testing.
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta
import random

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"
USERNAME = "cavin_admin"
PASSWORD = "secure_password_123"

def login():
    """Login and get JWT token"""
    auth_resp = requests.post(f"{API_URL}/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    if auth_resp.status_code != 200:
        raise Exception(f"Login failed: {auth_resp.text}")
    
    return auth_resp.json()["access_token"]

def get_concepts(token):
    """Get available concepts from the API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = requests.get(f"{API_URL}/concepts", headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Failed to get concepts: {resp.text}")
    
    return resp.json()

def update_concept_progress(token, concept_id, time_spent=30, progress_percent=25, status="in_progress"):
    """Update progress for a concept"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "time_spent_minutes": time_spent,
        "progress_percent": progress_percent,
        "status": status
    }
    
    resp = requests.post(f"{API_URL}/progress/concepts/{concept_id}/update", 
                        json=data, headers=headers)
    
    if resp.status_code != 200:
        print(f"⚠️  Failed to update progress for {concept_id}: {resp.text}")
        return False
    
    print(f"✅ Updated progress for concept {concept_id}")
    return True

def populate_test_data():
    """Populate database with test progress data"""
    print("🚀 Starting Test Data Population")
    print("=" * 50)
    
    try:
        # 1. Login
        print("🔐 Authenticating...")
        token = login()
        print("✅ Authentication successful!")
        
        # 2. Get concepts
        print("\n📚 Fetching concepts...")
        concepts_data = get_concepts(token)
        concepts = concepts_data if isinstance(concepts_data, list) else concepts_data.get('concepts', [])
        
        if not concepts:
            print("⚠️  No concepts found in database. Please seed concepts first.")
            return
        
        print(f"✅ Found {len(concepts)} concepts")
        
        # 3. Update progress for some concepts
        print("\n📊 Creating test progress data...")
        
        # Create realistic progress data
        progress_scenarios = [
            # (time_spent, progress_percent, status)
            (45, 100, "completed"),
            (30, 75, "in_progress"),
            (60, 100, "completed"),
            (15, 25, "in_progress"),
            (90, 50, "in_progress"),
        ]
        
        for i, concept in enumerate(concepts[:5]):  # Update first 5 concepts
            scenario = progress_scenarios[i % len(progress_scenarios)]
            time_spent, progress_percent, status = scenario
            
            success = update_concept_progress(
                concept['concept_id'], 
                time_spent, 
                progress_percent, 
                status
            )
            
            if success:
                print(f"   📈 {concept['display_name']}: {progress_percent}% {status}")
        
        # 4. Test progress endpoint
        print("\n🔍 Testing progress endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        progress_resp = requests.get(f"{API_URL}/progress", headers=headers)
        
        if progress_resp.status_code == 200:
            progress_data = progress_resp.json()
            stats = progress_data.get('overall_stats', {})
            print(f"✅ Progress endpoint working!")
            print(f"   📊 Concepts learned: {stats.get('total_concepts_learned', 0)}")
            print(f"   ⏰ Time spent: {stats.get('total_time_spent', 0)} hours")
            print(f"   🎯 Completion rate: {stats.get('completion_rate', 0)}%")
            print(f"   🔥 Learning streak: {stats.get('learning_streak', 0)} days")
        else:
            print(f"⚠️  Progress endpoint test failed: {progress_resp.text}")
        
        # 5. Test learning paths endpoint
        print("\n🛤️  Testing learning paths endpoint...")
        paths_resp = requests.get(f"{API_URL}/learning-paths", headers=headers)
        
        if paths_resp.status_code == 200:
            paths_data = paths_resp.json()
            print(f"✅ Learning paths endpoint working!")
            print(f"   📋 Generated {len(paths_data)} learning paths")
            for path in paths_data[:2]:  # Show first 2 paths
                print(f"      • {path['title']} ({path['difficulty']})")
        else:
            print(f"⚠️  Learning paths endpoint test failed: {paths_resp.text}")
        
        print("\n" + "=" * 50)
        print("🎉 TEST DATA POPULATION COMPLETE!")
        print("\nNext steps:")
        print("1. Start the frontend: http://localhost:8080")
        print("2. Login with cavin_admin / secure_password_123")
        print("3. Check the Dashboard for real progress stats")
        print("4. Visit Progress page to see detailed analytics")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure backend is running: uvicorn main:app --reload")
        print("2. Check that concepts are seeded in the database")
        print("3. Verify database connections are working")

if __name__ == "__main__":
    populate_test_data()