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

st.markdown('<div class="big-card"><h2>🏥 Virtual RT Mirror</h2><p>CT Sim → TPS → LINAC / Cobalt-60</p><p><b>Part 1: Simulation | Part 2: Optics Behind It</b></p></div>', unsafe_allow_html=True)

# ================= PATIENTS - NO 01 =================
PATIENTS = {
    "BREAST-LEFT": {"site": "Breast - Left", "oar": "Heart / Lung", "limit": 20, "mask": False, "dose": 50, "fx": 25, "w": 11, "h": 8, "gtv": (2.5, 0.5), "oar_pos": (-1.0, -1.0), "oar2": (0.5, -1.8), "color": "#FF9FF3", "note": "Left Breast = Image Right | Heart paas hai, is liye OAR Heart hai", "devices": ["Breast Board", "Arm Rest", "Vac-Lok Bag"], "device_note": "Breast Board: Arm upar rakhta hai, Breast ko lift karta hai"},
    "BREAST-RIGHT": {"site": "Breast - Right", "oar": "Lung / Liver", "limit": 20, "mask": False, "dose": 50, "fx": 25, "w": 11, "h": 8, "gtv": (-2.5, 0.5), "oar_pos": (1.0, -1.0), "oar2": (0.5, -1.8), "color": "#F368E0", "note": "Right Breast = Image Left | Heart door hai, is liye OAR Lung hai", "devices": ["Breast Board", "Arm Rest", "Vac-Lok Bag"], "device_note": "Breast Board: Dono arms upar, chest stable"},
    "ESOPHAGUS": {"site": "Esophagus", "oar": "Lung / Heart / Cord", "limit": 45, "mask": False, "dose": 50, "fx": 25, "w": 9, "h": 9, "gtv": (0, 0.5), "oar_pos": (2.2, 0.5), "oar2": (-2.2, 0.5), "color": "#FF6B6B", "note": "Esophagus Center me | Dono taraf Lung, Peeche Cord, Aage Heart", "devices": ["Vac-Lok Bag", "Arm Rest", "Knee Sponge"], "device_note": "Vac-Lok: Body ko hilne nahi deta, same position har roz"},
    "HEAD & NECK": {"site": "Head & Neck", "oar": "Cord / Parotid", "limit": 45, "mask": True, "dose": 70, "fx": 35, "w": 7, "h": 9, "gtv": (0.5, 1.0), "oar_pos": (0, -2.0), "oar2": (2.0, 1.0), "color": "#FF6B6B", "note": "Head + Neck Combined | Mask zaroori hai | Tongue depressor bhi use hota hai", "devices": ["Thermoplastic Mask", "Head Rest", "Shoulder Puller", "Tongue Depressor"], "device_note": "Thermoplastic Mask: Garam karke face pe banaya jata hai, thanda hoke hard ho jata hai"},
    "BRAIN": {"site": "Brain", "oar": "Brainstem / Optic", "limit": 54, "mask": True, "dose": 60, "fx": 30, "w": 8, "h": 8.5, "gtv": (0.5, 0.5), "oar_pos": (0, -1.5), "oar2": (1.5, 1.5), "color": "#54A0FF", "note": "Mask zaroori hai", "devices": ["Thermoplastic Mask", "Head Rest", "Bite Block"], "device_note": "Mask + Head Rest: Head 1mm bhi hilna nahi chahiye"},
    "PELVIS": {"site": "Pelvis", "oar": "Bladder / Rectum", "limit": 65, "mask": False, "dose": 50, "fx": 25, "w": 11, "h": 9.5, "gtv": (0, 0.5), "oar_pos": (0, -2.2), "oar2": (0, 2.2), "color": "#1DD1A1", "note": "Bladder full, Rectum empty", "devices": ["Vac-Lok Bag", "Knee Sponge", "Foot Rest"], "device_note": "Knee Sponge: Legs ko same angle pe rakhta hai"},
    "ABDOMEN": {"site": "Abdomen", "oar": "Liver / Kidney / Bowel", "limit": 30, "mask": False, "dose": 45, "fx": 25, "w": 11, "h": 9, "gtv": (0, 0.5), "oar_pos": (2.5, 0.5), "oar2": (-2.5, -1.0), "color": "#FDCB6E", "note": "Abdomen Center me | Liver Right, Kidney dono taraf, Bowel aage", "devices": ["Vac-Lok Bag", "Arm Rest", "Belly Board"], "device_note": "Belly Board: Prone me belly ko neeche dabata hai taake Bowel door ho"},
    "CSI": {"site": "Cranio-Spinal (CSI)", "oar": "Heart / Lung / Kidney", "limit": 20, "mask": True, "dose": 36, "fx": 20, "w": 7, "h": 14, "gtv": (0, 4.0), "oar_pos": (2.0, -1.0), "oar2": (-2.0, -1.0), "color": "#FF6B6B", "note": "Brain + Full Spine | 3 Fields Join | Junction pe Overlap / Gap ka khatra | Mostly Bachon me Medulloblastoma", "devices": ["Thermoplastic Mask", "Vac-Lok Bag", "Prone Head Rest"], "device_note": "CSI me Prone position + Mask + Vac-Lok teeno zaroori hain"},
}

