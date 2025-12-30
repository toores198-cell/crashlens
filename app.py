import streamlit as st
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from model.predict import predict_scenario


def build_pdf(report_data, result):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "CrashLens AI - Accident Report (Prototype)")
    y -= 25

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "1) Accident Details")
    y -= 18
    c.setFont("Helvetica", 11)

    acc = report_data["accident"]
    lines = [
        f"Date: {acc['date']}",
        f"Time: {acc['time']}",
        f"Road Type: {acc['road_type']}",
        f"Location: {acc['location']}",
        f"Notes: {acc['notes']}",
    ]
    for line in lines:
        c.drawString(60, y, line[:110])
        y -= 14

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "2) Parties Information")
    y -= 18

    # Party 1
    c.setFont("Helvetica-Bold", 11)
    c.drawString(55, y, "Party 1")
    y -= 16
    c.setFont("Helvetica", 11)
    p1 = report_data["party1"]
    p1_lines = [
        f"Name: {p1['name']}",
        f"ID: {p1['id']}",
        f"Phone: {p1['phone']}",
        f"Role: {p1['role']}",
        f"Vehicle: {p1['vehicle']}",
        f"Plate: {p1['plate']}",
        f"Statement: {p1['statement']}",
    ]
    for line in p1_lines:
        c.drawString(60, y, line[:110])
        y -= 14

    y -= 8

    # Party 2
    c.setFont("Helvetica-Bold", 11)
    c.drawString(55, y, "Party 2")
    y -= 16
    c.setFont("Helvetica", 11)
    p2 = report_data["party2"]
    p2_lines = [
        f"Name: {p2['name']}",
        f"ID: {p2['id']}",
        f"Phone: {p2['phone']}",
        f"Role: {p2['role']}",
        f"Vehicle: {p2['vehicle']}",
        f"Plate: {p2['plate']}",
        f"Statement: {p2['statement']}",
    ]
    for line in p2_lines:
        if y < 90:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 11)
        c.drawString(60, y, line[:110])
        y -= 14

    # Analysis section
    if y < 170:
        c.showPage()
        y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "3) Scenario Analysis (A / B / C)")
    y -= 18
    c.setFont("Helvetica", 11)

    inputs = report_data["analysis_inputs"]
    c.drawString(60, y, f"Intersection: {inputs['intersection']} | Hour: {inputs['hour']}")
    y -= 14
    c.drawString(60, y, f"Vehicle 1: {inputs['v1_speed']} km/h | Direction: {inputs['v1_dir']}")
    y -= 14
    c.drawString(60, y, f"Vehicle 2: {inputs['v2_speed']} km/h | Direction: {inputs['v2_dir']}")
    y -= 18

    c.drawString(60, y, f"Scenario A: {result['A']:.3f}")
    y -= 14
    c.drawString(60, y, f"Scenario B: {result['B']:.3f}")
    y -= 14
    c.drawString(60, y, f"Scenario C: {result['C']:.3f}")
    y -= 18

    best = max(result, key=result.get)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y, f"Most likely scenario: {best} ({result[best]:.3f})")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="CrashLens AI", page_icon="🚗", layout="wide")

st.title("🚗 CrashLens AI")
st.caption("Traffic Accident Reporting + Scenario Analysis (Prototype)")
st.divider()

# -----------------------------
# Sidebar: Analysis Parameters
# -----------------------------
with st.sidebar:
    st.header("Analysis Parameters (A / B / C)")

    intersection = st.selectbox("Intersection Type", ["Crossroad", "Roundabout"])
    time_hour = st.slider("Time of Accident (Hour)", 0, 23, 14)

    st.subheader("Vehicle 1 (for analysis)")
    speed1 = st.slider("Speed V1 (km/h)", 0, 200, 60, key="speed1")
    dir1 = st.selectbox("Direction V1", ["N", "E", "S", "W"], key="dir1")

    st.subheader("Vehicle 2 (for analysis)")
    speed2 = st.slider("Speed V2 (km/h)", 0, 200, 50, key="speed2")
    dir2 = st.selectbox("Direction V2", ["N", "E", "S", "W"], key="dir2")

    analyze = st.button("Analyze A / B / C", use_container_width=True)

