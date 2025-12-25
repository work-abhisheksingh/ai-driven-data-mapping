import os

ALLOWED_EXTENSIONS = [".csv", ".xlsx"]

def validate_file(file_path):
    ext = os.path.splitext(file_path)[1]

    if ext not in ALLOWED_EXTENSIONS:
        return {"valid": False, "reason": "Unsupported file format"}

    if os.path.getsize(file_path) == 0:
        return {"valid": False, "reason": "Empty file"}

    return {"valid": True}
