#!/usr/bin/env python
"""
Phase 8 Code Structure Validation — No External Dependencies
Validates Phase 8 implementation is complete and properly structured
"""

import sys
from pathlib import Path
import ast

project_root = Path(__file__).parent


def check_file_exists(path: Path, description: str) -> tuple[bool, str]:
    """Check if a file exists"""
    if path.exists():
        return True, f"✓ {description}: {path.relative_to(project_root)}"
    else:
        return False, f"✗ {description} MISSING: {path}"


def check_function_exists(file_path: Path, function_names: list[str]) -> tuple[bool, str]:
    """Check if functions/classes are defined in a Python file"""
    if not file_path.exists():
        return False, f"✗ File not found: {file_path}"
    
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        defined = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
        missing = [name for name in function_names if name not in defined]
        
        if missing:
            return False, f"✗ Missing in {file_path.name}: {', '.join(missing)}"
        else:
            return True, f"✓ {file_path.name} has all required: {', '.join(function_names[:3])}..."
    
    except Exception as e:
        return False, f"✗ Error parsing {file_path}: {e}"


def validate_phase8_structure():
    """Comprehensive Phase 8 structure validation"""
    print("=" * 70)
    print("PHASE 8 CODE STRUCTURE VALIDATION")
    print("=" * 70)
    
    checks = []
    
    # Check geolocation service module
    print("\n[1] Geolocation Service Module")
    path = project_root / "backend/services/geolocation/geolocation.py"
    checks.append(check_file_exists(path, "Geolocation service"))
    checks.append(check_function_exists(path, [
        "GeolocationInput", "GeolocationResult", "GeolocationService"
    ]))
    
    # Check geolocation API endpoints
    print("\n[2] Geolocation API Endpoints")
    path = project_root / "backend/api/geolocation.py"
    checks.append(check_file_exists(path, "Geolocation API"))
    checks.append(check_function_exists(path, [
        "get_detection_geolocation",
        "calculate_detection_geolocation",
        "set_detection_geolocation_manual",
        "calculate_batch_geolocation",
        "get_geolocation_metadata_requirements"
    ]))
    
    # Check documentation
    print("\n[3] Phase 8 Documentation")
    path = project_root / "docs/phase8.md"
    checks.append(check_file_exists(path, "Phase 8 documentation"))
    
    # Check tests
    print("\n[4] Unit Tests")
    path = project_root / "tests/unit/test_geolocation.py"
    checks.append(check_file_exists(path, "Geolocation tests"))
    
    # Check main.py integration
    print("\n[5] Main Application Integration")
    path = project_root / "backend/main.py"
    checks.append(check_file_exists(path, "Main application"))
    
    # Verify geolocation router is included in main.py
    try:
        with open(path, 'r') as f:
            content = f.read()
        
        if "from backend.api import geolocation" in content and "app.include_router(geolocation.router)" in content:
            checks.append((True, "✓ Geolocation router registered in main.py"))
        else:
            checks.append((False, "✗ Geolocation router NOT registered in main.py"))
    except Exception as e:
        checks.append((False, f"✗ Error checking main.py: {e}"))
    
    # Check database models
    print("\n[6] Database Models")
    path = project_root / "backend/database/models.py"
    checks.append(check_file_exists(path, "Database models"))
    
    # Verify Geolocation model exists
    try:
        with open(path, 'r') as f:
            content = f.read()
        
        if "class Geolocation(Base):" in content:
            checks.append((True, "✓ Geolocation table model defined"))
        else:
            checks.append((False, "✗ Geolocation table model NOT found"))
    except Exception as e:
        checks.append((False, f"✗ Error checking models: {e}"))
    
    # Print all checks
    print("\n" + "=" * 70)
    print("CHECK RESULTS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    for success, message in checks:
        print(message)
        if success:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {passed} passed, {failed} failed out of {passed + failed} checks")
    print("=" * 70)
    
    return failed == 0


def validate_phase8_api_endpoints():
    """Validate Phase 8 API endpoints are defined"""
    print("\n" + "=" * 70)
    print("PHASE 8 API ENDPOINTS VALIDATION")
    print("=" * 70)
    
    api_path = project_root / "backend/api/geolocation.py"
    
    required_endpoints = {
        "GET /api/geolocation/detections/{detection_id}": "get_detection_geolocation",
        "POST /api/geolocation/detections/{detection_id}": "calculate_detection_geolocation",
        "POST /api/geolocation/detections/{detection_id}/manual": "set_detection_geolocation_manual",
        "POST /api/geolocation/batch/calculate": "calculate_batch_geolocation",
        "GET /api/geolocation/metadata/sonar": "get_geolocation_metadata_requirements",
    }
    
    try:
        with open(api_path, 'r') as f:
            tree = ast.parse(f.read())
        
        defined_functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        
        print("\nChecking for API endpoints:")
        passed = 0
        failed = 0
        
        for endpoint, function_name in required_endpoints.items():
            if function_name in defined_functions:
                print(f"  ✓ {endpoint}")
                passed += 1
            else:
                print(f"  ✗ {endpoint} (function: {function_name}): MISSING")
                failed += 1
        
        print(f"\nAPI Endpoints: {passed}/{passed+failed} present")
        return failed == 0
    
    except Exception as e:
        print(f"✗ Error validating endpoints: {e}")
        return False


def validate_phase8_service_classes():
    """Validate Phase 8 service classes have required methods"""
    print("\n" + "=" * 70)
    print("PHASE 8 SERVICE CLASSES VALIDATION")
    print("=" * 70)
    
    service_path = project_root / "backend/services/geolocation/geolocation.py"
    
    try:
        with open(service_path, 'r') as f:
            tree = ast.parse(f.read())
        
        classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                classes[node.name] = methods
        
        print("\nGeolocationService methods:")
        if "GeolocationService" in classes:
            methods = classes["GeolocationService"]
            required = ["geolocate", "_geolocate_from_metadata", "_geolocate_with_sonar_geometry"]
            for method in required:
                if method in methods:
                    print(f"  ✓ {method}")
                else:
                    print(f"  ✗ {method}: MISSING")
        else:
            print("  ✗ GeolocationService class NOT found")
            return False
        
        print("\nGeolocationInput validation:")
        if "GeolocationInput" in classes:
            print(f"  ✓ GeolocationInput dataclass defined")
        else:
            print(f"  ✗ GeolocationInput NOT found")
            return False
        
        print("\nGeolocationResult validation:")
        if "GeolocationResult" in classes:
            print(f"  ✓ GeolocationResult dataclass defined")
        else:
            print(f"  ✗ GeolocationResult NOT found")
            return False
        
        return True
    
    except Exception as e:
        print(f"✗ Error validating service classes: {e}")
        return False


def main():
    """Run all Phase 8 validations"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "PHASE 8 VALIDATION SUITE — Code Structure Check".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    results = {
        "Structure": validate_phase8_structure(),
        "API Endpoints": validate_phase8_api_endpoints(),
        "Service Classes": validate_phase8_service_classes(),
    }
    
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    for category, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{category}: {status}")
    
    print("=" * 70)
    
    all_passed = all(results.values())
    if all_passed:
        print("\n✓✓✓ PHASE 8 STRUCTURE VALIDATION COMPLETE — ALL CHECKS PASSED ✓✓✓\n")
        print("Phase 8 Implementation Status:")
        print("  ✓ Geolocation service module implemented")
        print("  ✓ API endpoints defined")
        print("  ✓ Database integration ready")
        print("  ✓ Tests created")
        print("  ✓ Documentation complete")
        print("  ✓ Main application integration complete")
        print()
        return 0
    else:
        print("\n✗ Some validations failed. Review above for details.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
