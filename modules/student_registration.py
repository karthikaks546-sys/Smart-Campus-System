"""
modules/student_registration.py
Lab 1 — Student Registration + Grade Evaluation
"""
from dataclasses import dataclass, field
from typing import Optional
import re


# ── Custom Exceptions ─────────────────────────────────────────────────────────
class InvalidScoreError(Exception):
    pass

class DuplicateStudentError(Exception):
    pass

class StudentNotFoundError(Exception):
    pass


# ── Grade Logic (Lab 1) ───────────────────────────────────────────────────────
def evaluate_grade(score: float) -> tuple[str, str]:
    """Return (grade, remark) for a given score."""
    if not (0 <= score <= 100):
        raise InvalidScoreError("Score must be between 0 and 100.")
    if score >= 90:
        return "A", "Excellent"
    elif score >= 75:
        return "B", "Very Good"
    elif score >= 60:
        return "C", "Good"
    elif score >= 40:
        return "D", "Average"
    else:
        return "F", "Needs Improvement"


# ── Student OOP Model ─────────────────────────────────────────────────────────
@dataclass
class Student:
    student_id: str
    name: str
    age: int
    email: str
    contact: str

    def validate(self):
        if not self.student_id.strip():
            raise ValueError("Student ID cannot be empty.")
        if not self.name.strip():
            raise ValueError("Name cannot be empty.")
        if not (1 <= self.age <= 120):
            raise ValueError("Age must be between 1 and 120.")
        if self.email and not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Invalid email format.")

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": str(self.age),
            "email": self.email,
            "contact": self.contact,
        }

    @staticmethod
    def from_dict(d: dict) -> "Student":
        return Student(
            student_id=d["student_id"],
            name=d["name"],
            age=int(d.get("age", 0)),
            email=d.get("email", ""),
            contact=d.get("contact", ""),
        )
