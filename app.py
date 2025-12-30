import io
import json
import datetime as dt
from dataclasses import dataclass
from typing import Dict, Any, Tuple, List

import streamlit as st

# PDF generation (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm


# =========================
# App Config + Modern UI
# =========================
st.set_page_config(
    page_title="CrashLens AI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
  background: radial-gradient(1200px 600px at 20% 0%, rgba(59,130,246,0.15), transparent 60%),
              radial-gradient(900px 500px at 90% 10%, rgba(34,197,94,0.12), transparent 55%),
              linear-gradient(180deg, #0b1220 0%, #070b14 100%);
}

section[data-testid="stSidebar"]{
  background: rgba(255,255,255,0.04);
  border-right: 1px solid rgba(255,255,255,0.08);
}

.card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: 0 12px 30px rgba(0,0,0,0.25);
}

.small {
  opacity: 0.85;
  font-size: 0.92rem;
}

.stButton>button {
  border-radius: 14px;
  padding: 0.55rem 1rem;
  border: 1px solid rgba(255,255,255,0.18);
}

input, textarea {
  border-radius: 12px !important;
}

.badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(59,130,246,0.18);
  border: 1px solid rgba(59,130,246,0.35);
  margin-right: 8px;
  font-size: 0.85rem;
}

hr { border-color: rgba(255,255,255,0.08); }
</style>
""", unsafe_allow_html=True)


# =========================
# Helpers
# =========================
DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def normalize_probs(p: List[float]) -> List[float]:
    s = sum(p)
    if s <= 0:
        return [1/3, 1/3, 1/3]
    return [v/s for v in p]

def make_report_payload(accident: Dict[str, Any], party1: Dict[str, Any], party2: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "accident": accident,
        "party1": party1,
        "party2": party2,
        "analysis": analysis,
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "app": "CrashLens AI"
    }

def build_pdf(report: Dict[str, Any]) -> bytes:
    """
    Simple PDF generator (English).
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    def draw_title(text, y):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, y, text)

    def draw_section(title, y):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, title)
        c.setFont("Helvetica", 10)
        return y - 0.6*cm

    def draw_kv(k, v, y):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, y, f"{k}:")
        c.setFont("Helvetica", 10)
        txt = str(v) if v is not None else ""
        c.drawString(6.2*cm, y, txt[:110])
        return y - 0.5*cm

    y = height - 2.2*cm
    draw_title("CrashLens AI — Traffic Accident Report (Prototype)", y)
    y -= 1.0*cm

    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, "This report is auto-generated for demo/prototype purposes.")
    y -= 0.8*cm

    # Accident section
    y = draw_section("1) Accident Details", y)
    acc = report.get("accident", {})
    for k in ["date", "time", "road_type", "intersection_type", "location", "notes"]:
        y = draw_kv(k.replace("_", " ").title(), acc.get(k, ""), y)

    y -= 0.3*cm

    # Parties section
    y = draw_section("2) Party 1", y)
    p1 = report.get("party1", {})
    for k in ["name", "id", "phone", "role", "vehicle", "plate", "insurance", "damage_notes", "statement"]:
        y = draw_kv(k.replace("_", " ").title(), p1.get(k, ""), y)

    y -= 0.3*cm

    y = draw_section("3) Party 2", y)
    p2 = report.get("party2", {})
    for k in ["name", "id", "phone", "role", "vehicle", "plate", "insurance", "damage_notes", "statement"]:
        y = draw_kv(k.replace("_", " ").title(), p2.get(k, ""), y)

    y -= 0.3*cm

    # Analysis
    y = draw_section("4) Scenario Analysis", y)
    an = report.get("analysis", {})
    y = draw_kv("Intersection Type", an.get("intersection_type", ""), y)
    y = draw_kv("Hour", an.get("hour", ""), y)
    y = draw_kv("Vehicle 1 Speed (km/h)", an.get("v1_speed", ""), y)
    y = draw_kv("Vehicle 1 Direction", an.get("v1_dir", ""), y)
    y = draw_kv("Vehicle 2 Speed (km/h)", an.get("v2_speed", ""), y)
    y = draw_kv("Vehicle 2 Direction", an.get("v2_dir", ""), y)

    probs = an.get("probs", {"A": 0.33, "B": 0.33, "C": 0.34})
    y -= 0.2*cm
    y = draw_kv("Scenario A Probability", f"{probs.get('A', 0):.2f}", y)
    y = draw_kv("Scenario B Probability", f"{probs.get('B', 0):.2f}", y)
    y = draw_kv("Scenario C Probability", f"{probs.get('C', 0):.2f}", y)

    best = an.get("best", "")
    y = draw_kv("Most Likely Scenario", best, y)

    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(2*cm, 1.5*cm, f"Generated at: {report.get('generated_at','')}")
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.read()


