import streamlit as st
from model.predict import predict_scenario

st.set_page_config(
    page_title="CrashLens AI",
    page_icon="🚗",
    layout="wide"
)

# ---- UI Header ----
st.title("🚗 CrashLens AI")
st.caption("Traffic Accident Scenario Analysis (Prototype) — powered by MindSpore")

st.divider()

# ---- Sidebar Inputs ----
with st.sidebar:
    st.header("Inputs")
    st.caption("Fill the key accident parameters")

    st.subheader("Accident Context")
    intersection = st.selectbox("Intersection Type", ["Crossroad", "Roundabout"])
    time_hour = st.slider("Time of Accident (hour)", 0, 23, 14)

    st.subheader("Vehicle 1")
    speed1 = st.slider("Speed (km/h) — Vehicle 1", 0, 200, 60)
    dir1 = st.selectbox("Direction — Vehicle 1", ["N", "E", "S", "W"])

    st.subheader("Vehicle 2")
    speed2 = st.slider("Speed (km/h) — Vehicle 2", 0, 200, 50)
    dir2 = st.selectbox("Direction — Vehicle 2", ["N", "E", "S", "W"])

    run_btn = st.button("Analyze A / B / C", use_container_width=True)

# ---- Mapping ----
dir_map = {"N": 0, "E": 1, "S": 2, "W": 3}
int_map = {"Crossroad": 0, "Roundabout": 1}

# ---- Main Layout ----
col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.subheader("Scenario Results")
    st.write(
        "This prototype generates **three possible scenarios** and assigns a probability to each:"
        "\n- **A**: Fault mostly on Vehicle 1"
        "\n- **B**: Fault mostly on Vehicle 2"
        "\n- **C**: Shared fault"
    )

    if run_btn:
        inputs = [
            float(speed1),
            float(speed2),
            float(dir_map[dir1]),
            float(dir_map[dir2]),
            float(time_hour),
            float(int_map[intersection]),
        ]

        result = predict_scenario(inputs)  # returns dict A/B/C probabilities

        st.success("Analysis completed ✅")

        st.write("### Probability Distribution")
        st.bar_chart(result)

        best = max(result, key=result.get)
        st.info(f"Most likely scenario: **{best}** ({result[best]:.2f})")

        st.write("### Raw Output")
        st.json({k: round(v, 4) for k, v in result.items()})

    else:
        st.warning("Use the sidebar and click **Analyze A / B / C**.")

with col2:
    st.subheader("Accident Summary")
    st.metric("Intersection", intersection)
    st.metric("Time (hour)", time_hour)

    st.divider()
    st.write("**Vehicle 1**")
    st.write(f"- Speed: **{speed1} km/h**")
    st.write(f"- Direction: **{dir1}**")

    st.write("**Vehicle 2**")
    st.write(f"- Speed: **{speed2} km/h**")
    st.write(f"- Direction: **{dir2}**")

    st.divider()
    st.caption(
        "Disclaimer: This is a prototype for visualization and analysis support only — "
        "not a legal determination of liability."
    )
