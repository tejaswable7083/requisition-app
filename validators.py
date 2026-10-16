import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
MOBILE_RE = re.compile(r"^(\+91[- ]?)?[6-9]\d{9}$")


def valid_contact(value: str) -> bool:
    """Accepts a valid email OR a 10-digit Indian mobile number (optional +91)."""
    v = value.strip()
    return bool(EMAIL_RE.match(v) or MOBILE_RE.match(v))


def validate(d: dict, declaration_ok: bool) -> list:
    errs = []
    for key, label in [("department", "Department"), ("name", "Student Name"), ("roll_no", "Roll Number"),
                       ("semester", "Semester"), ("division", "Division"),
                       ("contact", "Email / Mobile"), ("purpose", "Purpose / Details")]:
        if not str(d.get(key, "")).strip():
            errs.append(f"{label} is required.")
    c = str(d.get("contact", "")).strip()
    if c and not valid_contact(c):
        if "@" in c:
            errs.append("Enter a valid email address (e.g. name@example.com).")
        else:
            errs.append("Mobile number must be 10 digits (starting 6-9), digits only.")
    if d.get("docs_attached") and not str(d.get("doc_names", "")).strip():
        errs.append("Enter the supporting document name(s) since documents are attached.")
    if not declaration_ok:
        errs.append("You must accept the Student Declaration.")
    return errs
