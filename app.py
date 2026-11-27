import streamlit as st
import math
import pydicom
import requests
import urllib.parse
import matplotlib.patches as patches
import numpy as np
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Virtual RT Mirror | Radiotherapy Simulation",page_icon="iconpng.jpg",layout="centered")
# ===== SIDEBAR NAVIGATION - NEW =====
page = st.sidebar.radio(
    "Go To Module",
    [" RT Mirror - Main App", "👩🏻‍⚕️ AI Tutor"]
)
st.sidebar.markdown("---")
st.sidebar.info("Virtual RT Mirror")
if page == "👩🏻‍⚕️ AI Tutor":
    st.title("👩🏻‍⚕️ AI Tutor")
    st.caption("Ask anything")

    import urllib.parse

    if "messages" not in st.session_state:
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything - e.g. What is QUANTEC?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Pollinations - Free, No Key Needed
                    full_prompt = f"You are an Advanced Radiotherapy Physics professor. Answer formally in 150 words with Definition, Clinical Significance and Example. Question: {prompt}"
                    encoded = urllib.parse.quote(full_prompt)
                    url = f"https://text.pollinations.ai/{encoded}"
                    r = requests.get(url, timeout=60)
                    ans = r.text
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                except Exception as e:
                    st.error(f"Error: {e} - Try again")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #0A0A0A; color: #F1F1F1; }
