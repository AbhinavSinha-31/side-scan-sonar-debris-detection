#!/usr/bin/env python
"""
Phase 7 Code Structure Validation — No External Dependencies
Validates that all required components are present and properly structured
"""

import sys
from pathlib import Path
import ast
import json

project_root = Path(__file__).parent


def check_file_exists(path: Path, description: str) -> tuple[bool, str]:
    """Check if a file exists"""
    if path.exists():
        return True, f"✓ {description}: {path.relative_to(project_root)}"
    else:
        return False, f"✗ {description} MISSING: {path}"


def check_function_exists(file_path: Path, function_names: list[str]) -> tuple[bool, str]:
    """Check if functions are defined in a Python file"""
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
            return True, f"✓ {file_path.name} has all required functions: {', '.join(function_names[:3])}..."
    
    except Exception as e:
        return False, f"✗ Error parsing {file_path}: {e}"


def validate_phase7_structure():
    """Comprehensive Phase 7 structure validation"""
    print("=" * 70)
    print("PHASE 7 CODE STRUCTURE VALIDATION")
    print("=" * 70)
    
    checks = []
    
    # Check core filtering module
    print("\n[1] Core Filtering Module")
    path = project_root / "backend/services/filtering/filter.py"
    checks.append(check_file_exists(path, "Filtering module"))
    checks.append(check_function_exists(path, [
        "default_filter_config", "box_iou", "combined_score", "_suppress_overlaps",
        "FalsePositiveFilter"
    ]))
    
    # Check geometry module
    print("\n[2] Geometry Analysis Module")
    path = project_root / "backend/services/filtering/geometry.py"
    checks.append(check_file_exists(path, "Geometry module"))
    checks.append(check_function_exists(path, [
        "box_geometry", "geometry_hard_reject", "geometry_score"
    ]))
    
    # Check shape module
    print("\n[3] Shape Analysis Module")
    path = project_root / "backend/services/filtering/shape.py"
    checks.append(check_file_exists(path, "Shape module"))
    checks.append(check_function_exists(path, [
        "analyze_shape", "shape_score"
    ]))
    
    # Check metrics module
    print("\n[4] Metrics Module")
    path = project_root / "backend/services/filtering/metrics.py"
    checks.append(check_file_exists(path, "Metrics module"))
    checks.append(check_function_exists(path, [
        "match_detections", "precision_recall_f1", "compare_before_after"
    ]))
    
    # Check visualization module
    print("\n[5] Visualization Module")
    path = project_root / "backend/services/filtering/visualize.py"
    checks.append(check_file_exists(path, "Visualization module"))
    checks.append(check_function_exists(path, ["render_comparison"]))
    
    # Check detection types
    print("\n[6] Detection Types")
    path = project_root / "backend/services/detection/types.py"
    checks.append(check_file_exists(path, "Detection types"))
    checks.append(check_function_exists(path, ["DetectionResult"]))
    
    # Check YOLO service
    print("\n[7] YOLO Inference Service")
    path = project_root / "backend/services/detection/yolo.py"
    checks.append(check_file_exists(path, "YOLO service"))
    checks.append(check_function_exists(path, ["YOLOInferenceService"]))
    
    # Check API endpoints
    print("\n[8] Detection API Endpoints")
    path = project_root / "backend/api/detections.py"
    checks.append(check_file_exists(path, "Detection API"))
    checks.append(check_function_exists(path, [
        "get_filter_config", "filter_raw_detections", "detect_file", "compare_visualization"
    ]))
    
    # Check configuration
    print("\n[9] Configuration")
    path = project_root / "backend/utils/config.py"
    checks.append(check_file_exists(path, "Config module"))
    
    # Check tests
    print("\n[10] Unit Tests")
    path = project_root / "tests/unit/test_false_positive_filter.py"
    checks.append(check_file_exists(path, "FP filter tests"))
    checks.append(check_function_exists(path, [
        "test_confidence_filter_rejects_low_scores",
        "test_geometry_rejects_noise_and_full_frame_artifacts_but_keeps_elongated_net",
        "test_shape_analysis_runs_on_image_crops"
    ]))
    
    # Check documentation
    print("\n[11] Documentation")
    path = project_root / "docs/phase7.md"
    checks.append(check_file_exists(path, "Phase 7 documentation"))
    
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


def validate_config_parameters():
    """Validate that all Phase 7 configuration parameters are defined"""
    print("\n" + "=" * 70)
    print("PHASE 7 CONFIGURATION VALIDATION")
    print("=" * 70)
    
    config_path = project_root / "backend/utils/config.py"
    
    required_params = {
        "confidence_threshold": "float",
        "model_confidence_weight": "float",
        "shadow_score_weight": "float",
        "shape_score_weight": "float",
        "fp_geometry_score_weight": "float",
        "fp_min_relative_area": "float",
        "fp_max_relative_area": "float",
        "fp_max_aspect_ratio": "float",
        "fp_min_box_side_px": "int",
        "fp_overlap_iou": "float",
        "fp_confirmed_score": "float",
        "fp_possible_score": "float",
    }
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        
        print("\nChecking for Phase 7 configuration parameters:")
        passed = 0
        failed = 0
        
        for param_name, param_type in required_params.items():
            if param_name in content:
                print(f"  ✓ {param_name}: {param_type}")
                passed += 1
            else:
                print(f"  ✗ {param_name}: MISSING")
                failed += 1
        
        print(f"\nConfiguration Parameters: {passed}/{passed+failed} present")
        return failed == 0
    
    except Exception as e:
        print(f"✗ Error reading config: {e}")
        return False


def validate_api_endpoints():
    """Validate that all Phase 7 API endpoints are defined"""
    print("\n" + "=" * 70)
    print("PHASE 7 API ENDPOINTS VALIDATION")
    print("=" * 70)
    
    api_path = project_root / "backend/api/detections.py"
    
    required_endpoints = {
        "GET /api/detections/filter/config": "get_filter_config",
        "POST /api/detections/filter": "filter_raw_detections",
        "POST /api/detections/files/{file_id}": "detect_file",
        "POST /api/detections/files/{file_id}/compare": "compare_visualization",
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


def main():
    """Run all validations"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "PHASE 7 VALIDATION SUITE — Code Structure Check".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    results = {
        "Structure": validate_phase7_structure(),
        "Configuration": validate_config_parameters(),
        "API Endpoints": validate_api_endpoints(),
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
        print("\n✓✓✓ PHASE 7 STRUCTURE VALIDATION COMPLETE — ALL CHECKS PASSED ✓✓✓\n")
        return 0
    else:
        print("\n✗ Some validations failed. Review above for details.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
