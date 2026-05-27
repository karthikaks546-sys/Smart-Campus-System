# 🎓 Smart Campus Information System
### Python Lab Final Project — Dayananda Sagar College of Engineering

A Streamlit-based web dashboard integrating all 8 lab experiments into one complete application.

---

## 📁 Project Structure

```
smart_campus/
├── app.py                        # Main Streamlit application (Lab 9 entry point)
├── requirements.txt              # Python dependencies
├── data/                         # Auto-created CSV storage
│   ├── students.csv
│   ├── courses.csv
│   ├── academic_records.csv
│   ├── enrollments.csv
│   └── fees.csv
└── modules/
    ├── __init__.py
    ├── data_store.py             # CSV/JSON read-write helpers
    ├── student_registration.py   # Lab 1 — Grade evaluation, Student OOP model
    ├── course_enrollment.py      # Lab 2 — Loop/continue/break enrollment logic
    ├── search_sort.py            # Lab 4 — Bubble sort, Selection sort, Linear/Binary search
    ├── fee_calculation.py        # Lab 5 — Fee functions with optional parameters
    ├── file_manager.py           # Lab 6+7 — File I/O, directory scanner, custom exceptions
    └── analytics.py              # Lab 8 — NumPy, Pandas, Matplotlib charts
```

---

## 🚀 How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the app
```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 📋 Lab-to-Module Mapping

| Lab | Topic | Module |
|-----|-------|--------|
| Lab 1 | Student Registration & Grade Evaluation | `student_registration.py` |
| Lab 2 | Course Enrollment (loops, continue, break) | `course_enrollment.py` |
| Lab 3 | Data Structures (lists, dicts, sets) | `data_store.py` + Analytics page |
| Lab 4 | Sorting & Searching | `search_sort.py` |
| Lab 5 | Fee Calculation (functions) | `fee_calculation.py` |
| Lab 6 | File Handling (read/write/report) | `file_manager.py` |
| Lab 7 | Directory Scanning + Exceptions | `file_manager.py` |
| Lab 8 | Performance Analytics (NumPy/Pandas/Matplotlib) | `analytics.py` |
| **Lab 9** | **Smart Campus System (Full Integration)** | **`app.py`** |

---

## 🖥️ Dashboard Pages

- **🏠 Dashboard** — Summary cards, recent entries, performance snapshot
- **📋 Student Registration** — Register students, grade evaluator (Lab 1), CRUD
- **📚 Course Management** — Add courses, enroll students (Lab 2), max 5 per student
- **🗂️ Student Records** — Add/edit/delete academic scores (Lab 3 data structures)
- **🔍 Search & Sort** — Bubble/Selection sort, Linear/Binary search (Lab 4)
- **💰 Fee Management** — Calculate fees with optional parameters (Lab 5)
- **📁 File Manager** — CSV import/export, directory scanner (Lab 6+7)
- **📊 Analytics** — Charts, statistics, grade distribution, set analysis (Lab 8)

---

## 💾 Data Storage

All data is stored as CSV files in the `data/` folder (auto-created on first run).
Export to JSON is available from the File Manager page.

## 🛡️ Exception Handling

Custom exceptions defined across modules:
- `InvalidScoreError`, `DuplicateStudentError`
- `MaxCourseLimitError`, `DuplicateEnrollmentError`, `InvalidCreditError`
- `NegativeFeeError`
- `MissingFileOrFolderError`, `InvalidFileFormatError`, `EmptyDirectoryError`