.main { background: #0A0A0A; }
h1, h2, h3, h4 { font-family: 'Playfair Display', serif; color: #FFFFFF; }
p, label, span, div { color: #E5E5E5; }
.stRadio > div { background: #141414; padding: 8px 12px; border-radius: 10px; border: 1px solid #2A2A2A; }
.stSelectbox > div > div { border-radius: 8px !important; border: 1px solid #333333 !important; background: #141414 !important; color: white !important; }
.stSelectbox div[data-baseweb="select"] span { color: white !important; }
.stSlider > div > div > div > div { background: #D4AF37 !important; }
.stButton>button {
    border-radius: 8px !important; font-weight: 600 !important; height: 46px !important; font-size: 14px !important;
    background: #D4AF37 !important; color: #000000 !important; border: none !important;
}
.stButton>button:hover { background: #FFFFFF !important; color: #000000 !important; }
div[data-testid="stExpander"] { background: #141414; border-radius: 10px; border: 1px solid #2A2A2A; }
div[data-testid="stExpander"] p { color: #E5E5E5; }
hr { border-color: #2A2A2A; }
[data-testid="stTable"] { background: #141414; }
table { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #000000 0%, #111111 55%, #1E1E1E 100%); border: 1px solid #2A2A2A; border-left: 4px solid #D4AF37; padding: 28px 24px; border-radius: 14px; color: white;">
  <div style="font-family: 'Playfair Display', serif; font-size: 32px; font-weight: 700; margin: 6px 0 2px; line-height: 1.1; color: white;">Virtual RT Mirror</div>
  <div style="font-size: 14px; color: #BBBBBB;">CT Simulation &nbsp;→&nbsp; Treatment Planning &nbsp;→&nbsp; LINAC / Cobalt-60 Delivery</div>
  <div style="margin-top: 14px; display: flex; gap: 8px; flex-wrap: wrap;">
    <span style="background: #1E1E1E; border: 1px solid #333333; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; color: white;">PART 1 &nbsp;|&nbsp; Simulation</span>
    <span style="background: #D4AF37; color: #000000; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;">PART 2 &nbsp;|&nbsp; Optics Behind It</span>
  </div>
</div>
""", unsafe_allow_html=True)
st.write("")

PATIENTS = {
    "BREAST-LEFT": {"site": "Breast - Left", "oar": "Heart / Lung", "limit": 20, "mask": False, "dose": 50, "fx": 25, "w": 11, "h": 8, "gtv": (2.5, 0.5), "oar_pos": (-1.0, -1.0), "oar2": (0.5, -1.8), "color": "#D4AF37", "note": "Left Breast = Image Right. Heart is close, therefore OAR is Heart.", "devices": ["Breast Board", "Knee and Foot Lock"]},
    "BREAST-RIGHT": {"site": "Breast - Right", "oar": "Lung / Liver", "limit": 20, "mask": False, "dose": 50, "fx": 25, "w": 11, "h": 8, "gtv": (-2.5, 0.5), "oar_pos": (1.0, -1.0), "oar2": (0.5, -1.8), "color": "#888888", "note": "Right Breast = Image Left. Heart is away, therefore OAR is Lung.", "devices": ["Breast Board", "Knee and Foot Lock"]},
    "ESOPHAGUS": {"site": "Esophagus", "oar": "Lung / Heart / Cord", "limit": 45, "mask": False, "dose": 50, "fx": 25, "w": 9, "h": 9, "gtv": (0, 0.5), "oar_pos": (2.2, 0.5), "oar2": (-2.2, 0.5), "color": "#B45309", "note": "Esophagus in center. Lung on both sides, Cord posterior, Heart anterior.", "devices": ["Knee and Foot Lock", "Head Rest B"]},
    "HEAD & NECK": {"site": "Head & Neck", "oar": "Cord / Parotid", "limit": 45, "mask": True, "dose": 70, "fx": 35, "w": 7, "h": 9, "gtv": (0.5, 1.0), "oar_pos": (0, -2.0), "oar2": (2.0, 1.0), "color": "#7C3AED", "note": "Head + Neck combined. Mask is required. Shoulder Puller is used.", "devices": ["Thermoplastic Mask", "Head Rest E", "Head Rest B", "Shoulder Puller"]},
    "BRAIN": {"site": "Brain", "oar": "Brainstem / Optic", "limit": 54, "mask": True, "dose": 60, "fx": 30, "w": 8, "h": 8.5, "gtv": (0.5, 0.5), "oar_pos": (0, -1.5), "oar2": (1.5, 1.5), "color": "#FFFFFF", "note": "Mask is required.", "devices": ["Thermoplastic Mask", "Head Rest E"]},
    "PELVIS": {"site": "Pelvis", "oar": "Bladder / Rectum", "limit": 65, "mask": False, "dose": 50, "fx": 25, "w": 11, "h": 9.5, "gtv": (0, 0.5), "oar_pos": (0, -2.2), "oar2": (0, 2.2), "color": "#D4AF37", "note": "Bladder full, Rectum empty.", "devices": ["Knee and Foot Lock", "Head Rest B"]},
    "ABDOMEN": {"site": "Abdomen", "oar": "Liver / Kidney / Bowel", "limit": 30, "mask": False, "dose": 45, "fx": 25, "w": 11, "h": 9, "gtv": (0, 0.5), "oar_pos": (2.5, 0.5), "oar2": (-2.5, -1.0), "color": "#92400E", "note": "Abdomen in center. Liver right, Kidney both sides, Bowel anterior.", "devices": ["Knee and Foot Lock", "Head Rest B"]},
    "CSI": {"site": "Cranio-Spinal (CSI)", "oar": "Heart / Lung / Kidney", "limit": 20, "mask": True, "dose": 36, "fx": 20, "w": 7, "h": 14, "gtv": (0, 4.0), "oar_pos": (2.0, -1.0), "oar2": (-2.0, -1.0), "color": "#BE123C", "note": "Brain + Full Spine. 3 Fields Join. Junction - Overlap / Gap risk. Mostly in children - Medulloblastoma.", "devices": ["Thermoplastic Mask", "Knee and Foot Lock", "Head Rest B"]},
}

def prof_card(label, value, accent="#D4AF37"):
    st.markdown(f'<div style="background:#141414; padding:16px 12px; border-radius:12px; border:1px solid #2A2A2A; border-top:3px solid {accent}; text-align:center;"><div style="font-size:11px; letter-spacing:1.2px; color:#999999; font-weight:700;">{label}</div><div style="font-size:15px; color:#FFFFFF; font-weight:700; margin-top:6px; line-height:1.3;">{value}</div></div>', unsafe_allow_html=True)

part = st.radio("Select Section", ["PART 1 — Virtual RT Mirror", "PART 2 — Optics Behind It"], horizontal=True)

if "PART 1" in part:
    patient = st.selectbox("Select Patient / Site", list(PATIENTS.keys()))
    p = PATIENTS[patient]
    c1, c2, c3 = st.columns(3)
    with c1: prof_card("SITE", p["site"], "#D4AF37")
    with c2: prof_card("ORGAN AT RISK", p["oar"], "#FFFFFF")
    with c3: prof_card("PRESCRIBED DOSE", f"{p['dose']} Gy / {p['fx']} Fractions", "#B45309")
    st.write("")
    st.markdown(f'<div style="background:#141414; border:1px solid #2A2A2A; border-left:4px solid #D4AF37; padding:12px 14px; border-radius:8px; font-size:13px; color:#DDDDDD;"><b style="color:white;">Clinical Note:</b> {p["note"]}</div>', unsafe_allow_html=True)

    st.markdown("### Immobilization Devices")
    st.caption("Immobilization — Keeping the patient in the exact same position every day, so radiation is delivered to the same target daily.")
    ALL_DEVICES = {
        "Thermoplastic Mask": "Warm plastic that is soft on the face and becomes hard on cooling. Prevents head movement. Used in Brain, Head & Neck and CSI.",
        "Knee and Foot Lock": "Locks knees and feet together. Legs remain at the same angle every day. Used in Breast, Pelvis, Abdomen, Esophagus and CSI.",
        "Breast Board": "Board for breast patients. Keeps both arms elevated and lifts the chest. Used in Breast.",
        "Head Rest E": "Head Rest Type E — For head and neck patients with extended neck position. Keeps the head tilted back.",
        "Head Rest B": "Head Rest Type B — For Brain patients with neutral neck position. Keeps the head straight.",
        "Shoulder Puller": "Pulls shoulders down, so the neck area becomes clear and visible. Used in Head & Neck.",
    }
    device = st.selectbox("Select Immobilization Device", list(ALL_DEVICES.keys()))
    st.markdown(f'<div style="background:#141414; padding:14px 16px; border-radius:10px; border:1px solid #2A2A2A; border-left:4px solid #D4AF37; font-size:13.5px; line-height:1.6; color:#EEEEEE;"><b style="color:white;">{device}:</b> {ALL_DEVICES[device]}</div>', unsafe_allow_html=True)
    st.write(f"**Commonly used for this patient:** {', '.join(p['devices'])}")

    position = st.selectbox("Position", ["Supine — Patient lying straight, face up", "Prone — Patient lying face down"], index=0)
    if "Supine" in position: st.caption("Supine — Patient lying straight, face up. Most commonly used.")
    else: st.caption("Prone — Patient lying face down. Used in Breast to spare Heart, in CSI to keep Spine straight.")
    mask = st.checkbox(f"Mask / Immobilization {'(Required)' if p['mask'] else '(Not Used)'}", value=p["mask"])
    mirror= st.radio("Select Module", ["A — CT Sim", "B — TPS", "C — LINAC", "D — Cobalt-60"], horizontal=True)
      # Default values taake NameError na aaye
    ct_mode = "Simulated CT"
    tps_mode = "Simulated TPS"

    if mirror == "A — CT Sim":
        st.subheader("A — CT Simulation")
            # --- REAL DICOM OPTION ---
        ct_mode = st.radio("CT Type", ["Simulated CT (Drawing)", "Real DICOM CT (Upload)"], horizontal=True)

    if ct_mode == "Real DICOM CT (Upload)":
        st.info("Apni poori CT ke saare .dcm files ek saath select karo")
        uploaded_files = st.file_uploader("CT DICOM Upload Karo", type=["dcm"], accept_multiple_files=True)
        
        if uploaded_files:
            datasets = []
            for f in uploaded_files:
                try:
                    ds = pydicom.dcmread(f)
                    datasets.append(ds)
                except:
                    pass
            
            datasets = sorted(datasets, key=lambda x: float(x.get('SliceLocation', 0)))
            
            slice_num = st.slider("Real Slice Badlo", 0, len(datasets)-1, len(datasets)//2)
            ds = datasets[slice_num]
            
            window = st.selectbox("Window", ["Brain", "Lung", "Bone", "Soft Tissue"])
            
            img = ds.pixel_array.astype(float)
            if 'RescaleSlope' in ds:
                img = img * float(ds.RescaleSlope) + float(ds.get('RescaleIntercept', 0))
            
            windows = {"Brain": (40, 80), "Lung": (-600, 1500), "Bone": (400, 1800), "Soft Tissue": (50, 350)}
            center, width = windows[window]
            low = center - width/2
            high = center + width/2
            img = np.clip(img, low, high)
            img = ((img - low) / (high - low) * 255).astype(np.uint8)
            
            st.image(img, caption=f"Real CT - Slice {slice_num+1} / {len(datasets)}", use_column_width=True)
            st.write(f"Patient: {ds.get('PatientName', 'Anonymous')} | Thickness: {ds.get('SliceThickness', '')} mm")
        # Agar file nahi hai to neeche wala simulated wala chalega
    if ct_mode == "Simulated CT (Drawing)":
        # --- YAHAN SE TUMHARA PURANA CT SIM CODE SHURU HOGA ---
        scan_type = st.radio("Scan Protocol", ["1 — Plain Scan", "2 — Contrast Scan", "3 — Post-Contrast Scan"], horizontal=True)
        slice_no = st.slider("CT Slice Number", 1, 20, 10)
        if "Plain" in scan_type:
            bg = "white"; gtv_col = "#94A3B8"; gtv_alpha = 0.7; desc = "Plain Scan: Without contrast. Only anatomy is visible. Tumor appears faint."
            enh = "No Enhancement"
        elif "Post" not in scan_type:
            bg = "white"; gtv_col = "#DC2626"; gtv_alpha = 0.9; desc = "Contrast Scan: After contrast injection. Tumor becomes bright, vessels visible. GTV is contoured on this scan."
            enh = "Bright Enhancement"
        else:
            bg = "white"; gtv_col = "#B45309"; gtv_alpha = 0.85; desc = "Post-Contrast Scan: 60–90 sec after contrast. Washout of tumor is seen. Difference between OAR and tumor becomes clear."
            enh = "Washout Phase"
        st.write(desc)
        if st.button("ACQUIRE SCAN", use_container_width=True):
            st.success(f"{scan_type} acquired — Slice {slice_no}/20 — {p['site']} — {enh}")
            fig, ax = plt.subplots(figsize=(5, 5))
            fig.patch.set_facecolor('white'); ax.set_facecolor(bg)
            ax.tick_params(colors='black'); ax.xaxis.label.set_color('black'); ax.yaxis.label.set_color('black'); ax.title.set_color('black')
            for s in ax.spines.values(): s.set_color('black')
            if patient == "CSI":
                ax.add_patch(patches.Ellipse((0, 0), 6, 12, facecolor="#E5E7EB", edgecolor="black", linewidth=1.8))
            else:
                ax.add_patch(patches.Ellipse((0, 0), p["w"], p["h"], facecolor="#E5E7EB", edgecolor="black", linewidth=1.8))
            gtv_r = 1.2 if 8 <= slice_no <= 12 else 0.7
            ax.add_patch(patches.Circle(p["gtv"], gtv_r+0.6, facecolor="none", edgecolor="#B45309", linewidth=2, linestyle="--"))
            ax.text(p["gtv"][0], p["gtv"][1]+gtv_r+0.9, "PTV", ha="center", fontsize=9, color="#B45309", fontweight="bold")
            ax.add_patch(patches.Circle(p["gtv"], gtv_r, facecolor=gtv_col, alpha=gtv_alpha, edgecolor="black"))
            ax.text(p["gtv"][0], p["gtv"][1], "GTV", ha="center", va="center", fontsize=10, fontweight="bold", color="white")
            ax.add_patch(patches.Circle(p["oar_pos"], 0.7, facecolor="#D4AF37", edgecolor="black"))
            ax.text(p["oar_pos"][0], p["oar_pos"][1], p["oar"].split("/")[0], ha="center", va="center", fontsize=7, fontweight="bold", color="black")
            ax.add_patch(patches.Circle(p["oar2"], 0.7, facecolor="#9CA3AF", edgecolor="black"))
            ax.text(p["oar2"][0], p["oar2"][1], "OAR-2", ha="center", va="center", fontsize=6, fontweight="bold", color="black")
            ax.text(0, 6.5, "Patient Left → Image Right", ha="center", fontsize=8, color="black", fontweight="bold")
            ax.text(0, -6.5, f"{scan_type} | {enh}", ha="center", fontsize=8, fontweight="bold", color="white", bbox=dict(facecolor="black", edgecolor="#D4AF37", boxstyle="round,pad=0.4"))
            ax.set_xlim(-7, 7); ax.set_ylim(-7, 7); ax.set_aspect("equal")
            ax.set_title(f"CT — {patient} — {scan_type} — Slice {slice_no}", fontweight="bold", color="black", fontsize=11); ax.grid(True, alpha=0.3, color="#CCCCCC")
            st.pyplot(fig)
            st.markdown(f"**GTV** — Gross Tumor Volume &nbsp;|&nbsp; **PTV Ring** — Planning Target Volume &nbsp;|&nbsp; **OAR** — {p['oar']}")
            st.table({"Scan": ["Plain", "Contrast", "Post-Contrast"], "Visibility": ["Anatomy Only", "Tumor Bright + Vessels", "Washout + OAR Clear"], "GTV Contour": ["Difficult", "Best — Contoured Here", "For Confirmation"]})
       
    if mirror == "B — TPS":
        st.subheader(" B — Treatment Planning System (TPS)")
        tps_mode = st.radio("TPS Type", ["Simulated TPS", "Real TPS - Marking (RTSTRUCT)"], horizontal=True)
        if tps_mode == "Real TPS - Marking (RTSTRUCT)":
            st.info("Pehle CT upload karo, phir RTSTRUCT wali file (RS...dcm)")
            ct_files = st.file_uploader("1. CT DICOM Upload Karo", type=["dcm"], accept_multiple_files=True, key="tps_ct")
            rs_file = st.file_uploader("2. RTSTRUCT File Upload Karo (Sirf 1 file)", type=["dcm"], key="tps_rs")

            if ct_files and rs_file:
                roi_names = {}
                # CT load karo - BytesIO wala fix
                ct_datasets = []
                for f in ct_files:
                    try:
                        f.seek(0)
                        ds = pydicom.dcmread(io.BytesIO(f.read()))
                        ct_datasets.append(ds)
                    except Exception as e:
                        st.warning(f"Ek CT file skip hui: {e}")

                # Safe sort - SliceLocation na bhi ho to error nahi
                def get_slice_loc(ds):
                    try:
                        if hasattr(ds, 'SliceLocation'):
                            return float(ds.SliceLocation)
                        if hasattr(ds, 'ImagePositionPatient'):
                            return float(ds.ImagePositionPatient[2])
                        return float(ds.get('InstanceNumber', 0))
                    except:
                        return 0

                ct_datasets = sorted(ct_datasets, key=get_slice_loc)

                # RTSTRUCT load karo - Isme bhi wahi BytesIO wala fix
                rs_file.seek(0)
                rs = pydicom.dcmread(io.BytesIO(rs_file.read()))
            
                # Saare structures ke naam dikhao
                st.write("--- **Structures Found:** ---")
                roi_names = {}
                for roi in rs.StructureSetROISequence:
                    roi_names[roi.ROINumber] = roi.ROIName
                    st.write(f"✅ {roi.ROIName}")

                # Kaunsi marking dikhani hai?
                selected_roi = st.multiselect("Kaunsi Marking Dikhani Hai?", list(roi_names.values()), default=list(roi_names.values()))

                slice_no = st.slider("Slice Badlo", 0, len(ct_datasets)-1, len(ct_datasets)//2)
                ds = ct_datasets[slice_no]
                
                # CT Image banao - Soft Tissue window
                img = ds.pixel_array.astype(float)
                if 'RescaleSlope' in ds:
                    img = img * float(ds.RescaleSlope) + float(ds.get('RescaleIntercept', 0))
                img = np.clip(img, -160, 240)
                img = ((img + 160) / 400 * 255).astype(np.uint8)

                fig, ax = plt.subplots(figsize=(6, 6))
                ax.imshow(img, cmap='gray')
                
                # Colors har structure ke liye
                color_map = {"GTV": "red", "CTV": "orange", "PTV": "yellow", "Heart": "pink", "Lung": "green", "Spinal Cord": "cyan", "Cord": "cyan", "Bladder": "blue", "Rectum": "purple"}
                
                # Contours draw karo
                for roi_contour in rs.ROIContourSequence:
                    roi_num = roi_contour.ReferencedROINumber
                    roi_name = roi_names.get(roi_num, "")
                    
                    # Agar user ne select nahi kiya to skip karo
                    if roi_name not in selected_roi:
                        continue
                    if not hasattr(roi_contour, 'ContourSequence'):
                        continue
                    
                    for contour in roi_contour.ContourSequence:
                        # Check karo ye contour isi slice ka hai ya nahi
                        if hasattr(contour, 'ContourImageSequence'):
                            ref_uid = contour.ContourImageSequence[0].ReferencedSOPInstanceUID
                            if ref_uid != ds.SOPInstanceUID:
                                continue
                        
                        # Contour points
                        data = np.array(contour.ContourData).reshape(-1, 3)
                        # DICOM coordinates -> Pixel coordinates
                        ipp = np.array(ds.ImagePositionPatient)
                        spacing = np.array(ds.PixelSpacing)
                        px = (data[:, 0] - ipp[0]) / spacing[0]
                        py = (data[:, 1] - ipp[1]) / spacing[1]
                        
                        # Color select karo
                        c = "red"
                        for key in color_map:
                            if key.lower() in roi_name.lower():
                                c = color_map[key]
                                break
                        
                        ax.plot(px, py, color=c, linewidth=2, label=roi_name)
                
                ax.set_title(f"Real TPS - Slice {slice_no+1}")
                ax.axis('off')
                st.pyplot(fig)
                st.success("Yehi asli TPS marking hai - Doctor ne jo contour banaya tha, wohi dikh raha hai!")
                st.stop()
                 break
                    
                    ax.plot(px, py, color=c, linewidth=2, label=roi_name)
            
            ax.set_title(f"Real TPS - Slice {slice_no+1} - {roi_names}")
            ax.axis('off')
            st.pyplot(fig)
            st.success("Yehi asli TPS marking hai - Doctor ne jo contour banaya tha, wohi dikh raha hai!")
            
            # Neeche wala simulated TPS na chale, isliye return
            st.stop()
        if patient == "CSI":
            st.warning("CSI — 3 Fields: Brain + Upper Spine + Lower Spine. Check Junction carefully.")
            junction_gap = st.slider("Junction Gap / Overlap (cm)", -1.0, 1.0, 0.0, 0.1)
            if junction_gap == 0: st.success("✧ Perfect Junction — No Gap, No Overlap")
            elif junction_gap > 0: st.error(f"Gap {junction_gap} cm — Cold Spot — Tumor will not receive dose.")
            else: st.error(f"Overlap {abs(junction_gap)} cm — Hot Spot — Double Dose.")
            fig_j, ax_j = plt.subplots(figsize=(5, 3))
            fig_j.patch.set_facecolor('white'); ax_j.set_facecolor('white'); ax_j.title.set_color('black')
            ax_j.add_patch(patches.Rectangle((-3, 0.5), 6, 1, facecolor="#E5E7EB", alpha=0.95, edgecolor="black"))
            ax_j.text(0, 1.0, "BRAIN FIELD", ha="center", fontsize=8, fontweight="bold", color="black")
            ax_j.add_patch(patches.Rectangle((-3, -0.5), 6, 1, facecolor="#D4AF37", alpha=0.95, edgecolor="black"))
            ax_j.text(0, 0.0, "SPINE FIELD 1", ha="center", fontsize=8, fontweight="bold", color="black")
            ax_j.add_patch(patches.Rectangle((-3, -1.5), 6, 1, facecolor="#9CA3AF", alpha=0.95, edgecolor="black"))
            ax_j.text(0, -1.0, "SPINE FIELD 2", ha="center", fontsize=8, fontweight="bold", color="black")
            ax_j.plot([junction_gap, junction_gap], [-1.5, 1.5], color="#DC2626", linewidth=2.5, linestyle="--")
            ax_j.text(junction_gap+0.3, 1.7, f"Junction {junction_gap} cm", fontsize=8, color="#DC2626", fontweight="bold")
            ax_j.set_xlim(-4, 4); ax_j.set_ylim(-2, 2); ax_j.set_title("CSI — Field Junction", fontweight="bold", color="black"); ax_j.axis("off")
            st.pyplot(fig_j)
        dose = st.slider("Prescription Dose (Gy)", 30, 70, p["dose"], 5)
        beam_type = st.selectbox("Beam Technique", ["VMAT — 2 Arcs", "3D-CRT — 3 Fields", "IMRT — 5 Fields"])
        tech = {"VMAT — 2 Arcs": 0.38, "IMRT — 5 Fields": 0.45, "3D-CRT — 3 Fields": 0.58}[beam_type]
        oar_dose = round(p["limit"] * tech, 1)
        fig0, ax0 = plt.subplots(figsize=(5, 3))
        fig0.patch.set_facecolor('white'); ax0.set_facecolor('white'); ax0.title.set_color('black')
        ax0.add_patch(patches.Ellipse((0, 0), p["w"], p["h"], facecolor="#E5E7EB", edgecolor="black", linewidth=1.5))
        col = "#F59E0B" if dose <= 40 else "#EA580C" if dose <= 55 else "#DC2626"
        ax0.add_patch(patches.Circle(p["gtv"], 2.5, facecolor=col, alpha=0.3))
        ax0.add_patch(patches.Circle(p["gtv"], 0.8, facecolor="#DC2626", alpha=0.95))
        ax0.text(p["gtv"][0], p["gtv"][1], f"{dose} Gy", ha="center", va="center", fontsize=10, fontweight="bold", color="white")
        ax0.set_xlim(-7, 7); ax0.set_ylim(-7, 7); ax0.set_aspect("equal"); ax0.set_title(f"Dose Wash — {dose} Gy — {beam_type}", fontsize=11, fontweight="bold", color="black"); ax0.axis("off")
        st.pyplot(fig0)
        if oar_dose < p["limit"]: st.success(f"✧ PTV 95% PASS | {p['oar']} = {oar_dose} Gy < {p['limit']} Gy PASS")
        else: st.error(f"OAR FAIL — {oar_dose} Gy > {p['limit']} Gy")
        fig2, ax2 = plt.subplots(figsize=(5, 3.5))
        fig2.patch.set_facecolor('white'); ax2.set_facecolor('white')
        ax2.tick_params(colors='black'); ax2.xaxis.label.set_color('black'); ax2.yaxis.label.set_color('black'); ax2.title.set_color('black')
        for s in ax2.spines.values(): s.set_color('black')
        x = np.linspace(0, 80, 200)
        ax2.plot(x, 100/(1+np.exp((x-dose)/3)), color="#DC2626", linewidth=2.5, label=f"PTV — {dose} Gy")
        ax2.plot(x, 100/(1+np.exp((x-oar_dose)/4)), color="#B45309", linewidth=2.5, label=f"{p['oar']} — {oar_dose} Gy")
        ax2.set_xlim(0, 80); ax2.set_ylim(0, 105); ax2.set_xlabel("Dose (Gy)"); ax2.set_ylabel("Volume (%)")
        ax2.set_title(f"DVH — {patient} — {beam_type}", fontweight="bold", color="black"); ax2.grid(True, linestyle="--", alpha=0.3, color="#CCCCCC"); ax2.legend(frameon=True, facecolor="white", edgecolor="black", labelcolor="black")
        st.pyplot(fig2)
        if st.button("✦ APPROVE PLAN", use_container_width=True):
            st.balloons(); st.success("✧ Plan Approved")

    elif mirror == "C — LINAC":
        st.subheader(" C — Linear Accelerator (LINAC)")
        gantry = st.slider("Gantry Angle", 0, 360, 90, 5)
        st.markdown("### ✦ Collimator Jaws — Field Setting")
        st.caption("X1 = Left Jaw | X2 = Right Jaw | Y1 = Upper Jaw | Y2 = Lower Jaw | Field X = X1 + X2 | Field Y = Y1 + Y2")
        j1, j2 = st.columns(2)
        with j1:
            x1 = st.slider("X1 — Left Jaw (cm)", 0, 10, 5, 1)
            y1 = st.slider("Y1 — Upper Jaw (cm)", 0, 10, 5, 1)
        with j2:
            x2 = st.slider("X2 — Right Jaw (cm)", 0, 10, 5, 1)
            y2 = st.slider("Y2 — Lower Jaw (cm)", 0, 10, 5, 1)
        field_x = x1 + x2; field_y = y1 + y2
        shift_x = (x2 - x1) / 2; shift_y = (y2 - y1) / 2
        if x1 == x2 and y1 == y2: sym = "Symmetric Field — Centered"
        else: sym = f"Asymmetric Field — Shift {shift_x:.1f} cm X, {shift_y:.1f} cm Y"
        st.markdown(f'<div style="background:white; padding:12px 14px; border-radius:8px; border:1px solid #CCCCCC; font-size:13px; color:black;"><b style="color:black;">Field Size: {field_x} x {field_y} cm</b> &nbsp;|&nbsp; X1 {x1} + X2 {x2} = {field_x} &nbsp;|&nbsp; Y1 {y1} + Y2 {y2} = {field_y} &nbsp;|&nbsp; {sym}</div>', unsafe_allow_html=True)
        cx = st.slider("Couch X", -5, 5, 0); cy = st.slider("Couch Y", -5, 5, 0); cz = st.slider("Couch Z", -5, 5, 0)
        st.write(f"Gantry: {gantry}° | Field: {field_x} x {field_y} cm | Couch: {cx}, {cy}, {cz} | SSD 100 cm | Energy 6 MV")
        cbct = st.checkbox("CBCT Matched", value=True)
        if not cbct: st.warning("CBCT Not Matched — Beam will NOT turn ON")
        b1, b2 = st.columns(2)
        with b1: beam_on = st.button("▶️ BEAM ON", use_container_width=True)
        with b2: beam_off = st.button("⏸️ BEAM OFF", use_container_width=True)
        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor('white'); ax.set_facecolor('white'); ax.title.set_color('black')
        ax.add_patch(patches.Rectangle((-13, -13), 26, 26, facecolor="#F3F4F6", edgecolor="#CCCCCC"))
        ax.text(-12, 12, "TREATMENT ROOM", fontsize=8, color="#6B7280", fontweight="bold")
        ax.add_patch(patches.Rectangle((-2, -12), 4, 6, facecolor="white", edgecolor="black"))
        ax.text(0, -9, "GANTRY\nSTAND", ha="center", va="center", fontsize=7, color="black", fontweight="bold")
        ang = math.radians(gantry); dx = math.sin(ang)*10; dy = math.cos(ang)*10
        ax.plot([0, dx], [-6, dy], color="#9CA3AF", linewidth=10, solid_capstyle='round')
        ax.add_patch(patches.FancyBboxPatch((dx-2.2, dy-1.5), 4.4, 3, boxstyle="round,pad=0.2", facecolor="white", edgecolor="black", linewidth=1.2))
        ax.text(dx, dy+0.5, "LINAC HEAD", ha="center", va="center", fontsize=7, color="black", fontweight="bold")
        st.markdown("---")
        st.markdown("### LINAC QA — Quality Assurance")
        st.caption("QA = Quality Assurance. Verification before the first patient. Treatment is permitted only after QA passes.")
        qa_freq = st.selectbox("QA Type", ["Daily QA", "Weekly QA", "Monthly QA"], key="linac_qa_type")
        q1 = st.slider("Output — Measured Dose (cGy) for 100 MU", 90, 110, 100, 1, key="linac_output")
        q2 = st.slider("Flatness (%) — Beam should be flat", 0.0, 5.0, 1.5, 0.1, key="linac_flat")
        q3 = st.slider("Symmetry (%) — Left and Right should be equal", 0.0, 5.0, 1.0, 0.1, key="linac_sym")
        q4 = st.slider("Laser vs Isocenter Shift (mm)", 0.0, 3.0, 0.5, 0.1, key="linac_laser")
        q5 = st.slider("Light Field vs Radiation Field Mismatch (mm)", 0.0, 3.0, 0.5, 0.1, key="linac_light")
        q6 = st.checkbox("Door Interlock Working?", value=True, key="linac_door")
        q7 = st.checkbox("Emergency Stop Working?", value=True, key="linac_emg")
        q8 = st.checkbox("Gantry / Couch Movement OK?", value=True, key="linac_move")
        linac_pass = (98 <= q1 <= 102) and (q2 <= 3) and (q3 <= 2) and (q4 <= 1) and (q5 <= 2) and q6 and q7 and q8
        st.table({"QA Test": ["Output", "Flatness", "Symmetry", "Laser Alignment", "Light Field Match", "Door Interlock", "Emergency Stop", "Gantry / Couch"], "Result": [f"{q1} cGy", f"{q2}%", f"{q3}%", f"{q4} mm", f"{q5} mm", "OK" if q6 else "FAIL", "OK" if q7 else "FAIL", "OK" if q8 else "FAIL"], "Tolerance": ["98–102 cGy", "< 3%", "< 2%", "< 1 mm", "< 2 mm", "Must be OK", "Must be OK", "Must be OK"], "Status": ["PASS" if 98 <= q1 <= 102 else "FAIL", "PASS" if q2 <= 3 else "FAIL", "PASS" if q3 <= 2 else "FAIL", "PASS" if q4 <= 1 else "FAIL", "PASS" if q5 <= 2 else "FAIL", "PASS" if q6 else "FAIL", "PASS" if q7 else "FAIL", "PASS" if q8 else "FAIL"]})
        if linac_pass: st.success(f"LINAC {qa_freq} PASSED — Machine is safe for treatment.")
        else: st.error(f"LINAC {qa_freq} FAILED — Do NOT treat. Contact Physicist.")

    elif mirror == "D — Cobalt-60":
        st.subheader("D — Cobalt-60 Unit")
        st.write("**Source: Co-60 | Half-Life 5.27 years | Energy 1.17 + 1.33 MeV | SSD 80 cm**")
        st.markdown("### ✦ Collimator Jaws — Field Setting (No MLC in Cobalt)")
        cj1, cj2 = st.columns(2)
        with cj1:
            cx1 = st.slider("X1 — Left Jaw (cm)", 0, 10, 5, 1, key="c_x1")
            cy1 = st.slider("Y1 — Upper Jaw (cm)", 0, 10, 5, 1, key="c_y1")
        with cj2:
            cx2 = st.slider("X2 — Right Jaw (cm)", 0, 10, 5, 1, key="c_x2")
            cy2 = st.slider("Y2 — Lower Jaw (cm)", 0, 10, 5, 1, key="c_y2")
        c_field_x = cx1 + cx2; c_field_y = cy1 + cy2
        c_shift_x = (cx2 - cx1) / 2; c_shift_y = (cy2 - cy1) / 2
        if cx1 == cx2 and cy1 == cy2: c_sym = "Symmetric Field"
        else: c_sym = f"Asymmetric Field — Shift {c_shift_x:.1f}, {c_shift_y:.1f} cm"
        st.markdown(f'<div style="background:white; padding:12px 14px; border-radius:8px; border:1px solid #CCCCCC; font-size:13px; color:black;"><b style="color:black;">Field Size: {c_field_x} x {c_field_y} cm</b> &nbsp;|&nbsp; X1 {cx1} + X2 {cx2} = {c_field_x} &nbsp;|&nbsp; Y1 {cy1} + Y2 {cy2} = {c_field_y} &nbsp;|&nbsp; {c_sym}</div>', unsafe_allow_html=True)
        years = st.slider("Source Age (Years)", 0, 10, 2, 1)
        init_rate = 2.0; decayed = init_rate * (0.5 ** (years / 5.27))
        st.info(f"Calibration: {init_rate} Gy/min → After {years} years: **{decayed:.2f} Gy/min** (Decay)")
        beams = st.selectbox("Beam Arrangement", ["2 Beams — Lat + Lat", "1 Beam — Direct", "3 Beams"])
        dose_c = st.slider("Total Dose (Gy)", 30, 70, 60, 5)
        fx = st.slider("Fractions", 10, 35, 30, 1)
        per_fx = round(dose_c/fx, 2)
        rate = st.slider("Current Dose Rate (Gy/min)", 0.5, 2.0, round(decayed, 2), 0.05)
        t = round(per_fx/rate, 2)
        st.success(f"✧ Manual Calculation: {per_fx} Gy / {rate} Gy/min = **{t} min per Fraction** | Field {c_field_x} x {c_field_y} cm")
        s1, s2 = st.columns(2)
        with s1: source_on = st.button("🔴 SOURCE ON", use_container_width=True)
        with s2: source_off = st.button("⏸️ SOURCE OFF", use_container_width=True)
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        fig2.patch.set_facecolor('white'); ax2.set_facecolor('white'); ax2.title.set_color('black')
        ax2.add_patch(patches.Rectangle((-13, -13), 26, 26, facecolor="#F3F4F6", edgecolor="#CCCCCC"))
        ax2.text(-12, 12, "COBALT ROOM — SHIELDED WALLS", fontsize=8, color="#6B7280", fontweight="bold")
        ax2.add_patch(patches.FancyBboxPatch((-3, 5), 6, 5, boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", linewidth=1.5))
        ax2.text(0, 9, "SOURCE HEAD", ha="center", va="center", fontsize=8, color="black", fontweight="bold")
        ax2.text(0, 8, "(Lead Shield)", ha="center", va="center", fontsize=6, color="#B45309")
        col_src = "#DC2626" if source_on else "#9CA3AF"
        ax2.add_patch(patches.Circle((0, 6.5), 0.9, facecolor=col_src, edgecolor="black", linewidth=1.2))
        ax2.text(0, 6.5, "Co-60", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
        c_jaw_w = max(c_field_x / 2.5, 0.8)
        ax2.add_patch(patches.Rectangle((-c_jaw_w/2, 3.5), c_jaw_w, 1.5, facecolor="#D4AF37", edgecolor="black"))
        ax2.text(0, 4.2, f"COLLIMATOR {c_field_x}x{c_field_y}", ha="center", va="center", fontsize=6, fontweight="bold", color="black")
        ax2.text(5.5, 4.2, f"X1 {cx1} | X2 {cx2}\nY1 {cy1} | Y2 {cy2}", fontsize=7, color="black", bbox=dict(facecolor="white", edgecolor="#D4AF37", boxstyle="round,pad=0.3"))
        if source_on:
            ax2.plot([0, 0], [3.5, 0], color="#DC2626", linewidth=4, alpha=0.85)
            ax2.text(6, 6, "SOURCE ON", fontsize=10, color="#DC2626", fontweight="bold", bbox=dict(facecolor="white", edgecolor="#DC2626", boxstyle="round,pad=0.3"))
        else:
            ax2.plot([0, 0], [3.5, 0], color="#9CA3AF", linewidth=1, linestyle="--")
            ax2.text(6, 6, "SOURCE OFF\n(In Shield)", fontsize=8, color="#6B7280", fontweight="bold", bbox=dict(facecolor="white", edgecolor="#9CA3AF", boxstyle="round,pad=0.3"))
        ax2.add_patch(patches.Rectangle((-6, -1.5), 12, 2, facecolor="#E5E7EB", edgecolor="black"))
        ax2.text(0, -0.5, "COUCH", ha="center", va="center", fontsize=7, color="black", fontweight="bold")
        ax2.add_patch(patches.Ellipse((0, 0), 5, 2.5, facecolor=p["color"], alpha=0.9, edgecolor="black"))
        st.markdown("---")
        st.markdown("### Cobalt-60 QA — Quality Assurance")
        st.caption("QA = Quality Assurance. Verification before the first patient. Source movement and timer must be correct.")
        c_qa_freq = st.selectbox("QA Type", ["Daily QA", "Weekly QA", "Monthly QA"], key="cobalt_qa_type")
        cq1 = st.slider("Output — Measured Dose Rate (Gy/min)", 0.5, 2.5, round(decayed, 2), 0.05, key="cobalt_output")
        cq2 = st.slider("Timer Error (sec) — Set Time vs Actual Time", 0.0, 5.0, 0.5, 0.1, key="cobalt_timer")
        cq3 = st.slider("Light Field vs Radiation Field Mismatch (mm)", 0.0, 3.0, 0.5, 0.1, key="cobalt_light")
        cq4 = st.slider("Laser vs Isocenter Shift (mm)", 0.0, 3.0, 0.5, 0.1, key="cobalt_laser")
        cq5 = st.checkbox("Source Moves ON and OFF Smoothly?", value=True, key="cobalt_source_move")
        cq6 = st.checkbox("Door Interlock Working?", value=True, key="cobalt_door")
        cq7 = st.checkbox("Emergency Stop Working?", value=True, key="cobalt_emg")
        cq8 = st.checkbox("Radiation Monitor in Room Working?", value=True, key="cobalt_monitor")
        cobalt_pass = (abs(cq1 - decayed) <= 0.1) and (cq2 <= 1) and (cq3 <= 2) and (cq4 <= 2) and cq5 and cq6 and cq7 and cq8
        st.table({"QA Test": ["Output / Dose Rate", "Timer Accuracy", "Light Field Match", "Laser Alignment", "Source Movement", "Door Interlock", "Emergency Stop", "Radiation Monitor"], "Result": [f"{cq1} Gy/min", f"{cq2} sec", f"{cq3} mm", f"{cq4} mm", "OK" if cq5 else "FAIL", "OK" if cq6 else "FAIL", "OK" if cq7 else "FAIL", "OK" if cq8 else "FAIL"], "Tolerance": [f"{decayed:.2f} ± 0.1 Gy/min", "< 1 sec", "< 2 mm", "< 2 mm", "Must be OK", "Must be OK", "Must be OK", "Must be OK"], "Status": ["PASS" if abs(cq1 - decayed) <= 0.1 else "FAIL", "PASS" if cq2 <= 1 else "FAIL", "PASS" if cq3 <= 2 else "FAIL", "PASS" if cq4 <= 2 else "FAIL", "PASS" if cq5 else "FAIL", "PASS" if cq6 else "FAIL", "PASS" if cq7 else "FAIL", "PASS" if cq8 else "FAIL"]})
        if cobalt_pass: st.success(f"Cobalt-60 {c_qa_freq} PASSED — Machine is safe for treatment.")
        else: st.error(f"Cobalt-60 {c_qa_freq} FAILED — Do NOT treat. Contact Physicist.")

else:
    st.subheader("Part 2 — Optics Behind It")
    st.write("The clinical workflow shown in Part 1 is explained here through fundamental optics.")

    optics_mirror = st.radio("Select Optics Module", ["CT Sim", "TPS", "LINAC", "Cobalt-60", "CSI Junction"], horizontal=True)

    if optics_mirror == "CT Sim":
        st.markdown("### 1. CT Sim — Beer-Lambert Law + Wavelength")
        st.write("**Definition:** Beer-Lambert Law states that radiation intensity decreases exponentially as it passes through tissue.")
        st.latex(r"I = I_0 e^{-\mu x}")
        st.latex(r"c = f \lambda \quad , \quad E = hf = \frac{hc}{\lambda}")
        mu = st.slider("Attenuation Coefficient μ (cm⁻¹) — Tissue Density", 0.1, 1.0, 0.3, 0.05)
        x_arr = np.linspace(0, 20, 100)
        I_arr = np.exp(-mu * x_arr)
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#141414'); ax.set_facecolor('#0A0A0A')
        ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white'); ax.title.set_color('white')
        for s in ax.spines.values(): s.set_color('#333333')
        ax.plot(x_arr, I_arr, color="#D4AF37", linewidth=2.5, label=f"μ = {mu}")
        ax.fill_between(x_arr, I_arr, alpha=0.15, color="#D4AF37")
        ax.set_xlabel("Thickness x (cm)"); ax.set_ylabel("Intensity I / I0"); ax.set_title("Beer-Lambert Law — CT Sim", fontweight="bold", color="white"); ax.grid(True, alpha=0.25, color="#333333"); ax.legend(facecolor="#141414", edgecolor="#333333", labelcolor="white")
        st.pyplot(fig)
        st.write("**Plain Scan:** Low μ = Dark Image | **Contrast Scan:** High μ = Bright Image")
        st.write("**Concept:** X-Ray Source → Patient (μ varies) → Detector. Where bone is present, absorption is high, image is bright.")
        fig2, ax2 = plt.subplots(figsize=(5, 2.5))
        fig2.patch.set_facecolor('#141414'); ax2.set_facecolor('#0A0A0A'); ax2.title.set_color('white')
        ax2.add_patch(patches.Rectangle((-4, 0.5), 1, 1, facecolor="#D4AF37", edgecolor="white")); ax2.text(-3.5, 1, "X-Ray", ha="center", fontsize=7, fontweight="bold", color="black")
        ax2.add_patch(patches.Ellipse((0, 1), 4, 2, facecolor="#1E1E1E", edgecolor="white")); ax2.text(0, 1, "PATIENT\nμ1 Bone / μ2 Soft", ha="center", fontsize=7, fontweight="bold", color="white")
        ax2.add_patch(patches.Rectangle((3, 0.5), 1, 1, facecolor="#444444", edgecolor="white")); ax2.text(3.5, 1, "DETECTOR", ha="center", fontsize=7, fontweight="bold", color="white")
        ax2.annotate("", xy=(-1.5, 1), xytext=(-3, 1), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=2))
        ax2.annotate("", xy=(3, 1), xytext=(1.5, 1), arrowprops=dict(arrowstyle="->", color="#D4AF37", lw=2))
        ax2.set_xlim(-5, 5); ax2.set_ylim(-0.5, 2.5); ax2.axis("off"); ax2.set_title("CT Sim — Ray Diagram", fontweight="bold", color="white")
        st.pyplot(fig2)

    elif optics_mirror == "TPS":
        st.markdown("### 2. TPS — Ray Tracing + Young's Interference")
        st.write("**Definition:** Ray Tracing is drawing each beam as a ray. Interference is two rays meeting and adding up or cancelling.")
        st.latex(r"E = hf = \frac{hc}{\lambda}")
        st.latex(r"I = I_1 + I_2 + 2\sqrt{I_1 I_2}\cos\delta")
        st.write("**Dose Wash = Interference Pattern:** Where rays overlap = Constructive = Red (High Dose). Where rays do not overlap = Destructive = Blue (Low Dose).")
        y = np.linspace(-5, 5, 500)
        I_y = (np.cos(y*2)**2) * np.exp(-y**2/8) * 100
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#141414'); ax.set_facecolor('#0A0A0A')
        ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white'); ax.title.set_color('white')
        for s in ax.spines.values(): s.set_color('#333333')
        ax.plot(y, I_y, color="#D4AF37", linewidth=2.5)
        ax.fill_between(y, I_y, alpha=0.15, color="#D4AF37")
        ax.set_xlabel("Position (Like Young's Screen)"); ax.set_ylabel("Intensity / Dose"); ax.set_title("Young's Fringes = Dose Wash", fontweight="bold", color="white"); ax.grid(True, alpha=0.25, color="#333333")
        st.pyplot(fig)
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        fig2.patch.set_facecolor('#141414'); ax2.set_facecolor('#0A0A0A'); ax2.title.set_color('white')
        ax2.add_patch(patches.Circle((0, 0), 1.0, facecolor="#DC2626", alpha=0.9)); ax2.text(0, 0, "TUMOR", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
        for ang in [30, 90, 150, 210, 270, 330]:
            a = math.radians(ang); ax2.plot([0, math.cos(a)*3], [0, math.sin(a)*3], color="#D4AF37", linewidth=2, alpha=0.85)
        ax2.add_patch(patches.Ellipse((0, 0), 7, 7, facecolor="none", edgecolor="white"))
        ax2.text(0, 3.8, "Ray Tracing — 6 Beams Meeting at Tumor", ha="center", fontsize=7, fontweight="bold", color="white")
        ax2.set_xlim(-4, 4); ax2.set_ylim(-4, 4); ax2.set_aspect("equal"); ax2.axis("off"); ax2.set_title("TPS — Ray Tracing Diagram", fontweight="bold", color="white")
        st.pyplot(fig2)
        st.write("**DVH:** Analogous to Young's Intensity vs Position graph. PTV = Bright Fringe, OAR = Dark Fringe.")

    elif optics_mirror == "LINAC":
        st.markdown("### 3. LINAC — Mirror Reflection + Laser + Lens")
        st.write("**Definition:** Reflection is light bouncing from a mirror. Laser is coherent light used for alignment. Collimator functions like an aperture / lens.")
        st.latex(r"i = r \quad \text{(Law of Reflection)}")
        st.latex(r"c = f \lambda \quad , \quad E = \frac{hc}{\lambda}")
        lam = st.slider("Wavelength λ (nm)", 0.001, 700.0, 635.0)
        c = 3e8; f = c / (lam * 1e-9); E = 6.626e-34 * f
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Wavelength λ", f"{lam} nm")
        with col2: st.metric("Frequency f", f"{f:.2e} Hz")
        with col3: st.metric("Energy E", f"{E:.2e} J")
        lam_arr = np.array([0.001, 0.01, 1, 100, 635, 700])
        E_arr = 6.626e-34 * 3e8 / (lam_arr*1e-9)
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#141414'); ax.set_facecolor('#0A0A0A')
        ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white'); ax.title.set_color('white')
        for s in ax.spines.values(): s.set_color('#333333')
        ax.plot(lam_arr, E_arr, marker="o", color="#D4AF37", linewidth=2.5, markersize=6)
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("Wavelength λ (nm) — Log"); ax.set_ylabel("Energy E (J) — Log"); ax.set_title("Small λ = High E", fontweight="bold", color="white"); ax.grid(True, alpha=0.25, color="#333333")
        ax.annotate("Gamma", xy=(0.001, E_arr[0]), fontsize=7, fontweight="bold", color="white")
        ax.annotate("Laser 635nm", xy=(635, E_arr[4]), fontsize=7, fontweight="bold", color="white")
        st.pyplot(fig)
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        fig2.patch.set_facecolor('#141414'); ax2.set_facecolor('#0A0A0A'); ax2.title.set_color('white')
        ax2.plot([-2, 2], [-1, 1], color="#666666", linewidth=9, alpha=0.9); ax2.text(0, 0.5, "45° MIRROR", ha="center", fontsize=7, fontweight="bold", color="white")
        ax2.annotate("", xy=(0, 0), xytext=(-2, 2), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=2)); ax2.text(-1.8, 2.1, "Incident i", fontsize=7, color="#DC2626")
        ax2.annotate("", xy=(2, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="#D4AF37", lw=2)); ax2.text(1.5, 0.4, "Reflected r", fontsize=7, color="#D4AF37")
        ax2.text(0, -1.5, "i = r  |  Mirror Reflects Light Field on Patient", ha="center", fontsize=7, fontweight="bold", color="black", bbox=dict(facecolor="white", edgecolor="#D4AF37", boxstyle="round,pad=0.4"))
        ax2.set_xlim(-3, 3); ax2.set_ylim(-2, 3); ax2.set_aspect("equal"); ax2.axis("off"); ax2.set_title("LINAC Mirror — Reflection Diagram", fontweight="bold", color="white")
        st.pyplot(fig2)
        st.write("**Laser (635 nm):** Coherent — Sharp line, used for alignment. **Collimator:** Aperture / Lens type, shapes the beam.")
        st.success("Laser is visible only on skin. X-Ray reaches the tumor because its λ is very small, therefore its energy is high.")

    elif optics_mirror == "Cobalt-60":
        st.markdown("### 4. Cobalt-60 — Young's Double Slit + Penumbra + Inverse Square Law")
        st.write("**Definition:** Penumbra is the blurred edge. Inverse Square Law states intensity falls with distance squared.")
        st.latex(r"\beta = \frac{\lambda D}{d}")
        st.latex(r"I \propto \frac{1}{d^2}")
        st.write("**Two Edges of Source = Two Slits of Young.** Where rays meet = Umbra (High Dose) = Bright Fringe. Where rays do not meet = Penumbra (Low Dose) = Dark Fringe.")
        d_src = st.slider("Source Size d (cm)", 1.0, 3.0, 2.0, 0.1)
        penumbra = d_src * 0.8
        st.metric("Penumbra Width", f"{penumbra:.2f} cm", f"Source {d_src} cm")
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#141414'); ax.set_facecolor('#0A0A0A'); ax.title.set_color('white')
        ax.add_patch(patches.Rectangle((-1, 2.5), 2, 0.5, facecolor="#444444", edgecolor="white")); ax.text(0, 2.75, f"Source d={d_src}cm", ha="center", fontsize=7, fontweight="bold", color="white")
        ax.plot([-d_src/2, -1], [2.5, -1], color="#DC2626", linewidth=2); ax.plot([d_src/2, 1], [2.5, -1], color="#DC2626", linewidth=2)
        ax.plot([-d_src/2, 1], [2.5, -1], color="#D4AF37", linewidth=1.5, linestyle="--"); ax.plot([d_src/2, -1], [2.5, -1], color="#D4AF37", linewidth=1.5, linestyle="--")
        ax.add_patch(patches.Rectangle((-1, -1.5), 2, 0.5, facecolor="#DC2626", alpha=0.85)); ax.text(0, -1.25, "UMBRA", ha="center", fontsize=7, fontweight="bold", color="white")
        ax.add_patch(patches.Rectangle((-1.8, -1.5), 0.8, 0.5, facecolor="#D4AF37", alpha=0.9)); ax.add_patch(patches.Rectangle((1.0, -1.5), 0.8, 0.5, facecolor="#D4AF37", alpha=0.9))
        ax.text(-1.4, -1.9, "PENUMBRA", ha="center", fontsize=6, color="white"); ax.text(1.4, -1.9, "PENUMBRA", ha="center", fontsize=6, color="white")
        ax.set_xlim(-3, 3); ax.set_ylim(-2.5, 3.5); ax.axis("off"); ax.set_title("Cobalt Penumbra = Young's Fringes", fontweight="bold", color="white")
        st.pyplot(fig)
        dist = np.linspace(50, 150, 100); inten = 10000 / (dist**2) * 100
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        fig2.patch.set_facecolor('#141414'); ax2.set_facecolor('#0A0A0A')
        ax2.tick_params(colors='white'); ax2.xaxis.label.set_color('white'); ax2.yaxis.label.set_color('white'); ax2.title.set_color('white')
        for s in ax2.spines.values(): s.set_color('#333333')
        ax2.plot(dist, inten, color="#D4AF37", linewidth=2.5); ax2.set_xlabel("Distance d (cm)"); ax2.set_ylabel("Intensity"); ax2.set_title("Inverse Square Law — I ∝ 1/d²", fontweight="bold", color="white"); ax2.grid(True, alpha=0.25, color="#333333")
        st.pyplot(fig2)
        st.write("**Gamma Wavelength:** Approx. 0.001 nm — Smallest, Energy highest, Penetration highest.")

    else:
        st.markdown("### 5. CSI Junction — Young's Interference")
        st.write("**Definition:** Junction is where two fields meet. Hot Spot = Excess dose, Cold Spot = Underdose.")
        st.latex(r"I = I_1 + I_2 + 2\sqrt{I_1 I_2}\cos\delta")
        st.write("In CSI, 3 fields join: Brain + Upper Spine + Lower Spine. At their junction, Hot Spot / Cold Spot is formed.")
        gap = st.slider("Junction Gap / Overlap (cm)", -1.0, 1.0, 0.0, 0.1)
        x = np.linspace(-3, 3, 300)
        b1 = np.exp(-((x+gap/2+1)**2)/0.5); b2 = np.exp(-((x-gap/2-1)**2)/0.5)
        total = b1 + b2
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#141414'); ax.set_facecolor('#0A0A0A')
        ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white'); ax.title.set_color('white')
        for s in ax.spines.values(): s.set_color('#333333')
        ax.plot(x, b1, color="#DC2626", linestyle="--", label="Brain Field", linewidth=2)
        ax.plot(x, b2, color="#FFFFFF", linestyle="--", label="Spine Field", linewidth=2)
        ax.plot(x, total, color="#D4AF37", linewidth=3, label="Total Dose at Junction")
        ax.fill_between(x, total, alpha=0.15, color="#D4AF37")
        ax.set_xlabel("Position"); ax.set_ylabel("Dose"); ax.set_title(f"CSI Junction — Gap {gap} cm", fontweight="bold", color="white"); ax.legend(facecolor="#141414", edgecolor="#333333", labelcolor="white"); ax.grid(True, alpha=0.25, color="#333333")
        st.pyplot(fig)
        if gap == 0: st.success("Perfect Junction — No Hot / Cold Spot")
        elif gap > 0: st.error(f"Gap {gap} cm = Cold Spot — Analogous to Young's Destructive Interference")
        else: st.error(f"Overlap {abs(gap)} cm = Hot Spot — Analogous to Young's Constructive Interference")

st.markdown("---")
st.markdown("""
<div style="background: #000000; border: 1px solid #2A2A2A; border-top: 3px solid #D4AF37; padding: 20px 22px; border-radius: 12px; text-align: center; color: white;">
  <div style="font-family: 'Playfair Display', serif; font-size: 18px; font-weight: 700; color: white;">Optics Behind Virtual RT Mirror App</div>
  <div style="font-size: 12.5px; color: #AAAAAA; margin-top: 4px;">Part 1: Simulation &nbsp;|&nbsp; Part 2: Wavelength, Reflection & Young's Interference</div>
  <div style="font-size: 12px; color: #D4AF37; font-weight: 600; margin-top: 8px; letter-spacing: 0.5px;">DEVELOPED BY: NAHEED &nbsp;|&nbsp; BS PHYSICS</div>
</div>
""", unsafe_allow_html=True)
st.caption("Virtual RT Mirror")
