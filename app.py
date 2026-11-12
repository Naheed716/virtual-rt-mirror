import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math

st.set_page_config(page_title="Virtual RT Mirror - Realistic", layout="centered")
st.title("Virtual RT Mirror")
st.markdown("**Mobile Only | No Hardware | Radiotherapy Department**")
st.caption("Realistic Simulation - CT Sim → TPS → LINAC / Cobalt-60")

# ---------- PATIENT DATA - REALISTIC ----------
PATIENTS = {
    "NECK-01": {"site": "Head & Neck", "oar": "Cord / Parotid", "oar_limit": 45, "mask": True, "position": "Supine", "ct_w": 7, "ct_h": 9, "gtv_pos": (0.5, 1.0), "oar_pos": (0, -2.0), "dose": 70, "fx": 35},
    "BREAST-01": {"site": "Breast - Left", "oar": "Heart / Lung", "oar_limit": 20, "mask": False, "position": "Supine", "ct_w": 11, "ct_h": 8, "gtv_pos": (-2.5, 0.5), "oar_pos": (1.5, -1.0), "dose": 50, "fx": 25},
    "BRAIN-01": {"site": "Brain", "oar": "Brainstem / Optic", "oar_limit": 54, "mask": True, "position": "Supine", "ct_w": 8, "ct_h": 8.5, "gtv_pos": (0.5, 0.5), "oar_pos": (0, -1.5), "dose": 60, "fx": 30},
    "PELVIS-01": {"site": "Pelvis", "oar": "Bladder / Rectum", "oar_limit": 65, "mask": False, "position": "Supine", "ct_w": 11, "ct_h": 9.5, "gtv_pos": (0, 0.5), "oar_pos": (0, -2.2), "dose": 50, "fx": 25},
}

st.subheader("Patient")
patient = st.selectbox("Patient Select Karo", list(PATIENTS.keys()))
p = PATIENTS[patient]

# Auto-correct Position / Mask - Realistic
position = st.selectbox("Position", ["Supine", "Prone"], index=0 if p["position"]=="Supine" else 1)
mask = st.checkbox(f"Mask / Immobilization {'(Required for Neck/Brain)' if p['mask'] else '(Not used for this site)'}", value=p["mask"])
if p["mask"] and not mask:
    st.warning("⚠️ Is patient ke liye Mask ON hona chahiye - Neck/Brain me bina Mask ke position hil jayegi")
if patient=="BREAST-01" and position=="Prone":
    st.info("Note: Breast me zyada tar Supine use hota hai, Prone sirf khaas cases me")

mirror = st.radio("Mirror Select Karo", ["A - CT Sim", "B - TPS", "C - LINAC", "D - Cobalt-60"], horizontal=True)

# ================= A - CT SIM - REALISTIC =================
if mirror == "A - CT Sim":
    st.subheader("A - CT Sim Mirror")
    st.write(f"Patient: **{patient} - {p['site']}** | Position: **{position}** | Mask: **{'ON' if mask else 'OFF'}** | OAR: **{p['oar']}**")
    laser = st.checkbox("Laser - Tattoo OK", value=True)
    slice_no = st.slider("CT Slice Number", 1, 20, 10)
    scan = st.button("📸 SCAN", use_container_width=True)
    if scan:
        st.success(f"CT Scan Ho Gaya - Slice {slice_no} / 20 - {p['site']}")
        fig, ax = plt.subplots(figsize=(4, 4))
        # Realistic body shape per site
        body = patches.Ellipse((0, 0), p["ct_w"], p["ct_h"], facecolor="#E8E8E8", edgecolor="black", linewidth=1.2)
        ax.add_patch(body)
        # GTV - size changes with slice - middle slice me bara
        gtv_r = 1.2 if 8 <= slice_no <= 12 else 0.7
        gtv = patches.Circle(p["gtv_pos"], gtv_r, facecolor="red", alpha=0.85)
        ax.add_patch(gtv)
        ax.text(p["gtv_pos"][0], p["gtv_pos"][1], "GTV", ha="center", va="center", fontsize=8, fontweight="bold", color="white")
        # OAR - realistic per patient
        oar = patches.Circle(p["oar_pos"], 0.7, facecolor="yellow", edgecolor="black")
        ax.add_patch(oar)
        ax.text(p["oar_pos"][0], p["oar_pos"][1], p["oar"].split("/")[0].strip(), ha="center", va="center", fontsize=6)
        # Breast me 2nd breast outline
        if patient == "BREAST-01":
            ax.add_patch(patches.Ellipse((2.8, 0.5), 3, 3.5, facecolor="none", edgecolor="gray", linestyle="--"))
            ax.text(2.8, 2.5, "Right Breast", ha="center", fontsize=6, color="gray")
        ax.set_xlim(-7, 7)
        ax.set_ylim(-7, 7)
        ax.set_aspect("equal")
        ax.set_title(f"CT - {patient} - Axial Slice {slice_no} - {p['site']}")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        st.write(f"GTV = Red | {p['oar']} = Yellow")
        if st.button("Send to TPS →", use_container_width=True):
            st.info("CT TPS ko Send Ho Gaya - Ab B - TPS Mirror kholo")
    else:
        st.info("Pehle SCAN dabao, phir CT aayega")

