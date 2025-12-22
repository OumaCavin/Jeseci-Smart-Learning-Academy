#!/usr/bin/env python3
"""
Example script to create a concept via the Jeseci Smart Learning Companion API
"""

import requests
import json
import os

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1_STR = os.getenv("API_V1_STR", "/api/v1")
CONCEPTS_ENDPOINT = f"{API_BASE_URL}{API_V1_STR}/concepts"

def create_concept(concept_data, auth_token=None):
    """
    Create a new concept via the API
    
    Args:
        concept_data (dict): The concept data to create
        auth_token (str): JWT authentication token (optional for testing)
    
    Returns:
        dict: API response
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        response = requests.post(CONCEPTS_ENDPOINT, json=concept_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating concept: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return None

def main():
    """Main function to demonstrate concept creation"""
    
    # Load sample concept data
    with open("sample_concept_data.json", "r") as f:
        concept_data = json.load(f)
    
    print("🚀 Creating Object-Oriented Programming concept...")
    print(f"Endpoint: {CONCEPTS_ENDPOINT}")
    print("\n📝 Concept Data:")
    print(json.dumps(concept_data, indent=2))
    
    # Create the concept
    result = create_concept(concept_data)
    
    if result:
        print("\n✅ Concept created successfully!")
        print("Response:", json.dumps(result, indent=2))
    else:
        print("\n❌ Failed to create concept")
        print("Make sure the API server is running and accessible")

if __name__ == "__main__":
    main()