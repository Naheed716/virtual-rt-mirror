import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np, math
st.set_page_config(page_title="Virtual RT Mirror", layout="centered")
st.markdown('<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:15px;border-radius:15px;text-align:center"><h2>🏥 Virtual RT Mirror</h2><p>CT Sim → TPS → LINAC / Cobalt-60</p></div>', unsafe_allow_html=True)
PATIENTS={
"BREAST-LEFT":{"site":"Breast - Left","oar":"Heart","oar_full":"Heart / Lung","limit":20,"mask":False,"dose":50,"fx":25,"w":11,"h":8,"gtv":(2.5,0.5),"oar_pos":(0.3,-1.2),"oar2":(-1.8,-1.0),"color":"#FF9FF3","note":"Left Breast = Image Right | Heart Center me hai | Isko Bachana Hai"},
"BREAST-RIGHT":{"site":"Breast - Right","oar":"Lung","oar_full":"Lung / Liver","limit":20,"mask":False,"dose":50,"fx":25,"w":11,"h":8,"gtv":(-2.5,0.5),"oar_pos":(0.3,-1.2),"oar2":(1.8,-1.0),"color":"#F368E0","note":"Right Breast = Image Left | Heart Door hai"},
"ESOPHAGUS-01":{"site":"Esophagus","oar":"Lung","oar_full":"Lung / Heart / Cord","limit":45,"mask":False,"dose":50,"fx":25,"w":9,"h":9,"gtv":(0,0.5),"oar_pos":(2.2,0.5),"oar2":(-2.2,0.5),"color":"#FF6B6B","note":"Esophagus Center me"},
"NECK-01":{"site":"Head & Neck","oar":"Cord","oar_full":"Cord / Parotid","limit":45,"mask":True,"dose":70,"fx":35,"w":7,"h":9,"gtv":(0.5,1.0),"oar_pos":(0,-2.0),"oar2":(2.0,1.0),"color":"#FF6B6B","note":"Mask zaroori hai"},
"BRAIN-01":{"site":"Brain","oar":"Stem","oar_full":"Brainstem / Optic","limit":54,"mask":True,"dose":60,"fx":30,"w":8,"h":8.5,"gtv":(0.5,0.5),"oar_pos":(0,-1.5),"oar2":(1.5,1.5),"color":"#54A0FF","note":"Mask zaroori hai"},
"PELVIS-01":{"site":"Pelvis","oar":"Bladder","oar_full":"Bladder / Rectum","limit":65,"mask":False,"dose":50,"fx":25,"w":11,"h":9.5,"gtv":(0,0.5),"oar_pos":(0,-2.2),"oar2":(0,2.2),"color":"#1DD1A1","note":"Bladder full, Rectum empty"}}
patient=st.selectbox("👤 Patient Select Karo",list(PATIENTS.keys()),key="ps")
p=PATIENTS[patient]
c1,c2,c3=st.columns(3)
c1.info(f"📍 {p['site']}");c2.info(f"🛡️ {p['oar_full']}");c3.info(f"🎯 {p['dose']} Gy / {p['fx']} Fx")
st.info(f"📝 {p['note']}")
position=st.selectbox("Position",["Supine - Seedha Letna","Prone - Ulta Letna"],key="pos")
st.caption("Supine = Seedha | Prone = Ulta, Breast me Heart bachane ke liye")
mask=st.checkbox("Mask / Immobilization",value=p["mask"],key="msk")
mirror=st.radio("Mirror", ["A - CT Sim","B - TPS","C - LINAC","D - Cobalt-60"],horizontal=True,key="mir")
if mirror=="A - CT Sim":
    st.subheader("🖥️ A - CT Sim - 3 Scans")
    scan_type=st.radio("Scan Type",["1 - Plain Scan","2 - Contrast Scan","3 - Post-Contrast Scan"],horizontal=True,key="st")
    slice_no=st.slider("CT Slice Number",1,20,10,key="sl")
    if "Plain" in scan_type: bg="#F1F2F6";gc="#B2BEC3";al=0.6;desc="Plain: Bina Contrast, Tumor halka";enh="No Enhancement"
        elif "Post" not in scan_type: bg="#FFEAA7";gc="#E17055";al=0.9;desc="Contrast: Tumor bright, Boundary isi me banti hai";enh="Bright"
    else: bg="#FDCB6E";gc="#D63031";al=0.8;desc="Post-Contrast: Washout dekhte hain";enh="Washout"
    st.write(desc)
    if st.button("📸 SCAN",use_container_width=True,key="sb"):
        st.success(f"✅ {scan_type} - Slice {slice_no}/20 - {enh}")
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
        ax.text(0,6.5,"Patient's Left -> Image Right",ha="center",fontsize=7,color="blue",fontweight="bold")
        ax.set_xlim(-7,7);ax.set_ylim(-7,7);ax.set_aspect("equal");ax.set_title(f"CT - {patient} - {scan_type} - Slice {slice_no}",fontweight="bold");ax.grid(True,alpha=0.2)
        st.pyplot(fig);plt.close(fig)
        st.markdown(f"🔴 **GTV** | 🟠 **PTV = GTV + Margin (Bahar)** | 🟡 **{p['oar_full']} - Original Position, Isko Bachana hai**")