# ================= B - TPS - REALISTIC =================
elif mirror == "B - TPS":
    st.subheader("B - TPS Mirror")
    st.write(f"Patient: **{patient} - {p['site']}** - CT Aa Gaya Hai")
    dose = st.slider("Prescription Dose (Gy)", 30, 70, p["dose"], 5)
    beam_type = st.selectbox("Beam Technique", ["VMAT - 2 Arcs", "3D-CRT - 3 Fields", "IMRT - 5 Fields"])
    # Technique se OAR dose realistic - VMAT me OAR kam, 3D me zyada
    tech_factor = {"VMAT - 2 Arcs": 0.38, "IMRT - 5 Fields": 0.45, "3D-CRT - 3 Fields": 0.58}[beam_type]
    oar_dose = round(p["oar_limit"] * tech_factor, 1)
    # PTV coverage realistic - dose zyada to coverage thora kam ho sakta hai
    ptv_cover = 95 if dose <= 60 else 93
    st.write(f"GTV = Red | {p['oar']} = Yellow | PTV = {dose} Gy | Beam = {beam_type}")

    if dose <= 40:
        dc, dl = "#FFEB3B", "Low - Yellow"
    elif dose <= 55:
        dc, dl = "#FF9800", "Medium - Orange"
    else:
        dc, dl = "#F44336", "High - Red"
    st.markdown(f"**Dose Wash:** <span style='background:{dc}; padding:4px 10px; border-radius:6px'>{dl} - {dose} Gy</span>", unsafe_allow_html=True)

    if oar_dose < p["oar_limit"]:
        st.success(f"PTV {ptv_cover}% PASS | {p['oar']} = {oar_dose} Gy < {p['oar_limit']} Gy PASS - {beam_type} se OAR bacha")
    else:
        st.error(f"PTV PASS | {p['oar']} = {oar_dose} Gy > Limit - Plan FAIL, Technique badlo")

    # DVH - OAR curve ab technique se badlegi, PTV dose se
    fig2, ax2 = plt.subplots(figsize=(5, 3.5))
    x = np.linspace(0, 80, 200)
    ptv_y = 100 / (1 + np.exp((x - dose) / 3))
    oar_y = 100 / (1 + np.exp((x - oar_dose) / 4))
    ax2.plot(x, ptv_y, color="red", linewidth=2.5, label=f"PTV - {dose} Gy ({ptv_cover}%)")
    ax2.plot(x, oar_y, color="blue", linewidth=2.5, label=f"{p['oar']} - {oar_dose} Gy (Limit {p['oar_limit']} Gy)")
    ax2.axvline(dose, color="red", linestyle="--", alpha=0.4)
    ax2.axvline(p["oar_limit"], color="blue", linestyle="--", alpha=0.4)
    ax2.set_xlim(0, 80); ax2.set_ylim(0, 105)
    ax2.set_xlabel("Dose (Gy)"); ax2.set_ylabel("Volume (%)")
    ax2.set_title(f"DVH - {patient} - {beam_type}")
    ax2.grid(True, linestyle="--", alpha=0.4); ax2.legend(fontsize=8)
    st.pyplot(fig2)
    if st.button("✅ APPROVE", use_container_width=True):
        st.success("Plan APPROVED - Ab C - LINAC Mirror kholo")

