# 🎓 Smart Campus Information System
### Python Lab Final Project — Dayananda Sagar College of Engineering

A Streamlit-based web dashboard integrating all 8 lab experiments into one complete application.

---

## 📁 Project Structure

```
smart_campus/
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── data/                         # Auto-created CSV storag
│   ├── students.csv
│   ├── courses.csv
│   ├── academic_records.csv
│   ├── enrollments.csv
│   └── fees.csv
└── modules/
    ├── __init__.py
    ├── data_store.py             # CSV/JSON read-write helpers
    ├── student_registration.py   # Grade evaluation, Student OOP model
    ├── course_enrollment.py      # Loop/continue/break enrollment logic
    ├── search_sort.py            # Bubble sort, Selection sort, Linear/Binary search
    ├── fee_calculation.py        # Fee functions with optional parameters
    ├── file_manager.py           # File I/O, directory scanner, custom exceptions
    └── analytics.py              # NumPy, Pandas, Matplotlib charts
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

Live web link: [https://smart-campus-system-for-dsce.streamlit.app/](url)


