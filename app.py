import streamlit as st
from model.predict import predict_scenario

st.set_page_config(
    page_title="CrashLens AI",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 CrashLens AI")
st.caption("Traffic Accident Scenario Analysis (Prototype)")

st.divider()

with st.sidebar:
    st.header("Input Parameters")

    intersection = st.selectbox(
        "Intersection Type",
        ["Crossroad", "Roundabout"]
    )

    time_hour = st.slider(
        "Time of Accident (Hour)",
        0, 23, 14
    )

    st.subheader("Vehicle 1")
    speed1 = st.slider(
        "Speed (km/h)",
        0, 200, 60,
        key="speed1"
    )
    dir1 = st.selectbox(
        "Direction",
        ["N", "E", "S", "W"],
        key="dir1"
    )

    st.subheader("Vehicle 2")
    speed2 = st.slider(
        "Speed (km/h)",
        0, 200, 50,
        key="speed2"
    )
    dir2 = st.selectbox(
        "Direction",
        ["N", "E", "S", "W"],
        key="dir2"
    )

    analyze = st.button("Analyze A / B / C", use_container_width=True)

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

    st.subheader("Scenario Probability Distribution")
    st.bar_chart(result)

    best = max(result, key=result.get)
    st.info(
        f"Most likely scenario: {best} "
        f"({result[best]:.2f})"
    )

else:
    st.info("Fill the inputs and click Analyze")
