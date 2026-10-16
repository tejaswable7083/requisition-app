"""Generates the Student Academic Requisition Form PDF (layout follows the institute .docx form)."""
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader, simpleSplit

W, H = A4
LM, RM = 40, W - 40          # left / right margin
LOGO = os.path.join(os.path.dirname(__file__), "assets", "logo.png")

APP_TYPES = ["Bonafide", "Student Certificate", "Scholarship", "NOC",
             "Academic Permission", "Examination", "Internship", "Placement", "Other request"]
FORWARD_LIST = ("VICE PRINCIPAL/ CHIEF ACADEMIC OFFICER/ ACCOUNTS/ SPORTS/ "
                "PLACEMENT CELL/ SCHOLARSHIP CELL/ EXAM CELL) (if required)")
DECLARATION = ("I certify that the information provided above is correct and that the request is "
               "being submitted for academic purposes. I understand that the request will be processed "
               "as per applicable Institute/University rules and within the stipulated processing time.")
PROCESSING = ("The request will normally be processed within 4 working days after receiving the completed "
              "form and all required supporting documents. Students are advised to apply in advance, "
              "as incomplete applications may require additional processing time.")


def _line(c, x1, x2, y, w=0.6):
    c.setLineWidth(w)
    c.line(x1, y, x2, y)


def _box(c, x, y, checked=False, size=9):
    c.setLineWidth(0.8)
    c.rect(x, y - 1, size, size)
    if checked:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 1.2, y + 0.3, "X")


def _field(c, label, x, y, x_end, value="", bold_label=False):
    """Label followed by an underlined value area."""
    c.setFont("Helvetica-Bold" if bold_label else "Helvetica", 10)
    c.drawString(x, y, label)
    lx = x + c.stringWidth(label, "Helvetica-Bold" if bold_label else "Helvetica", 10) + 4
    _line(c, lx, x_end, y - 3, 0.5)
    if value:
        c.setFont("Helvetica", 10)
        c.drawString(lx + 3, y, str(value)[:int((x_end - lx) / 4.8)])
    return lx


