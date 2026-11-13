import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np, math
st.set_page_config(page_title="Virtual RT Mirror", layout="centered")
st.markdown('<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:15px;border-radius:15px;text-align:center"><h2>Virtual RT Mirror</h2><p>CT Sim to TPS to LINAC / Cobalt-60</p></div>', unsafe_allow_html=True)
PATIENTS={
"BREAST-LEFT":{"site":"Breast - Left","oar":"Heart","oar_full":"Heart / Lung","limit":20,"mask":False,"dose":50,"fx":25,"w":11,"h":8,"gtv":(2.5,0.5),"oar_pos":(0.3,-1.2),"oar2":(-1.8,-1.0),"color":"#FF9FF3","note":"Left Breast = Image Right | Heart Center me hai | Isko Bachana Hai"},
"BREAST-RIGHT":{"site":"Breast - Right","oar":"Lung","oar_full":"Lung / Liver","limit":20,"mask":False,"dose":50,"fx":25,"w":11,"h":8,"gtv":(-2.5,0.5),"oar_pos":(0.3,-1.2),"oar2":(1.8,-1.0),"color":"#F368E0","note":"Right Breast = Image Left | Heart Door hai"},
"ESOPHAGUS-01":{"site":"Esophagus","oar":"Lung","oar_full":"Lung / Heart / Cord","limit":45,"mask":False,"dose":50,"fx":25,"w":9,"h":9,"gtv":(0,0.5),"oar_pos":(2.2,0.5),"oar2":(-2.2,0.5),"color":"#FF6B6B","note":"Esophagus Center me"},
"NECK-01":{"site":"Head and Neck","oar":"Cord","oar_full":"Cord / Parotid","limit":45,"mask":True,"dose":70,"fx":35,"w":7,"h":9,"gtv":(0.5,1.0),"oar_pos":(0,-2.0),"oar2":(2.0,1.0),"color":"#FF6B6B","note":"Mask zaroori hai"},
"BRAIN-01":{"site":"Brain","oar":"Stem","oar_full":"Brainstem / Optic","limit":54,"mask":True,"dose":60,"fx":30,"w":8,"h":8.5,"gtv":(0.5,0.5),"oar_pos":(0,-1.5),"oar2":(1.5,1.5),"color":"#54A0FF","note":"Mask zaroori hai"},
"PELVIS-01":{"site":"Pelvis","oar":"Bladder","oar_full":"Bladder / Rectum","limit":65,"mask":False,"dose":50,"fx":25,"w":11,"h":9.5,"gtv":(0,0.5),"oar_pos":(0,-2.2),"oar2":(0,2.2),"color":"#1DD1A1","note":"Bladder full, Rectum empty"}}
patient=st.selectbox("Patient Select Karo",list(PATIENTS.keys()),key="ps")
p=PATIENTS[patient]
c1,c2,c3=st.columns(3)
c1.info(f"Site {p['site']}");c2.info(f"OAR {p['oar_full']}");c3.info(f"Dose {p['dose']} Gy / {p['fx']} Fx")
st.info(f"Note {p['note']}")
position=st.selectbox("Position",["Supine - Seedha Letna","Prone - Ulta Letna"],key="pos")
st.caption("Supine = Seedha | Prone = Ulta, Breast me Heart bachane ke liye")
mask=st.checkbox("Mask / Immobilization",value=p["mask"],key="msk")
mirror=st.radio("Mirror", ["A - CT Sim","B - TPS","C - LINAC","D - Cobalt-60"],horizontal=True,key="mir")
if mirror=="A - CT Sim":
    st.subheader("A - CT Sim - 3 Scans")
    scan_type=st.radio("Scan Type",["1 - Plain Scan","2 - Contrast Scan","3 - Post-Contrast Scan"],horizontal=True,key="st")
    slice_no=st.slider("CT Slice Number",1,20,10,key="sl")
    if "Plain" in scan_type: bg="#F1F2F6";gc="#B2BEC3";al=0.6;desc="Plain: Bina Contrast, Tumor halka";enh="No Enhancement"
    elif "Post" not in scan_type: bg="#FFEAA7";gc="#E17055";al=0.9;desc="Contrast: Tumor bright, Boundary isi me banti hai";enh="Bright"
    else: bg="#FDCB6E";gc="#D63031";al=0.8;desc="Post-Contrast: Washout dekhte hain";enh="Washout"
    st.write(desc)
    if st.button("SCAN",use_container_width=True,key="sb"):
        st.success(f"{scan_type} - Slice {slice_no}/20 - {enh}")
        fig,ax=plt.subplots(figsize=(5,5));ax.set_facecolor(bg)
        ax.add_patch(patches.Ellipse((0,0),p["w"],p["h"],facecolor="#E8E8E8",edgecolor="black"))
        gr=1.2 if 8<=slice_no<=12 else 0.7
        ax.add_patch(patches.Circle(p["gtv"],gr+0.6,facecolor="none",edgecolor="orange",linewidth=2,linestyle="--"))
        ax.text(p["gtv"][0],p["gtv"][1]+gr+0.9,"PTV",ha="center",fontsize=8,color="orange",fontweight="bold")
        ax.add_patch(patches.Circle(p["gtv"],gr,facecolor=gc,alpha=al,edgecolor="black"))
        ax.text(p["gtv"][0],p["gtv"][1],"GTV",ha="center",va="center",fontsize=9,fontweight="bold",color="black")
        ax.add_patch(patches.Circle(p["oar_pos"],0.9,facecolor="yellow",edgecolor="black"))
        ax.text(p["oar_pos"][0],p["oar_pos"][1],p["oar"],ha="center",va="center",fontsize=6,fontweight="bold")
        ax.add_patch(patches.Circle(p["oar2"],0.7,facecolor="lightblue",edgecolor="black"))
        ax.text(p["oar2"][0],p["oar2"][1],"OAR-2",ha="center",va="center",fontsize=6,fontweight="bold")
        ax.text(0,6.5,"Patient Left = Image Right",ha="center",fontsize=7,color="blue",fontweight="bold")
        ax.set_xlim(-7,7);ax.set_ylim(-7,7);ax.set_aspect("equal");ax.set_title(f"CT - {patient} - {scan_type} - Slice {slice_no}",fontweight="bold");ax.grid(True,alpha=0.2)
        st.pyplot(fig);plt.close(fig)
        st.markdown(f"GTV = Tumor | PTV = GTV + Margin (Bahar) | {p['oar_full']} - Original Position, Isko Bachana hai")
