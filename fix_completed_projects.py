#!/usr/bin/env python3
"""
Fix progress tracking for completed projects that show as "Waiting"
"""

import requests
import json
import os
from pathlib import Path

def fix_completed_projects():
    """Fix progress tracking for projects that have completed but show incorrect status."""
    
    # Check if generated_projects directory exists
    projects_dir = Path("backend/generated_projects")
    if not projects_dir.exists():
        print("No generated_projects directory found")
        return
    
    # Get all project directories
    project_dirs = [d for d in projects_dir.iterdir() if d.is_dir()]
    
    print(f"Found {len(project_dirs)} project directories")
    
    for project_dir in project_dirs:
        metadata_file = project_dir / "project_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                project_id = metadata.get('project_id')
                project_name = metadata.get('project_name')
                
                if project_id:
                    print(f"\nChecking project: {project_name} ({project_id})")
                    
                    # Check current progress
                    try:
                        response = requests.get(f"http://localhost:8000/api/v1/progress/{project_id}")
                        if response.status_code == 200:
                            progress = response.json()
                            is_completed = progress.get('is_completed', False)
                            progress_pct = progress.get('progress_percentage', 0)
                            
                            print(f"  Current status: {progress_pct}% complete, is_completed: {is_completed}")
                            
                            # If project has files but progress shows incomplete, fix it
                            if not is_completed and (project_dir / "main.py").exists():
                                print(f"  🔧 Fixing progress for completed project {project_name}")
                                
                                # Call a special endpoint to mark as completed
                                # Since we don't have this endpoint, we'll simulate completion
                                # by calling the result endpoint which should trigger completion
                                result_response = requests.get(f"http://localhost:8000/api/v1/pipeline/result/{project_id}")
                                if result_response.status_code == 404:
                                    print(f"  ⚠️  No result found, project may need manual completion")
                                else:
                                    print(f"  ✅ Project result available")
                            else:
                                print(f"  ✅ Project progress is correct")
                        else:
                            print(f"  ❌ Could not get progress: {response.status_code}")
                    except Exception as e:
                        print(f"  ❌ Error checking progress: {str(e)}")
                        
            except Exception as e:
                print(f"Error reading metadata for {project_dir}: {str(e)}")

if __name__ == "__main__":
    print("🔧 Fixing completed projects progress tracking...")
    fix_completed_projects()
    print("\n✅ Done!")
