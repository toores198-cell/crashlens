import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="CrashLens AI", layout="wide")

st.title("🚗 CrashLens AI — تسجيل حادث مروري (Prototype)")
st.write("👋 مرحبا! هذا نموذج أولي لتسجيل الحوادث المرورية")

# =========================
# 1) بيانات الحادث
# =========================
st.subheader("1) بيانات الحادث")

col1, col2, col3 = st.columns(3)
with col1:
    time = st.text_input("وقت الحادث", placeholder="مثال: 02:15")
with col2:
    location = st.text_input("موقع الحادث", placeholder="مثال: دوار الشاطئ")
with col3:
    road_type = st.selectbox("نوع الطريق", ["دوّار", "تقاطع", "شارع مستقيم"])

st.divider()

# =========================
# 2) بيانات الأطراف
# =========================
st.subheader("2) بيانات الأطراف")

st.markdown("### الطرف الأول")
c1, c2, c3 = st.columns(3)
with c1:
    p1_name = st.text_input("اسم الطرف الأول")
with c2:
    p1_id = st.text_input("هوية الطرف الأول / إقامة")
with c3:
    p1_phone = st.text_input("رقم الجوال (الطرف الأول)")

c4, c5, c6 = st.columns(3)
with c4:
    p1_plate = st.text_input("رقم لوحة المركبة (الطرف الأول)")
with c5:
    p1_car = st.text_input("نوع المركبة (الطرف الأول)", placeholder="مثال: Toyota Camry")
with c6:
    p1_speed = st.number_input("السرعة التقريبية (كم/س) — الطرف الأول", min_value=0, max_value=250, value=40)

st.divider()

st.markdown("### الطرف الثاني")
d1, d2, d3 = st.columns(3)
with d1:
    p2_name = st.text_input("اسم الطرف الثاني")
with d2:
    p2_id = st.text_input("هوية الطرف الثاني / إقامة")
with d3:
    p2_phone = st.text_input("رقم الجوال (الطرف الثاني)")

d4, d5, d6 = st.columns(3)
with d4:
    p2_plate = st.text_input("رقم لوحة المركبة (الطرف الثاني)")
with d5:
    p2_car = st.text_input("نوع المركبة (الطرف الثاني)", placeholder="مثال: Hyundai Elantra")
with d6:
    p2_speed = st.number_input("السرعة التقريبية (كم/س) — الطرف الثاني", min_value=0, max_value=250, value=40)

# =========================
# طرف ثالث (اختياري)
# =========================
st.divider()
has_third = st.checkbox("هل يوجد طرف ثالث؟")

p3_data = None
if has_third:
    st.markdown("### الطرف الثالث (اختياري)")
    e1, e2, e3 = st.columns(3)
    with e1:
        p3_name = st.text_input("اسم الطرف الثالث")
    with e2:
        p3_id = st.text_input("هوية الطرف الثالث / إقامة")
    with e3:
        p3_phone = st.text_input("رقم الجوال (الطرف الثالث)")

    e4, e5, e6 = st.columns(3)
    with e4:
        p3_plate = st.text_input("رقم لوحة المركبة (الطرف الثالث)")
    with e5:
        p3_car = st.text_input("نوع المركبة (الطرف الثالث)")
    with e6:
        p3_speed = st.number_input("السرعة التقريبية (كم/س) — الطرف الثالث", min_value=0, max_value=250, value=40)

    p3_data = {
        "name": p3_name,
        "id": p3_id,
        "phone": p3_phone,
        "plate": p3_plate,
        "car": p3_car,
        "speed_kmh": p3_speed,
    }

st.divider()

# =========================
# 3) وصف الحادث
# =========================
st.subheader("3) وصف الحادث")

accident_type = st.selectbox(
    "نوع الحادث",
    [
        "صدم خلفي",
        "تغيير مسار مفاجئ",
        "عدم التزام بالأولوية",
        "دخول دوّار",
        "قطع إشارة",
        "أخرى"
    ]
)

accident_description = st.text_area(
    "اشرح كيف صار الحادث (باختصار)",
    placeholder="مثال: الطرف الثاني دخل الدوار بدون إعطاء أولوية..."
)

st.divider()

# =========================
# 4) رسم الحادث على الخريطة (أوضاع متعددة)
# =========================
st.subheader("4) رسم الحادث على الخريطة")