elif mirror=="B - TPS":
    st.subheader("📊 B - TPS Mirror")
    dose=st.slider("Prescription Dose (Gy)",30,70,p["dose"],5,key="td")
    beam_type=st.selectbox("Beam Technique",["VMAT - 2 Arcs","3D-CRT - 3 Fields","IMRT - 5 Fields"],key="tb")
    tech={"VMAT - 2 Arcs":0.38,"IMRT - 5 Fields":0.45,"3D-CRT - 3 Fields":0.58}[beam_type]
    oar_dose=round(p["limit"]*tech,1)
    if "BREAST-LEFT" in patient:
        st.warning("⚠️ Left Breast hai, Heart paas hai - Heart Sparing Zaroori hai")
        hp=st.selectbox("Heart Bachane ka Tareeqa",["DIBH - Saans Rok Kar","Prone Position","MLC se Heart Block","VMAT - Beam Ghuma Kar"],key="hp")
        info={"DIBH - Saans Rok Kar":"Saans rokne se Heart peeche chala jata hai","Prone Position":"Ulta letne se Breast latak jati hai, Heart se door","MLC se Heart Block":"MLC Heart ko dhaanp deta hai","VMAT - Beam Ghuma Kar":"Dose sirf GTV par rehta hai"}[hp]
        st.success(f"✅ {hp} - {info} | Heart Secure hai")
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
    if oar_dose<p["limit"]: st.success(f"✅ PTV PASS | {p['oar_full']} = {oar_dose} Gy < {p['limit']} Gy PASS")
    else: st.error(f"❌ OAR FAIL - {oar_dose} Gy > {p['limit']} Gy")
    fig2,ax2=plt.subplots(figsize=(5,3.5));x=np.linspace(0,80,200)
    ax2.plot(x,100/(1+np.exp((x-dose)/3)),color="red",linewidth=3,label=f"PTV - {dose} Gy")
    ax2.plot(x,100/(1+np.exp((x-oar_dose)/4)),color="blue",linewidth=3,label=f"{p['oar_full']} - {oar_dose} Gy")
    ax2.set_xlim(0,80);ax2.set_ylim(0,105);ax2.set_xlabel("Dose (Gy)");ax2.set_ylabel("Volume (%)");ax2.set_title(f"DVH - {patient}");ax2.grid(True,linestyle="--",alpha=0.4);ax2.legend()
    st.pyplot(fig2);plt.close(fig2)
    if st.button("✅ APPROVE",use_container_width=True,key="ap"): st.balloons();st.success("Plan APPROVED - Heart Secure hai")
    elif mirror=="C - LINAC":
    st.subheader("⚡ C - LINAC Mirror")
    gantry=st.slider("Gantry Angle",0,360,90,5,key="lg")
    st.markdown("### 🔲 Collimator Jaws")
    st.caption("X1=Left | X2=Right | Y1=Upper | Y2=Lower | Field X=X1+X2 | Field Y=Y1+Y2")
    j1,j2=st.columns(2)
    with j1: x1=st.slider("X1 - Left Jaw (cm)",0,10,5,1,key="lx1");y1=st.slider("Y1 - Upper Jaw (cm)",0,10,5,1,key="ly1")
    with j2: x2=st.slider("X2 - Right Jaw (cm)",0,10,5,1,key="lx2");y2=st.slider("Y2 - Lower Jaw (cm)",0,10,5,1,key="ly2")
    field_x=x1+x2;field_y=y1+y2;shift_x=(x2-x1)/2;shift_y=(y2-y1)/2
    sym="✅ Symmetric" if x1==x2 and y1==y2 else f"⚠️ Asymmetric - Shift {shift_x:.1f}, {shift_y:.1f} cm"
    st.info(f"**Field: {field_x} x {field_y} cm** | X1 {x1}+X2 {x2}={field_x} | Y1 {y1}+Y2 {y2}={field_y} | {sym}")
    cx=st.slider("Couch X",-5,5,0,key="lcx");cy=st.slider("Couch Y",-5,5,0,key="lcy");cz=st.slider("Couch Z",-5,5,0,key="lcz")
    st.write(f"Gantry {gantry}° | Field {field_x}x{field_y} | SSD 100 cm | 6 MV")
    cbct=st.checkbox("CBCT Matched",value=True,key="lcb")
    if not cbct: st.warning("CBCT NOT Matched - Beam ON nahi hogi")
    b1,b2=st.columns(2)
    with b1: beam_on=st.button("🔴 BEAM ON",use_container_width=True,key="lbo")
    with b2: beam_off=st.button("BEAM OFF",use_container_width=True,key="lbf")
    fig,ax=plt.subplots(figsize=(6,6));fig.patch.set_facecolor('white');ax.set_facecolor('#F8F9FA')
    ax.add_patch(patches.Rectangle((-13,-13),26,26,facecolor="#F1F2F6",edgecolor="gray"))
    ax.text(-12,12,"TREATMENT ROOM",fontsize=8,color="gray",fontweight="bold")
    ax.add_patch(patches.Rectangle((-2,-12),4,6,facecolor="#2F3542",edgecolor="black"));ax.text(0,-9,"GANTRY\nSTAND",ha="center",va="center",fontsize=7,color="white",fontweight="bold")
    ang=math.radians(gantry);dx=math.sin(ang)*10;dy=math.cos(ang)*10
    ax.plot([0,dx],[-6,dy],color="#57606F",linewidth=10,solid_capstyle='round')
    ax.add_patch(patches.FancyBboxPatch((dx-2.2,dy-1.5),4.4,3,boxstyle="round,pad=0.2",facecolor="#2F3542",edgecolor="black"))
    ax.text(dx,dy+0.5,"LINAC HEAD",ha="center",va="center",fontsize=7,color="white",fontweight="bold")
    ax.text(dx,dy-0.5,"Target + MLC",ha="center",va="center",fontsize=6,color="#FFD700")
    jw=max(field_x/2.5,0.8);ax.add_patch(patches.Rectangle((dx-jw/2,dy-2.5),jw,1.0,facecolor="#FFD700",edgecolor="black"))
    ax.text(dx,dy-2.0,f"Jaws {field_x}x{field_y}",ha="center",va="center",fontsize=6,fontweight="bold")
    ax.text(dx+3.5,dy-2.0,f"X1 {x1} | X2 {x2}\nY1 {y1} | Y2 {y2}",fontsize=6,fontweight="bold",bbox=dict(facecolor="white",edgecolor="black"))
    ax.add_patch(patches.Rectangle((-6,-1.5),12,2,facecolor="#57606F",edgecolor="black"));ax.text(0,-0.5,"COUCH",ha="center",va="center",fontsize=7,color="white",fontweight="bold")
    ax.add_patch(patches.Ellipse((cx,cy),5,2.5,facecolor=p["color"],alpha=0.8,edgecolor="black"));ax.text(cx,cy,f"{patient}",ha="center",va="center",fontsize=7,fontweight="bold")
    ax.add_patch(patches.Rectangle((shift_x-field_x/4,shift_y-field_y/4),field_x/2,field_y/2,facecolor="none",edgecolor="red",linewidth=2,linestyle="--"))
    ax.plot([0],[0],marker="+",color="red",markersize=18,markeredgewidth=2.5);ax.text(1.2,0.8,"✚ ISOCENTER",fontsize=7,color="red",fontweight="bold")
    if beam_on and cbct: ax.plot([dx,0],[dy-2.5,0],color="red",linewidth=4,alpha=0.8);ax.text(6,6,"🔴 BEAM ON",fontsize=10,color="red",fontweight="bold",bbox=dict(facecolor="white",edgecolor="red"))
    ax.plot([dx,0],[dy-2.5,0],color="blue",linewidth=1,linestyle="--",alpha=0.5);ax.text(dx/2+1,(dy-2.5)/2,"SSD 100 cm",fontsize=7,color="blue")
    ax.set_xlim(-13,13);ax.set_ylim(-13,13);ax.set_aspect("equal");ax.axis("off");ax.set_title(f"LINAC - Gantry {gantry}° - Field {field_x}x{field_y} cm",fontweight="bold")
    st.pyplot(fig);plt.close(fig)
    if beam_on and not cbct: st.error("Beam ON nahi ho sakti - CBCT Match nahi!")
    elif beam_on: st.error(f"BEAM ON - Gantry {gantry}° - Field {field_x}x{field_y}")
    if beam_off: st.info("Beam OFF - Pause")
    if st.button("🛑 EMERGENCY STOP",use_container_width=True,key="les"): st.error("EMERGENCY STOP")