# =========================
# MindSpore (Optional) Predictor
# =========================
@st.cache_resource
def get_predictor():
    """
    Tries to load a MindSpore predictor if available.
    If not, returns None and we do a deterministic fallback scoring.
    """
    try:
        # If you have your own predictor file, adjust import:
        # from model.predict import predict_proba
        from model.predict import predict_proba  # expected: (features)-> [pA,pB,pC]
        return predict_proba
    except Exception:
        return None

def fallback_proba(intersection_type: str, hour: int, v1_speed: int, v1_dir: str, v2_speed: int, v2_dir: str) -> List[float]:
    """
    Simple deterministic fallback (no ML) so the app always works.
    """
    # base weights
    a, b, c = 0.33, 0.33, 0.34

    # heuristics
    speed_gap = abs(v1_speed - v2_speed)
    high_speed = (v1_speed + v2_speed) / 2

    # intersection influence
    if intersection_type.lower() in ["roundabout", "circle", "rotary"]:
        c += 0.10
        a -= 0.03
        b -= 0.07
    elif intersection_type.lower() in ["crossroad", "intersection", "cross"]:
        a += 0.08
        b += 0.02
        c -= 0.10

    # speed influence
    if high_speed >= 90:
        b += 0.08
        a -= 0.03
        c -= 0.05
    if speed_gap >= 40:
        a += 0.06
        c -= 0.04
        b -= 0.02

    # night vs day
    if hour <= 5 or hour >= 22:
        b += 0.04
        c -= 0.02
        a -= 0.02

    return normalize_probs([a, b, c])


# =========================
# Header
# =========================
h1, h2 = st.columns([1, 6])
with h1:
    try:
        st.image("assets/logo.png", width=110)
    except Exception:
        st.write("🚗")
with h2:
    st.markdown("## CrashLens AI")
    st.caption("Traffic Accident Scenario Analysis (Prototype) • MindSpore-ready • PDF report")

st.markdown(
    '<span class="badge">English UI</span>'
    '<span class="badge">Parties + Vehicles</span>'
    '<span class="badge">Scenario A/B/C</span>'
    '<span class="badge">PDF Export</span>',
    unsafe_allow_html=True
)
st.divider()


# =========================
# Sidebar: Analysis Inputs
# =========================
st.sidebar.markdown("### Input Parameters")

intersection_type = st.sidebar.selectbox(
    "Intersection Type",
    ["Crossroad", "Roundabout", "T-Junction", "Highway Merge", "Parking / Low Speed", "Other"],
    index=0
)

hour = st.sidebar.slider("Time of Accident (Hour)", 0, 23, 14)

st.sidebar.markdown("### Vehicle 1 (for analysis)")
v1_speed = st.sidebar.slider("Speed V1 (km/h)", 0, 180, 60)
v1_dir = st.sidebar.selectbox("Direction V1", DIRECTIONS, index=0)

st.sidebar.markdown("### Vehicle 2 (for analysis)")
v2_speed = st.sidebar.slider("Speed V2 (km/h)", 0, 180, 50)
v2_dir = st.sidebar.selectbox("Direction V2", DIRECTIONS, index=0)