# ================= PART SELECT =================
part = st.radio("Select Part", ["🪞 PART 1: Virtual RT Mirror", "🔬 PART 2: Optics Behind It"], horizontal=True)

# ============================================================
# ================= PART 1 =================
# ============================================================
if "PART 1" in part:
    patient = st.selectbox("👤 Patient Select Karo", list(PATIENTS.keys()))
    p = PATIENTS[patient]
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="small-card">📍 Site<br><b>{p["site"]}</b></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="small-card">🛡️ OAR<br><b>{p["oar"]}</b></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="small-card">🎯 Dose<br><b>{p["dose"]} Gy / {p["fx"]} Fx</b></div>', unsafe_allow_html=True)
    st.info(f"📝 Note: {p['note']}")

    # ---- Mobilization Device + Little Picture ----
    st.markdown("### 🛏️ Mobilization Device")
    device = st.selectbox("Device Select Karo", p["devices"])
    st.caption(f"ℹ️ {p['device_note']} | Selected: {device}")
    # Little picture per patient + device
    fig_d, ax_d = plt.subplots(figsize=(5, 2.8))
    ax_d.set_facecolor("#F8F9FA")
    # Couch
    ax_d.add_patch(patches.Rectangle((-6, -1.2), 12, 1.0, facecolor="#57606F", edgecolor="black"))
    ax_d.text(0, -0.7, "COUCH", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
    # Body shape - CSI is long
    if patient == "CSI":
        ax_d.add_patch(patches.Ellipse((0, 1.5), 2.2, 4.5, facecolor=p["color"], alpha=0.8, edgecolor="black"))
        ax_d.add_patch(patches.Circle((0, 4.2), 1.0, facecolor=p["color"], alpha=0.9, edgecolor="black"))
        ax_d.text(0, 4.2, "BRAIN", ha="center", va="center", fontsize=6, fontweight="bold")
        ax_d.text(0, 1.5, "SPINE", ha="center", va="center", fontsize=6, fontweight="bold")
        ax_d.text(0, -2.2, "Prone + Mask + Vac-Lok", ha="center", fontsize=7, fontweight="bold", bbox=dict(facecolor="white", edgecolor="black"))
    elif "HEAD" in patient or patient == "BRAIN":
        ax_d.add_patch(patches.Circle((0, 1.5), 1.2, facecolor=p["color"], alpha=0.9, edgecolor="black"))
        ax_d.text(0, 1.5, "HEAD", ha="center", va="center", fontsize=7, fontweight="bold")
        # Mask lines
        ax_d.add_patch(patches.Rectangle((-1.4, 0.3), 2.8, 0.4, facecolor="white", edgecolor="red", hatch="///"))
        ax_d.text(0, 0.5, "MASK", ha="center", fontsize=6, color="red", fontweight="bold")
        ax_d.add_patch(patches.Rectangle((-1.5, -0.2), 3, 0.5, facecolor="#FDCB6E", edgecolor="black"))
        ax_d.text(0, 0.0, "HEAD REST", ha="center", fontsize=6, fontweight="bold")
        ax_d.text(0, -2.2, f"{device}", ha="center", fontsize=7, fontweight="bold", bbox=dict(facecolor="white", edgecolor="black"))
    elif "BREAST" in patient:
        ax_d.add_patch(patches.Ellipse((0, 1.2), 5, 2.5, facecolor=p["color"], alpha=0.8, edgecolor="black"))
        ax_d.text(0, 1.2, "CHEST", ha="center", va="center", fontsize=7, fontweight="bold")
        ax_d.add_patch(patches.Rectangle((-3, 2.4), 1.2, 1.0, facecolor="#54A0FF", edgecolor="black"))
        ax_d.add_patch(patches.Rectangle((1.8, 2.4), 1.2, 1.0, facecolor="#54A0FF", edgecolor="black"))
        ax_d.text(0, 3.0, "ARMS UP - Breast Board", ha="center", fontsize=6, fontweight="bold")
        ax_d.text(0, -2.2, f"{device}", ha="center", fontsize=7, fontweight="bold", bbox=dict(facecolor="white", edgecolor="black"))
    elif patient == "ABDOMEN":
        ax_d.add_patch(patches.Ellipse((0, 1.2), 5, 2.8, facecolor=p["color"], alpha=0.8, edgecolor="black"))
        ax_d.text(0, 1.2, "ABDOMEN", ha="center", va="center", fontsize=7, fontweight="bold")
        ax_d.add_patch(patches.Rectangle((-2.5, -0.2), 5, 0.4, facecolor="#1DD1A1", edgecolor="black"))
        ax_d.text(0, 0.0, "VAC-LOK / BELLY BOARD", ha="center", fontsize=6, fontweight="bold")
        ax_d.text(0, -2.2, f"{device}", ha="center", fontsize=7, fontweight="bold", bbox=dict(facecolor="white", edgecolor="black"))
    else:
        ax_d.add_patch(patches.Ellipse((0, 1.2), 5, 2.8, facecolor=p["color"], alpha=0.8, edgecolor="black"))
        ax_d.text(0, 1.2, f"{patient}", ha="center", va="center", fontsize=7, fontweight="bold")
        ax_d.add_patch(patches.Rectangle((-2.5, -0.2), 5, 0.4, facecolor="#1DD1A1", edgecolor="black"))
        ax_d.text(0, 0.0, f"{device}", ha="center", fontsize=6, fontweight="bold")
        ax_d.text(0, -2.2, f"{device} Applied", ha="center", fontsize=7, fontweight="bold", bbox=dict(facecolor="white", edgecolor="black"))
    ax_d.set_xlim(-6, 6); ax_d.set_ylim(-2.8, 4.5); ax_d.set_aspect("equal"); ax_d.axis("off")
    ax_d.set_title(f"Mobilization - {patient} - {device}", fontweight="bold", fontsize=9)
    st.pyplot(fig_d)

    position = st.selectbox("Position", ["Supine - Seedha Letna", "Prone - Ulta Letna"], index=0)
    if "Supine" in position:
        st.caption("Supine = Patient seedha leta hai, munh upar | Sab se zyada use hota hai")
    else:
        st.caption("Prone = Patient ulta leta hai, munh neeche | Breast me Heart bachane ke liye | CSI me Spine seedhi rakhne ke liye")
    mask = st.checkbox(f"Mask / Immobilization {'(Required)' if p['mask'] else '(Not Used)'}", value=p["mask"])
    mirror = st.radio("Mirror Select Karo", ["A - CT Sim", "B - TPS", "C - LINAC", "D - Cobalt-60"], horizontal=True)

    # ================= A - CT SIM =================
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
            # CSI me lambi body
            if patient == "CSI":
                ax.add_patch(patches.Ellipse((0, 0), 6, 12, facecolor="#E8E8E8", edgecolor="black", linewidth=1.5))
            else:
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
        # CSI special - 3 fields junction
        if patient == "CSI":
            st.warning("⚠️ CSI - 3 Fields: Brain + Upper Spine + Lower Spine - Junction pe dhyan do!")
            junction_gap = st.slider("Junction Gap / Overlap (cm)", -1.0, 1.0, 0.0, 0.1)
            if junction_gap == 0:
                st.success("✅ Perfect Junction - No Gap, No Overlap")
            elif junction_gap > 0:
                st.error(f"❌ Gap {junction_gap} cm - Cold Spot - Tumor ko dose nahi milegi!")
            else:
                st.error(f"❌ Overlap {abs(junction_gap)} cm - Hot Spot - Double Dose!")
            fig_j, ax_j = plt.subplots(figsize=(5, 3))
            ax_j.add_patch(patches.Rectangle((-3, 0.5), 6, 1, facecolor="#FF6B6B", alpha=0.6, edgecolor="black"))
            ax_j.text(0, 1.0, "BRAIN FIELD", ha="center", fontsize=7, fontweight="bold")
            ax_j.add_patch(patches.Rectangle((-3, -0.5), 6, 1, facecolor="#54A0FF", alpha=0.6, edgecolor="black"))
            ax_j.text(0, 0.0, "SPINE FIELD 1", ha="center", fontsize=7, fontweight="bold")
            ax_j.add_patch(patches.Rectangle((-3, -1.5), 6, 1, facecolor="#1DD1A1", alpha=0.6, edgecolor="black"))
            ax_j.text(0, -1.0, "SPINE FIELD 2", ha="center", fontsize=7, fontweight="bold")
            ax_j.plot([junction_gap, junction_gap], [-1.5, 1.5], color="red", linewidth=3, linestyle="--")
            ax_j.text(junction_gap+0.3, 1.7, f"Junction {junction_gap} cm", fontsize=7, color="red", fontweight="bold")
            ax_j.set_xlim(-4, 4); ax_j.set_ylim(-2, 2); ax_j.set_title("CSI - Field Junction", fontweight="bold"); ax_j.axis("off")
            st.pyplot(fig_j)
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

    # ================= C - LINAC =================
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
        field_x = x1 + x2; field_y = y1 + y2
        shift_x = (x2 - x1) / 2; shift_y = (y2 - y1) / 2
        if x1 == x2 and y1 == y2: sym = "✅ Symmetric Field - Center pe hai"
        else: sym = f"⚠️ Asymmetric Field - Field {shift_x:.1f} cm X aur {shift_y:.1f} cm Y pe Shift hai"
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
        ang = math.radians(gantry); dx = math.sin(ang)*10; dy = math.cos(ang)*10
        ax.plot([0, dx], [-6, dy], color="#57606F", linewidth=10, solid_capstyle='round')
        ax.add_patch(patches.FancyBboxPatch((dx-2.2, dy-1.5), 4.4, 3, boxstyle="round,pad=0.2", facecolor="#2F3542", edgecolor="black", linewidth=1.5))
        ax.text(dx, dy+0.5, "LINAC HEAD", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
        ax.text(dx, dy-0.5, "Target + MLC", ha="center", va="center", fontsize=6, color="#FFD700")
        jaw_w = max(field_x / 2.5, 0.8)
        ax.add_patch(patches.Rectangle((dx-jaw_w/2, dy-2.5), jaw_w, 1.0, facecolor="#FFD700", edgecolor="black"))
        ax.text(dx, dy-2.0, f"Jaws {field_x}x{field_y}", ha="center", va="center", fontsize=6, fontweight="bold")
                ax.text(dx+3.5, dy-2.0, f"X1 {x1} | X2 {x2}\nY1 {y1} | Y2 {y2}", fontsize=6, fontweight="bold", bbox=dict(facecolor="white", edgecolor="black"))
        ax.add_patch(patches.Rectangle((-6, -1.5), 12, 2, facecolor="#57606F", edgecolor="black"))
        ax.text(0, -0.5, "COUCH", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
        ax.add_patch(patches.Ellipse((cx, cy), 5, 2.5, facecolor=p["color"], alpha=0.8, edgecolor="black"))
        ax.text(cx, cy, f"{patient}", ha="center", va="center", fontsize=7, fontweight="bold")
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

    # ================= D - COBALT =================
    else:
        st.subheader("☢️ D - Cobalt-60 Mirror - Real Structure")
        st.write("**Source: Co-60 | Half-Life 5.27y | Energy 1.17 + 1.33 MeV | SSD 80 cm**")
        st.markdown("### 🔲 Collimator Jaws - Field Setting (Cobalt me MLC nahi hota)")
        cj1, cj2 = st.columns(2)
        with cj1:
            cx1 = st.slider("X1 - Left Jaw (cm)", 0, 10, 5, 1, key="c_x1")
            cy1 = st.slider("Y1 - Upper Jaw (cm)", 0, 10, 5, 1, key="c_y1")
        with cj2:
            cx2 = st.slider("X2 - Right Jaw (cm)", 0, 10, 5, 1, key="c_x2")
            cy2 = st.slider("Y2 - Lower Jaw (cm)", 0, 10, 5, 1, key="c_y2")
        c_field_x = cx1 + cx2; c_field_y = cy1 + cy2
        c_shift_x = (cx2 - cx1) / 2; c_shift_y = (cy2 - cy1) / 2
        if cx1 == cx2 and cy1 == cy2: c_sym = "✅ Symmetric Field"
        else: c_sym = f"⚠️ Asymmetric Field - Shift {c_shift_x:.1f}, {c_shift_y:.1f} cm"
        st.info(f"**Field Size: {c_field_x} x {c_field_y} cm** | X1 {cx1} + X2 {cx2} = {c_field_x} | Y1 {cy1} + Y2 {cy2} = {c_field_y} | {c_sym}")
        years = st.slider("Source Kitna Purana Hai? (Years)", 0, 10, 2, 1)
        init_rate = 2.0; decayed = init_rate * (0.5 ** (years / 5.27))
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
        c_jaw_w = max(c_field_x / 2.5, 0.8)
        ax2.add_patch(patches.Rectangle((-c_jaw_w/2, 3.5), c_jaw_w, 1.5, facecolor="#FFD700", edgecolor="black"))
        ax2.text(0, 4.2, f"COLLIMATOR {c_field_x}x{c_field_y}", ha="center", va="center", fontsize=6, fontweight="bold")
        ax2.text(5.5, 4.2, f"X1 {cx1} | X2 {cx2}\nY1 {cy1} | Y2 {cy2}", fontsize=7, color="black", bbox=dict(facecolor="white", edgecolor="black"))
        if source_on:
            ax2.plot([0, 0], [3.5, 0], color="red", linewidth=4, alpha=0.8)
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
        if source_on: st.error(f"SOURCE ON - Co-60 - {beams} - {t} min - SSD 80 cm - Field {c_field_x}x{c_field_y}")
        if source_off: st.info("Source OFF - Source Wapas Shield Me")

# ============================================================
# ================= PART 2 - OPTICS BEHIND IT =================
# ============================================================
else:
    st.subheader("🔬 PART 2: Optics Behind It")
    st.write("Part 1 me jo dikhaya, uske peeche ye Optics hai. Ma'am wala Part.")
    optics_mirror = st.radio("Optics Kis Ka Dekhna Hai?", ["CT Sim", "TPS", "LINAC", "Cobalt-60", "CSI Junction"], horizontal=True)

    if optics_mirror == "CT Sim":
        st.markdown("### 1. CT Sim = Beer-Lambert Law + Wavelength")
        st.latex(r"I = I_0 e^{-\mu x}")
        st.latex(r"c = f \lambda \quad , \quad E = hf = \frac{hc}{\lambda}")
        mu = st.slider("Attenuation Coefficient μ (cm⁻¹) - Tissue Density", 0.1, 1.0, 0.3, 0.05)
        x_arr = np.linspace(0, 20, 100)
        I_arr = np.exp(-mu * x_arr)
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(x_arr, I_arr, color="red", linewidth=3, label=f"μ = {mu}")
        ax.fill_between(x_arr, I_arr, alpha=0.2, color="red")
        ax.set_xlabel("Thickness x (cm)"); ax.set_ylabel("Intensity I / I0"); ax.set_title("Beer-Lambert Law - CT Sim"); ax.grid(True, alpha=0.3); ax.legend()
        st.pyplot(fig)
        st.write("**Plain Scan:** μ kam = Image Dark | **Contrast Scan:** μ zyada = Image Bright")
        st.write("**Diagram:** X-Ray Source → Patient (μ alag) → Detector. Jahan bone hai wahan absorption zyada, image bright.")
        fig2, ax2 = plt.subplots(figsize=(5, 2.5))
        ax2.add_patch(patches.Rectangle((-4, 0.5), 1, 1, facecolor="yellow", edgecolor="black")); ax2.text(-3.5, 1, "X-Ray", ha="center", fontsize=7, fontweight="bold")
        ax2.add_patch(patches.Ellipse((0, 1), 4, 2, facecolor="#E8E8E8", edgecolor="black")); ax2.text(0, 1, "PATIENT\nμ1 Bone / μ2 Soft", ha="center", fontsize=7, fontweight="bold")
        ax2.add_patch(patches.Rectangle((3, 0.5), 1, 1, facecolor="lightblue", edgecolor="black")); ax2.text(3.5, 1, "DETECTOR", ha="center", fontsize=7, fontweight="bold")
        ax2.annotate("", xy=(-1.5, 1), xytext=(-3, 1), arrowprops=dict(arrowstyle="->", color="red", lw=2))
        ax2.annotate("", xy=(3, 1), xytext=(1.5, 1), arrowprops=dict(arrowstyle="->", color="blue", lw=2))
        ax2.set_xlim(-5, 5); ax2.set_ylim(-0.5, 2.5); ax2.axis("off"); ax2.set_title("CT Sim - Ray Diagram", fontweight="bold")
        st.pyplot(fig2)
        st.info("Ma'am ko bolo: CT me X-Ray ki intensity Beer-Lambert Law se girti hai.")

    elif optics_mirror == "TPS":
        st.markdown("### 2. TPS = Ray Tracing + Young's Interference")
        st.latex(r"E = hf = \frac{hc}{\lambda}")
        st.latex(r"I = I_1 + I_2 + 2\sqrt{I_1 I_2}\cos\delta")
        st.write("**Dose Wash = Interference Pattern:** Jahan Rays overlap = Constructive = Red (High Dose). Jahan overlap nahi = Destructive = Blue (Low Dose).")
        y = np.linspace(-5, 5, 500)
        I_y = (np.cos(y*2)**2) * np.exp(-y**2/8) * 100
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(y, I_y, color="purple", linewidth=2)
        ax.fill_between(y, I_y, alpha=0.3, color="purple")
        ax.set_xlabel("Position (Young's Screen jesa)"); ax.set_ylabel("Intensity / Dose"); ax.set_title("Young's Fringes = Dose Wash"); ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.add_patch(patches.Circle((0, 0), 1.0, facecolor="red", alpha=0.8)); ax2.text(0, 0, "TUMOR", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
        for ang in [30, 90, 150, 210, 270, 330]:
            a = math.radians(ang); ax2.plot([0, math.cos(a)*3], [0, math.sin(a)*3], color="orange", linewidth=2, alpha=0.7)
        ax2.add_patch(patches.Ellipse((0, 0), 7, 7, facecolor="none", edgecolor="black"))
        ax2.text(0, 3.8, "Ray Tracing - 6 Beams Tumor pe mil rahi hain", ha="center", fontsize=7, fontweight="bold")
        ax2.set_xlim(-4, 4); ax2.set_ylim(-4, 4); ax2.set_aspect("equal"); ax2.axis("off"); ax2.set_title("TPS - Ray Tracing Diagram", fontweight="bold")
        st.pyplot(fig2)
        st.write("**DVH:** Young's ke Intensity vs Position graph jesa hai. PTV = Bright Fringe, OAR = Dark Fringe.")
        st.info("Ma'am ko bolo: TPS me hum Lens ke Ray Diagram jese Ray Tracing karte hain.")

    elif optics_mirror == "LINAC":
        st.markdown("### 3. LINAC = Mirror Reflection + Laser + Lens")
        st.latex(r"i = r \quad \text{(Law of Reflection)}")
        st.latex(r"c = f \lambda \quad , \quad E = \frac{hc}{\lambda}")
        lam = st.slider("Wavelength λ Select Karo (nm)", 0.001, 700.0, 635.0)
        c = 3e8; f = c / (lam * 1e-9); E = 6.626e-34 * f
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Wavelength λ", f"{lam} nm")
        with col2: st.metric("Frequency f", f"{f:.2e} Hz")
        with col3: st.metric("Energy E", f"{E:.2e} J")
        lam_arr = np.array([0.001, 0.01, 1, 100, 635, 700])
        E_arr = 6.626e-34 * 3e8 / (lam_arr*1e-9)
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(lam_arr, E_arr, marker="o", color="red", linewidth=2)
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("Wavelength λ (nm) - Log"); ax.set_ylabel("Energy E (J) - Log"); ax.set_title("λ kam = E zyada"); ax.grid(True, alpha=0.3)
        ax.annotate("Gamma", xy=(0.001, E_arr[0]), fontsize=7, fontweight="bold")
        ax.annotate("Laser 635nm", xy=(635, E_arr[4]), fontsize=7, fontweight="bold")
        st.pyplot(fig)
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.plot([-2, 2], [-1, 1], color="gray", linewidth=8, alpha=0.7); ax2.text(0, 0.5, "45° MIRROR", ha="center", fontsize=7, fontweight="bold")
        ax2.annotate("", xy=(0, 0), xytext=(-2, 2), arrowprops=dict(arrowstyle="->", color="red", lw=2)); ax2.text(-1.8, 2.1, "Incident i", fontsize=7, color="red")
        ax2.annotate("", xy=(2, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="blue", lw=2)); ax2.text(1.5, 0.4, "Reflected r", fontsize=7, color="blue")
        ax2.text(0, -1.5, "i = r  |  Mirror se Light Field Patient pe", ha="center", fontsize=7, fontweight="bold", bbox=dict(facecolor="white", edgecolor="black"))
        ax2.set_xlim(-3, 3); ax2.set_ylim(-2, 3); ax2.set_aspect("equal"); ax2.axis("off"); ax2.set_title("LINAC Mirror - Reflection Diagram", fontweight="bold")
        st.pyplot(fig2)
        st.write("**Laser (635nm):** Coherent = Sharp line, Alignment ke liye. **Collimator:** Aperture / Lens jesa, Beam ko shape deta hai.")
        st.success("Ma'am ko bolo: Laser sirf skin pe nazar aata hai, X-Ray tumor tak jati hai kyunki uski λ choti hai.")

    elif optics_mirror == "Cobalt-60":
        st.markdown("### 4. Cobalt-60 = Young's Double Slit + Penumbra + Inverse Square Law")
        st.latex(r"\beta = \frac{\lambda D}{d}")
        st.latex(r"I \propto \frac{1}{d^2}")
        st.write("**Source ke 2 Edges = Young's ke 2 Slits.** Jahan Rays milti hain = Umbra (High Dose) = Bright Fringe. Jahan nahi milti = Penumbra (Low Dose) = Dark Fringe.")
        d_src = st.slider("Source Size d (cm)", 1.0, 3.0, 2.0, 0.1)
        penumbra = d_src * 0.8
        st.metric("Penumbra Width", f"{penumbra:.2f} cm", f"Source {d_src} cm pe")
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.add_patch(patches.Rectangle((-1, 2.5), 2, 0.5, facecolor="gray", edgecolor="black")); ax.text(0, 2.75, f"Source d={d_src}cm", ha="center", fontsize=7, fontweight="bold")
        ax.plot([-d_src/2, -1], [2.5, -1], color="red", linewidth=1.5); ax.plot([d_src/2, 1], [2.5, -1], color="red", linewidth=1.5)
        ax.plot([-d_src/2, 1], [2.5, -1], color="orange", linewidth=1, linestyle="--"); ax.plot([d_src/2, -1], [2.5, -1], color="orange", linewidth=1, linestyle="--")
        ax.add_patch(patches.Rectangle((-1, -1.5), 2, 0.5, facecolor="red", alpha=0.6)); ax.text(0, -1.25, "UMBRA", ha="center", fontsize=7, fontweight="bold")
        ax.add_patch(patches.Rectangle((-1.8, -1.5), 0.8, 0.5, facecolor="orange", alpha=0.5)); ax.add_patch(patches.Rectangle((1.0, -1.5), 0.8, 0.5, facecolor="orange", alpha=0.5))
        ax.text(-1.4, -1.9, "PENUMBRA", ha="center", fontsize=6); ax.text(1.4, -1.9, "PENUMBRA", ha="center", fontsize=6)
        ax.set_xlim(-3, 3); ax.set_ylim(-2.5, 3.5); ax.axis("off"); ax.set_title("Cobalt Penumbra = Young's Fringes", fontweight="bold")
        st.pyplot(fig)
        dist = np.linspace(50, 150, 100); inten = 10000 / (dist**2) * 100
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.plot(dist, inten, color="blue", linewidth=3); ax2.set_xlabel("Distance d (cm)"); ax2.set_ylabel("Intensity"); ax2.set_title("Inverse Square Law - I ∝ 1/d²"); ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)
        st.write("**Gamma Wavelength:** ~0.001 nm = Sab se choti, Energy sab se zyada, Penetration sab se zyada.")
        st.info("Ma'am ko bolo: Penumbra hi Young's ka Interference hai.")

    else:
        st.markdown("### 5. CSI Junction = Young's Interference - Sab Se Mushkil Part")
        st.latex(r"I = I_1 + I_2 + 2\sqrt{I_1 I_2}\cos\delta")
        st.write("CSI me 3 Fields join hote hain: Brain + Upper Spine + Lower Spine. Jahan wo milte hain wahan Hot Spot / Cold Spot banta hai.")
        gap = st.slider("Junction Gap / Overlap (cm)", -1.0, 1.0, 0.0, 0.1)
        x = np.linspace(-3, 3, 300)
        b1 = np.exp(-((x+gap/2+1)**2)/0.5); b2 = np.exp(-((x-gap/2-1)**2)/0.5)
        total = b1 + b2
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(x, b1, color="red", linestyle="--", label="Brain Field")
        ax.plot(x, b2, color="blue", linestyle="--", label="Spine Field")
        ax.plot(x, total, color="purple", linewidth=3, label="Total Dose at Junction")
        ax.fill_between(x, total, alpha=0.2, color="purple")
        ax.set_xlabel("Position"); ax.set_ylabel("Dose"); ax.set_title(f"CSI Junction - Gap {gap} cm"); ax.legend(); ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        if gap == 0: st.success("✅ Perfect Junction - No Hot / Cold Spot")
        elif gap > 0: st.error(f"Gap {gap} cm = Cold Spot - Young's Destructive Interference jesa")
        else: st.error(f"Overlap {abs(gap)} cm = Hot Spot - Young's Constructive Interference jesa")
        st.info("Ma'am ko bolo: CSI Junction ko samajhna matlab Young's Interference ko samajhna hai.")

st.markdown("---")
st.caption("Virtual RT Mirror | CT Sim → TPS → LINAC / Cobalt-60 | Part 1: Simulation | Part 2: Optics Behind It")
st.markdown("---")
st.markdown("**FYP Title: Optics Behind Virtual RT Mirror App**")
st.caption("Part 1: Simulation | Part 2: Wavelength, Reflection & Young's Interference")
st.markdown("Developed by: Naheed | BS Physics")
