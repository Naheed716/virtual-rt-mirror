import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Virtual RT Dept - Mobile", layout="centered")
st.title("📱 Virtual Radiotherapy Dept")
st.caption("3D + Technologist Screen | Mobile Only | No Hardware | FREE")
st.caption("Patient: NECK-01 | 45Y/M | Right Neck Tumor")

patient = st.selectbox("Patient Chuno", ["NECK-01 - Neck", "BREAST-02 - Breast"])
st.success(f"Patient: {patient} - Selected ✅")

tab1, tab2, tab3, tab4 = st.tabs(["A-CT Sim 3D", "B-TPS 3D", "C-LINAC 3D", "D-Cobalt 3D"])

# ---------- A - CT SIM ----------
with tab1:
    st.header("A - CT Sim Mirror - 3D")
    st.write("**3D Machine:** Gantry + Couch")
    # 3D jaisa dikhne wala simple visual
    fig, ax = plt.subplots(figsize=(5,3))
    ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis('off')
    # Gantry circle - 3D feel
    th = np.linspace(0, 2*np.pi, 100)
    ax.plot(3+2*np.cos(th), 3+2*np.sin(th), color='#1976D2', lw=12, alpha=0.9)
    ax.plot(3+1.2*np.cos(th), 3+1.2*np.sin(th), color='#90CAF9', lw=2)
    ax.text(3,3,'PATIENT\nNECK MASK', ha='center', va='center', fontsize=8, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFF9C4'))
    ax.text(3,5.7,'CT SIM GANTRY - 3D', ha='center', fontsize=9, fontweight='bold', color='#1976D2')
    ax.text(3,0.3,'Couch Aage / Peeche', ha='center', fontsize=8, bbox=dict(boxstyle="round,pad=0.3", facecolor='#C8E6C9'))
    st.pyplot(fig)
    st.subheader("👩‍⚕️ Technologist Screen - CT Sim")
    st.write("Protocol: Neck 3mm | kV 120 | mAs 250 | Slice 3mm")
    st.write("Laser: Tattoo = OK ✅ | Position: Supine + Mask")
    kv = st.slider("kV", 80, 140, 120, key="ct_kv")
    if st.button("🔍 [ START SCAN ]", key="scan"):
        st.balloons()
        N=200; y,x=np.ogrid[:N,:N]; cx,cy=100,105
        body=((x-cx)/65)**2+((y-cy)/68)**2<=1
        hu=np.full((N,N),-1000.); hu[body]=45
        tx,ty=cx-32,cy+8; tum=((x-tx)/18)**2+((y-ty)/20)**2<=1; hu[tum]=68
        cord=((x-cx)/7)**2+((y-(cy+45))/7)**2<=1
        hu[((x-cx)/20)**2+((y-(cy+45))/16)**2<=1]=350; hu[cord]=30
        hu[((x-cx)/12)**2+((y-(cy-32))/11)**2<=1]=-950
        fig2,ax2=plt.subplots(); ax2.imshow(np.clip((hu+150)/400,0,1),cmap='gray'); ax2.set_title(f"CT - {kv} kV | Tumor HU 68 Visible"); ax2.axis('off')
        st.pyplot(fig2)
        st.success("CT Ho Gaya! DICOM TPS ko bhej diya ✅")

# ---------- B - TPS ----------
with tab2:
    st.header("B - TPS Mirror - 3D")
    st.write("**3D Patient:** Tumor Laal, Dose Wash 3D me")
    dose_pres = st.slider("Prescription Dose (Gy)", 50, 70, 70, key="tps_dose")
    if st.button("📊 [ CALCULATE ]", key="tps_calc"):
        N=200; y,x=np.ogrid[:N,:N]; cx,cy=100,105
        body=((x-cx)/65)**2+((y-cy)/68)**2<=1
        tx,ty=cx-32,cy+8
        dose=dose_pres*np.exp(-(((x-tx)**2+(y-ty)**2)/(2*26**2))); dose=dose*body
        fig, axes=plt.subplots(1,2, figsize=(8,3))
        axes[0].imshow(dose, cmap='jet', vmin=0, vmax=75); axes[0].set_title("Dose Wash - VMAT 3D"); axes[0].axis('off')
        ds=np.linspace(0,75,100)
        axes[1].plot(ds, np.clip(105-ds*0.8,0,100), label='PTV', color='darkred', lw=2)
        axes[1].plot(ds, 100*np.exp(-np.maximum(ds-5,0)/8), label='Cord / Parotid', color='green')
        axes[1].axhline(95, ls=':', color='black'); axes[1].axvline(66.5, ls=':', color='black')
        axes[1].set_xlabel("Dose Gy"); axes[1].set_ylabel("Volume %"); axes[1].legend(); axes[1].grid(alpha=0.3)
        st.pyplot(fig)
        st.success(f"Plan PASS ✅ PTV 95% dose mili, Cord <45 Gy")
    st.subheader("👩‍⚕️ Physicist / Tech Screen - TPS")
    st.write("Contour: GTV Red | Cord Yellow | PTV 70 Gy")
    if st.button("✅ [ APPROVE ]", key="approve"):
        st.success("Plan Approved - LINAC ko bheja gaya ✅")

# ---------- C - LINAC ----------
with tab3:
    st.header("C - LINAC Mirror - 3D")
    gantry = st.slider("Gantry Angle (3D me ghoomega)", 0, 360, 90, step=10, key="lin_gantry")
    coll = st.selectbox("Field Size", ["5x5","10x10","15x15","20x20"], key="lin_coll")
    # 3D jaisa Gantry visual - angle se badalta hai
    fig, ax = plt.subplots(figsize=(5,3))
    ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis('off')
    # Gantry arm angle se
    ang = np.deg2rad(gantry)
    x0, y0 = 2, 4.5
    x1, y1 = x0 + 2.5*np.cos(ang), y0 + 1.5*np.sin(ang)
    ax.plot([x0, x1], [y0, y1], color='#1976D2', lw=8)
    ax.add_patch(plt.Circle((x0,y0), 0.6, color='#90CAF9', ec='black'))
    ax.text(x0,y0,'G', ha='center', va='center', fontweight='bold')
    ax.add_patch(plt.Rectangle((5,1.5),3.5,0.6, facecolor='#BDBDBD', ec='black'))
    ax.text(6.7,1.8,'COUCH + PATIENT', ha='center', fontsize=7, fontweight='bold')
    ax.plot([x1, 6.7],[y1, 2.1], color='red', lw=2, ls='--')
    ax.text(5,5.5,f'3D LINAC - Gantry {gantry}°', ha='center', fontsize=10, fontweight='bold', color='#2E7D32')
    ax.text(5,0.4,f'Field {coll} | Beam = Laser (Demo)', ha='center', fontsize=8)
    st.pyplot(fig)
    st.subheader("👩‍⚕️ Technologist Console - LINAC")
    st.info(f"Gantry: {gantry}° | Field: {coll} | MU: 250 | Fraction: 12/35 | CBCT: Matched ✅")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("🟢 BEAM ON", key="lin_on"):
            st.success("BEAM ON - Laser Chal Raha Hai 🔴🔴🔴")
    with c2:
        if st.button("🔴 BEAM OFF", key="lin_off"):
            st.warning("BEAM OFF")
    if st.button("⛔ EMERGENCY STOP", key="lin_stop"):
        st.error("EMERGENCY STOP - Sab Band!")

# ---------- D - COBALT ----------
with tab4:
    st.header("D - Cobalt-60 Mirror - 3D")
    st.write("**3D Cobalt:** Head + Source upar/neeche")
    fig, ax = plt.subplots(figsize=(5,2.5))
    ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis('off')
    ax.add_patch(plt.Rectangle((1,2),2,2, facecolor='#FFCC80', ec='#EF6C00', lw=2))
    ax.text(2,3,'CO-60\nHEAD', ha='center', va='center', fontweight='bold', fontsize=8)
    ax.add_patch(plt.Rectangle((4,1),3.5,0.6, facecolor='#BDBDBD', ec='black'))
    ax.text(5.7,1.3,'COUCH + PATIENT', ha='center', fontsize=7)
    ax.plot([2,5.7],[2,1.6], color='orange', lw=2, ls='--')
    ax.text(5,4.5,'3D COBALT-60 - Source CLICK', ha='center', fontsize=10, fontweight='bold', color='#EF6C00')
    st.pyplot(fig)
    st.subheader("👩‍⚕️ Technologist Console - Cobalt")
    dose = st.number_input("Prescribed Dose (Gy)", value=60, key="co_dose")
    rate = st.number_input("Aaj ki Dose Rate (Gy/min) - Decay Chart se", value=1.2, key="co_rate")
    pdd = st.number_input("PDD (0-1)", value=0.70, key="co_pdd")
    if st.button("🧮 Time Calculate Karo", key="co_calc"):
        t = dose/(rate*pdd)
        st.success(f"Time = {dose} / ({rate} x {pdd}) = **{t:.2f} min**")
        st.write("Formula: Time = Dose / (Dose Rate x PDD x Output x Wedge)")
    st.write("Beams: Ant+Post | Plan: 3D-CRT | Blocks + Wedge | SSD 80cm")
    if st.button("☢️ [ SOURCE ON ]", key="co_on"):
        st.warning("SOURCE ON - CLICK - 3-5 min Treatment")
    if st.button("SOURCE OFF", key="co_off"):
        st.success("SOURCE OFF - Source Wapas Neeche ✅")
    st.caption("Half-Life 5.27y | Energy 1.25 MeV | Neck, Breast, Skin ke liye Best")
