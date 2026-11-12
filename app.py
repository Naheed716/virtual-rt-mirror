import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math

st.set_page_config(page_title="Virtual RT Mirror", layout="centered", initial_sidebar_state="collapsed")

# ---------- BEAUTIFUL CSS ----------
st.markdown("""
<style>
.main { background-color: #F8F9FA; }
.big-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 15px; text-align: center; }
.small-card { background: white; padding: 12px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid #667eea; }
.stButton>button { border-radius: 12px !important; font-weight: bold !important; height: 48px !important; font-size: 16px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-card"><h2>🏥 Virtual RT Mirror</h2><p>Mobile Only | No Hardware | Radiotherapy Department</p></div>', unsafe_allow_html=True)
st.caption("CT Sim → TPS → LINAC / Cobalt-60 | Realistic Simulation")

# ---------- PATIENTS ----------
PATIENTS = {
    "NECK-01": {"site": "Head & Neck", "oar": "Cord / Parotid", "limit": 45, "mask": True, "pos": "Supine", "w": 7, "h": 9, "gtv": (0.5, 1.0), "oar_pos": (0, -2.0), "dose": 70, "fx": 35, "color": "#FF6B6B"},
    "BREAST-01": {"site": "Breast - Left", "oar": "Heart / Lung", "limit": 20, "mask": False, "pos": "Supine", "w": 11, "h": 8, "gtv": (-2.5, 0.5), "oar_pos": (1.5, -1.0), "dose": 50, "fx": 25, "color": "#FF9FF3"},
    "BRAIN-01": {"site": "Brain", "oar": "Brainstem / Optic", "limit": 54, "mask": True, "pos": "Supine", "w": 8, "h": 8.5, "gtv": (0.5, 0.5), "oar_pos": (0, -1.5), "dose": 60, "fx": 30, "color": "#54A0FF"},
    "PELVIS-01": {"site": "Pelvis", "oar": "Bladder / Rectum", "limit": 65, "mask": False, "pos": "Supine", "w": 11, "h": 9.5, "gtv": (0, 0.5), "oar_pos": (0, -2.2), "dose": 50, "fx": 25, "color": "#1DD1A1"},
}

patient = st.selectbox("👤 Patient Select Karo", list(PATIENTS.keys()))
p = PATIENTS[patient]

# Patient Card
col1, col2, col3 = st.columns(3)
with col1: st.markdown(f'<div class="small-card">📍 Site<br><b>{p["site"]}</b></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="small-card">🛡️ OAR<br><b>{p["oar"]}</b></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="small-card">🎯 Dose<br><b>{p["dose"]} Gy / {p["fx"]} Fx</b></div>', unsafe_allow_html=True)

position = st.selectbox("Position", ["Supine", "Prone"], index=0)
mask = st.checkbox(f"Mask / Immobilization {'(Required)' if p['mask'] else '(Not Used)'}", value=p["mask"])
if p["mask"] and not mask:
    st.warning("⚠️ Is patient ke liye Mask ON hona chahiye")

mirror = st.radio("Mirror Select Karo", ["A - CT Sim", "B - TPS", "C - LINAC", "D - Cobalt-60"], horizontal=True)

# Progress Bar - Workflow
steps = {"A - CT Sim": 25, "B - TPS": 50, "C - LINAC": 75, "D - Cobalt-60": 100}
st.progress(steps[mirror])
st.caption(f"Workflow: CT Sim → TPS → LINAC / Cobalt | Abhi: {mirror}")

# ================= A - CT SIM =================
if mirror == "A - CT Sim":
    st.subheader("🖥️ A - CT Sim Mirror")
    slice_no = st.slider("CT Slice Number", 1, 20, 10)
    if st.button("📸 SCAN", use_container_width=True):
        st.success(f"✅ CT Scan Ho Gaya - Slice {slice_no}/20 - {p['site']}")
        fig, ax = plt.subplots(figsize=(5, 5))
        fig.patch.set_facecolor('white'); ax.set_facecolor('#F1F2F6')
        ax.add_patch(patches.Ellipse((0, 0), p["w"], p["h"], facecolor="#E8E8E8", edgecolor="black", linewidth=1.5))
        # PTV Ring - NEW
        gtv_r = 1.2 if 8 <= slice_no <= 12 else 0.7
        ax.add_patch(patches.Circle(p["gtv"], gtv_r+0.6, facecolor="none", edgecolor="orange", linewidth=2, linestyle="--"))
        ax.text(p["gtv"][0], p["gtv"][1]+gtv_r+0.9, "PTV", ha="center", fontsize=8, color="orange", fontweight="bold")
        ax.add_patch(patches.Circle(p["gtv"], gtv_r, facecolor="red", alpha=0.9))
        ax.text(p["gtv"][0], p["gtv"][1], "GTV", ha="center", va="center", fontsize=9, fontweight="bold", color="white")
        ax.add_patch(patches.Circle(p["oar_pos"], 0.7, facecolor="yellow", edgecolor="black", linewidth=1.2))
        ax.text(p["oar_pos"][0], p["oar_pos"][1], p["oar"].split("/")[0], ha="center", va="center", fontsize=7, fontweight="bold")
        if patient == "BREAST-01":
            ax.add_patch(patches.Ellipse((2.8, 0.5), 3, 3.5, facecolor="none", edgecolor="gray", linestyle="--"))
            ax.add_patch(patches.Circle((1.5, -1), 0.5, facecolor="#FF6B81", alpha=0.6))
            ax.text(1.5, -1, "Heart", ha="center", va="center", fontsize=6)
        ax.set_xlim(-7, 7); ax.set_ylim(-7, 7); ax.set_aspect("equal")
        ax.set_title(f"CT - {patient} - Slice {slice_no} - {p['site']}", fontweight="bold")
        ax.grid(True, alpha=0.2)
        st.pyplot(fig)
        st.markdown(f"🔴 **GTV** | 🟠 **PTV Ring** | 🟡 **{p['oar']}**")
        if st.button("Send to TPS →", use_container_width=True):
            st.info("CT TPS ko Send Ho Gaya - Ab B - TPS kholo")
    else:
        st.info("Pehle SCAN dabao")

# ================= B - TPS =================
elif mirror == "B - TPS":
    st.subheader("📊 B - TPS Mirror")
    dose = st.slider("Prescription Dose (Gy)", 30, 70, p["dose"], 5)
    beam_type = st.selectbox("Beam Technique", ["VMAT - 2 Arcs", "3D-CRT - 3 Fields", "IMRT - 5 Fields"])
    tech = {"VMAT - 2 Arcs": 0.38, "IMRT - 5 Fields": 0.45, "3D-CRT - 3 Fields": 0.58}[beam_type]
    oar_dose = round(p["limit"] * tech, 1)
    ptv_cover = 95 if dose <= 60 else 93

    # Dose Wash Image - NEW VISUAL
    fig0, ax0 = plt.subplots(figsize=(5, 3))
    ax0.add_patch(patches.Ellipse((0, 0), p["w"], p["h"], facecolor="#E8E8E8", edgecolor="black"))
    # Dose wash circles - dose zyada to bara/ghera
    alpha = 0.3 + (dose-30)/40 * 0.5
    col = "#FFEB3B" if dose <= 40 else "#FF9800" if dose <= 55 else "#F44336"
    ax0.add_patch(patches.Circle(p["gtv"], 2.5, facecolor=col, alpha=alpha))
    ax0.add_patch(patches.Circle(p["gtv"], 1.5, facecolor=col, alpha=alpha+0.2))
    ax0.add_patch(patches.Circle(p["gtv"], 0.8, facecolor="red", alpha=0.9))
    ax0.text(p["gtv"][0], p["gtv"][1], f"{dose} Gy", ha="center", va="center", fontsize=9, fontweight="bold", color="white")
    ax0.add_patch(patches.Circle(p["oar_pos"], 0.6, facecolor="yellow", edgecolor="black"))
    ax0.set_xlim(-7, 7); ax0.set_ylim(-7, 7); ax0.set_aspect("equal"); ax0.set_title(f"Dose Wash - {dose} Gy - {beam_type}")
    ax0.axis("off")
    st.pyplot(fig0)

    if oar_dose < p["limit"]:
        st.success(f"✅ PTV {ptv_cover}% PASS | {p['oar']} = {oar_dose} Gy < {p['limit']} Gy PASS")
    else:
        st.error("❌ Plan FAIL - Technique badlo")

    fig2, ax2 = plt.subplots(figsize=(5, 3.5))
    x = np.linspace(0, 80, 200)
    ax2.plot(x, 100/(1+np.exp((x-dose)/3)), color="red", linewidth=3, label=f"PTV - {dose} Gy")
    ax2.plot(x, 100/(1+np.exp((x-oar_dose)/4)), color="blue", linewidth=3, label=f"{p['oar']} - {oar_dose} Gy")
    ax2.fill_between(x, 100/(1+np.exp((x-dose)/3)), alpha=0.15, color="red")
    ax2.axvline(dose, color="red", linestyle="--", alpha=0.4)
    ax2.axvline(p["limit"], color="blue", linestyle="--", alpha=0.4)
    ax2.set_xlim(0, 80); ax2.set_ylim(0, 105)
    ax2.set_xlabel("Dose (Gy)"); ax2.set_ylabel("Volume (%)")
    ax2.set_title(f"DVH - {patient} - {beam_type}", fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.4); ax2.legend()
    st.pyplot(fig2)
    if st.button("✅ APPROVE", use_container_width=True):
        st.balloons()
        st.success("Plan APPROVED - Ab C - LINAC kholo")

# ================= C - LINAC =================
elif mirror == "C - LINAC":
    st.subheader("⚡ C - LINAC Mirror")
    gantry = st.slider("Gantry Angle", 0, 360, 90, 5)
    coll = st.slider("Field Size (cm)", 0, 20, 10, 1)
    c1, c2, c3 = st.columns(3)
    with c1: cx = st.slider("Couch X", -5, 5, 0)
    with c2: cy = st.slider("Couch Y", -5, 5, 0)
    with c3: cz = st.slider("Couch Z", -5, 5, 0)
    st.write(f"Gantry: {gantry}° | Field: {coll}x{coll} cm | Couch: {cx},{cy},{cz} | SSD 100 cm | 6 MV")
    cbct = st.checkbox("CBCT Matched", value=True)
    if not cbct: st.warning("CBCT NOT Matched - Beam ON nahi hogi")

    b1, b2 = st.columns(2)
    with b1: beam_on = st.button("🔴 BEAM ON", use_container_width=True)
    with b2: beam_off = st.button("BEAM OFF", use_container_width=True)
    if beam_on and not cbct:
        st.error("Beam ON nahi ho sakti - CBCT Match nahi hai!")
    elif beam_on:
        st.error(f"BEAM ON - Gantry {gantry}° - Field {coll}x{coll} cm")
        # LINAC Machine Drawing - NEW
        fig, ax = plt.subplots(figsize=(5, 5))
        fig.patch.set_facecolor('white')
        # Room
        ax.add_patch(patches.Rectangle((-12, -12), 24, 24, facecolor="#F1F2F6", edgecolor="gray"))
        # Couch
        ax.add_patch(patches.Rectangle((-6, -1), 12, 2, facecolor="#57606F", edgecolor="black"))
        ax.text(0, 0, "COUCH + PATIENT", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        # Patient
        ax.add_patch(patches.Ellipse((0, 0), 5, 2.5, facecolor=p["color"], alpha=0.7))
        # Field
        ax.add_patch(patches.Rectangle((-coll/2, -coll/2), coll, coll, facecolor="#FFF9C4", edgecolor="#FFD700", linewidth=2))
        # Gantry - ghoomta hua
        ang = math.radians(gantry)
        dx = math.sin(ang)*10; dy = math.cos(ang)*10
        ax.plot([0, dx], [0, dy], color="black", linewidth=8, alpha=0.8)
        ax.plot([dx, dx*0.7], [dy, dy*0.7], color="red", linewidth=4)
        ax.add_patch(patches.Circle((dx, dy), 1.2, facecolor="#2F3542", edgecolor="black"))
        ax.text(dx, dy, "LINAC", ha="center", va="center", fontsize=6, color="white", fontweight="bold")
        ax.text(0, -10, f"Gantry {gantry}°", ha="center", fontsize=10, fontweight="bold")
        ax.set_xlim(-13, 13); ax.set_ylim(-13, 13); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(f"LINAC - Beam ON - Gantry {gantry}°", fontweight="bold")
        st.pyplot(fig)
    if beam_off: st.info("Beam OFF - Pause")
    if st.button("🛑 EMERGENCY STOP", use_container_width=True):
        st.error("EMERGENCY STOP - Sab Ruk Gaya")

# ================= D - COBALT =================
else:
    st.subheader("☢️ D - Cobalt-60 Mirror")
    st.markdown(f"**Source: Co-60 | Half-Life 5.27y | Energy 1.17 + 1.33 MeV | SSD 80 cm**")
    years = st.slider("Source Kitna Purana Hai? (Years)", 0, 10, 2, 1)
    init_rate = 2.0
    decayed = init_rate * (0.5 ** (years / 5.27))
    st.info(f"Calibration: {init_rate} Gy/min → Ab {years} saal baad: **{decayed:.2f} Gy/min** (Decay)")
    # Decay Graph - NEW
    figd, axd = plt.subplots(figsize=(5, 2.5))
    yy = np.linspace(0, 10, 50)
    rr = init_rate * (0.5 ** (yy / 5.27))
    axd.plot(yy, rr, color="green", linewidth=3)
    axd.plot([years], [decayed], marker="o", color="red", markersize=10)
    axd.set_xlabel("Years"); axd.set_ylabel("Dose Rate Gy/min")
    axd.set_title("Co-60 Decay Curve - Source Kam Hota Ja Raha Hai", fontsize=10)
    axd.grid(True, alpha=0.3)
    st.pyplot(figd)
    beams = st.selectbox("Beams", ["2 Beams - Lat + Lat", "1 Beam - Direct", "3 Beams"])
    dose_c = st.slider("Total Dose (Gy)", 30, 70, 60, 5)
    fx = st.slider("Fractions", 10, 35, 30, 1)
    per_fx = round(dose_c/fx, 2)
    rate = st.slider("Current Dose Rate (Gy/min)", 0.5, 2.0, round(decayed, 2), 0.05)
    t = round(per_fx/rate, 2)
    st.success(f"Manual Calc: {per_fx} Gy / {rate} Gy/min = **{t} min per Fx**")
    if st.button("🟢 SOURCE ON", use_container_width=True):
        st.error(f"SOURCE ON - Co-60 - {beams} - {t} min - SSD 80 cm")
    if st.button("SOURCE OFF", use_container_width=True):
        st.info("Source OFF - Shield Me Wapas")

st.markdown("---")
st.caption("Virtual RT Mirror - Visual Version | CT Sim → TPS → LINAC / Cobalt-60")
