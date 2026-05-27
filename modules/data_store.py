"""
modules/data_store.py
Handles all CSV/JSON read-write operations for the Smart Campus system.
"""
import csv
import json
import os
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
STUDENTS_FILE  = DATA_DIR / "students.csv"
COURSES_FILE   = DATA_DIR / "courses.csv"
RECORDS_FILE   = DATA_DIR / "academic_records.csv"
ENROLLMENTS_FILE = DATA_DIR / "enrollments.csv"
FEES_FILE      = DATA_DIR / "fees.csv"

STUDENT_FIELDS  = ["student_id", "name", "age", "email", "contact"]
COURSE_FIELDS   = ["course_id", "course_name", "credits", "instructor"]
RECORD_FIELDS = ["student_id", "name"]  
ENROLL_FIELDS   = ["student_id", "course_id", "course_name", "credits"]
FEE_FIELDS      = ["student_id", "name", "tuition_fee", "hostel_fee",
                   "transportation_fee", "total_fee"]


def _ensure_file(path: Path, fieldnames: list):
    """Create CSV with header if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()


# ── Generic helpers ───────────────────────────────────────────────────────────
def read_csv(path: Path, fieldnames: list) -> list[dict]:
    _ensure_file(path, fieldnames)
    with open(path, "r", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list):
    _ensure_file(path, fieldnames)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def append_csv(path: Path, row: dict, fieldnames: list):
    _ensure_file(path, fieldnames)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(row)


# ── Student CRUD ─────────────────────────────────────────────────────────────
def get_students() -> list[dict]:
    return read_csv(STUDENTS_FILE, STUDENT_FIELDS)


def add_student(student: dict):
    append_csv(STUDENTS_FILE, student, STUDENT_FIELDS)


def update_student(student_id: str, updated: dict):
    rows = get_students()
    rows = [updated if r["student_id"] == student_id else r for r in rows]
    write_csv(STUDENTS_FILE, rows, STUDENT_FIELDS)


def delete_student(student_id: str):
    rows = [r for r in get_students() if r["student_id"] != student_id]
    write_csv(STUDENTS_FILE, rows, STUDENT_FIELDS)


def student_exists(student_id: str) -> bool:
    return any(s["student_id"] == student_id for s in get_students())


# ── Course CRUD ───────────────────────────────────────────────────────────────
def get_courses() -> list[dict]:
    return read_csv(COURSES_FILE, COURSE_FIELDS)


def add_course(course: dict):
    append_csv(COURSES_FILE, course, COURSE_FIELDS)


def update_course(course_id: str, updated: dict):
    rows = get_courses()
    rows = [updated if r["course_id"] == course_id else r for r in rows]
    write_csv(COURSES_FILE, rows, COURSE_FIELDS)


def delete_course(course_id: str):
    rows = [r for r in get_courses() if r["course_id"] != course_id]
    write_csv(COURSES_FILE, rows, COURSE_FIELDS)


# ── Academic Records ──────────────────────────────────────────────────────────
def get_records() -> list[dict]:
    return read_csv(RECORDS_FILE, RECORD_FIELDS)


def add_record(record: dict):
    rows = get_records()
    rows = [record if r["student_id"] == record["student_id"] else r for r in rows]
    if not any(r["student_id"] == record["student_id"] for r in rows):
        rows.append(record)
    # Derive fieldnames dynamically from all rows combined
    all_keys = list(dict.fromkeys(
        k for row in rows for k in row.keys()
    ))
    write_csv(RECORDS_FILE, rows, all_keys)


def delete_record(student_id: str):
    rows = [r for r in get_records() if r["student_id"] != student_id]
    write_csv(RECORDS_FILE, rows, RECORD_FIELDS)


# ── Enrollments ───────────────────────────────────────────────────────────────
def get_enrollments() -> list[dict]:
    return read_csv(ENROLLMENTS_FILE, ENROLL_FIELDS)


def add_enrollment(row: dict):
    append_csv(ENROLLMENTS_FILE, row, ENROLL_FIELDS)


def get_student_enrollments(student_id: str) -> list[dict]:
    return [r for r in get_enrollments() if r["student_id"] == student_id]


def remove_enrollment(student_id: str, course_id: str):
    rows = [r for r in get_enrollments()
            if not (r["student_id"] == student_id and r["course_id"] == course_id)]
    write_csv(ENROLLMENTS_FILE, rows, ENROLL_FIELDS)


# ── Fees ─────────────────────────────────────────────────────────────────────
def get_fees() -> list[dict]:
    return read_csv(FEES_FILE, FEE_FIELDS)


def save_fee(record: dict):
    rows = get_fees()
    rows = [record if r["student_id"] == record["student_id"] else r for r in rows]
    if not any(r["student_id"] == record["student_id"] for r in rows):
        rows.append(record)
    write_csv(FEES_FILE, rows, FEE_FIELDS)


# ── Export helpers ────────────────────────────────────────────────────────────
def export_json(data: list[dict], filepath: str):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def import_json(filepath: str) -> list[dict]:
    with open(filepath, "r") as f:
        return json.load(f)
