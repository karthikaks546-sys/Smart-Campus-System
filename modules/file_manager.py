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


def normalize_header(header: str) -> str:
    """Normalize a CSV header for flexible detection."""
    return "".join(
        ch.lower() if ch.isalnum() else "_"
        for ch in header.strip()
    ).strip("_")


def normalize_headers(headers: list[str]) -> dict[str, str]:
    """Return normalized header -> original header mapping."""
    return {
        normalize_header(h): h
        for h in headers if h is not None
    }


def validate_csv_columns(filepath: str, required_columns: list[str]):
    """Check that a CSV file contains the required column headers."""
    try:
        with open(filepath, "r", newline="") as f:
            reader = csv.DictReader(f)
            headers = [h for h in (reader.fieldnames or []) if h]
            normalized = normalize_headers(headers)
            missing = [c for c in required_columns if c not in normalized]
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
    Read an uploaded CSV and return a list of record dicts.
    Expected columns: student_id plus one or more score columns.
    The student name is optional and, when available, is preserved.
    """
    required = ["student_id"]
    validate_csv_columns(filepath, required)

    records = []
    with open(filepath, "r", newline="") as f:
        reader = csv.DictReader(f)
        headers = [h for h in (reader.fieldnames or []) if h]
        normalized = normalize_headers(headers)
        student_key = normalized["student_id"]
        name_key = normalized.get("name")
        score_keys = [h for h in headers if normalize_header(h) not in ("student_id", "name")]

        if not score_keys:
            raise InvalidFileFormatError("Academic records CSV must contain at least one score column.")

        for row in reader:
            if not row.get(student_key, "").strip():
                raise InvalidFileFormatError(f"Missing student_id in row: {row}")

            record = {
                "student_id": row.get(student_key, "").strip(),
                "name": row.get(name_key, "").strip() if name_key else "",
            }

            for key in score_keys:
                raw_score = row.get(key, "").strip()
                if raw_score == "":
                    raise InvalidFileFormatError(
                        f"Missing score value for '{key}' in row: {row}")
                try:
                    record[key.strip()] = str(float(raw_score))
                except ValueError as e:
                    raise InvalidFileFormatError(
                        f"Invalid score for '{key}' in row {row}: {e}")

            records.append(record)

    return records


def parse_uploaded_students_csv(filepath: str) -> list[dict]:
    """Read uploaded student CSV. Expected: student_id, name, age, email, contact"""
    required = ["student_id", "name", "age"]
    validate_csv_columns(filepath, required)

    students = []
    with open(filepath, "r", newline="") as f:
        reader = csv.DictReader(f)
        headers = [h for h in (reader.fieldnames or []) if h]
        normalized = normalize_headers(headers)
        student_key = normalized["student_id"]
        name_key = normalized["name"]
        age_key = normalized["age"]
        email_key = normalized.get("email")
        contact_key = normalized.get("contact")

        for row in reader:
            students.append({
                "student_id": row.get(student_key, "").strip(),
                "name": row.get(name_key, "").strip(),
                "age": row.get(age_key, "0").strip(),
                "email": row.get(email_key, "").strip() if email_key else "",
                "contact": row.get(contact_key, "").strip() if contact_key else "",
            })
    return students


def parse_uploaded_courses_csv(filepath: str) -> list[dict]:
    """Read uploaded course CSV. Expected: course_id, course_name, credits, instructor"""
    required = ["course_id", "course_name", "credits", "instructor"]
    validate_csv_columns(filepath, required)

    courses = []
    with open(filepath, "r", newline="") as f:
        reader = csv.DictReader(f)
        headers = [h for h in (reader.fieldnames or []) if h]
        normalized = normalize_headers(headers)
        course_id_key = normalized["course_id"]
        course_name_key = normalized["course_name"]
        credits_key = normalized["credits"]
        instructor_key = normalized["instructor"]

        for row in reader:
            credits_value = row.get(credits_key, "").strip()
            try:
                credits = int(float(credits_value))
            except ValueError as e:
                raise InvalidFileFormatError(
                    f"Invalid credits value for '{credits_key}' in row {row}: {e}")

            courses.append({
                "course_id": row.get(course_id_key, "").strip(),
                "course_name": row.get(course_name_key, "").strip(),
                "credits": str(credits),
                "instructor": row.get(instructor_key, "").strip(),
            })
    return courses


def parse_uploaded_fees_csv(filepath: str) -> list[dict]:
    """Read uploaded fee CSV. Expected: student_id, tuition_fee and optional name/hostel_fee/transportation_fee/total_fee"""
    required = ["student_id", "tuition_fee"]
    validate_csv_columns(filepath, required)

    fees = []
    with open(filepath, "r", newline="") as f:
        reader = csv.DictReader(f)
        headers = [h for h in (reader.fieldnames or []) if h]
        normalized = normalize_headers(headers)
        student_key = normalized["student_id"]
        name_key = normalized.get("name")
        tuition_key = normalized["tuition_fee"]
        hostel_key = normalized.get("hostel_fee")
        transportation_key = normalized.get("transportation_fee")
        total_key = normalized.get("total_fee")

        for row in reader:
            if not row.get(student_key, "").strip():
                raise InvalidFileFormatError(f"Missing student_id in row: {row}")

            def parse_fee(key: str | None) -> float:
                if key is None:
                    return 0.0
                raw = row.get(key, "").strip()
                return float(raw) if raw else 0.0

            try:
                tuition = parse_fee(tuition_key)
                hostel = parse_fee(hostel_key)
                transportation = parse_fee(transportation_key)
                total = parse_fee(total_key)
            except ValueError as e:
                raise InvalidFileFormatError(f"Invalid fee value in row {row}: {e}")

            if total == 0.0:
                total = tuition + hostel + transportation

            fees.append({
                "student_id": row.get(student_key, "").strip(),
                "name": row.get(name_key, "").strip() if name_key else "",
                "tuition_fee": str(tuition),
                "hostel_fee": str(hostel),
                "transportation_fee": str(transportation),
                "total_fee": str(total),
            })
    return fees