# -----------------------------
# Main: Accident Report Form
# -----------------------------
st.subheader("1) Accident Details")

colA, colB, colC = st.columns(3)
with colA:
    accident_date = st.date_input("Accident Date")
with colB:
    accident_time_text = st.text_input("Accident Time (HH:MM)", value="02:15")
with colC:
    road_type = st.selectbox("Road Type", ["Crossroad", "Roundabout", "Highway", "Street"])

location = st.text_input("Accident Location (e.g., King Fahd Rd / Roundabout name)")
notes = st.text_area("Short Description / Notes", height=90)

st.divider()
st.subheader("2) Parties Information")

tab1, tab2 = st.tabs(["Party 1", "Party 2"])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        p1_name = st.text_input("Full Name", key="p1_name")
        p1_id = st.text_input("National ID / Iqama", key="p1_id")
    with c2:
        p1_phone = st.text_input("Phone Number", key="p1_phone")
        p1_role = st.selectbox("Role", ["Driver", "Owner", "Passenger"], key="p1_role")
    with c3:
        p1_vehicle = st.text_input("Vehicle Make/Model", placeholder="e.g., Toyota Camry", key="p1_vehicle")
        p1_plate = st.text_input("Plate Number", key="p1_plate")

    p1_statement = st.text_area("Party 1 Statement (What happened?)", height=90, key="p1_statement")

with tab2:
    c1, c2, c3 = st.columns(3)
    with c1:
        p2_name = st.text_input("Full Name", key="p2_name")
        p2_id = st.text_input("National ID / Iqama", key="p2_id")
    with c2:
        p2_phone = st.text_input("Phone Number", key="p2_phone")
        p2_role = st.selectbox("Role", ["Driver", "Owner", "Passenger"], key="p2_role")
    with c3:
        p2_vehicle = st.text_input("Vehicle Make/Model", placeholder="e.g., Hyundai Elantra", key="p2_vehicle")
        p2_plate = st.text_input("Plate Number", key="p2_plate")

    p2_statement = st.text_area("Party 2 Statement (What happened?)", height=90, key="p2_statement")

st.divider()

# -----------------------------
# Collect report data
# -----------------------------
report_data = {
    "accident": {
        "date": str(accident_date),
        "time": accident_time_text,
        "road_type": road_type,
        "location": location,
        "notes": notes,
    },
    "party1": {
        "name": p1_name,
        "id": p1_id,
        "phone": p1_phone,
        "role": p1_role,
        "vehicle": p1_vehicle,
        "plate": p1_plate,
        "statement": p1_statement,
    },
    "party2": {
        "name": p2_name,
        "id": p2_id,
        "phone": p2_phone,
        "role": p2_role,
        "vehicle": p2_vehicle,
        "plate": p2_plate,
        "statement": p2_statement,
    },
    "analysis_inputs": {
        "intersection": intersection,
        "hour": time_hour,
        "v1_speed": speed1,
        "v1_dir": dir1,
        "v2_speed": speed2,
        "v2_dir": dir2,
    },
}

# -----------------------------
# Run analysis + Results + PDF
# -----------------------------
dir_map = {"N": 0, "E": 1, "S": 2, "W": 3}
int_map = {"Crossroad": 0, "Roundabout": 1}

if analyze:
    inputs = [
        float(speed1),
        float(speed2),
        float(dir_map[dir1]),
        float(dir_map[dir2]),
        float(time_hour),
        float(int_map[intersection]),
    ]

    result = predict_scenario(inputs)

    st.success("Analysis completed")

    st.subheader("3) Scenario Probability Distribution")
    st.bar_chart(result)

    best = max(result, key=result.get)
    st.info(f"Most likely scenario: {best} ({result[best]:.2f})")

    pdf_bytes = build_pdf(report_data, result)
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name="CrashLens_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )

else:
    st.info("Fill the report fields, then click Analyze A / B / C from the sidebar.")