def build_pdf(d: dict) -> bytes:
    """d keys: department, outward_no, date, name, roll_no, semester, division, contact,
    app_type, purpose, docs_attached (bool), doc_names, signature_bytes (optional)"""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Requisition {d.get('roll_no', '')}")

    # ---------- Header box ----------
    top, bh = H - 40, 62
    c.setLineWidth(1)
    c.rect(LM, top - bh, RM - LM, bh)
    c.line(LM + 165, top, LM + 165, top - bh)
    if os.path.exists(LOGO):
        c.drawImage(ImageReader(LOGO), LM + 8, top - bh + 8, width=120, height=44,
                    preserveAspectRatio=True, mask="auto")
    c.setFont("Helvetica", 6.5)
    c.drawString(LM + 6, top - 9, "(Autonomous College Affiliated to University of Mumbai)")
    c.setFont("Helvetica-Bold", 15)
    cx = LM + 165 + (RM - LM - 165) / 2
    c.drawCentredString(cx, top - 27, "STUDENT ACADEMIC")
    c.drawCentredString(cx, top - 46, "REQUISITION FORM")

    # ---------- Dept / Outward / Date ----------
    y = top - bh - 28
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(LM, y, "Name of the Department.:")
    _line(c, LM + 118, LM + 275, y - 3, 0.5)
    c.setFont("Helvetica", 9.5)
    c.drawString(LM + 121, y, d["department"][:34])
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(LM + 290, y, "Dept. Outward No.:")
    _line(c, LM + 378, LM + 450, y - 3, 0.5)
    c.setFont("Helvetica", 9)
    c.drawString(LM + 380, y, d.get("outward_no", ""))
    y -= 18
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(LM, y, "Date:")
    _line(c, LM + 30, LM + 130, y - 3, 0.5)
    c.setFont("Helvetica", 9.5)
    c.drawString(LM + 33, y, d["date"])

    # ---------- Processing time ----------
    y -= 22
    c.setFont("Helvetica-Bold", 9)
    c.drawString(LM, y, "Processing Time:")
    c.setFont("Helvetica", 9)
    first = LM + c.stringWidth("Processing Time: ", "Helvetica-Bold", 9)
    words, line, lines, x0 = PROCESSING.split(), "", [], first
    maxw = RM - first
    for w_ in words:
        t = (line + " " + w_).strip()
        if c.stringWidth(t, "Helvetica", 9) <= maxw:
            line = t
        else:
            lines.append(line); line = w_; maxw = RM - LM
    lines.append(line)
    c.drawString(first, y, lines[0])
    for ln in lines[1:]:
        y -= 12
        c.drawString(LM, y, ln)
    y -= 8
    _line(c, LM, RM, y, 0.4)

    def heading(text, yy):
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(LM, yy, text)

    # ---------- 1. Student details ----------
    y -= 20
    heading("1. STUDENT DETAILS", y)
    y -= 24
    _field(c, "Name of Student:", LM, y, RM, d["name"])
    y -= 26
    _field(c, "Roll No.:", LM, y, LM + 150, d["roll_no"])
    _field(c, "Semester:", LM + 175, y, LM + 290, d["semester"])
    _field(c, "Division:", LM + 315, y, RM, d["division"])
    y -= 26
    _field(c, "Email / Mobile:", LM, y, RM, d["contact"])
    y -= 24
    c.setFont("Helvetica-Bold", 10)
    c.drawString(LM, y, "Application for")
    y -= 17
    # two rows of tick boxes, selected type is ticked
    row1, row2 = APP_TYPES[:5], APP_TYPES[5:]
    for row in (row1, row2):
        x = LM
        for t in row:
            _box(c, x, y, checked=(t == d["app_type"]))
            c.setFont("Helvetica", 9.5)
            c.drawString(x + 13, y, t)
            x += 13 + c.stringWidth(t, "Helvetica", 9.5) + 16
        y -= 17

    # ---------- 2. Purpose ----------
    y -= 6
    heading("2. PURPOSE / BRIEF DETAILS OF REQUEST", y)
    c.setFont("Helvetica", 10)
    lines = []
    for para in d["purpose"].splitlines() or [""]:
        lines += simpleSplit(para, "Helvetica", 10, RM - LM - 4) or [""]
    n_lines = 5
    y -= 20
    for i in range(n_lines):
        if i < len(lines):
            c.drawString(LM + 2, y, lines[i])
        _line(c, LM, RM, y - 3, 0.4)
        y -= 18
    if len(lines) > n_lines:
        # overflow: shrink text note
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(LM, y + 8, "(continued) " + " ".join(lines[n_lines:])[:120])

    # ---------- 3. Supporting docs ----------
    y -= 4
    heading("3. SUPPORTING DOCUMENTS", y)
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(LM, y, "Documents attached:")
    _box(c, LM + 112, y, checked=d["docs_attached"])
    c.drawString(LM + 126, y, "Yes")
    _box(c, LM + 170, y, checked=not d["docs_attached"])
    c.drawString(LM + 184, y, "No")
    y -= 22
    _field(c, "Document name(s), if applicable:", LM, y, RM,
           d["doc_names"] if d["docs_attached"] else "")

    # ---------- 4. Declaration ----------
    y -= 28
    heading("4. STUDENT DECLARATION", y)
    c.setFont("Helvetica", 10)
    y -= 16
    for ln in simpleSplit(DECLARATION, "Helvetica", 10, RM - LM):
        c.drawString(LM, y, ln)
        y -= 13
    y -= 14
    sig_y = y
    c.drawString(LM, y, "Student Signature:")
    _line(c, LM + 92, LM + 215, y - 3, 0.6)
    sig = d.get("signature_bytes")
    if sig:
        try:
            c.drawImage(ImageReader(io.BytesIO(sig)), LM + 95, y - 2, width=85, height=28,
                        preserveAspectRatio=True, mask="auto")
        except Exception:
            pass
    c.drawString(LM + 260, y, "Date:")
    _line(c, LM + 290, LM + 390, y - 3, 0.5)
    c.drawString(LM + 293, y, d["date"])

    # ---------- 5. HoD (blank) ----------
    y -= 34
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(LM, y, "5. HoD Signature:")
    _line(c, LM + 100, LM + 235, y - 3, 0.5)
    c.drawString(LM + 255, y, "Remarks:")
    _line(c, LM + 312, RM, y - 3, 0.5)
    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(LM, y, "Forwarded to")
    c.setFont("Helvetica", 9.5)
    fl = simpleSplit("(" + FORWARD_LIST, "Helvetica", 9.5, RM - LM - 68)
    c.drawString(LM + 68, y, fl[0])
    for ln in fl[1:]:
        y -= 12
        c.drawString(LM, y, ln)
    y -= 26
    c.setFont("Helvetica-Bold", 10)
    c.drawString(LM, y, "Signature:")
    _line(c, LM + 58, LM + 200, y - 3, 0.5)
    c.drawString(LM + 235, y, "Remarks:")
    _line(c, LM + 290, RM, y - 3, 0.5)

    # ---------- 6. Principal (blank) ----------
    y -= 30
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(LM, y, "6. PRINCIPAL OFFICE USE ONLY")
    y -= 22
    c.setFont("Helvetica", 10)
    c.drawString(LM, y, "Decision by Principal.:")
    x = LM + 115
    for t in ("Approved", "Not Approved", "Clarification Required"):
        _box(c, x, y)
        c.drawString(x + 13, y, t)
        x += 13 + c.stringWidth(t, "Helvetica", 10) + 18
    y -= 24
    _field(c, "Remarks (if any):", LM, y, RM)
    y -= 26
    _field(c, "Principal Signature:", LM, y, LM + 260)

    c.showPage()
    c.save()
    return buf.getvalue()
