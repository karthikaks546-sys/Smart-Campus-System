"""
modules/file_manager.py
Lab 6 — File Handling (read/write/process)
Lab 7 — Directory Scanning + Exception Handling + User-defined Exceptions
"""
import os
import csv
import json
from pathlib import Path
from typing import Generator


# ── User-defined Exceptions (Lab 7) ───────────────────────────────────────────
class MissingFileOrFolderError(Exception):
    """Raised when a required file or folder is missing."""
    pass

class InvalidFileFormatError(Exception):
    """Raised when an uploaded file has an unexpected format."""
    pass

class EmptyDirectoryError(Exception):
    """Raised when a scanned directory contains no files."""
    pass


# ── File Validation (Lab 7 pattern) ──────────────────────────────────────────
def validate_path(path: str) -> Path:
    """Validate that a path exists; raise FileNotFoundError otherwise."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    return p


def validate_csv_columns(filepath: str, required_columns: list[str]):
    """Check that a CSV file contains the required column headers."""
    try:
        with open(filepath, "r", newline="") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            missing = [c for c in required_columns if c not in headers]
            if missing:
                raise InvalidFileFormatError(
                    f"CSV missing columns: {missing}. Found: {headers}")
    except FileNotFoundError:
        raise MissingFileOrFolderError(f"File not found: {filepath}")


# ── Directory Scanner (Lab 7) ─────────────────────────────────────────────────
def scan_directory(path: str) -> Generator[str, None, None]:
    """
    Yields formatted lines of a directory tree.
    Raises custom exceptions for missing paths or empty folders.
    """
    try:
        root_path = validate_path(path)
        yield f"📁 Scanning: {root_path}\n"

        for root, dirs, files in os.walk(root_path):
            level = root.replace(str(root_path), "").count(os.sep)
            indent = "    " * level
            yield f"{indent}📂 {os.path.basename(root)}/"

            sub_indent = "    " * (level + 1)
            for f in files:
                yield f"{sub_indent}📄 {f}"

            if not files and not dirs:
                raise EmptyDirectoryError(f"Empty folder detected: {root}")

    except FileNotFoundError as e:
        yield f"❌ Error: {e}"
    except EmptyDirectoryError as e:
        yield f"⚠️  Warning: {e}"
    except PermissionError:
        yield "❌ Error: Permission denied."
    except Exception as e:
        yield f"❌ Unexpected Error: {e}"


# ── CSV Import for Academic Records (Lab 6 pattern) ──────────────────────────
def parse_uploaded_records_csv(filepath: str) -> list[dict]:
    """
    Read an uploaded CSV and return list of record dicts.
    Expected columns: student_id, name, math, science, english
    """
    required = ["student_id", "name", "math", "science", "english"]
    validate_csv_columns(filepath, required)

    records = []
    with open(filepath, "r", newline="") as f:
        for row in csv.DictReader(f):
            try:
                records.append({
                    "student_id": row["student_id"].strip(),
                    "name": row["name"].strip(),
                    "math": str(float(row["math"])),
                    "science": str(float(row["science"])),
                    "english": str(float(row["english"])),
                })
            except (ValueError, KeyError) as e:
                raise InvalidFileFormatError(f"Bad row {row}: {e}")
    return records


def parse_uploaded_students_csv(filepath: str) -> list[dict]:
    """Read uploaded student CSV. Expected: student_id, name, age, email, contact"""
    required = ["student_id", "name", "age"]
    validate_csv_columns(filepath, required)

    students = []
    with open(filepath, "r", newline="") as f:
        for row in csv.DictReader(f):
            students.append({
                "student_id": row.get("student_id", "").strip(),
                "name": row.get("name", "").strip(),
                "age": row.get("age", "0").strip(),
                "email": row.get("email", "").strip(),
                "contact": row.get("contact", "").strip(),
            })
    return students