else:
    st.subheader("☢️ D - Cobalt-60 Mirror")
    st.write("**Source: Co-60 | Half-Life 5.27y | 1.17 + 1.33 MeV | SSD 80 cm**")
    st.markdown("### 🔲 Collimator Jaws (Cobalt me MLC nahi hota)")
    cj1,cj2=st.columns(2)
    with cj1: cx1=st.slider("X1 - Left Jaw (cm)",0,10,5,1,key="cx1");cy1=st.slider("Y1 - Upper Jaw (cm)",0,10,5,1,key="cy1")
    with cj2: cx2=st.slider("X2 - Right Jaw (cm)",0,10,5,1,key="cx2");cy2=st.slider("Y2 - Lower Jaw (cm)",0,10,5,1,key="cy2")
    cfx=cx1+cx2;cfy=cy1+cy2;csx=(cx2-cx1)/2;csy=(cy2-cy1)/2
    csym="✅ Symmetric" if cx1==cx2 and cy1==cy2 else f"⚠️ Asymmetric - Shift {csx:.1f}, {csy:.1f} cm"
    st.info(f"**Field: {cfx} x {cfy} cm** | X1 {cx1}+X2 {cx2}={cfx} | Y1 {cy1}+Y2 {cy2}={cfy} | {csym}")
    years=st.slider("Source Kitna Purana Hai? (Years)",0,10,2,1,key="cy")
    decayed=2.0*(0.5**(years/5.27));dc=max(0.5,min(2.0,round(decayed,2)))
    st.info(f"Calibration: 2.0 Gy/min → Ab {years} saal baad: **{decayed:.2f} Gy/min** (Decay)")
    beams=st.selectbox("Beams",["2 Beams - Lat + Lat","1 Beam - Direct","3 Beams"],key="cb")
    binfo={"2 Beams - Lat + Lat":"Dono side se - Lat=Side se - Skin bachti hai","1 Beam - Direct":"Samne se 1 Beam - Simple, OAR ko zyada Dose","3 Beams":"3 taraf se - OAR sab se zyada bachta hai"}[beams]
    st.write(f"Beam Info: {binfo}")
    dose_c=st.slider("Total Dose (Gy)",30,70,60,5,key="cd");fx=st.slider("Fractions",10,35,30,1,key="cf")
    per_fx=round(dose_c/fx,2);rate=st.slider("Current Dose Rate (Gy/min)",0.5,2.0,dc,0.05,key="cr")
    t=round(per_fx/rate,2) if rate>0 else 0
    st.success(f"Manual Calc: {per_fx} Gy / {rate} Gy/min = **{t} min per Fx** | Field {cfx} x {cfy} cm")
    s1,s2=st.columns(2)
    with s1: source_on=st.button("🟢 SOURCE ON",use_container_width=True,key="con")
    with s2: source_off=st.button("SOURCE OFF",use_container_width=True,key="cof")
    fig2,ax2=plt.subplots(figsize=(6,6));fig2.patch.set_facecolor('white');ax2.set_facecolor('#F8F9FA')
    ax2.add_patch(patches.Rectangle((-13,-13),26,26,facecolor="#FFF3E0",edgecolor="gray"));ax2.text(-12,12,"COBALT ROOM - THICK WALLS",fontsize=8,color="gray",fontweight="bold")
    ax2.add_patch(patches.FancyBboxPatch((-3,5),6,5,boxstyle="round,pad=0.3",facecolor="#2F3542",edgecolor="black"))
    ax2.text(0,9,"SOURCE HEAD",ha="center",va="center",fontsize=8,color="white",fontweight="bold");ax2.text(0,8,"(Lead Shield)",ha="center",va="center",fontsize=6,color="#FFD700")
    col_src="red" if source_on else "gray";ax2.add_patch(patches.Circle((0,6.5),0.9,facecolor=col_src,edgecolor="black"));ax2.text(0,6.5,"Co-60",ha="center",va="center",fontsize=7,color="white",fontweight="bold")
    cjw=max(cfx/2.5,0.8);ax2.add_patch(patches.Rectangle((-cjw/2,3.5),cjw,1.5,facecolor="#FFD700",edgecolor="black"));ax2.text(0,4.2,f"COLLIMATOR {cfx}x{cfy}",ha="center",va="center",fontsize=6,fontweight="bold")
    ax2.text(5.5,4.2,f"X1 {cx1} | X2 {cx2}\nY1 {cy1} | Y2 {cy2}",fontsize=7,bbox=dict(facecolor="white",edgecolor="black"))
    if source_on: ax2.plot([0,0],[3.5,0],color="red",linewidth=4,alpha=0.8);ax2.text(6,6,"🟢 SOURCE ON",fontsize=10,color="red",fontweight="bold",bbox=dict(facecolor="white",edgecolor="red"))
    else: ax2.plot([0,0],[3.5,0],color="gray",linewidth=1,linestyle="--");ax2.text(6,6,"SOURCE OFF\n(Shield Me)",fontsize=8,color="gray",fontweight="bold",bbox=dict(facecolor="white",edgecolor="gray"))
    ax2.add_patch(patches.Rectangle((-6,-1.5),12,2,facecolor="#57606F",edgecolor="black"));ax2.text(0,-0.5,"COUCH",ha="center",va="center",fontsize=7,color="white",fontweight="bold")
    ax2.add_patch(patches.Ellipse((0,0),5,2.5,facecolor=p["color"],alpha=0.8,edgecolor="black"));ax2.text(0,0,f"{patient}",ha="center",va="center",fontsize=7,fontweight="bold")
    ax2.add_patch(patches.Rectangle((csx-cfx/4,csy-cfy/4),cfx/2,cfy/2,facecolor="none",edgecolor="red",linewidth=2,linestyle="--"))
    ax2.plot([0],[0],marker="+",color="red",markersize=18,markeredgewidth=2.5);ax2.text(1.2,0.8,"✚ ISOCENTER",fontsize=7,color="red",fontweight="bold")
    ax2.annotate("",xy=(-4,3.5),xytext=(-4,0),arrowprops=dict(arrowstyle="<->",color="blue"));ax2.text(-5.5,1.7,"SSD\n80 cm",fontsize=7,color="blue",fontweight="bold",ha="center")
    ax2.text(0,-8,f"Decay: {years} saal baad Rate {decayed:.2f} Gy/min - Time {t} min",ha="center",fontsize=8,fontweight="bold",bbox=dict(facecolor="white",edgecolor="green"))
    ax2.set_xlim(-13,13);ax2.set_ylim(-13,13);ax2.set_aspect("equal");ax2.axis("off");ax2.set_title(f"Cobalt-60 - SSD 80 cm - {beams} - Field {cfx}x{cfy}",fontweight="bold")
    st.pyplot(fig2);plt.close(fig2)
    if source_on: st.error(f"SOURCE ON - Co-60 - {beams} - {t} min - SSD 80 cm - Field {cfx}x{cfy}")
    if source_off: st.info("Source OFF - Source Wapas Shield Me")
st.markdown("---")
st.caption("Virtual RT Mirror | CT Sim → TPS → LINAC / Cobalt-60")
