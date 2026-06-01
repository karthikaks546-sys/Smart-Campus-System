"""
modules/fee_calculation.py
Lab 5 — Fee Calculation using Functions with default/optional parameters
"""
from dataclasses import dataclass


# ── Custom Exception ──────────────────────────────────────────────────────────
class NegativeFeeError(Exception):
    pass


# ── Core Fee Function (Lab 5 pattern) ─────────────────────────────────────────
def calculate_fee(tuition_fee: float,
                  hostel_fee: float = 0.0,
                  transportation_fee: float = 0.0) -> float:
    """
    Calculates total fee.  hostel_fee and transportation_fee are optional.
    Mirrors the Lab 5 function signature exactly.
    """
    for label, val in [("Tuition fee", tuition_fee),
                       ("Hostel fee", hostel_fee),
                       ("Transportation fee", transportation_fee)]:
        if val < 0:
            raise NegativeFeeError(f"{label} cannot be negative.")
    return tuition_fee + hostel_fee + transportation_fee


# ── OOP Wrapper ───────────────────────────────────────────────────────────────
@dataclass
class FeeRecord:
    student_id: str
    name: str
    tuition_fee: float
    hostel_fee: float = 0.0
    transportation_fee: float = 0.0

    @property
    def total_fee(self) -> float:
        return calculate_fee(self.tuition_fee, self.hostel_fee, self.transportation_fee)

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "tuition_fee": str(self.tuition_fee),
            "hostel_fee": str(self.hostel_fee),
            "transportation_fee": str(self.transportation_fee),
            "total_fee": str(self.total_fee),
        }

    @staticmethod
    def from_dict(d: dict) -> "FeeRecord":
        return FeeRecord(
            student_id=d["student_id"],
            name=d["name"],
            tuition_fee=float(d.get("tuition_fee", 0)),
            hostel_fee=float(d.get("hostel_fee", 0)),
            transportation_fee=float(d.get("transportation_fee", 0)),
        )
