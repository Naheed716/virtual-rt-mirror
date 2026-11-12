import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

st.set_page_config(page_title="Virtual RT Mirror - 4 Mirrors", layout="centered")
st.title("Virtual RT Mirror")
st.markdown("**Mobile Only | No Hardware | Radiotherapy Department**")

# --- Patient - Sab Mirrors ke liye same ---
st.subheader("Patient")
patient = st.selectbox("Patient Select Karo", ["NECK-01", "BREAST-01", "BRAIN-01", "PELVIS-01"])
position = st.selectbox("Position", ["Supine", "Prone"])
mask = st.checkbox("Mask ON", value=True)

# --- 4 Mirrors Tabs ---
mirror = st.radio("Mirror Select Karo", ["A - CT Sim", "B - TPS", "C - LINAC", "D - Cobalt-60"], horizontal=True)

# ================= A - CT SIM =================
if mirror == "A - CT Sim":
    st.subheader("A - CT Sim Mirror")
    st.write(f"Patient: **{patient}** | Position: **{position}** | Mask: **{'ON' if mask else 'OFF'}**")
    laser = st.checkbox("Laser - Tattoo OK", value=True)
    scan = st.button("📸 SCAN", use_container_width=True)
    if scan:
        st.success("CT Scan Ho Gaya - Slices Ready")
        # CT jesa circle
        fig, ax = plt.subplots(figsize=(4, 4))
        body = patches.Ellipse((0, 0), 8, 10, facecolor="#E0E0E0", edgecolor="black")
        ax.add_patch(body)
        tumor = patches.Circle((0.5, 1), 1.2, facecolor="red", alpha=0.8)
        ax.add_patch(tumor)
        cord = patches.Circle((0, -2), 0.7, facecolor="yellow", edgecolor="black")
        ax.add_patch(cord)
        ax.text(0.5, 1, "GTV", ha="center", va="center", fontsize=8, fontweight="bold", color="white")
        ax.text(0, -2, "Cord", ha="center", va="center", fontsize=7)
        ax.set_xlim(-6, 6)
        ax.set_ylim(-6, 6)
        ax.set_aspect("equal")
        ax.set_title(f"CT - {patient} - Axial Slice")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        st.write("GTV = Red | Cord = Yellow")
        if st.button("Send to TPS →", use_container_width=True):
            st.info("CT TPS ko Send Ho Gaya - Ab B - TPS Mirror kholo")
    else:
        st.info("Pehle SCAN dabao, phir CT aayega")

# ================= B - TPS =================
elif mirror == "B - TPS":
    st.subheader("B - TPS Mirror")
    st.write(f"Patient: **{patient}** - CT Aa Gaya Hai")
    dose = st.slider("Prescription Dose (Gy)", 30, 70, 50, 5)
    if patient == "BREAST-01":
        oar_name = "Heart / Lung"
        oar_limit = 20
    elif patient == "NECK-01":
        oar_name = "Cord / Parotid"
        oar_limit = 45
    elif patient == "BRAIN-01":
        oar_name = "Brainstem / Optic"
        oar_limit = 54
    else:
        oar_name = "Bladder / Rectum"
        oar_limit = 65

    beam_type = st.selectbox("Beam Technique", ["VMAT - 2 Arcs", "3D-CRT - 3 Fields", "IMRT - 5 Fields"])
    st.write(f"GTV = Red | Cord = Yellow | PTV = {dose} Gy | Beam = {beam_type}")

    # Dose Wash
    if dose <= 40:
        dc = "#FFEB3B"
        dl = "Low - Yellow"
    elif dose <= 55:
        dc = "#FF9800"
        dl = "Medium - Orange"
    else:
        dc = "#F44336"
        dl = "High - Red"
    st.markdown(f"**Dose Wash:** <span style='background:{dc}; padding:4px 10px; border-radius:6px'>{dl} - {dose} Gy</span>", unsafe_allow_html=True)

    oar_dose = round(oar_limit * 0.45, 1)
    st.success(f"PTV 95% PASS | {oar_name} = {oar_dose} Gy < {oar_limit} Gy PASS")

    # DVH
    fig2, ax2 = plt.subplots(figsize=(5, 3.5))
    x = np.linspace(0, 80, 200)
    ptv_y = 100 / (1 + np.exp((x - dose) / 3))
    oar_y = 100 / (1 + np.exp((x - oar_dose) / 4))
    ax2.plot(x, ptv_y, color="red", linewidth=2.5, label=f"PTV - {dose} Gy")
    ax2.plot(x, oar_y, color="blue", linewidth=2.5, label=f"{oar_name} - {oar_dose} Gy")
    ax2.set_xlim(0, 80)
    ax2.set_ylim(0, 105)
    ax2.set_xlabel("Dose (Gy)")
    ax2.set_ylabel("Volume (%)")
    ax2.set_title(f"DVH - {patient}")
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend()
    st.pyplot(fig2)

    if st.button("✅ APPROVE", use_container_width=True):
        st.success("Plan APPROVED - Ab C - LINAC Mirror kholo")