# =========================
# Main: Data Entry
# =========================
left, right = st.columns([1.15, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 1) Accident Details")

    c1, c2 = st.columns(2)
    with c1:
        acc_date = st.date_input("Date", dt.date.today())
    with c2:
        acc_time = st.time_input("Time", dt.time(2, 15))

    road_type = st.selectbox("Road Type", ["Crossroad", "Roundabout", "Highway", "Street", "Parking", "Other"], index=0)
    location = st.text_input("Location (city/landmark)", placeholder="e.g., King Fahd Road / Signal 3")
    notes = st.text_area("Notes (optional)", placeholder="Any extra context…", height=90)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 2) Party 1")
    p1_name = st.text_input("Full Name (Party 1)", key="p1_name")
    p1_id = st.text_input("ID / Iqama (Party 1)", key="p1_id")
    p1_phone = st.text_input("Phone (Party 1)", key="p1_phone")
    p1_role = st.selectbox("Role (Party 1)", ["Driver", "Owner", "Witness"], index=0, key="p1_role")
    p1_vehicle = st.text_input("Vehicle (Party 1)", placeholder="e.g., Toyota Camry", key="p1_vehicle")
    p1_plate = st.text_input("Plate Number (Party 1)", key="p1_plate")
    p1_ins = st.text_input("Insurance (Party 1)", placeholder="Company / policy", key="p1_ins")
    p1_damage = st.text_area("Damage Notes (Party 1)", placeholder="e.g., front bumper, right door…", height=70, key="p1_damage")
    p1_statement = st.text_area("Statement (Party 1)", placeholder="What party 1 says happened…", height=110, key="p1_stmt")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 3) Party 2")
    p2_name = st.text_input("Full Name (Party 2)", key="p2_name")
    p2_id = st.text_input("ID / Iqama (Party 2)", key="p2_id")
    p2_phone = st.text_input("Phone (Party 2)", key="p2_phone")
    p2_role = st.selectbox("Role (Party 2)", ["Driver", "Owner", "Witness"], index=0, key="p2_role")
    p2_vehicle = st.text_input("Vehicle (Party 2)", placeholder="e.g., Hyundai Elantra", key="p2_vehicle")
    p2_plate = st.text_input("Plate Number (Party 2)", key="p2_plate")
    p2_ins = st.text_input("Insurance (Party 2)", placeholder="Company / policy", key="p2_ins")
    p2_damage = st.text_area("Damage Notes (Party 2)", placeholder="e.g., rear bumper, left fender…", height=70, key="p2_damage")
    p2_statement = st.text_area("Statement (Party 2)", placeholder="What party 2 says happened…", height=110, key="p2_stmt")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 4) Evidence (optional)")
    imgs = st.file_uploader("Upload photos (optional)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    st.markdown('<p class="small">Tip: Keep it prototype-friendly. You can add mapping later.</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


st.divider()


# =========================
# Analyze
# =========================
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
with btn_col1:
    analyze = st.button("Analyze A / B / C", use_container_width=True)
with btn_col2:
    make_pdf = st.button("Generate PDF", use_container_width=True)
with btn_col3:
    st.caption("If MindSpore predictor is not available, app uses a safe fallback so the demo always runs.")

# Build base dicts
accident = {
    "date": str(acc_date),
    "time": acc_time.strftime("%H:%M"),
    "road_type": road_type,
    "intersection_type": intersection_type,
    "location": location,
    "notes": notes
}

party1 = {
    "name": p1_name,
    "id": p1_id,
    "phone": p1_phone,
    "role": p1_role,
    "vehicle": p1_vehicle,
    "plate": p1_plate,
    "insurance": p1_ins,
    "damage_notes": p1_damage,
    "statement": p1_statement
}

party2 = {
    "name": p2_name,
    "id": p2_id,
    "phone": p2_phone,
    "role": p2_role,
    "vehicle": p2_vehicle,
    "plate": p2_plate,
    "insurance": p2_ins,
    "damage_notes": p2_damage,
    "statement": p2_statement
}

analysis_payload = {
    "intersection_type": intersection_type,
    "hour": hour,
    "v1_speed": v1_speed,
    "v1_dir": v1_dir,
    "v2_speed": v2_speed,
    "v2_dir": v2_dir,
    "probs": {"A": 0.33, "B": 0.33, "C": 0.34},
    "best": "C"
}

if "last_report" not in st.session_state:
    st.session_state["last_report"] = None

if analyze:
    predictor = get_predictor()

    # Features expected by ML predictor (you can modify depending on your model)
    features = {
        "intersection_type": intersection_type,
        "hour": hour,
        "v1_speed": v1_speed,
        "v1_dir": v1_dir,
        "v2_speed": v2_speed,
        "v2_dir": v2_dir
    }

    if predictor is not None:
        try:
            probs_list = predictor(features)  # should return list [pA,pB,pC]
            probs_list = normalize_probs([safe_float(probs_list[0]), safe_float(probs_list[1]), safe_float(probs_list[2])])
        except Exception:
            probs_list = fallback_proba(intersection_type, hour, v1_speed, v1_dir, v2_speed, v2_dir)
    else:
        probs_list = fallback_proba(intersection_type, hour, v1_speed, v1_dir, v2_speed, v2_dir)

    probs = {"A": probs_list[0], "B": probs_list[1], "C": probs_list[2]}
    best = max(probs, key=probs.get)

    analysis_payload["probs"] = probs
    analysis_payload["best"] = f"{best} ({probs[best]:.2f})"

    st.success("Analysis completed")

    # Chart
    st.markdown("### Scenario Probability Distribution")
    st.bar_chart({"A": probs["A"], "B": probs["B"], "C": probs["C"]})

    st.info(f"Most likely scenario: **{best}**  (probability **{probs[best]:.2f}**)")

    report = make_report_payload(accident, party1, party2, analysis_payload)
    st.session_state["last_report"] = report

    st.markdown("### Report Summary (Preview)")
    st.json(report)

# PDF generation from last report (or current if exists)
if make_pdf:
    report = st.session_state.get("last_report")
    if report is None:
        # generate minimal report even if they didn't click Analyze
        report = make_report_payload(accident, party1, party2, analysis_payload)
        st.session_state["last_report"] = report

    try:
        pdf_bytes = build_pdf(report)
        st.success("PDF is ready")
        st.download_button(
            label="Download Report (PDF)",
            data=pdf_bytes,
            file_name="crashlens_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"PDF generation failed: {e}")

st.divider()

# Optional: show uploaded images preview (if any)
if imgs:
    st.markdown("### Evidence Preview")
    cols = st.columns(3)
    for i, f in enumerate(imgs):
        with cols[i % 3]:
            st.image(f, caption=f.name, use_container_width=True)
