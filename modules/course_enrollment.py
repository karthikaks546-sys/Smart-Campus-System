"""
modules/course_enrollment.py
Lab 2 — Course Enrollment Management
"""
from dataclasses import dataclass

MAX_COURSES_PER_STUDENT = 5


# ── Custom Exceptions ─────────────────────────────────────────────────────────
class MaxCourseLimitError(Exception):
    pass

class DuplicateEnrollmentError(Exception):
    pass

class InvalidCreditError(Exception):
    pass


# ── OOP Model ─────────────────────────────────────────────────────────────────
@dataclass
class Course:
    course_id: str
    course_name: str
    credits: int
    instructor: str

    def validate(self):
        if not self.course_id.strip():
            raise ValueError("Course ID cannot be empty.")
        if not self.course_name.strip():
            raise ValueError("Course name cannot be empty.")
        if self.credits <= 0:
            raise InvalidCreditError("Credits must be a positive integer.")

    def to_dict(self) -> dict:
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "credits": str(self.credits),
            "instructor": self.instructor,
        }

    @staticmethod
    def from_dict(d: dict) -> "Course":
        return Course(
            course_id=d["course_id"],
            course_name=d["course_name"],
            credits=int(d.get("credits", 0)),
            instructor=d.get("instructor", ""),
        )


# ── Enrollment Validation (Lab 2 loop/continue/break logic) ──────────────────
def validate_enrollment(student_id: str, course_id: str,
                         existing_enrollments: list[dict],
                         all_student_courses: list[dict]) -> None:
    """
    Raises an exception if enrollment is not allowed.
    Mirrors the Lab 2 loop logic: skip duplicates, stop at max limit.
    """
    enrolled_for_student = [e for e in all_student_courses
                            if e["student_id"] == student_id]

    # break equivalent — max limit check
    if len(enrolled_for_student) >= MAX_COURSES_PER_STUDENT:
        raise MaxCourseLimitError(
            f"Student already enrolled in {MAX_COURSES_PER_STUDENT} courses (maximum).")

    # continue equivalent — skip duplicate
    already = any(e["student_id"] == student_id and e["course_id"] == course_id
                  for e in existing_enrollments)
    if already:
        raise DuplicateEnrollmentError("Student is already enrolled in this course.")
