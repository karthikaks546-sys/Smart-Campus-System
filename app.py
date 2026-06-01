"""
app.py — Smart Campus Information System
Streamlit dashboard integrating Labs 1–8 (Q9 final project)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import tempfile
import json
import csv
from pathlib import Path

# ── Module imports ─────────────────────────────────────────────────────────────
from modules import data_store as ds
from modules.student_registration import (
    Student, evaluate_grade, InvalidScoreError, DuplicateStudentError
)
from modules.course_enrollment import (
    Course, validate_enrollment,
    MaxCourseLimitError, DuplicateEnrollmentError, InvalidCreditError
)
from modules.fee_calculation import FeeRecord, calculate_fee, NegativeFeeError
from modules.file_manager import (
    scan_directory, parse_uploaded_records_csv, parse_uploaded_students_csv,
    parse_uploaded_courses_csv, parse_uploaded_fees_csv,
    MissingFileOrFolderError, InvalidFileFormatError
)
from modules.auth import hash_password, verify_password
from modules.analytics import (
    records_to_dataframe, compute_statistics, get_top_performers,
    compute_average_per_student, grade_distribution,
    chart_avg_per_subject, chart_student_comparison,
    chart_grade_distribution, chart_avg_per_student,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Campus Information System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .metric-card .value { font-size: 2rem; font-weight: 700; }
    .metric-card .label { font-size: 0.85rem; opacity: 0.9; margin-top: 4px; }
    .card-green  { background: linear-gradient(135deg, #11998e, #38ef7d); }
    .card-orange { background: linear-gradient(135deg, #f7971e, #ffd200); }
    .card-red    { background: linear-gradient(135deg, #cb2d3e, #ef473a); }
    .card-blue   { background: linear-gradient(135deg, #2193b0, #6dd5ed); }
    .section-header {
        font-size: 1.4rem; font-weight: 700;
        color: #1a1a2e; margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        padding-left: 10px;
    }
    .stAlert { border-radius: 8px; }
    div[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar Navigation ────────────────────────────────────────────────────────
PAGES = {
    "🏠 Dashboard":            "dashboard",
    "📋 Student Registration": "registration",
    "📚 Course Management":    "courses",
    "🗂️  Student Records":     "records",
    "💰 Fee Management":       "fees",
    "📁 File Manager":         "files",
    "📊 Analytics":            "analytics",
}
AUTH_PAGE = {"🔐 Login / Register": "auth"}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

with st.sidebar:
    st.markdown("## 🎓 Smart Campus")
    st.markdown("---")
    pages = PAGES if st.session_state.authenticated else AUTH_PAGE
    page = st.radio("Navigate", list(pages.keys()), label_visibility="collapsed")

    st.markdown("---")
    if st.session_state.authenticated:
        st.markdown(f"**Logged in as:** {st.session_state.user['student_id']}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

    st.caption("Dayananda Sagar College of Engineering")
    st.caption("Python Lab — Final Project")

current = pages[page]


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════════
if current == "auth":
    st.markdown('<div class="section-header">🔐 Admin Login / Register</div>', unsafe_allow_html=True)
    login_tab, register_tab, reset_tab = st.tabs(["🔐 Admin Login", "➕ Admin Register", "❔ Forgot Password"])

    with login_tab:
        with st.form("login_form"):
            sid = st.text_input("Admin ID", value="")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login", use_container_width=True)

        if login_btn:
            if ds.authenticate_user(sid.strip(), password, verify_password):
                st.success("✅ Login successful.")
                st.session_state.authenticated = True
                st.session_state.user = ds.get_user(sid.strip())
                st.rerun()
            else:
                st.error("Invalid Admin ID or password.")

    with register_tab:
        with st.form("register_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sid      = st.text_input("Admin ID *", placeholder="e.g. ADM001")
                name     = st.text_input("Full Name *", placeholder="e.g. Priya Sharma")
                age      = st.number_input("Age *", min_value=1, max_value=120, value=20)
                email    = st.text_input("Email *", placeholder="admin@example.com")
            with col2:
                contact  = st.text_input("Contact Number", placeholder="9876543210")
                password = st.text_input("Password *", type="password")
                confirm  = st.text_input("Confirm Password *", type="password")
            register_btn = st.form_submit_button("Register", use_container_width=True)

        if register_btn:
            sid_val = sid.strip()
            if not sid_val or not name.strip() or not email.strip() or not password:
                st.error("All required fields must be filled.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif ds.user_exists(sid_val):
                st.error("A login account with this Admin ID already exists.")
            else:
                password_hash = hash_password(password)
                user_data = {
                    "student_id": sid_val,
                    "name": name.strip(),
                    "age": str(age),
                    "email": email.strip(),
                    "contact": contact.strip(),
                    "password_hash": password_hash,
                }
                ds.add_user(user_data)
                st.success("✅ Registration successful. You can now login.")

    with reset_tab:
        with st.form("reset_form"):
            sid = st.text_input("Admin ID", value="")
            email = st.text_input("Registered Email", value="")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            reset_btn = st.form_submit_button("Reset Password", use_container_width=True)

        if reset_btn:
            user = ds.get_user(sid.strip())
            if not user or user.get("email", "").strip().lower() != email.strip().lower():
                st.error("Admin ID and email do not match our records.")
            elif not new_password:
                st.error("Enter a new password.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                user["password_hash"] = hash_password(new_password)
                ds.update_user(sid.strip(), user)
                st.success("✅ Password reset successfully. Please login with your new password.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if current == "dashboard":
    st.markdown('<div class="section-header">📊 Smart Campus Dashboard</div>',
                unsafe_allow_html=True)

    students    = ds.get_students()
    courses     = ds.get_courses()
    records     = ds.get_records()
    fees        = ds.get_fees()
    enrollments = ds.get_enrollments()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card card-blue">
            <div class="value">{len(students)}</div>
            <div class="label">👩‍🎓 Students</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card card-green">
            <div class="value">{len(courses)}</div>
            <div class="label">📚 Courses</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card card-orange">
            <div class="value">{len(enrollments)}</div>
            <div class="label">📋 Enrollments</div></div>""", unsafe_allow_html=True)
    with c4:
        total_rev = sum(float(f.get("total_fee", 0)) for f in fees)
        st.markdown(f"""<div class="metric-card card-red">
            <div class="value">₹{total_rev:,.0f}</div>
            <div class="label">💰 Total Fees</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### 👩‍🎓 Recent Students")
        if students:
            df_s = pd.DataFrame(students[-5:][::-1])
            st.dataframe(df_s[["student_id", "name", "age", "email"]],
                         use_container_width=True, hide_index=True)
        else:
            st.info("No students registered yet.")

    with col_r:
        st.markdown("#### 📚 Recent Courses")
        if courses:
            df_c = pd.DataFrame(courses[-5:][::-1])
            st.dataframe(df_c[["course_id", "course_name", "credits", "instructor"]],
                         use_container_width=True, hide_index=True)
        else:
            st.info("No courses added yet.")

    if records:
        st.markdown("---")
        st.markdown("#### 📈 Quick Performance Snapshot")
        df_r = records_to_dataframe(records)
        df_r = compute_average_per_student(df_r)
        img = chart_avg_per_student(df_r)
        if img:
            st.image(img, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: STUDENT REGISTRATION (Lab 1)
# ═══════════════════════════════════════════════════════════════════════════════
elif current == "registration":
    st.markdown('<div class="section-header">📋 Student Registration & Grade Evaluation</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["➕ Register Student", "📊 Grade Evaluator", "🗃️ All Students"])

    # ── Register ──────────────────────────────────────────────────────────────
    with tab1:
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sid   = st.text_input("Student ID *", placeholder="e.g. STU001")
                name  = st.text_input("Full Name *", placeholder="e.g. Priya Sharma")
                age   = st.number_input("Age *", min_value=1, max_value=120, value=20)
            with col2:
                email   = st.text_input("Email", placeholder="student@example.com")
                contact = st.text_input("Contact Number", placeholder="9876543210")

            submitted = st.form_submit_button("✅ Register Student", use_container_width=True)

        if submitted:
            try:
                student = Student(sid.strip(), name.strip(), int(age),
                                  email.strip(), contact.strip())
                student.validate()
                if ds.student_exists(student.student_id):
                    st.error(f"Student ID '{sid}' already exists.")
                else:
                    ds.add_student(student.to_dict())
                    st.success(f"✅ Student **{name}** registered successfully!")
            except ValueError as e:
                st.error(f"Validation Error: {e}")

    # ── Grade Evaluator (Lab 1) ───────────────────────────────────────────────
    with tab2:
        students = ds.get_students()
        if not students:
            st.warning("No students registered. Register students first.")
        else:
            st.markdown("#### 🧠 Grade Evaluator")
            with st.form("grade_eval_form"):
                student_opts = {f"{s['student_id']} — {s['name']}": s for s in students}
                sel = st.selectbox("Select Student", list(student_opts.keys()))
                score_input = st.text_input("Enter Score (0-100)", value="75")
                evaluate_btn = st.form_submit_button("📈 Evaluate Grade", use_container_width=True)

            if evaluate_btn:
                try:
                    try:
                        score = float(score_input)
                    except ValueError:
                        raise InvalidScoreError("Score must be a number between 0 and 100.")

                    grade, remark = evaluate_grade(score)
                    student = student_opts[sel]
                    st.success(f"✅ {student['name']} gets grade **{grade}**")
                    st.info(f"Remark: {remark}")
                except InvalidScoreError as e:
                    st.error(str(e))

            st.markdown("---")
            st.markdown("#### 👩‍🎓 Selected Student")
            st.write(student_opts[sel])

    # ── View all students ─────────────────────────────────────────────────────
    with tab3:
        students = ds.get_students()
        if students:
            df = pd.DataFrame(students)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("#### ✏️ Edit / Delete Student")
            sid_list = [s["student_id"] for s in students]
            sel = st.selectbox("Select Student ID", sid_list, key="edit_sel")
            sel_data = next(s for s in students if s["student_id"] == sel)

            with st.expander("✏️ Edit Student", expanded=False):
                with st.form("edit_form"):
                    e_name    = st.text_input("Name", sel_data["name"])
                    e_age     = st.number_input("Age", value=int(sel_data.get("age", 20)),
                                                min_value=1, max_value=120)
                    e_email   = st.text_input("Email", sel_data.get("email", ""))
                    e_contact = st.text_input("Contact", sel_data.get("contact", ""))
                    if st.form_submit_button("💾 Save Changes"):
                        updated = {"student_id": sel, "name": e_name,
                                   "age": str(e_age), "email": e_email,
                                   "contact": e_contact}
                        ds.update_student(sel, updated)
                        st.success("Student updated.")
                        st.rerun()

            if st.button("🗑️ Delete Selected Student", type="secondary"):
                ds.delete_student(sel)
                st.warning(f"Student {sel} deleted.")
                st.rerun()
            # ── Student's Enrolled Courses (allow removing individual enrollments)
            st.markdown("#### 🧾 Enrolled Courses")
            student_enrolls = ds.get_student_enrollments(sel)
            if student_enrolls:
                for e in student_enrolls:
                    course_label = f"{e.get('course_name', '')} ({e.get('course_id', '')})"
                    cols_e = st.columns([8, 2])
                    cols_e[0].write(course_label)
                    if cols_e[1].button("❌ Remove", key=f"remove_{sel}_{e.get('course_id','')}"):
                        ds.remove_enrollment(sel, e.get('course_id', ''))
                        st.success(f"✅ Removed **{course_label}** for **{sel}**.")
                        st.rerun()
            else:
                st.info("This student is not enrolled in any courses.")
        else:
            st.info("No students registered yet. Use the Register tab.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: COURSE MANAGEMENT (Lab 2)
# ═══════════════════════════════════════════════════════════════════════════════
elif current == "courses":
    st.markdown('<div class="section-header">📚 Course Enrollment Management</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["➕ Add Course", "📋 Enroll / Unenroll", "🗃️ All Courses"])

    with tab1:
        with st.form("course_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                cid        = st.text_input("Course ID *", placeholder="e.g. CS101")
                cname      = st.text_input("Course Name *", placeholder="e.g. Data Structures")
            with col2:
                credits    = st.number_input("Credits *", min_value=1, max_value=10, value=3)
                instructor = st.text_input("Instructor", placeholder="e.g. Dr. Sharma")
            submitted = st.form_submit_button("✅ Add Course", use_container_width=True)

        if submitted:
            try:
                course = Course(cid.strip(), cname.strip(), int(credits), instructor.strip())
                course.validate()
                existing = ds.get_courses()
                if any(c["course_id"] == cid.strip() for c in existing):
                    st.error(f"Course ID '{cid}' already exists.")
                else:
                    ds.add_course(course.to_dict())
                    st.success(f"✅ Course **{cname}** added!")
            except (ValueError, InvalidCreditError) as e:
                st.error(str(e))

    with tab2:
        students = ds.get_students()
        courses  = ds.get_courses()
        if not students:
            st.warning("No students registered. Register students first.")
        elif not courses:
            st.warning("No courses added. Add courses first.")
        else:
            enroll_tab, unenroll_tab = st.tabs(["➕ Enroll", "❌ Unenroll"])

            with enroll_tab:
                with st.form("course_enroll_form"):
                    s_opts = {f"{s['student_id']} — {s['name']}": s["student_id"]
                              for s in students}
                    c_opts = {f"{c['course_id']} — {c['course_name']} ({c['credits']} cr)": c["course_id"]
                              for c in courses}

                    sel_s = st.selectbox("Select Student", list(s_opts.keys()))
                    sel_c = st.selectbox("Select Course",  list(c_opts.keys()))
                    enroll_btn = st.form_submit_button("📋 Enroll", use_container_width=True)

                if enroll_btn:
                    sid = s_opts[sel_s]
                    cid = c_opts[sel_c]
                    course_obj = next(c for c in courses if c["course_id"] == cid)
                    all_enrolls = ds.get_enrollments()
                    try:
                        validate_enrollment(sid, cid, all_enrolls, all_enrolls)
                        row = {"student_id": sid, "course_id": cid,
                               "course_name": course_obj["course_name"],
                               "credits": course_obj["credits"]}
                        ds.add_enrollment(row)
                        st.success(f"✅ Enrolled in **{course_obj['course_name']}**!")
                    except (MaxCourseLimitError, DuplicateEnrollmentError) as e:
                        st.error(str(e))

            with unenroll_tab:
                all_enrollments = ds.get_enrollments()
                if not all_enrollments:
                    st.info("No enrollments found.")
                else:
                    student_opts = {f"{s['student_id']} — {s['name']}": s["student_id"]
                                    for s in students}
                    sel_student = st.selectbox("Select Student", list(student_opts.keys()),
                                               key="course_unenroll_student")
                    sid_u = student_opts[sel_student]
                    student_enrollments = ds.get_student_enrollments(sid_u)
                    if not student_enrollments:
                        st.info("This student has no enrollments.")
                    else:
                        course_opts = {
                            f"{e['course_name']} ({e['course_id']})": e["course_id"]
                            for e in student_enrollments
                        }
                        sel_course = st.selectbox("Select Course to Remove",
                                                  list(course_opts.keys()),
                                                  key="course_unenroll_course")
                        cid_u = course_opts[sel_course]
                        if st.button("❌ Remove Enrollment", type="secondary",
                                     use_container_width=True):
                            ds.remove_enrollment(sid_u, cid_u)
                            st.success(f"✅ Removed **{sel_course}** for **{sel_student}**.")
                            st.rerun()

            st.markdown("---")
            st.markdown("#### 📋 Current Enrollments")
            enrollments = ds.get_enrollments()
            if enrollments:
                st.dataframe(pd.DataFrame(enrollments), use_container_width=True, hide_index=True)
            else:
                st.info("No enrollments yet.")

    with tab3:
        courses = ds.get_courses()
        if courses:
            df_c = pd.DataFrame(courses)
            st.dataframe(df_c, use_container_width=True, hide_index=True)

            st.markdown("---")
            cid_list = [c["course_id"] for c in courses]
            del_cid  = st.selectbox("Select Course to Delete", cid_list)
            if st.button("🗑️ Delete Course", type="secondary"):
                ds.delete_course(del_cid)
                st.warning(f"Course {del_cid} deleted.")
                st.rerun()
        else:
            st.info("No courses added yet.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: STUDENT RECORDS (Lab 3)
# ═══════════════════════════════════════════════════════════════════════════════
elif current == "records":
    st.markdown('<div class="section-header">🗂️ Student Academic Records</div>',
                unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["➕ Add / Edit Record", "🗃️ All Records"])

    with tab1:
        students = ds.get_students()
        if not students:
            st.warning("No students registered yet.")
        else:
            s_opts = {f"{s['student_id']} — {s['name']}": s for s in students}
            sel = st.selectbox("Select Student", list(s_opts.keys()))
            sel_s = s_opts[sel]

            # Fetch this student's enrolled courses dynamically
            enrolled = ds.get_student_enrollments(sel_s["student_id"])

            if not enrolled:
                st.warning(
                    f"⚠️ **{sel_s['name']}** is not enrolled in any courses yet. "
                    f"Please go to **Course Management → Enroll Student** first."
                )
            else:
                # Pre-fill existing scores if a record already exists
                existing_records = ds.get_records()
                existing = next(
                    (r for r in existing_records if r["student_id"] == sel_s["student_id"]),
                    {}
                )

                st.markdown(f"**Enrolled courses for {sel_s['name']}:**")
                with st.form("record_form"):
                    score_inputs = {}
                    cols = st.columns(min(len(enrolled), 3))
                    for i, course in enumerate(enrolled):
                        cname = course["course_name"]
                        current_val = float(existing.get(cname, 0.0))
                        with cols[i % 3]:
                            score_inputs[cname] = st.number_input(
                                f"📘 {cname}",
                                min_value=0.0,
                                max_value=100.0,
                                value=current_val,
                                step=0.5,
                                key=f"score_{course['course_id']}",
                            )
                    save_btn = st.form_submit_button("💾 Save Record", use_container_width=True)

                if save_btn:
                    record = {
                        "student_id": sel_s["student_id"],
                        "name": sel_s["name"],
                    }
                    for cname, score in score_inputs.items():
                        record[cname] = str(score)
                    ds.add_record(record)
                    st.success(f"✅ Record saved for **{sel_s['name']}**.")

    with tab2:
        records = ds.get_records()
        if records:
            df = pd.DataFrame(records)
            # Dynamically find score columns (everything except student_id and name)
            score_cols = [c for c in df.columns if c not in ("student_id", "name")]
            for col in score_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            if score_cols:
                df["average"] = df[score_cols].mean(axis=1).round(2)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("---")
            del_id = st.selectbox("Select Student ID to Delete Record",
                                   [r["student_id"] for r in records])
            if st.button("🗑️ Delete Record", type="secondary"):
                ds.delete_record(del_id)
                st.warning(f"Record for {del_id} deleted.")
                st.rerun()
        else:
            st.info("No records found.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: FEE MANAGEMENT (Lab 5)
# ═══════════════════════════════════════════════════════════════════════════════
elif current == "fees":
    st.markdown('<div class="section-header">💰 Student Fee Management</div>',
                unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🧮 Calculate & Save Fee", "📋 Fee Records"])

    with tab1:
        students = ds.get_students()
        if not students:
            st.warning("Register students first.")
        else:
            s_opts = {f"{s['student_id']} — {s['name']}": s for s in students}
            sel    = st.selectbox("Select Student", list(s_opts.keys()))
            sel_s  = s_opts[sel]

            with st.form("fee_form"):
                st.markdown("**Enter Fee Components (₹)**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    tuition = st.number_input("Tuition Fee *", min_value=0.0,
                                              value=50000.0, step=500.0)
                with col2:
                    hostel  = st.number_input("Hostel Fee (optional)", min_value=0.0,
                                              value=0.0, step=500.0)
                with col3:
                    transport = st.number_input("Transport Fee (optional)", min_value=0.0,
                                                value=0.0, step=500.0)
                calc_btn = st.form_submit_button("💰 Calculate & Save", use_container_width=True)

            if calc_btn:
                try:
                    total = calculate_fee(tuition, hostel, transport)
                    fee_rec = FeeRecord(sel_s["student_id"], sel_s["name"],
                                        tuition, hostel, transport)
                    ds.save_fee(fee_rec.to_dict())

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Tuition",     f"₹{tuition:,.0f}")
                    c2.metric("Hostel",      f"₹{hostel:,.0f}")
                    c3.metric("Transport",   f"₹{transport:,.0f}")
                    c4.metric("💰 Total Fee", f"₹{total:,.0f}")
                    st.success(f"✅ Fee record saved for **{sel_s['name']}**.")
                except NegativeFeeError as e:
                    st.error(str(e))

    with tab2:
        fees = ds.get_fees()
        if fees:
            df = pd.DataFrame(fees)
            for col in ["tuition_fee", "hostel_fee", "transportation_fee", "total_fee"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            st.dataframe(df, use_container_width=True, hide_index=True)
            total_collected = df["total_fee"].sum()
            st.metric("💰 Total Fees Collected", f"₹{total_collected:,.0f}")
        else:
            st.info("No fee records yet.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: FILE MANAGER (Lab 6 + Lab 7)
# ═══════════════════════════════════════════════════════════════════════════════
elif current == "files":
    st.markdown('<div class="section-header">📁 File Manager & Directory Scanner</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📥 Import CSV", "📤 Export Data", "📂 Directory Scanner"])

    # ── Import ─────────────────────────────────────────────────────────────────
    with tab1:
        import_type = st.radio("Import type",
                                ["Student Records (scores)", "Students (registration)", "Courses", "Fees"],
                                horizontal=True)
        uploaded = st.file_uploader("Upload CSV", type=["csv"])

        if uploaded:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name
            try:
                with open(tmp_path, "r", newline="") as f:
                    detected_headers = [h.strip() for h in (csv.DictReader(f).fieldnames or []) if h]

                normalized_headers = {h.lower().replace(" ", "_") for h in detected_headers}
                course_headers = {"course_id", "course_name", "credits", "instructor"}
                fee_headers = {"student_id", "tuition_fee"}
                student_headers = {"student_id", "name", "age"}

                if course_headers.issubset(normalized_headers):
                    active_import = "Courses"
                elif fee_headers.issubset(normalized_headers):
                    active_import = "Fees"
                elif student_headers.issubset(normalized_headers):
                    active_import = "Students"
                elif "student_id" in normalized_headers and len(normalized_headers) > 1:
                    active_import = "Student Records"
                else:
                    active_import = import_type

                if active_import != import_type:
                    st.info(f"Detected {active_import} CSV format. Importing as {active_import}.")

                if active_import == "Student Records":
                    rows = parse_uploaded_records_csv(tmp_path)
                    imported = 0
                    for row in rows:
                        if ds.student_exists(row["student_id"]):
                            student = ds.get_student(row["student_id"])
                            row["name"] = student["name"]
                        else:
                            row["name"] = row.get("name", "").strip() or "Unknown"
                        ds.add_record(row)
                        imported += 1
                    st.success(f"✅ Imported {imported} academic records.")
                elif active_import == "Students":
                    rows = parse_uploaded_students_csv(tmp_path)
                    added = 0
                    for row in rows:
                        if not ds.student_exists(row["student_id"]):
                            ds.add_student(row)
                            added += 1
                    st.success(f"✅ Imported {added} new students "
                               f"({len(rows)-added} duplicates skipped).")
                elif active_import == "Courses":
                    rows = parse_uploaded_courses_csv(tmp_path)
                    added = 0
                    for row in rows:
                        if not ds.course_exists(row["course_id"]):
                            ds.add_course(row)
                            added += 1
                    st.success(f"✅ Imported {added} new courses "
                               f"({len(rows)-added} duplicates skipped).")
                elif active_import == "Fees":
                    rows = parse_uploaded_fees_csv(tmp_path)
                    added = 0
                    for row in rows:
                        if ds.student_exists(row["student_id"]):
                            student = ds.get_student(row["student_id"])
                            row["name"] = row.get("name", "").strip() or student.get("name", "")
                        ds.save_fee(row)
                        added += 1
                    st.success(f"✅ Imported {added} fee records.")
                else:
                    raise InvalidFileFormatError(
                        "Unable to detect import type. Please upload a supported CSV format.")

                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            except (MissingFileOrFolderError, InvalidFileFormatError) as e:
                st.error(f"Import Error: {e}")
            finally:
                os.unlink(tmp_path)

        st.markdown("---")
        st.markdown("##### 📋 Expected CSV Format")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Academic Records:")
            st.code("student_id,Maths,Chemistry,English\nSTU001,85,90,78")
            st.caption("Name is optional when the student is already registered.")
            st.caption("Courses:")
            st.code("course_id,course_name,credits,instructor\nC101,Maths,4,Dr. Rao")
        with col2:
            st.caption("Students:")
            st.code("student_id,name,age,email,contact\nSTU001,Priya,20,p@x.com,9876")
            st.caption("Fees:")
            st.code("student_id,name,tuition_fee,hostel_fee,transportation_fee,total_fee\nSTU001,Priya,50000,0,0,50000")

    # ── Export ─────────────────────────────────────────────────────────────────
    with tab2:
        export_src = st.selectbox("Choose data to export",
                                   ["Students", "Courses", "Academic Records", "Fees"])
        export_fmt = st.radio("Format", ["CSV", "JSON"], horizontal=True)

        data_map = {
            "Students":          ds.get_students,
            "Courses":           ds.get_courses,
            "Academic Records":  ds.get_records,
            "Fees":              ds.get_fees,
        }
        data = data_map[export_src]()

        if not data:
            st.info(f"No {export_src} data to export.")
        else:
            if export_fmt == "CSV":
                df = pd.DataFrame(data)
                csv_str = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    f"⬇️ Download {export_src}.csv",
                    data=csv_str,
                    file_name=f"{export_src.lower().replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            else:
                json_str = json.dumps(data, indent=2).encode("utf-8")
                st.download_button(
                    f"⬇️ Download {export_src}.json",
                    data=json_str,
                    file_name=f"{export_src.lower().replace(' ', '_')}.json",
                    mime="application/json",
                    use_container_width=True,
                )
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    # ── Directory Scanner ──────────────────────────────────────────────────────
    with tab3:
        st.markdown("**Enter a directory path on this machine to scan:**")
        dir_path = st.text_input("Directory Path",
                                  value=str(Path(__file__).parent),
                                  placeholder="/path/to/directory")
        if st.button("🔍 Scan Directory", use_container_width=True):
            output_lines = list(scan_directory(dir_path))
            full_output  = "\n".join(output_lines)
            st.code(full_output, language="")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS (Lab 8)
# ═══════════════════════════════════════════════════════════════════════════════
elif current == "analytics":
    st.markdown('<div class="section-header">📊 Performance Analytics</div>',
                unsafe_allow_html=True)

    records = ds.get_records()
    if not records:
        st.info("No academic records found. Add records in the Student Records module.")
    else:
        df = records_to_dataframe(records)
        stats = compute_statistics(df)
        tops  = get_top_performers(df)
        dist  = grade_distribution(df)

        # ── Summary metrics ──────────────────────────────────────────────────
        st.markdown("#### 📈 Subject Averages")
        if stats and "mean" in stats:
            n_cols = max(1, len(stats["mean"]))
            cols = st.columns(n_cols)
            for i, (subj, val) in enumerate(stats["mean"].items()):
                cols[i].metric(subj.capitalize(), f"{val:.1f}",
                               delta=f"σ = {stats['std_dev'][subj]:.1f}")

        # ── Top Performers ────────────────────────────────────────────────────
        st.markdown("#### 🏆 Top Performers")
        if tops:
            tc = st.columns(len(tops))
            for i, (subj, name) in enumerate(tops.items()):
                tc[i].success(f"**{subj.capitalize()}**: {name}")

        st.markdown("---")

        # ── Charts ────────────────────────────────────────────────────────────
        col1, col2 = st.columns(2)
        with col1:
            img = chart_avg_per_subject(stats)
            if img:
                st.image(img, use_container_width=True)

        with col2:
            img2 = chart_grade_distribution(dist)
            if img2:
                st.image(img2, use_container_width=True)

        img3 = chart_student_comparison(df)
        if img3:
            st.image(img3, use_container_width=True)

        img4 = chart_avg_per_student(df)
        if img4:
            st.image(img4, use_container_width=True)

        # ── Full Stats Table ──────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("#### 📋 Detailed Statistics (Pandas describe)")
        if stats and "summary" in stats:
            st.dataframe(stats["summary"], use_container_width=True)

        st.markdown("#### 🗃️ All Records with Average")
        df_display = compute_average_per_student(df)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # ── Event Participation (Lab 3 Set logic) ─────────────────────────────
        st.markdown("---")
        st.markdown("#### 🎪 Event Participation Analysis (Sets — Lab 3)")
        col1, col2 = st.columns(2)
        with col1:
            evt_a = st.text_area("Event A Participants (comma-separated)",
                                  value=", ".join(df["name"].tolist()[:3]))
        with col2:
            evt_b = st.text_area("Event B Participants (comma-separated)",
                                  value=", ".join(df["name"].tolist()[1:4]))

        if st.button("Analyze Participation"):
            set_a = {n.strip() for n in evt_a.split(",") if n.strip()}
            set_b = {n.strip() for n in evt_b.split(",") if n.strip()}
            c1, c2, c3 = st.columns(3)
            with c1:
                st.info(f"**Common (A ∩ B)**\n\n" + "\n".join(set_a & set_b) or "None")
            with c2:
                st.info(f"**All (A ∪ B)**\n\n" + "\n".join(set_a | set_b))
            with c3:
                st.info(f"**Only in A (A − B)**\n\n" + "\n".join(set_a - set_b) or "None")