elif mirror=="B - TPS":
    st.subheader("B - TPS Mirror")
    dose=st.slider("Prescription Dose (Gy)",30,70,p["dose"],5,key="td")
    beam_type=st.selectbox("Beam Technique",["VMAT - 2 Arcs","3D-CRT - 3 Fields","IMRT - 5 Fields"],key="tb")
    tech={"VMAT - 2 Arcs":0.38,"IMRT - 5 Fields":0.45,"3D-CRT - 3 Fields":0.58}[beam_type]
    oar_dose=round(p["limit"]*tech,1)
    if "BREAST-LEFT" in patient:
        st.warning("Left Breast hai, Heart paas hai - Heart Sparing Zaroori hai")
        hp=st.selectbox("Heart Bachane ka Tareeqa",["DIBH - Saans Rok Kar","Prone Position","MLC se Heart Block","VMAT - Beam Ghuma Kar"],key="hp")
        info={"DIBH - Saans Rok Kar":"Saans rokne se Heart peeche chala jata hai","Prone Position":"Ulta letne se Breast latak jati hai, Heart se door","MLC se Heart Block":"MLC Heart ko dhaanp deta hai","VMAT - Beam Ghuma Kar":"Dose sirf GTV par rehta hai"}[hp]
        st.success(f"{hp} - {info} | Heart Secure hai")
    fig0,ax0=plt.subplots(figsize=(5,3))
    ax0.add_patch(patches.Ellipse((0,0),p["w"],p["h"],facecolor="#E8E8E8",edgecolor="black"))
    col="#FFEB3B" if dose<=40 else "#FF9800" if dose<=55 else "#F44336"
    ax0.add_patch(patches.Circle(p["gtv"],2.5,facecolor=col,alpha=0.4))
    ax0.add_patch(patches.Circle(p["gtv"],0.8,facecolor="red",alpha=0.9))
    ax0.text(p["gtv"][0],p["gtv"][1],f"{dose} Gy",ha="center",va="center",fontsize=9,fontweight="bold",color="white")
    ax0.add_patch(patches.Circle(p["oar_pos"],0.9,facecolor="yellow",edgecolor="black"))
    ax0.text(p["oar_pos"][0],p["oar_pos"][1],p["oar"],ha="center",va="center",fontsize=6,fontweight="bold")
    ax0.set_xlim(-7,7);ax0.set_ylim(-7,7);ax0.set_aspect("equal");ax0.set_title(f"Dose Wash - {dose} Gy - Heart Bachaya Hua");ax0.axis("off")
    st.pyplot(fig0);plt.close(fig0)
    if oar_dose<p["limit"]: st.success(f"PTV PASS | {p['oar_full']} = {oar_dose} Gy < {p['limit']} Gy PASS")
    else: st.error(f"OAR FAIL - {oar_dose} Gy > {p['limit']} Gy")
    fig2,ax2=plt.subplots(figsize=(5,3.5));x=np.linspace(0,80,200)
    ax2.plot(x,100/(1+np.exp((x-dose)/3)),color="red",linewidth=3,label=f"PTV - {dose} Gy")
    ax2.plot(x,100/(1+np.exp((x-oar_dose)/4)),color="blue",linewidth=3,label=f"{p['oar_full']} - {oar_dose} Gy")
    ax2.set_xlim(0,80);ax2.set_ylim(0,105);ax2.set_xlabel("Dose (Gy)");ax2.set_ylabel("Volume (%)");ax2.set_title(f"DVH - {patient}");ax2.grid(True,linestyle="--",alpha=0.4);ax2.legend()
    st.pyplot(fig2);plt.close(fig2)
    if st.button("APPROVE",use_container_width=True,key="ap"): st.balloons();st.success("Plan APPROVED - Heart Secure hai")
