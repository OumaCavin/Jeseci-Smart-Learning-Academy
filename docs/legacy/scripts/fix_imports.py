#!/usr/bin/env python3
"""
Fix import paths in all API files
"""

import os
import sys

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    print(f"Fixing imports in {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix backend imports
    content = content.replace('from api.v1.auth import get_current_user', 
                             'from api.v1.auth import get_current_user')
    content = content.replace('from config.database import get_db', 
                             'from config.database import get_db')
    content = content.replace('from database.models import User', 
                             'from database.models import User')
    content = content.replace('from database.models import', 
                             'from database.models import')
    
    # Add sys.path append at the top
    if 'import sys' not in content:
        import_insert = """import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

"""
        content = import_insert + content
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)

# Fix all API files
api_files = [
    'backend/api/v1/learning_paths.py',
    'backend/api/v1/progress.py', 
    'backend/api/v1/quizzes.py',
    'backend/api/v1/achievements.py',
    'backend/api/v1/analytics.py',
    'backend/api/v1/concepts.py'
]

for file_path in api_files:
    if os.path.exists(file_path):
        fix_imports_in_file(file_path)

print("All import fixes completed!")