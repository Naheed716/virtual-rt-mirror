import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math

st.set_page_config(page_title="Virtual RT Mirror", layout="centered")
st.markdown("""
<style>
.big-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 15px; text-align: center; }
.small-card { background: white; padding: 12px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid #667eea; }
.stButton>button { border-radius: 12px !important; font-weight: bold !important; height: 48px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-card"><h2>🏥 Virtual RT Mirror</h2><p>CT Sim → TPS → LINAC / Cobalt-60</p></div>', unsafe_allow_html=True)

PATIENTS = {
    "BREAST-LEFT": {"site": "Breast - Left", "oar": "Heart / Lung", "limit": 20, "mask": False, "dose": 50, "fx": 25, "w": 11, "h": 8, "gtv": (2.5, 0.5), "oar_pos": (-1.0, -1.0), "oar2": (0.5, -1.8), "color": "#FF9FF3", "note": "Left Breast = Image Right | Heart paas hai, is liye OAR Heart hai"},
    "BREAST-RIGHT": {"site": "Breast - Right", "oar": "Lung / Liver", "limit": 20, "mask": False, "dose": 50, "fx": 25, "w": 11, "h": 8, "gtv": (-2.5, 0.5), "oar_pos": (1.0, -1.0), "oar2": (0.5, -1.8), "color": "#F368E0", "note": "Right Breast = Image Left | Heart door hai, is liye OAR Lung hai"},
    "ESOPHAGUS-01": {"site": "Esophagus", "oar": "Lung / Heart / Cord", "limit": 45, "mask": False, "dose": 50, "fx": 25, "w": 9, "h": 9, "gtv": (0, 0.5), "oar_pos": (2.2, 0.5), "oar2": (-2.2, 0.5), "color": "#FF6B6B", "note": "Esophagus Center me | Dono taraf Lung, Peeche Cord, Aage Heart"},
    "NECK-01": {"site": "Head & Neck", "oar": "Cord / Parotid", "limit": 45, "mask": True, "dose": 70, "fx": 35, "w": 7, "h": 9, "gtv": (0.5, 1.0), "oar_pos": (0, -2.0), "oar2": (2.0, 1.0), "color": "#FF6B6B", "note": "Mask zaroori hai"},
    "BRAIN-01": {"site": "Brain", "oar": "Brainstem / Optic", "limit": 54, "mask": True, "dose": 60, "fx": 30, "w": 8, "h": 8.5, "gtv": (0.5, 0.5), "oar_pos": (0, -1.5), "oar2": (1.5, 1.5), "color": "#54A0FF", "note": "Mask zaroori hai"},
    "PELVIS-01": {"site": "Pelvis", "oar": "Bladder / Rectum", "limit": 65, "mask": False, "dose": 50, "fx": 25, "w": 11, "h": 9.5, "gtv": (0, 0.5), "oar_pos": (0, -2.2), "oar2": (0, 2.2), "color": "#1DD1A1", "note": "Bladder full, Rectum empty"},
}

patient = st.selectbox("👤 Patient Select Karo", list(PATIENTS.keys()))
p = PATIENTS[patient]
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="small-card">📍 Site<br><b>{p["site"]}</b></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="small-card">🛡️ OAR<br><b>{p["oar"]}</b></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="small-card">🎯 Dose<br><b>{p["dose"]} Gy / {p["fx"]} Fx</b></div>', unsafe_allow_html=True)
st.info(f"📝 Note: {p['note']}")
position = st.selectbox("Position", ["Supine - Seedha Letna", "Prone - Ulta Letna"], index=0)
if "Supine" in position:
    st.caption("Supine = Patient seedha leta hai, munh upar | Sab se zyada use hota hai")
else:
    st.caption("Prone = Patient ulta leta hai, munh neeche | Breast me Heart bachane ke liye")
mask = st.checkbox(f"Mask / Immobilization {'(Required)' if p['mask'] else '(Not Used)'}", value=p["mask"])
mirror = st.radio("Mirror Select Karo", ["A - CT Sim", "B - TPS", "C - LINAC", "D - Cobalt-60"], horizontal=True)

# ================= A - CT SIM - 3 SCANS =================
if mirror == "A - CT Sim":
    st.subheader("🖥️ A - CT Sim Mirror - 3 Scans")
    scan_type = st.radio("Scan Type Select Karo", ["1 - Plain Scan", "2 - Contrast Scan", "3 - Post-Contrast Scan"], horizontal=True)
    slice_no = st.slider("CT Slice Number", 1, 20, 10)
    if "Plain" in scan_type:
        bg = "#F1F2F6"; gtv_col = "#B2BEC3"; gtv_alpha = 0.6; desc = "Plain Scan: Bina Contrast ke. Sirf Anatomy dikhti hai. Tumor halka dikhta hai."
        enh = "No Enhancement"
    elif "Post" not in scan_type:
        bg = "#FFEAA7"; gtv_col = "#E17055"; gtv_alpha = 0.9; desc = "Contrast Scan: Contrast inject karne ke baad. Tumor bright ho jata hai, Vessels dikhte hain. Tumor ki sahi boundary isi me banti hai."
        enh = "Bright Enhancement"
    else:
        bg = "#FDCB6E"; gtv_col = "#D63031"; gtv_alpha = 0.8; desc = "Post-Contrast Scan: Contrast ke 60-90 sec baad. Tumor ka Washout dekhte hain. OAR aur Tumor ka farq clear hota hai."
        enh = "Washout Phase"
    st.write(desc)
    if st.button("📸 SCAN", use_container_width=True):
        st.success(f"✅ {scan_type} Ho Gaya - Slice {slice_no}/20 - {p['site']} - {enh}")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_facecolor(bg)
        ax.add_patch(patches.Ellipse((0, 0), p["w"], p["h"], facecolor="#E8E8E8", edgecolor="black", linewidth=1.5))
        gtv_r = 1.2 if 8 <= slice_no <= 12 else 0.7
        ax.add_patch(patches.Circle(p["gtv"], gtv_r+0.6, facecolor="none", edgecolor="orange", linewidth=2, linestyle="--"))
        ax.text(p["gtv"][0], p["gtv"][1]+gtv_r+0.9, "PTV", ha="center", fontsize=8, color="orange", fontweight="bold")
        ax.add_patch(patches.Circle(p["gtv"], gtv_r, facecolor=gtv_col, alpha=gtv_alpha, edgecolor="black"))
        ax.text(p["gtv"][0], p["gtv"][1], "GTV", ha="center", va="center", fontsize=9, fontweight="bold", color="white")
        ax.add_patch(patches.Circle(p["oar_pos"], 0.7, facecolor="yellow", edgecolor="black"))
        ax.text(p["oar_pos"][0], p["oar_pos"][1], p["oar"].split("/")[0], ha="center", va="center", fontsize=7, fontweight="bold")
        ax.add_patch(patches.Circle(p["oar2"], 0.7, facecolor="lightblue", edgecolor="black"))
        ax.text(p["oar2"][0], p["oar2"][1], "OAR-2", ha="center", va="center", fontsize=6, fontweight="bold")
        ax.text(0, 6.5, "Patient's Left -> Image Right", ha="center", fontsize=7, color="blue", fontweight="bold")
        ax.text(0, -6.5, f"{scan_type} | {enh}", ha="center", fontsize=7, fontweight="bold", bbox=dict(facecolor="white", edgecolor="black"))
        ax.set_xlim(-7, 7); ax.set_ylim(-7, 7); ax.set_aspect("equal")
        ax.set_title(f"CT - {patient} - {scan_type} - Slice {slice_no}", fontweight="bold"); ax.grid(True, alpha=0.2)
        st.pyplot(fig)
        st.markdown(f"🔴 **GTV** | 🟠 **PTV Ring** | 🟡 **{p['oar']}**")
        st.table({"Scan": ["Plain", "Contrast", "Post-Contrast"], "Kya Dikhta Hai": ["Anatomy Only", "Tumor Bright + Vessels", "Washout + OAR Clear"], "GTV Contour": ["Mushkil", "Best - Isi pe banta hai", "Confirm karne ke liye"]})

# ================= B - TPS =================
elif mirror == "B - TPS":
    st.subheader("📊 B - TPS Mirror")
    dose = st.slider("Prescription Dose (Gy)", 30, 70, p["dose"], 5)
    beam_type = st.selectbox("Beam Technique", ["VMAT - 2 Arcs", "3D-CRT - 3 Fields", "IMRT - 5 Fields"])
    tech = {"VMAT - 2 Arcs": 0.38, "IMRT - 5 Fields": 0.45, "3D-CRT - 3 Fields": 0.58}[beam_type]
    oar_dose = round(p["limit"] * tech, 1)
    fig0, ax0 = plt.subplots(figsize=(5, 3))
    ax0.add_patch(patches.Ellipse((0, 0), p["w"], p["h"], facecolor="#E8E8E8", edgecolor="black"))
    col = "#FFEB3B" if dose <= 40 else "#FF9800" if dose <= 55 else "#F44336"
    ax0.add_patch(patches.Circle(p["gtv"], 2.5, facecolor=col, alpha=0.4))
    ax0.add_patch(patches.Circle(p["gtv"], 0.8, facecolor="red", alpha=0.9))
    ax0.text(p["gtv"][0], p["gtv"][1], f"{dose} Gy", ha="center", va="center", fontsize=9, fontweight="bold", color="white")
    ax0.set_xlim(-7, 7); ax0.set_ylim(-7, 7); ax0.set_aspect("equal"); ax0.set_title(f"Dose Wash - {dose} Gy - {beam_type}"); ax0.axis("off")
    st.pyplot(fig0)
    if oar_dose < p["limit"]:
        st.success(f"✅ PTV 95% PASS | {p['oar']} = {oar_dose} Gy < {p['limit']} Gy PASS")
    else:
        st.error(f"❌ OAR FAIL - {oar_dose} Gy > {p['limit']} Gy")
    fig2, ax2 = plt.subplots(figsize=(5, 3.5))
    x = np.linspace(0, 80, 200)
    ax2.plot(x, 100/(1+np.exp((x-dose)/3)), color="red", linewidth=3, label=f"PTV - {dose} Gy")
    ax2.plot(x, 100/(1+np.exp((x-oar_dose)/4)), color="blue", linewidth=3, label=f"{p['oar']} - {oar_dose} Gy")
    ax2.set_xlim(0, 80); ax2.set_ylim(0, 105); ax2.set_xlabel("Dose (Gy)"); ax2.set_ylabel("Volume (%)")
    ax2.set_title(f"DVH - {patient} - {beam_type}", fontweight="bold"); ax2.grid(True, linestyle="--", alpha=0.4); ax2.legend()
    st.pyplot(fig2)
    if st.button("✅ APPROVE", use_container_width=True):
        st.balloons(); st.success("Plan APPROVED")

# ================= C - LINAC - X1 X2 Y1 Y2 =================
elif mirror == "C - LINAC":
    st.subheader("⚡ C - LINAC Mirror - Real Structure")
    gantry = st.slider("Gantry Angle", 0, 360, 90, 5)
    st.markdown("### 🔲 Collimator Jaws - Field Setting")
    st.caption("X1 = Left Jaw | X2 = Right Jaw | Y1 = Upper Jaw | Y2 = Lower Jaw | Field X = X1+X2 | Field Y = Y1+Y2")
    j1, j2 = st.columns(2)
    with j1:
        x1 = st.slider("X1 - Left Jaw (cm)", 0, 10, 5, 1)
        y1 = st.slider("Y1 - Upper Jaw (cm)", 0, 10, 5, 1)
    with j2:
        x2 = st.slider("X2 - Right Jaw (cm)", 0, 10, 5, 1)
        y2 = st.slider("Y2 - Lower Jaw (cm)", 0, 10, 5, 1)
    field_x = x1 + x2
    field_y = y1 + y2
    shift_x = (x2 - x1) / 2
    shift_y = (y2 - y1) / 2
    if x1 == x2 and y1 == y2:
        sym = "✅ Symmetric Field - Center pe hai"
    else:
        sym = f"⚠️ Asymmetric Field - Field {shift_x:.1f} cm X aur {shift_y:.1f} cm Y pe Shift hai"
    st.info(f"**Field Size: {field_x} x {field_y} cm** | X1 {x1} + X2 {x2} = {field_x} | Y1 {y1} + Y2 {y2} = {field_y} | {sym}")
    cx = st.slider("Couch X", -5, 5, 0); cy = st.slider("Couch Y", -5, 5, 0); cz = st.slider("Couch Z", -5, 5, 0)
    st.write(f"Gantry: {gantry}° | Field: {field_x}x{field_y} cm | Couch: {cx},{cy},{cz} | SSD 100 cm | Energy 6 MV")
    cbct = st.checkbox("CBCT Matched", value=True)
    if not cbct: st.warning("CBCT NOT Matched - Beam ON nahi hogi")
    b1, b2 = st.columns(2)
    with b1: beam_on = st.button("🔴 BEAM ON", use_container_width=True)
    with b2: beam_off = st.button("BEAM OFF", use_container_width=True)
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor('white'); ax.set_facecolor('#F8F9FA')
    ax.add_patch(patches.Rectangle((-13, -13), 26, 26, facecolor="#F1F2F6", edgecolor="gray"))
    ax.text(-12, 12, "TREATMENT ROOM", fontsize=8, color="gray", fontweight="bold")
    ax.add_patch(patches.Rectangle((-2, -12), 4, 6, facecolor="#2F3542", edgecolor="black"))
    ax.text(0, -9, "GANTRY\nSTAND", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
    ang = math.radians(gantry)
    dx = math.sin(ang)*10; dy = math.cos(ang)*10
    ax.plot([0, dx], [-6, dy], color="#57606F", linewidth=10, solid_capstyle='round')
    ax.add_patch(patches.FancyBboxPatch((dx-2.2, dy-1.5), 4.4, 3, boxstyle="round,pad=0.2", facecolor="#2F3542", edgecolor="black", linewidth=1.5))
    ax.text(dx, dy+0.5, "LINAC HEAD", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
    ax.text(dx, dy-0.5, "Target + MLC", ha="center", va="center", fontsize=6, color="#FFD700")
    # Jaws Drawing - X1 X2 ke hisab se
    jaw_w = max(field_x / 2.5, 0.8)
    ax.add_patch(patches.Rectangle((dx-jaw_w/2, dy-2.5), jaw_w, 1.0, facecolor="#FFD700", edgecolor="black"))
    ax.text(dx, dy-2.0, f"Jaws {field_x}x{field_y}", ha="center", va="center", fontsize=6, fontweight="bold")
    ax.text(dx+3.5, dy-2.0, f"X1 {x1} | X2 {x2}\nY1 {y1} | Y2 {y2}", fontsize=6, fontweight="bold", bbox=dict(facecolor="white", edgecolor="black"))
    ax.add_patch(patches.Rectangle((-6, -1.5), 12, 2, facecolor="#57606F", edgecolor="black"))
    ax.text(0, -0.5, "COUCH", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
    ax.add_patch(patches.Ellipse((cx, cy), 5, 2.5, facecolor=p["color"], alpha=0.8, edgecolor="black"))
    ax.text(cx, cy, f"{patient}", ha="center", va="center", fontsize=7, fontweight="bold")
    # Field on Patient - Shift ke saath
    ax.add_patch(patches.Rectangle((shift_x - field_x/4, shift_y - field_y/4), field_x/2, field_y/2, facecolor="none", edgecolor="red", linewidth=2, linestyle="--"))
    ax.plot([0], [0], marker="+", color="red", markersize=18, markeredgewidth=2.5)
    ax.text(1.2, 0.8, "✚ ISOCENTER\n(Tumor Center)", fontsize=7, color="red", fontweight="bold")
    if beam_on and cbct:
        ax.plot([dx, 0], [dy-2.5, 0], color="red", linewidth=4, alpha=0.8)
        ax.plot([dx, 0], [dy-2.5, 0], color="yellow", linewidth=1.5, alpha=0.9)
        ax.text(6, 6, "🔴 BEAM ON", fontsize=10, color="red", fontweight="bold", bbox=dict(facecolor="white", edgecolor="red"))
    ax.plot([dx, 0], [dy-2.5, 0], color="blue", linewidth=1, linestyle="--", alpha=0.5)
    ax.text(dx/2+1, (dy-2.5)/2, "SSD 100 cm", fontsize=7, color="blue")
    ax.add_patch(patches.Rectangle((8, -11), 3, 2, facecolor="#A4B0BE", edgecolor="black"))
    ax.text(9.5, -10, "CBCT", ha="center", va="center", fontsize=7, fontweight="bold")
    ax.plot([-11, -6], [0, 0], color="green", linewidth=1, linestyle=":")
    ax.text(-11, 0.8, "LASER", fontsize=6, color="green", fontweight="bold")
    ax.set_xlim(-13, 13); ax.set_ylim(-13, 13); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"LINAC - Gantry {gantry}° - Field {field_x}x{field_y} cm", fontweight="bold")
    st.pyplot(fig)
    st.caption("X1 Left | X2 Right | Y1 Upper | Y2 Lower | MLC = Field ki shape | Isocenter = Tumor center | SSD 100 cm | CBCT = Position check")
    if beam_on and not cbct: st.error("Beam ON nahi ho sakti - CBCT Match nahi hai!")
    elif beam_on: st.error(f"BEAM ON - Gantry {gantry}° - Field {field_x}x{field_y} cm")
    if beam_off: st.info("Beam OFF - Pause")
    if st.button("🛑 EMERGENCY STOP", use_container_width=True): st.error("EMERGENCY STOP")

# ================= D - COBALT - X1 X2 Y1 Y2 =================
else:
    st.subheader("☢️ D - Cobalt-60 Mirror - Real Structure")
    st.write("**Source: Co-60 | Half-Life 5.27y | Energy 1.17 + 1.33 MeV | SSD 80 cm**")
    st.markdown("### 🔲 Collimator Jaws - Field Setting (Cobalt me MLC nahi hota)")
    st.caption("X1 = Left Jaw | X2 = Right Jaw | Y1 = Upper Jaw | Y2 = Lower Jaw | Field X = X1+X2 | Field Y = Y1+Y2")
    cj1, cj2 = st.columns(2)
    with cj1:
        cx1 = st.slider("X1 - Left Jaw (cm)", 0, 10, 5, 1, key="c_x1")
        cy1 = st.slider("Y1 - Upper Jaw (cm)", 0, 10, 5, 1, key="c_y1")
    with cj2:
        cx2 = st.slider("X2 - Right Jaw (cm)", 0, 10, 5, 1, key="c_x2")
        cy2 = st.slider("Y2 - Lower Jaw (cm)", 0, 10, 5, 1, key="c_y2")
    c_field_x = cx1 + cx2
    c_field_y = cy1 + cy2
    c_shift_x = (cx2 - cx1) / 2
    c_shift_y = (cy2 - cy1) / 2
    if cx1 == cx2 and cy1 == cy2:
        c_sym = "✅ Symmetric Field"
    else:
        c_sym = f"⚠️ Asymmetric Field - Shift {c_shift_x:.1f}, {c_shift_y:.1f} cm"
    st.info(f"**Field Size: {c_field_x} x {c_field_y} cm** | X1 {cx1} + X2 {cx2} = {c_field_x} | Y1 {cy1} + Y2 {cy2} = {c_field_y} | {c_sym}")
    st.write("Field ko Light Field se check karte hain, phir Trimmer Bars se shape dete hain.")
    years = st.slider("Source Kitna Purana Hai? (Years)", 0, 10, 2, 1)
    init_rate = 2.0
    decayed = init_rate * (0.5 ** (years / 5.27))
    st.info(f"Calibration: {init_rate} Gy/min → Ab {years} saal baad: **{decayed:.2f} Gy/min** (Decay)")
    beams = st.selectbox("Beams", ["2 Beams - Lat + Lat", "1 Beam - Direct", "3 Beams"])
    dose_c = st.slider("Total Dose (Gy)", 30, 70, 60, 5)
    fx = st.slider("Fractions", 10, 35, 30, 1)
    per_fx = round(dose_c/fx, 2)
    rate = st.slider("Current Dose Rate (Gy/min)", 0.5, 2.0, round(decayed, 2), 0.05)
    t = round(per_fx/rate, 2)
    st.success(f"Manual Calc: {per_fx} Gy / {rate} Gy/min = **{t} min per Fx** | Field {c_field_x} x {c_field_y} cm")
    s1, s2 = st.columns(2)
    with s1: source_on = st.button("🟢 SOURCE ON", use_container_width=True)
    with s2: source_off = st.button("SOURCE OFF", use_container_width=True)
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    fig2.patch.set_facecolor('white'); ax2.set_facecolor('#F8F9FA')
    ax2.add_patch(patches.Rectangle((-13, -13), 26, 26, facecolor="#FFF3E0", edgecolor="gray"))
    ax2.text(-12, 12, "COBALT ROOM - THICK WALLS", fontsize=8, color="gray", fontweight="bold")
    ax2.add_patch(patches.FancyBboxPatch((-3, 5), 6, 5, boxstyle="round,pad=0.3", facecolor="#2F3542", edgecolor="black", linewidth=2))
    ax2.text(0, 9, "SOURCE HEAD", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    ax2.text(0, 8, "(Lead Shield)", ha="center", va="center", fontsize=6, color="#FFD700")
    col_src = "red" if source_on else "gray"
    ax2.add_patch(patches.Circle((0, 6.5), 0.9, facecolor=col_src, edgecolor="black", linewidth=1.5))
    ax2.text(0, 6.5, "Co-60", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
    ax2.text(4.5, 6.5, "← SOURCE\nPellets", fontsize=7, fontweight="bold", color="black")
    # Cobalt Collimator - Jaws ke hisab se width
    c_jaw_w = max(c_field_x / 2.5, 0.8)
    ax2.add_patch(patches.Rectangle((-c_jaw_w/2, 3.5), c_jaw_w, 1.5, facecolor="#FFD700", edgecolor="black"))
    ax2.text(0, 4.2, f"COLLIMATOR {c_field_x}x{c_field_y}", ha="center", va="center", fontsize=6, fontweight="bold")
    ax2.text(5.5, 4.2, f"X1 {cx1} | X2 {cx2}\nY1 {cy1} | Y2 {cy2}", fontsize=7, color="black", bbox=dict(facecolor="white", edgecolor="black"))
    if source_on:
        ax2.plot([0, 0], [3.5, 0], color="red", linewidth=4, alpha=0.8)
        ax2.plot([0, 0], [3.5, 0], color="yellow", linewidth=1.5)
        ax2.text(6, 6, "🟢 SOURCE ON", fontsize=10, color="red", fontweight="bold", bbox=dict(facecolor="white", edgecolor="red"))
    else:
        ax2.plot([0, 0], [3.5, 0], color="gray", linewidth=1, linestyle="--")
        ax2.text(6, 6, "SOURCE OFF\n(Shield Me)", fontsize=8, color="gray", fontweight="bold", bbox=dict(facecolor="white", edgecolor="gray"))
    ax2.add_patch(patches.Rectangle((-6, -1.5), 12, 2, facecolor="#57606F", edgecolor="black"))
    ax2.text(0, -0.5, "COUCH", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
    ax2.add_patch(patches.Ellipse((0, 0), 5, 2.5, facecolor=p["color"], alpha=0.8, edgecolor="black"))
    ax2.text(0, 0, f"{patient}", ha="center", va="center", fontsize=7, fontweight="bold")
    ax2.add_patch(patches.Rectangle((c_shift_x - c_field_x/4, c_shift_y - c_field_y/4), c_field_x/2, c_field_y/2, facecolor="none", edgecolor="red", linewidth=2, linestyle="--"))
    ax2.plot([0], [0], marker="+", color="red", markersize=18, markeredgewidth=2.5)
    ax2.text(1.2, 0.8, "✚ ISOCENTER", fontsize=7, color="red", fontweight="bold")
    ax2.annotate("", xy=(-4, 3.5), xytext=(-4, 0), arrowprops=dict(arrowstyle="<->", color="blue"))
    ax2.text(-5.5, 1.7, "SSD\n80 cm", fontsize=7, color="blue", fontweight="bold", ha="center")
    ax2.text(0, -8, f"Decay: {years} saal baad Rate {decayed:.2f} Gy/min - Time {t} min", ha="center", fontsize=8, fontweight="bold", bbox=dict(facecolor="white", edgecolor="green"))
    ax2.set_xlim(-13, 13); ax2.set_ylim(-13, 13); ax2.set_aspect("equal"); ax2.axis("off")
    ax2.set_title(f"Cobalt-60 - SSD 80 cm - {beams} - Field {c_field_x}x{c_field_y}", fontweight="bold")
    st.pyplot(fig2)
    st.caption("X1 Left | X2 Right | Y1 Upper | Y2 Lower | Cobalt me MLC nahi, sirf Jaws + Trimmer | SSD 80 cm | ON pe Source bahar, OFF pe wapas Shield me")
    if source_on: st.error(f"SOURCE ON - Co-60 - {beams} - {t} min - SSD 80 cm - Field {c_field_x}x{c_field_y}")
    if source_off: st.info("Source OFF - Source Wapas Shield Me")

st.markdown("---")
st.caption("Virtual RT Mirror | CT Sim → TPS → LINAC / Cobalt-60")