# ================= C - LINAC =================
elif mirror == "C - LINAC":
    st.subheader("C - LINAC Mirror")
    st.write(f"Patient: **{patient}** - Plan Approved")
    gantry = st.slider("Gantry Angle", 0, 360, 90, 5)
    coll = st.slider("Collimator / Field Size (cm)", 0, 20, 10, 1)
    couch_x = st.slider("Couch X", -5, 5, 0)
    couch_y = st.slider("Couch Y", -5, 5, 0)
    couch_z = st.slider("Couch Z", -5, 5, 0)
    st.write(f"Gantry: {gantry}° | Field: {coll} x {coll} cm | Couch: {couch_x}, {couch_y}, {couch_z}")
    cbct = st.checkbox("CBCT Matched", value=True)
    if cbct:
        st.success("CBCT Matched - Position Correct")

    col1, col2 = st.columns(2)
    with col1:
        beam_on = st.button("🔴 BEAM ON", use_container_width=True)
    with col2:
        beam_off = st.button("BEAM OFF", use_container_width=True)
    if beam_on:
        st.error(f"BEAM ON - Gantry {gantry}° - Field {coll} x {coll} cm - Beam Chal Rahi Hai")
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.add_patch(patches.Rectangle((-coll/2, -coll/2), coll, coll, facecolor="#FFF9C4", edgecolor="#FFD700", linewidth=2))
        ax.plot([0, 0], [8, coll/2], color="red", linewidth=3)
        ax.text(0, 0, f"{coll} x {coll} cm", ha="center", va="center", fontweight="bold")
        ax.set_xlim(-12, 12)
        ax.set_ylim(-12, 12)
        ax.set_aspect("equal")
        ax.set_title("Beam ON - Field Light")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    if beam_off:
        st.info("Beam OFF - Treatment Pause")
    if st.button("🛑 EMERGENCY STOP", use_container_width=True):
        st.error("EMERGENCY STOP - Beam Band, Sab Ruk Gaya")

# ================= D - COBALT-60 =================
else:
    st.subheader("D - Cobalt-60 Mirror")
    st.write(f"Patient: **{patient}**")
    st.write("Source: **Co-60** | Half-Life: **5.27 Years** | Energy: **1.25 MeV** | SSD: **80 cm**")
    beams = st.selectbox("Beams", ["2 Beams - Lat + Lat", "1 Beam - Direct", "3 Beams"])
    dose_c = st.slider("Total Dose (Gy)", 30, 70, 60, 5)
    fx = st.slider("Fractions", 10, 35, 30, 1)
    dose_per_fx = round(dose_c / fx, 2)
    st.write(f"Dose: {dose_c} Gy / {fx} Fx = {dose_per_fx} Gy per Fx")
    # Manual Time Calc
    dose_rate = st.slider("Dose Rate (Gy/min)", 0.5, 2.0, 1.0, 0.1)
    time_min = round(dose_per_fx / dose_rate, 2)
    st.write(f"Manual Time Calc: {dose_per_fx} Gy / {dose_rate} Gy/min = **{time_min} min per Fx**")
    if st.button("🟢 SOURCE ON", use_container_width=True):
        st.error(f"SOURCE ON - Co-60 - {beams} - {time_min} min - Treatment Chal Rahi Hai")
    if st.button("SOURCE OFF", use_container_width=True):
        st.info("Source OFF - Source Wapas Shield Me")

st.markdown("---")
st.caption("Virtual RT Mirror - Mobile Only | CT Sim → TPS → LINAC / Cobalt-60")
