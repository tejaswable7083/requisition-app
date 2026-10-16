# Student Academic Requisition Form – Streamlit App

Fill the requisition form online → validate → save to SQLite → generate PDF in the institute form layout → download.

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

Admin tab password: `admin123` (override via `ADMIN_PASSWORD` in Streamlit secrets / env var).

## Files
- `app.py` – Streamlit UI (form, tracking, admin dashboard)
- `pdf_generator.py` – builds the PDF following the institute form (ReportLab)
- `validators.py` – mandatory / email / mobile / declaration checks
- `database.py` – SQLite storage, auto requisition number, search, status
- `assets/logo.png` – logo from the provided form

## Deploy (Streamlit Community Cloud)
1. Push this folder to a public GitHub repo
2. share.streamlit.io → New app → select repo → main file `app.py` → Deploy
