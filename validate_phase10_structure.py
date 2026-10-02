#!/usr/bin/env python
"""
Phase 10 Structure Validation Script
Validates that all Phase 10 components are properly implemented
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_file_exists(path, description):
    """Check if file exists"""
    if Path(path).exists():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} - NOT FOUND")
        return False

def check_imports():
    """Check if modules can be imported"""
    checks = []
    
    try:
        from backend.services.database.detection_repository import DetectionRepository
        print("✓ DetectionRepository imported")
        checks.append(True)
    except Exception as e:
        print(f"✗ DetectionRepository: {e}")
        checks.append(False)
    
    try:
        from backend.services.reports.generator import ReportGenerator
        print("✓ ReportGenerator imported")
        checks.append(True)
    except Exception as e:
        print(f"✗ ReportGenerator: {e}")
        checks.append(False)
    
    try:
        from backend.services.reports.export import ExportService
        print("✓ ExportService imported")
        checks.append(True)
    except Exception as e:
        print(f"✗ ExportService: {e}")
        checks.append(False)
    
    try:
        from backend.api import database
        print("✓ Database API router imported")
        checks.append(True)
    except Exception as e:
        print(f"✗ Database API router: {e}")
        checks.append(False)
    
    return all(checks)

def check_files():
    """Check if required files exist"""
    files_to_check = [
        ("backend/services/database/detection_repository.py", "Detection Repository"),
        ("backend/services/reports/generator.py", "Report Generator"),
        ("backend/services/reports/export.py", "Export Service"),
        ("backend/api/database.py", "Database API"),
        ("tests/unit/test_phase10_database.py", "Phase 10 Tests"),
    ]
    
    checks = []
    for file_path, description in files_to_check:
        full_path = project_root / file_path
        checks.append(check_file_exists(full_path, description))
    
    return all(checks)

def check_database_models():
    """Check database models have Phase 10 fields"""
    try:
        from backend.database.models import Detection, Report
        
        # Check Detection model has size fields
        if hasattr(Detection, 'estimated_width_m'):
            print("✓ Detection model has size estimation fields")
        else:
            print("✗ Detection model missing size estimation fields")
            return False
        
        # Check Report model exists
        if Report:
            print("✓ Report model exists")
        else:
            print("✗ Report model missing")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Database model check failed: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("PHASE 10 — DATABASE/REPORT VALIDATION")
    print("="*70 + "\n")
    
    print("FILE STRUCTURE CHECK:")
    print("-" * 70)
    files_ok = check_files()
    
    print("\nDATABASE MODEL CHECK:")
    print("-" * 70)
    models_ok = check_database_models()
    
    print("\nIMPORT CHECK:")
    print("-" * 70)
    imports_ok = check_imports()
    
    print("\n" + "="*70)
    if files_ok and models_ok and imports_ok:
        print("✓✓✓ PHASE 10 VALIDATION PASSED ✓✓✓")
        print("="*70)
        return 0
    else:
        print("✗✗✗ PHASE 10 VALIDATION FAILED ✗✗✗")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
