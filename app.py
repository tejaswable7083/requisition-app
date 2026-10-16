"""Web-Based Student Academic Requisition Form with PDF Generation (Streamlit)."""
import os
import re
from datetime import date

import streamlit as st

import database as db
from pdf_generator import APP_TYPES, DECLARATION, build_pdf
from validators import validate

st.set_page_config(page_title="Student Academic Requisition Form", page_icon="📄", layout="centered")
db.init_db()

try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except Exception:
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
STATUSES = ["Submitted", "Under Review", "Approved", "Not Approved", "Clarification Required"]

st.title("📄 Student Academic Requisition Form")
st.caption("Fill the form, accept the declaration, generate the PDF and download it.")

tab_form, tab_track, tab_admin = st.tabs(["📝 New Requisition", "🔎 Track Status", "🛠 Admin"])

# ------------------------------------------------------------------ Student form
with tab_form:
    st.subheader("1. Student Details")
    department = st.text_input("Name of Department *", placeholder="e.g. Computer Engineering")
    name = st.text_input("Student Name *")
    c1, c2, c3 = st.columns(3)
    roll_no = c1.text_input("Roll Number *")
    semester = c2.selectbox("Semester *", [str(i) for i in range(1, 9)])
    division = c3.text_input("Division *", max_chars=3)
    contact = st.text_input("Email / Mobile Number *", placeholder="name@example.com or 9876543210")
    app_type = st.radio("Application for *", APP_TYPES, horizontal=True)

    st.subheader("2. Purpose / Brief Details of Request")
    purpose = st.text_area("Purpose *", height=120, max_chars=400)

    st.subheader("3. Supporting Documents")
    docs_attached = st.radio("Documents attached?", ["Yes", "No"], horizontal=True, index=1) == "Yes"
    uploads = st.file_uploader("Upload supporting documents (optional)", accept_multiple_files=True,
                               type=["pdf", "png", "jpg", "jpeg"]) if docs_attached else []
    default_names = ", ".join(u.name for u in uploads) if uploads else ""
    doc_names = st.text_input("Document name(s)", value=default_names,
                              key=f"docnames_{default_names}") if docs_attached else ""

    st.subheader("4. Student Declaration")
    st.info(DECLARATION)
    sig_file = st.file_uploader("Student signature (optional, PNG/JPG)", type=["png", "jpg", "jpeg"])
    form_date = st.date_input("Date", value=date.today())
    declaration_ok = st.checkbox("I confirm the above declaration *")

    st.caption("Sections 5 (HoD) and 6 (Principal Office) are left blank in the PDF for the institute.")

    if st.button("Generate PDF", type="primary"):
        data = dict(department=department.strip(), name=name.strip(), roll_no=roll_no.strip(),
                    semester=semester, division=division.strip().upper(), contact=contact.strip(),
                    app_type=app_type, purpose=purpose.strip(), docs_attached=docs_attached,
                    doc_names=doc_names.strip(), date=form_date.strftime("%d/%m/%Y"))
        errors = validate(data, declaration_ok)
        if errors:
            st.session_state.pop("pdf", None)
            for e in errors:
                st.error(e)
        else:
            req_no = db.save(data)
            data["outward_no"] = req_no
            data["signature_bytes"] = sig_file.getvalue() if sig_file else None
            safe = lambda s: re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
            st.session_state["pdf"] = dict(
                bytes=build_pdf(data), req_no=req_no,
                filename=f"Requisition_{safe(data['roll_no'])}_{safe(data['name'])}.pdf")

    if "pdf" in st.session_state:
        p = st.session_state["pdf"]
        st.success(f"Requisition submitted! Your Requisition No. is **{p['req_no']}** (use it to track status).")
        st.download_button("⬇ Download PDF", data=p["bytes"], file_name=p["filename"],
                           mime="application/pdf")

# ------------------------------------------------------------------ Status tracking
with tab_track:
    q = st.text_input("Enter Requisition No. (e.g. REQ-2026-0001)")
    if q:
        r = db.get_by_req(q)
        if r:
            st.write(f"**{r['name']}** ({r['roll_no']}) – {r['app_type']}")
            st.metric("Status", r["status"])
        else:
            st.warning("No requisition found with that number.")

# ------------------------------------------------------------------ Admin dashboard
with tab_admin:
    pwd = st.text_input("Admin password", type="password")
    if pwd and pwd == ADMIN_PASSWORD:
        col_a, col_b = st.columns([3, 1])
        query = col_a.text_input("Search (name / roll no / req no / type)")
        flt = col_b.selectbox("Status", ["All"] + STATUSES)
        rows = db.search(query, flt)
        st.write(f"{len(rows)} record(s)")
        st.dataframe(rows, use_container_width=True)
        if rows:
            st.markdown("**Update status**")
            u1, u2 = st.columns(2)
            sel = u1.selectbox("Requisition", [r["req_no"] for r in rows])
            new_status = u2.selectbox("New status", STATUSES)
            if st.button("Update"):
                db.update_status(sel, new_status)
                st.success("Status updated. Refresh the list to see it.")
    elif pwd:
        st.error("Wrong password.")
