#!/usr/bin/env python
"""
Phase 15 Structure Validation Script
Validates that all Phase 15 (Frontend Dashboard & Map) components are properly
implemented and integrated.
"""

import sys
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
    """Check if Phase 15 modules can be imported"""
    checks = []

    try:
        from backend.api import database
        print("✓ database API module imported (Phase 15 endpoints)")
        checks.append(True)
    except Exception as e:
        print(f"✗ database API: {e}")
        checks.append(False)

    from backend.main import app
    print("✓ backend.main imported")

    return all(checks)

def check_files():
    """Check if required Phase 15 files exist on backend and frontend"""
    files_to_check = [
        ("backend/api/database.py", "Dashboard API (Phase 15 endpoints)"),
        ("frontend/src/pages/Dashboard.jsx", "Dashboard page"),
        ("frontend/src/components/MapViewer.jsx", "Map (Leaflet) viewer"),
        ("frontend/src/components/dashboard/StatsCards.jsx", "Stats cards component"),
        ("frontend/src/components/dashboard/Filters.jsx", "Filters component"),
        ("frontend/src/components/dashboard/DetectionTable.jsx", "Detection table component"),
        ("frontend/src/components/dashboard/DetailPanel.jsx", "Detail panel component"),
        ("frontend/src/components/dashboard/Charts.jsx", "Charts component"),
        ("frontend/src/components/dashboard/SonarImageViewer.jsx", "Sonar image viewer component"),
        ("frontend/src/services/api.js", "Frontend API service layer"),
        ("tests/unit/test_phase15_dashboard.py", "Phase 15 Unit Tests"),
        ("docs/phase15.md", "Phase 15 Documentation"),
    ]

    checks = []
    for file_path, description in files_to_check:
        checks.append(check_file_exists(project_root / file_path, description))

    return all(checks)

def check_routes():
    """Check if Phase 15 dashboard routes are registered"""
    try:
        from backend.main import app

        def iter_route_paths():
            for route in app.routes:
                if hasattr(route, 'path'):
                    yield route.path
                original = getattr(route, 'original_router', None)
                if original is not None:
                    for sub in getattr(original, 'routes', []):
                        if hasattr(sub, 'path'):
                            yield sub.path

        paths = list(iter_route_paths())
        required = [
            "/api/database/detections/list",
            "/api/database/detections/detail/{detection_key}",
            "/api/database/detections/{detection_id}/image",
            "/api/database/statistics",
        ]
        missing = [r for r in required if r not in paths]

        if not missing:
            print("✓ Phase 15 dashboard routes registered")
            return True
        else:
            print(f"✗ Missing routes: {missing}")
            return False
    except Exception as e:
        print(f"✗ Route check failed: {e}")
        return False

def check_feature_flags():
    """Check that the /api/config feature flags expose Dashboard + Map"""
    try:
        from fastapi.testclient import TestClient
        from backend.main import app

        with TestClient(app) as client:
            response = client.get("/api/config")
            if response.status_code != 200:
                print(f"✗ /api/config returned {response.status_code}")
                return False
            config = response.json()
            features = config.get("features", {}) if isinstance(config, dict) else {}
            ok = True
            if features.get("dashboard") is not True:
                print("✗ dashboard feature flag not enabled in main.py")
                ok = False
            else:
                print("✓ dashboard feature flag enabled")
            if features.get("map_visualization") is not True:
                print("✗ map_visualization feature flag not enabled in main.py")
                ok = False
            else:
                print("✓ map_visualization feature flag enabled")
            if not config.get("phase", "").startswith("15"):
                print(f"✗ /api/config phase is not Phase 15: {config.get('phase')}")
                ok = False
            else:
                print("✓ /api/config phase is Phase 15")
            return ok
    except Exception as e:
        print(f"✗ Feature flag check failed: {e}")
        return False

def check_frontend_build_deps():
    """Check that the frontend declares the map/chart dependencies"""
    try:
        import json
        pkg = json.loads((project_root / "frontend" / "package.json").read_text())
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        ok = True
        for dep in ["react-leaflet", "leaflet", "recharts", "axios"]:
            if dep not in deps:
                print(f"✗ frontend dependency missing: {dep}")
                ok = False
            else:
                print(f"✓ frontend dependency present: {dep}")
        return ok
    except Exception as e:
        print(f"✗ Frontend dependency check failed: {e}")
        return False

def check_dashboard_wiring():
    """Check that the MapViewer is wired into the Dashboard page"""
    try:
        dash = (project_root / "frontend/src/pages/Dashboard.jsx").read_text()
        ok = True
        if "MapViewer" not in dash:
            print("✗ Dashboard.jsx does not import MapViewer")
            ok = False
        else:
            print("✓ Dashboard.jsx imports MapViewer")
        if "<MapViewer" not in dash:
            print("✗ Dashboard.jsx does not render MapViewer")
            ok = False
        else:
            print("✓ Dashboard.jsx renders MapViewer")
        return ok
    except Exception as e:
        print(f"✗ Dashboard wiring check failed: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("PHASE 15 — FRONTEND DASHBOARD & MAP VALIDATION")
    print("=" * 70 + "\n")

    print("FILE STRUCTURE CHECK:")
    print("-" * 70)
    files_ok = check_files()

    print("\nIMPORT CHECK:")
    print("-" * 70)
    imports_ok = check_imports()

    print("\nROUTE CHECK:")
    print("-" * 70)
    routes_ok = check_routes()

    print("\nFEATURE FLAG CHECK:")
    print("-" * 70)
    flags_ok = check_feature_flags()

    print("\nFRONTEND DEPENDENCY CHECK:")
    print("-" * 70)
    deps_ok = check_frontend_build_deps()

    print("\nDASHBOARD WIRING CHECK:")
    print("-" * 70)
    wiring_ok = check_dashboard_wiring()

    print("\n" + "=" * 70)
    results = [files_ok, imports_ok, routes_ok, flags_ok, deps_ok, wiring_ok]
    if all(results):
        print("✓✓✓ PHASE 15 VALIDATION PASSED ✓✓✓")
        print("=" * 70)
        return 0
    else:
        print("✗✗✗ PHASE 15 VALIDATION FAILED ✗✗✗")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