mode = st.radio(
    "وضع الإضافة:",
    ["📍 موقع الحادث", "🟦 مسار الطرف الأول", "🟧 مسار الطرف الثاني", "❌ نقطة التصادم", "🧹 مسح الكل"],
    horizontal=True
)

# تخزين النقاط في session_state
if "accident_location" not in st.session_state:
    st.session_state.accident_location = None
if "p1_path" not in st.session_state:
    st.session_state.p1_path = []
if "p2_path" not in st.session_state:
    st.session_state.p2_path = []
if "collision_point" not in st.session_state:
    st.session_state.collision_point = None

# مسح الكل
if mode == "🧹 مسح الكل":
    st.session_state.accident_location = None
    st.session_state.p1_path = []
    st.session_state.p2_path = []
    st.session_state.collision_point = None
    st.success("تم مسح جميع النقاط ✅")

# مركز الخريطة (افتراضي + يتحرك إذا حددتي موقع الحادث)
default_center = [26.4207, 50.0888]  # الدمام/الخبر تقريباً
center = st.session_state.accident_location or default_center

m = folium.Map(location=center, zoom_start=14)

# موقع الحادث
if st.session_state.accident_location:
    folium.Marker(
        st.session_state.accident_location,
        tooltip="موقع الحادث",
        icon=folium.Icon(color="blue")
    ).add_to(m)

# مسار الطرف الأول (خط + نقاط)
if st.session_state.p1_path:
    for pt in st.session_state.p1_path:
        folium.CircleMarker(pt, radius=5, color="blue", fill=True, fill_opacity=0.8).add_to(m)
    folium.PolyLine(st.session_state.p1_path, color="blue", weight=4).add_to(m)

# مسار الطرف الثاني (خط + نقاط)
if st.session_state.p2_path:
    for pt in st.session_state.p2_path:
        folium.CircleMarker(pt, radius=5, color="orange", fill=True, fill_opacity=0.8).add_to(m)
    folium.PolyLine(st.session_state.p2_path, color="orange", weight=4).add_to(m)

# نقطة التصادم
if st.session_state.collision_point:
    folium.Marker(
        st.session_state.collision_point,
        tooltip="نقطة التصادم",
        icon=folium.Icon(color="red")
    ).add_to(m)

map_data = st_folium(m, height=450, width=None)

# التقاط النقر
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    clicked = [lat, lon]

    if mode == "📍 موقع الحادث":
        st.session_state.accident_location = clicked
        st.toast("تم تحديد موقع الحادث ✅")

    elif mode == "🟦 مسار الطرف الأول":
        st.session_state.p1_path.append(clicked)
        st.toast("تمت إضافة نقطة لمسار الطرف الأول ✅")

    elif mode == "🟧 مسار الطرف الثاني":
        st.session_state.p2_path.append(clicked)
        st.toast("تمت إضافة نقطة لمسار الطرف الثاني ✅")

    elif mode == "❌ نقطة التصادم":
        st.session_state.collision_point = clicked
        st.toast("تم تحديد نقطة التصادم ✅")

st.caption(
    f"📍 موقع الحادث: {st.session_state.accident_location} | "
    f"🟦 نقاط مسار الطرف الأول: {len(st.session_state.p1_path)} | "
    f"🟧 نقاط مسار الطرف الثاني: {len(st.session_state.p2_path)} | "
    f"❌ نقطة التصادم: {st.session_state.collision_point}"
)

st.divider()

# =========================
# حفظ البلاغ (عرض البيانات)
# =========================
if st.button("✅ حفظ البلاغ"):
    report = {
        "accident": {
            "time": time,
            "location_text": location,
            "road_type": road_type,
            "accident_type": accident_type,
            "description": accident_description,
            "map": {
                "accident_location": st.session_state.accident_location,
                "party1_path": st.session_state.p1_path,
                "party2_path": st.session_state.p2_path,
                "collision_point": st.session_state.collision_point,
            },
        },
        "parties": [
            {
                "name": p1_name,
                "id": p1_id,
                "phone": p1_phone,
                "plate": p1_plate,
                "car": p1_car,
                "speed_kmh": p1_speed,
            },
            {
                "name": p2_name,
                "id": p2_id,
                "phone": p2_phone,
                "plate": p2_plate,
                "car": p2_car,
                "speed_kmh": p2_speed,
            }
        ]
    }

    if p3_data:
        report["parties"].append(p3_data)

    st.success("تم حفظ البلاغ ✅")
    st.write("### البيانات المدخلة:")
    st.json(report)
