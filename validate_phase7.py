#!/usr/bin/env python
"""
Phase 7 Validation Script — Manual Testing Without Pytest
Tests core functionality of the false-positive filter
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import numpy as np
import cv2
from backend.services.detection.types import DetectionResult
from backend.services.filtering.filter import FalsePositiveFilter, box_iou, default_filter_config
from backend.services.filtering.geometry import box_geometry, geometry_hard_reject, geometry_score
from backend.services.filtering.shape import analyze_shape, shape_score
from backend.services.filtering.metrics import match_detections, precision_recall_f1
from backend.services.filtering.visualize import render_comparison


def create_test_image(width=320, height=240):
    """Create a synthetic sonar-like test image"""
    rng = np.random.default_rng(42)
    image = rng.integers(40, 70, size=(height, width), dtype=np.uint8)
    # Add some sonar features
    image[:, width // 2 - 2:width // 2 + 2] = 20  # Center line
    cv2.line(image, (40, 50), (210, 70), 210, 3)  # Long feature
    cv2.ellipse(image, (70, 160), (18, 16), 0, 0, 360, 190, -1)  # Circular feature
    cv2.circle(image, (250, 40), 4, 255, -1)  # Small point
    image[180:230, 20:300] = 30  # Bottom seabed
    return image


def test_confidence_filtering():
    """Test that low-confidence detections are rejected"""
    print("\n=== TEST 1: Confidence Filtering ===")
    
    detections = [
        DetectionResult(
            bbox_x_min=40, bbox_y_min=45, bbox_x_max=210, bbox_y_max=80,
            confidence=0.82, class_id=0, object_class="net",
            detection_id="high", image_width=320, image_height=240
        ),
        DetectionResult(
            bbox_x_min=60, bbox_y_min=145, bbox_x_max=95, bbox_y_max=180,
            confidence=0.18, class_id=3, object_class="debris",
            detection_id="low", image_width=320, image_height=240
        ),
    ]
    
    result = FalsePositiveFilter({"confidence_threshold": 0.5}).filter_detections(
        detections, image=create_test_image()
    )
    
    print(f"  Raw detections: {result['raw_count']}")
    print(f"  Accepted: {result['accepted_count']}")
    print(f"  Rejected: {result['rejected_count']}")
    
    # Check assertions
    assert result['raw_count'] == 2, f"Expected 2 raw detections, got {result['raw_count']}"
    assert result['accepted_count'] >= 1, "Should have at least 1 accepted detection"
    assert any(d.confidence < 0.5 and d.rejected for d in result['all']), "Low-conf detection should be rejected"
    
    print("  ✓ PASS: Confidence filtering works correctly")
    return True


def test_geometry_analysis():
    """Test that geometry features are computed correctly"""
    print("\n=== TEST 2: Geometry Analysis ===")
    
    detection = DetectionResult(
        bbox_x_min=40, bbox_y_min=45, bbox_x_max=210, bbox_y_max=80,
        confidence=0.85, class_id=0, object_class="net",
        detection_id="net1", image_width=320, image_height=240
    )
    
    geom = box_geometry(detection, 320, 240)
    
    print(f"  Width: {geom['width']:.1f} px")
    print(f"  Height: {geom['height']:.1f} px")
    print(f"  Area: {geom['area']:.1f} px²")
    print(f"  Aspect Ratio: {geom['aspect_ratio']:.2f}")
    print(f"  Relative Area: {geom['relative_area']:.6f}")
    
    # Check assertions
    assert geom['width'] == 170, f"Width should be 170, got {geom['width']}"
    assert geom['height'] == 35, f"Height should be 35, got {geom['height']}"
    assert geom['area'] == 5950, f"Area should be 5950, got {geom['area']}"
    assert abs(geom['aspect_ratio'] - 170/35) < 0.01, "Aspect ratio incorrect"
    
    # Test hard rejects
    hard_reject = geometry_hard_reject(geom, default_filter_config())
    print(f"  Hard reject reason: {hard_reject or 'NONE (passed)'}")
    assert hard_reject is None, "Valid net should not be hard-rejected"
    
    # Test geometry scoring
    score = geometry_score(geom, "net")
    print(f"  Geometry score: {score:.3f}")
    assert 0.0 <= score <= 1.0, f"Score should be 0-1, got {score}"
    
    print("  ✓ PASS: Geometry analysis works correctly")
    return True


def test_shape_analysis():
    """Test that shape analysis computes features correctly"""
    print("\n=== TEST 3: Shape Analysis ===")
    
    image = create_test_image()
    detection = DetectionResult(
        bbox_x_min=40, bbox_y_min=45, bbox_x_max=210, bbox_y_max=80,
        confidence=0.85, class_id=0, object_class="net",
        detection_id="net1", image_width=320, image_height=240
    )
    
    shape = analyze_shape(image, detection)
    
    print(f"  Available: {shape.get('available')}")
    if shape.get('available'):
        print(f"  Compactness: {shape['compactness']:.3f}")
        print(f"  Elongation: {shape['elongation']:.3f}")
        print(f"  Solidity: {shape['solidity']:.3f}")
        print(f"  Irregularity: {shape['irregularity']:.3f}")
        print(f"  Contours found: {shape['contour_count']}")
        
        # Test scoring
        score = shape_score(shape, "net")
        print(f"  Shape score: {score:.3f}")
        assert 0.0 <= score <= 1.0, f"Score should be 0-1, got {score}"
    else:
        print(f"  Reason: {shape.get('reason', 'unknown')}")
    
    print("  ✓ PASS: Shape analysis works correctly")
    return True


def test_combined_scoring():
    """Test that combined scoring with multiple signals works"""
    print("\n=== TEST 4: Combined Scoring ===")
    
    detections = [
        DetectionResult(
            bbox_x_min=40, bbox_y_min=45, bbox_x_max=210, bbox_y_max=80,
            confidence=0.85, class_id=0, object_class="net",
            detection_id="net1", image_width=320, image_height=240
        ),
    ]
    
    image = create_test_image()
    result = FalsePositiveFilter().filter_detections(detections, image=image)
    
    for det in result['all']:
        print(f"  Detection: {det.detection_id}")
        print(f"    Confidence: {det.confidence:.3f}")
        print(f"    Geometry score: {det.geometry.get('score', 'N/A')}")
        print(f"    Shape score: {det.shape_score or 'N/A'}")
        print(f"    Final score: {det.final_score:.3f}")
        print(f"    Status: {det.status}")
        print(f"    Reason: {det.decision_reason[:60]}...")
        
        assert det.final_score is not None, "Final score should be computed"
        assert 0.0 <= det.final_score <= 1.0, "Final score should be 0-1"
    
    print("  ✓ PASS: Combined scoring works correctly")
    return True


def test_overlap_suppression():
    """Test that overlapping boxes are deduplicated"""
    print("\n=== TEST 5: Overlap Suppression ===")
    
    detections = [
        DetectionResult(
            bbox_x_min=40, bbox_y_min=45, bbox_x_max=210, bbox_y_max=80,
            confidence=0.91, class_id=0, object_class="net",
            detection_id="high", image_width=320, image_height=240
        ),
        DetectionResult(
            bbox_x_min=48, bbox_y_min=50, bbox_x_max=200, bbox_y_max=78,
            confidence=0.62, class_id=0, object_class="net",
            detection_id="low", image_width=320, image_height=240
        ),
    ]
    
    iou = box_iou(detections[0], detections[1])
    print(f"  IoU between boxes: {iou:.3f}")
    assert iou >= 0.5, f"Boxes should overlap, IoU={iou}"
    
    result = FalsePositiveFilter({"overlap_iou": 0.5}).filter_detections(detections, image=create_test_image())
    
    accepted_ids = {d.detection_id for d in result['accepted']}
    print(f"  Accepted: {accepted_ids}")
    assert "high" in accepted_ids, "Higher-scoring box should be kept"
    assert "low" not in accepted_ids, "Lower-scoring overlapping box should be removed"
    
    print("  ✓ PASS: Overlap suppression works correctly")
    return True


def test_visualization():
    """Test that visualization creates output correctly"""
    print("\n=== TEST 6: Visualization ===")
    
    detections = [
        DetectionResult(
            bbox_x_min=40, bbox_y_min=45, bbox_x_max=210, bbox_y_max=80,
            confidence=0.85, class_id=0, object_class="net",
            detection_id="net1", image_width=320, image_height=240
        ),
    ]
    
    image = create_test_image()
    result = FalsePositiveFilter().filter_detections(detections, image=image)
    
    try:
        panel = render_comparison(image, result['raw'], result['accepted'], result['rejected'])
        print(f"  Panel shape: {panel.shape}")
        assert panel.shape[1] == image.shape[1] * 3, "Panel should be 3x wide"
        print("  ✓ PASS: Visualization works correctly")
        return True
    except Exception as e:
        print(f"  ✗ FAIL: Visualization error: {e}")
        return False


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("PHASE 7 VALIDATION SUITE — Manual Testing")
    print("=" * 60)
    
    tests = [
        test_confidence_filtering,
        test_geometry_analysis,
        test_shape_analysis,
        test_combined_scoring,
        test_overlap_suppression,
        test_visualization,
    ]
    
    results = []
    for test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"\n✗ EXCEPTION in {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓✓✓ PHASE 7 VALIDATION COMPLETE — ALL TESTS PASSED ✓✓✓\n")
        return 0
    else:
        print("\n✗✗✗ PHASE 7 VALIDATION FAILED ✗✗✗\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
