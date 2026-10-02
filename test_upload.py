"""Phase 3 upload smoke tests for the Sonar ingestion API."""

import shutil
import tempfile
from pathlib import Path

import requests
from PIL import Image

from backend.database.models import SonarFile
from backend.database.session import SessionLocal
from backend.services.sonar.storage import storage_service

UPLOAD_URL = "http://localhost:8000/api/sonar/upload"


def create_valid_test_image(directory: Path) -> Path:
    """Create a real PNG image that passes Pillow/OpenCV validation."""
    image_path = directory / "valid_upload_test.png"
    image = Image.new("RGB", (320, 180), color=(10, 30, 50))
    for x in range(0, 320, 32):
        image.paste((40, 120, 180), (x, 40, x + 20, 140))
    image.save(image_path, format="PNG")
    return image_path


def upload_valid_image() -> tuple[dict, Path, SonarFile | None]:
    temp_dir = Path(tempfile.mkdtemp(prefix="sonar_upload_"))
    image_path = create_valid_test_image(temp_dir)

    try:
        with image_path.open("rb") as file_handle:
            response = requests.post(
                UPLOAD_URL,
                files={"file": (image_path.name, file_handle, "image/png")},
                timeout=30,
            )

        print(f"Valid upload status: {response.status_code}")
        print(response.text)
        assert response.status_code == 200, response.text

        data = response.json()
        required_fields = {"id", "original_filename", "file_type", "status", "metadata", "is_demo"}
        missing = sorted(required_fields - set(data.keys()))
        assert not missing, f"Missing response fields: {missing}"
        assert data["status"] == "READY"
        assert data["file_type"] == "image"
        assert data["is_demo"] is False
        assert data["original_filename"] == image_path.name

        db = SessionLocal()
        try:
            record = (
                db.query(SonarFile)
                .filter(SonarFile.original_filename == image_path.name)
                .order_by(SonarFile.id.desc())
                .first()
            )
            assert record is not None, "Database record was not created for the uploaded file"
            assert record.status == "READY"
            stored_path = storage_service.retrieve_file(record.stored_filename)
            assert stored_path is not None, "Uploaded file was not stored on disk"
            with Image.open(stored_path) as opened:
                assert opened.size == (320, 180)
            return data, stored_path, record
        finally:
            db.close()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def upload_invalid_file() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="sonar_invalid_"))
    invalid_path = temp_dir / "corrupt_upload.png"
    invalid_path.write_bytes(b"this-is-not-a-valid-image")

    try:
        with invalid_path.open("rb") as file_handle:
            response = requests.post(
                UPLOAD_URL,
                files={"file": (invalid_path.name, file_handle, "image/png")},
                timeout=30,
            )

        print(f"Invalid upload status: {response.status_code}")
        print(response.text)
        assert response.status_code == 400, response.text
        payload = response.json()
        assert payload.get("error") == "VALIDATION_ERROR" or payload.get("error") == "FILE_VALIDATION_ERROR"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("Running valid upload smoke test...")
    data, stored_path, record = upload_valid_image()
    print("Valid upload test passed")
    print(f"Upload ID: {data['id']}")
    print(f"Stored file exists: {stored_path.exists()}")
    print(f"Database status: {record.status}")

    print("\nRunning invalid upload rejection test...")
    upload_invalid_file()
    print("Invalid upload rejection test passed")
