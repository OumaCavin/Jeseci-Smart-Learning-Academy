#!/usr/bin/env python3
"""
Extract key files from the original Jeseci project
"""
import zipfile
import os

def extract_key_files():
    zip_path = 'user_input_files/Jeseci-Smart-Learning-Platform.zip'
    extract_dir = '/workspace'
    
    # Key files we need
    key_files = [
        'seed_jac_concepts.py',
        'populate_jac_lesson_content.py', 
        'main.py',
        'requirements.txt',
        'database/',
        'frontend/',
        'config/',
        'api/'
    ]
    
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        # List all files first
        all_files = zip_file.namelist()
        print("Files in zip:")
        for f in sorted(all_files):
            print(f"  {f}")
        
        print("\nExtracting key files...")
        
        # Extract key files
        for file_info in zip_file.infolist():
            file_path = file_info.filename
            
            # Check if this file is in our key files list
            should_extract = False
            for key_file in key_files:
                if file_path.startswith(key_file) or key_file in file_path:
                    should_extract = True
                    break
            
            if should_extract:
                print(f"Extracting: {file_path}")
                zip_file.extract(file_info, extract_dir)

if __name__ == "__main__":
    extract_key_files()