# ================= C - LINAC - REALISTIC =================
elif mirror == "C - LINAC":
    st.subheader("C - LINAC Mirror")
    st.write(f"Patient: **{patient}** - Plan Approved | SSD 100 cm | Energy 6 MV")
    gantry = st.slider("Gantry Angle", 0, 360, 90, 5)
    coll = st.slider("Collimator / Field Size (cm)", 0, 20, 10, 1)
    couch_x = st.slider("Couch X (cm)", -5, 5, 0)
    couch_y = st.slider("Couch Y (cm)", -5, 5, 0)
    couch_z = st.slider("Couch Z (cm)", -5, 5, 0)
    # MU realistic calc - Field bara to MU kam
    mu = int(200 * (10 / max(coll, 1)) + dose if False else 200)
    st.write(f"Gantry: {gantry}° | Field: {coll} x {coll} cm | Couch: {couch_x}, {couch_y}, {couch_z} | SSD: 100 cm")
    cbct = st.checkbox("CBCT Matched", value=True)
    if cbct:
        st.success("CBCT Matched - Position Correct")
    else:
        st.warning("CBCT NOT Matched - Pehle Couch Shift karo, Beam ON mat karo")

    col1, col2 = st.columns(2)
    with col1:
        beam_on = st.button("🔴 BEAM ON", use_container_width=True)
    with col2:
        beam_off = st.button("BEAM OFF", use_container_width=True)
    if beam_on and not cbct:
        st.error("Beam ON nahi ho sakti - CBCT Match nahi hai!")
    elif beam_on:
        st.error(f"BEAM ON - Gantry {gantry}° - Field {coll} x {coll} cm - Beam Chal Rahi Hai")
        # REALISTIC: Beam Gantry angle ke hisab se ghoomegi
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.add_patch(patches.Rectangle((-coll/2, -coll/2), coll, coll, facecolor="#FFF9C4", edgecolor="#FFD700", linewidth=2))
        # Gantry angle to direction
        ang = math.radians(gantry)
        # 0° = upar se, 90° = side se
        dx = math.sin(ang) * 10
        dy = math.cos(ang) * 10
        ax.plot([dx, 0], [dy, 0], color="red", linewidth=3)
        ax.plot(dx, dy, marker="o", color="black", markersize=6)
        ax.text(dx, dy+1, f"Gantry {gantry}°", ha="center", fontsize=8, fontweight="bold")
        ax.text(0, 0, f"{coll} x {coll} cm", ha="center", va="center", fontweight="bold")
        ax.set_xlim(-12, 12); ax.set_ylim(-12, 12); ax.set_aspect("equal")
        ax.set_title(f"Beam ON - Gantry {gantry}° - Beam Direction")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    if beam_off:
        st.info("Beam OFF - Treatment Pause")
    if st.button("🛑 EMERGENCY STOP", use_container_width=True):
        st.error("EMERGENCY STOP - Beam Band, Sab Ruk Gaya")

# ================= D - COBALT-60 - REALISTIC =================
else:
    st.subheader("D - Cobalt-60 Mirror")
    st.write(f"Patient: **{patient}**")
    st.write("Source: **Co-60** | Half-Life: **5.27 Years** | Energy: **1.17 + 1.33 MeV (Avg 1.25)** | SSD: **80 cm**")
    years_old = st.slider("Source Kitna Purana Hai? (Years Since Calibration)", 0, 10, 2, 1)
    # REALISTIC DECAY: Dose Rate kam hota hai
    initial_rate = 2.0
    decayed_rate = initial_rate * (0.5 ** (years_old / 5.27))
    st.write(f"Calibration pe Dose Rate: {initial_rate} Gy/min → Ab {years_old} saal baad: **{decayed_rate:.2f} Gy/min** (Decay ki wajah se kam)")
    beams = st.selectbox("Beams", ["2 Beams - Lat + Lat", "1 Beam - Direct", "3 Beams"])
    dose_c = st.slider("Total Dose (Gy)", 30, 70, 60, 5)
    fx = st.slider("Fractions", 10, 35, 30, 1)
    dose_per_fx = round(dose_c / fx, 2)
    st.write(f"Dose: {dose_c} Gy / {fx} Fx = {dose_per_fx} Gy per Fx")
    dose_rate = st.slider("Current Dose Rate (Gy/min) - Decay ke baad", 0.5, 2.0, round(decayed_rate, 2), 0.05)
    time_min = round(dose_per_fx / dose_rate, 2)
    st.success(f"Manual Time Calc: {dose_per_fx} Gy / {dose_rate} Gy/min = **{time_min} min per Fx**")
    st.caption(f"Source purana hoga to Time zyada lagega - Yehi Co-60 ka asal physics hai.")
    if st.button("🟢 SOURCE ON", use_container_width=True):
        st.error(f"SOURCE ON - Co-60 - {beams} - {time_min} min - Treatment Chal Rahi Hai - SSD 80 cm")
    if st.button("SOURCE OFF", use_container_width=True):
        st.info("Source OFF - Source Wapas Shield Me")

st.markdown("---")
st.caption("Virtual RT Mirror - Realistic | CT Sim → TPS → LINAC / Cobalt-60 | SSD LINAC 100 cm, Cobalt 80 cm")
