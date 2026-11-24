import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np, math

st.set_page_config(page_title="Virtual RT Mirror | Radiotherapy Simulation", layout="centered")

# ---------- STYLE ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#0A0A0A;color:#F1F1F1}
.main{background:#0A0A0A} h1,h2,h3,h4{font-family:'Playfair Display',serif;color:#fff}
p,label,span,div{color:#E5E5E5}
.stRadio>div{background:#141414;padding:8px 12px;border-radius:10px;border:1px solid #2A2A2A}
.stSelectbox>div>div{border-radius:8px!important;border:1px solid #333!important;background:#141414!important;color:#fff!important}
.stSelectbox div[data-baseweb="select"] span{color:#fff!important}
.stSlider>div>div>div>div{background:#D4AF37!important}
.stButton>button{border-radius:8px!important;font-weight:600!important;height:46px!important;font-size:14px!important;background:#D4AF37!important;color:#000!important;border:none!important}
.stButton>button:hover{background:#fff!important;color:#000!important}
div[data-testid="stExpander"]{background:#141414;border-radius:10px;border:1px solid #2A2A2A}
hr{border-color:#2A2A2A} table{color:#fff!important}
</style>""", unsafe_allow_html=True)

def card(html): st.markdown(html, unsafe_allow_html=True)
def box(text, accent="#D4AF37"):
    card(f'<div style="background:#141414;padding:12px 14px;border-radius:8px;border:1px solid #2A2A2A;border-left:4px solid {accent};font-size:13px;color:#EEE">{text}</div>')
def dark_fig(w=5,h=3):
    fig,ax=plt.subplots(figsize=(w,h)); fig.patch.set_facecolor('#141414'); ax.set_facecolor('#0A0A0A')
    ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white'); ax.title.set_color('white')
    for s in ax.spines.values(): s.set_color('#333333')
    return fig,ax
def style_ax(ax): ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white'); ax.title.set_color('white')

# ---------- HEADER ----------
card("""
<div style="background:linear-gradient(135deg,#000 0%,#111 55%,#1E1E1E 100%);border:1px solid #2A2A2A;border-left:4px solid #D4AF37;padding:28px 24px;border-radius:14px">
<div style="font-family:'Playfair Display',serif;font-size:32px;font-weight:700;line-height:1.1">Virtual RT Mirror</div>
<div style="font-size:14px;color:#BBB">CT Simulation &nbsp;→&nbsp; Treatment Planning &nbsp;→&nbsp; LINAC / Cobalt-60 Delivery</div>
<div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap">
<span style="background:#1E1E1E;border:1px solid #333;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:600">PART 1 &nbsp;|&nbsp; Simulation</span>
<span style="background:#D4AF37;color:#000;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700">PART 2 &nbsp;|&nbsp; Optics Behind It</span></div></div>""")
st.write("")

PATIENTS={
 "BREAST-LEFT":{"site":"Breast - Left","oar":"Heart / Lung","limit":20,"mask":False,"dose":50,"fx":25,"w":11,"h":8,"gtv":(2.5,0.5),"oar_pos":(-1,-1),"oar2":(.5,-1.8),"color":"#D4AF37","note":"Left Breast = Image Right. Heart is close, therefore OAR is Heart.","devices":["Breast Board","Knee and Foot Lock"]},
 "BREAST-RIGHT":{"site":"Breast - Right","oar":"Lung / Liver","limit":20,"mask":False,"dose":50,"fx":25,"w":11,"h":8,"gtv":(-2.5,.5),"oar_pos":(1,-1),"oar2":(.5,-1.8),"color":"#888888","note":"Right Breast = Image Left. Heart is away, therefore OAR is Lung.","devices":["Breast Board","Knee and Foot Lock"]},
 "ESOPHAGUS":{"site":"Esophagus","oar":"Lung / Heart / Cord","limit":45,"mask":False,"dose":50,"fx":25,"w":9,"h":9,"gtv":(0,.5),"oar_pos":(2.2,.5),"oar2":(-2.2,.5),"color":"#B45309","note":"Esophagus in center. Lung on both sides, Cord posterior, Heart anterior.","devices":["Knee and Foot Lock","Head Rest B"]},
 "HEAD & NECK":{"site":"Head & Neck","oar":"Cord / Parotid","limit":45,"mask":True,"dose":70,"fx":35,"w":7,"h":9,"gtv":(.5,1),"oar_pos":(0,-2),"oar2":(2,1),"color":"#7C3AED","note":"Head + Neck combined. Mask is required. Shoulder Puller is used.","devices":["Thermoplastic Mask","Head Rest E","Head Rest B","Shoulder Puller"]},
 "BRAIN":{"site":"Brain","oar":"Brainstem / Optic","limit":54,"mask":True,"dose":60,"fx":30,"w":8,"h":8.5,"gtv":(.5,.5),"oar_pos":(0,-1.5),"oar2":(1.5,1.5),"color":"#FFFFFF","note":"Mask is required.","devices":["Thermoplastic Mask","Head Rest E"]},
 "PELVIS":{"site":"Pelvis","oar":"Bladder / Rectum","limit":65,"mask":False,"dose":50,"fx":25,"w":11,"h":9.5,"gtv":(0,.5),"oar_pos":(0,-2.2),"oar2":(0,2.2),"color":"#D4AF37","note":"Bladder full, Rectum empty.","devices":["Knee and Foot Lock","Head Rest B"]},
 "ABDOMEN":{"site":"Abdomen","oar":"Liver / Kidney / Bowel","limit":30,"mask":False,"dose":45,"fx":25,"w":11,"h":9,"gtv":(0,.5),"oar_pos":(2.5,.5),"oar2":(-2.5,-1),"color":"#92400E","note":"Abdomen in center. Liver right, Kidney both sides, Bowel anterior.","devices":["Knee and Foot Lock","Head Rest B"]},
 "CSI":{"site":"Cranio-Spinal (CSI)","oar":"Heart / Lung / Kidney","limit":20,"mask":True,"dose":36,"fx":20,"w":7,"h":14,"gtv":(0,4),"oar_pos":(2,-1),"oar2":(-2,-1),"color":"#BE123C","note":"Brain + Full Spine. 3 Fields Join. Junction - Overlap / Gap risk. Mostly in children - Medulloblastoma.","devices":["Thermoplastic Mask","Knee and Foot Lock","Head Rest B"]},
}
DEVICES={
 "Thermoplastic Mask":"Warm plastic that is soft on the face and becomes hard on cooling. Prevents head movement. Used in Brain, Head & Neck and CSI.",
 "Knee and Foot Lock":"Locks knees and feet together. Legs remain at the same angle every day. Used in Breast, Pelvis, Abdomen, Esophagus and CSI.",
 "Breast Board":"Board for breast patients. Keeps both arms elevated and lifts the chest. Used in Breast.",
 "Head Rest E":"Head Rest Type E — For head and neck patients with extended neck position. Keeps the head tilted back.",
 "Head Rest B":"Head Rest Type B — For head and neck patients with neutral neck position. Keeps the head straight.",
 "Shoulder Puller":"Pulls shoulders down, so the neck area becomes clear and visible. Used in Head & Neck."}

def prof_card(label,value,accent="#D4AF37"):
    card(f'<div style="background:#141414;padding:16px 12px;border-radius:12px;border:1px solid #2A2A2A;border-top:3px solid {accent};text-align:center"><div style="font-size:11px;letter-spacing:1.2px;color:#999;font-weight:700">{label}</div><div style="font-size:15px;color:#fff;font-weight:700;margin-top:6px;line-height:1.3">{value}</div></div>')

def jaw_sliders(prefix):
    c1,c2=st.columns(2)
    with c1: x1=st.slider("X1 — Left Jaw (cm)",0,10,5,1,key=prefix+"x1"); y1=st.slider("Y1 — Upper Jaw (cm)",0,10,5,1,key=prefix+"y1")
    with c2: x2=st.slider("X2 — Right Jaw (cm)",0,10,5,1,key=prefix+"x2"); y2=st.slider("Y2 — Lower Jaw (cm)",0,10,5,1,key=prefix+"y2")
    fx,fy=x1+x2,y1+y2; sx,sy=(x2-x1)/2,(y2-y1)/2
    sym="Symmetric Field — Centered" if x1==x2 and y1==y2 else f"Asymmetric Field — Shift {sx:.1f} cm X, {sy:.1f} cm Y"
    box(f"<b style='color:white'>Field Size: {fx} x {fy} cm</b> &nbsp;|&nbsp; X1 {x1} + X2 {x2} = {fx} &nbsp;|&nbsp; Y1 {y1} + Y2 {y2} = {fy} &nbsp;|&nbsp; {sym}")
    return x1,x2,y1,y2,fx,fy,sx,sy

def qa_table(rows, passed, name, freq):
    st.table({"QA Test":[r[0] for r in rows],"Result":[r[1] for r in rows],"Tolerance":[r[2] for r in rows],"Status":["PASS" if r[3] else "FAIL" for r in rows]})
    if passed: st.success(f"{name} {freq} PASSED — Machine is safe for treatment.")
    else: st.error(f"{name} {freq} FAILED — Do NOT treat. Contact Physicist.")

part=st.radio("Select Section",["PART 1 — Virtual RT Mirror","PART 2 — Optics Behind It"],horizontal=True)

# ================= PART 1 =================
if "PART 1" in part:
    patient=st.selectbox("Select Patient / Site",list(PATIENTS.keys())); p=PATIENTS[patient]
    c1,c2,c3=st.columns(3)
    with c1: prof_card("SITE",p["site"])
    with c2: prof_card("ORGAN AT RISK",p["oar"],"#FFFFFF")
    with c3: prof_card("PRESCRIBED DOSE",f"{p['dose']} Gy / {p['fx']} Fractions","#B45309")
    st.write(""); box(f"<b style='color:white'>Clinical Note:</b> {p['note']}")

    st.markdown("### Immobilization Devices")
    st.caption("Immobilization — Keeping the patient in the exact same position every day, so radiation is delivered to the same target daily.")
    device=st.selectbox("Select Immobilization Device",list(DEVICES.keys()))
    box(f"<b style='color:white'>{device}:</b> {DEVICES[device]}")
    st.write(f"**Commonly used for this patient:** {', '.join(p['devices'])}")

    position=st.selectbox("Position",["Supine — Patient lying straight, face up","Prone — Patient lying face down"])
    st.caption("Supine — Patient lying straight, face up. Most commonly used." if "Supine" in position else "Prone — Patient lying face down. Used in Breast to spare Heart, in CSI to keep Spine straight.")
    st.checkbox(f"Mask / Immobilization {'(Required)' if p['mask'] else '(Not Used)'}",value=p["mask"])
    mirror=st.radio("Select Module",["A — CT Sim","B — TPS","C — LINAC","D — Cobalt-60"],horizontal=True)

    # ---- A: CT ----
    if mirror=="A — CT Sim":
        st.subheader("A — CT Simulation")
        scan_type=st.radio("Scan Protocol",["1 — Plain Scan","2 — Contrast Scan","3 — Post-Contrast Scan"],horizontal=True)
        slice_no=st.slider("CT Slice Number",1,20,10)
        if "Plain" in scan_type: gtv_col,gtv_a,desc,enh="#94A3B8",.7,"Plain Scan: Without contrast. Only anatomy is visible. Tumor appears faint.","No Enhancement"
        elif "Post" not in scan_type: gtv_col,gtv_a,desc,enh="#DC2626",.9,"Contrast Scan: After contrast injection. Tumor becomes bright, vessels visible. GTV is contoured on this scan.","Bright Enhancement"
        else: gtv_col,gtv_a,desc,enh="#B45309",.85,"Post-Contrast Scan: 60–90 sec after contrast. Washout of tumor is seen. Difference between OAR and tumor becomes clear.","Washout Phase"
        st.write(desc)
        if st.button("ACQUIRE SCAN",use_container_width=True):
            st.success(f"{scan_type} acquired — Slice {slice_no}/20 — {p['site']} — {enh}")
            fig,ax=dark_fig(5,5); ax.set_facecolor("#1A1A1A")
            ax.add_patch(patches.Ellipse((0,0),6,12 if patient=="CSI" else p["w"],12 if patient=="CSI" else p["h"],facecolor="#222222",edgecolor="white",linewidth=1.8))
            gr=1.2 if 8<=slice_no<=12 else .7
            ax.add_patch(patches.Circle(p["gtv"],gr+.6,facecolor="none",edgecolor="#D4AF37",linewidth=2,linestyle="--"))
            ax.text(p["gtv"][0],p["gtv"][1]+gr+.9,"PTV",ha="center",fontsize=9,color="#D4AF37",fontweight="bold")
            ax.add_patch(patches.Circle(p["gtv"],gr,facecolor=gtv_col,alpha=gtv_a,edgecolor="white"))
            ax.text(p["gtv"][0],p["gtv"][1],"GTV",ha="center",va="center",fontsize=10,fontweight="bold",color="white")
            ax.add_patch(patches.Circle(p["oar_pos"],.7,facecolor="#D4AF37",edgecolor="white"))
            ax.text(p["oar_pos"][0],p["oar_pos"][1],p["oar"].split("/")[0],ha="center",va="center",fontsize=7,fontweight="bold",color="black")
            ax.add_patch(patches.Circle(p["oar2"],.7,facecolor="#444444",edgecolor="white"))
            ax.text(p["oar2"][0],p["oar2"][1],"OAR-2",ha="center",va="center",fontsize=6,fontweight="bold",color="white")
            ax.text(0,6.5,"Patient Left → Image Right",ha="center",fontsize=8,color="white",fontweight="bold")
            ax.text(0,-6.5,f"{scan_type} | {enh}",ha="center",fontsize=8,fontweight="bold",color="black",bbox=dict(facecolor="white",edgecolor="#D4AF37",boxstyle="round,pad=0.4"))
            ax.set_xlim(-7,7); ax.set_ylim(-7,7); ax.set_aspect("equal"); ax.set_title(f"CT — {patient} — {scan_type} — Slice {slice_no}",fontweight="bold",fontsize=11); ax.grid(True,alpha=.2,color="#444444")
            st.pyplot(fig)
            st.markdown(f"**GTV** — Gross Tumor Volume &nbsp;|&nbsp; **PTV Ring** — Planning Target Volume &nbsp;|&nbsp; **OAR** — {p['oar']}")
            st.table({"Scan":["Plain","Contrast","Post-Contrast"],"Visibility":["Anatomy Only","Tumor Bright + Vessels","Washout + OAR Clear"],"GTV Contour":["Difficult","Best — Contoured Here","For Confirmation"]})

    # ---- B: TPS ----
    elif mirror=="B — TPS":
        st.subheader("B — Treatment Planning System (TPS)")
        if patient=="CSI":
            st.warning("CSI — 3 Fields: Brain + Upper Spine + Lower Spine. Check Junction carefully.")
            jgap=st.slider("Junction Gap / Overlap (cm)",-1.,1.,0.,.1)
            if jgap==0: st.success("Perfect Junction — No Gap, No Overlap")
            elif jgap>0: st.error(f"Gap {jgap} cm — Cold Spot — Tumor will not receive dose.")
            else: st.error(f"Overlap {abs(jgap)} cm — Hot Spot — Double Dose.")
            fig,ax=dark_fig(5,3); ax.set_facecolor('#141414')
            for y,txt,fc,tc in [(1,"BRAIN FIELD","#111111","white"),(0,"SPINE FIELD 1","#D4AF37","black"),(-1,"SPINE FIELD 2","#444444","white")]:
                ax.add_patch(patches.Rectangle((-3,y-.5),6,1,facecolor=fc,alpha=.95,edgecolor="white")); ax.text(0,y,txt,ha="center",fontsize=8,fontweight="bold",color=tc)
            ax.plot([jgap,jgap],[-1.5,1.5],color="#DC2626",linewidth=2.5,linestyle="--"); ax.text(jgap+.3,1.7,f"Junction {jgap} cm",fontsize=8,color="#DC2626",fontweight="bold")
            ax.set_xlim(-4,4); ax.set_ylim(-2,2); ax.set_title("CSI — Field Junction",fontweight="bold"); ax.axis("off"); st.pyplot(fig)
        dose=st.slider("Prescription Dose (Gy)",30,70,p["dose"],5)
        beam_type=st.selectbox("Beam Technique",["VMAT — 2 Arcs","3D-CRT — 3 Fields","IMRT — 5 Fields"])
        tech={"VMAT — 2 Arcs":.38,"IMRT — 5 Fields":.45,"3D-CRT — 3 Fields":.58}[beam_type]
        oar_dose=round(p["limit"]*tech,1)
        fig,ax=dark_fig(5,3); ax.set_facecolor('#141414')
        ax.add_patch(patches.Ellipse((0,0),p["w"],p["h"],facecolor="#1E1E1E",edgecolor="white",linewidth=1.5))
        col="#F59E0B" if dose<=40 else "#EA580C" if dose<=55 else "#DC2626"
        ax.add_patch(patches.Circle(p["gtv"],2.5,facecolor=col,alpha=.3)); ax.add_patch(patches.Circle(p["gtv"],.8,facecolor="#DC2626",alpha=.95))
        ax.text(p["gtv"][0],p["gtv"][1],f"{dose} Gy",ha="center",va="center",fontsize=10,fontweight="bold",color="white")
        ax.set_xlim(-7,7); ax.set_ylim(-7,7); ax.set_aspect("equal"); ax.set_title(f"Dose Wash — {dose} Gy — {beam_type}",fontsize=11,fontweight="bold"); ax.axis("off"); st.pyplot(fig)
        if oar_dose<p["limit"]: st.success(f"PTV 95% PASS | {p['oar']} = {oar_dose} Gy < {p['limit']} Gy PASS")
        else: st.error(f"OAR FAIL — {oar_dose} Gy > {p['limit']} Gy")
        fig,ax=dark_fig(5,3.5); ax.set_facecolor('#141414'); style_ax(ax)
        x=np.linspace(0,80,200)
        ax.plot(x,100/(1+np.exp((x-dose)/3)),color="#DC2626",linewidth=2.5,label=f"PTV — {dose} Gy")
        ax.plot(x,100/(1+np.exp((x-oar_dose)/4)),color="#D4AF37",linewidth=2.5,label=f"{p['oar']} — {oar_dose} Gy")
        ax.set_xlim(0,80); ax.set_ylim(0,105); ax.set_xlabel("Dose (Gy)"); ax.set_ylabel("Volume (%)"); ax.set_title(f"DVH — {patient} — {beam_type}",fontweight="bold"); ax.grid(True,linestyle="--",alpha=.25,color="#444444"); ax.legend(frameon=True,facecolor="#141414",edgecolor="#333333",labelcolor="white"); st.pyplot(fig)
        if st.button("APPROVE PLAN",use_container_width=True): st.balloons(); st.success("Plan Approved")

    # ---- C: LINAC ----
    elif mirror=="C — LINAC":
        st.subheader("C — Linear Accelerator (LINAC)")
        gantry=st.slider("Gantry Angle",0,360,90,5)
        st.markdown("### Collimator Jaws — Field Setting"); st.caption("X1 = Left Jaw | X2 = Right Jaw | Y1 = Upper Jaw | Y2 = Lower Jaw | Field X = X1 + X2 | Field Y = Y1 + Y2")
        x1,x2,y1,y2,field_x,field_y,shift_x,shift_y=jaw_sliders("L")
        cx=st.slider("Couch X",-5,5,0); cy=st.slider("Couch Y",-5,5,0); cz=st.slider("Couch Z",-5,5,0)
        st.write(f"Gantry: {gantry}° | Field: {field_x} x {field_y} cm | Couch: {cx}, {cy}, {cz} | SSD 100 cm | Energy 6 MV")
        cbct=st.checkbox("CBCT Matched",value=True)
        if not cbct: st.warning("CBCT Not Matched — Beam will NOT turn ON")
        b1,b2=st.columns(2)
        with b1: beam_on=st.button("BEAM ON",use_container_width=True)
        with b2: beam_off=st.button("BEAM OFF",use_container_width=True)
        fig,ax=plt.subplots(figsize=(6,6)); fig.patch.set_facecolor('#141414'); ax.set_facecolor('#0A0A0A'); ax.title.set_color('white')
        ax.add_patch(patches.Rectangle((-13,-13),26,26,facecolor="#111111",edgecolor="#2A2A2A")); ax.text(-12,12,"TREATMENT ROOM",fontsize=8,color="#999999",fontweight="bold")
        ax.add_patch(patches.Rectangle((-2,-12),4,6,facecolor="#000000",edgecolor="white")); ax.text(0,-9,"GANTRY\nSTAND",ha="center",va="center",fontsize=7,color="white",fontweight="bold")
        ang=math.radians(gantry); dx=math.sin(ang)*10; dy=math.cos(ang)*10
        ax.plot([0,dx],[-6,dy],color="#666666",linewidth=10,solid_capstyle='round')
        ax.add_patch(patches.FancyBboxPatch((dx-2.2,dy-1.5),4.4,3,boxstyle="round,pad=0.2",facecolor="#000000",edgecolor="white",linewidth=1.2))
        ax.text(dx,dy+.5,"LINAC HEAD",ha="center",va="center",fontsize=7,color="white",fontweight="bold"); ax.text(dx,dy-.5,"Target + MLC",ha="center",va="center",fontsize=6,color="#D4AF37")
        jaw_w=max(field_x/2.5,.8); ax.add_patch(patches.Rectangle((dx-jaw_w/2,dy-2.5),jaw_w,1,facecolor="#D4AF37",edgecolor="white"))
        ax.text(dx,dy-2,f"Jaws {field_x}x{field_y}",ha="center",va="center",fontsize=6,fontweight="bold",color="black")
        ax.text(dx+3.5,dy-2,f"X1 {x1} | X2 {x2}\nY1 {y1} | Y2 {y2}",fontsize=6,fontweight="bold",color="black",bbox=dict(facecolor="white",edgecolor="#D4AF37",boxstyle="round,pad=0.3"))
        ax.add_patch(patches.Rectangle((-6,-1.5),12,2,facecolor="#333333",edgecolor="white")); ax.text(0,-.5,"COUCH",ha="center",va="center",fontsize=7,color="white",fontweight="bold")
        ax.add_patch(patches.Ellipse((cx,cy),5,2.5,facecolor=p["color"],alpha=.9,edgecolor="white"))
        ax.text(cx,cy,f"{patient}",ha="center",va="center",fontsize=7,fontweight="bold",color="black" if p["color"] in ["#D4AF37","#FFFFFF"] else "white")
        ax.add_patch(patches.Rectangle((shift_x-field_x/4,shift_y-field_y/4),field_x/2,field_y/2,facecolor="none",edgecolor="#DC2626",linewidth=2,linestyle="--"))
        ax.plot([0],[0],marker="+",color="#DC2626",markersize=16,markeredgewidth=2.2); ax.text(1.2,.8,"ISOCENTER\n(Tumor Center)",fontsize=7,color="#DC2626",fontweight="bold")
        if beam_on and cbct:
            ax.plot([dx,0],[dy-2.5,0],color="#DC2626",linewidth=4,alpha=.85); ax.plot([dx,0],[dy-2.5,0],color="#D4AF37",linewidth=1.5,alpha=.9)
            ax.text(6,6,"BEAM ON",fontsize=10,color="#DC2626",fontweight="bold",bbox=dict(facecolor="white",edgecolor="#DC2626",boxstyle="round,pad=0.3"))
        ax.plot([dx,0],[dy-2.5,0],color="#D4AF37",linewidth=1,linestyle="--",alpha=.6); ax.text(dx/2+1,(dy-2.5)/2,"SSD 100 cm",fontsize=7,color="#D4AF37")
        ax.add_patch(patches.Rectangle((8,-11),3,2,facecolor="#222222",edgecolor="white")); ax.text(9.5,-10,"CBCT",ha="center",va="center",fontsize=7,fontweight="bold",color="white")
        ax.plot([-11,-6],[0,0],color="#D4AF37",linewidth=1,linestyle=":"); ax.text(-11,.8,"LASER",fontsize=6,color="#D4AF37",fontweight="bold")
        ax.set_xlim(-13,13); ax.set_ylim(-13,13); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(f"LINAC — Gantry {gantry}° — Field {field_x} x {field_y} cm",fontweight="bold"); st.pyplot(fig)
        st.caption("X1 Left | X2 Right | Y1 Upper | Y2 Lower | MLC = Field Shape | Isocenter = Tumor Center | SSD 100 cm | CBCT = Position Verification")
        if beam_on and not cbct: st.error("Beam cannot turn ON — CBCT Not Matched.")
        ax.set_xlim(-13,13); ax.set_ylim(-13,13); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(f"LINAC — Gantry {gantry}° — Field {field_x} x {field_y} cm",fontweight="bold"); st.pyplot(fig)
        st.caption("X1 Left | X2 Right | Y1 Upper | Y2 Lower | MLC = Field Shape | Isocenter = Tumor Center | SSD 100 cm | CBCT = Position Verification")
        if beam_on and not cbct: st.error("Beam cannot turn ON — CBCT Not Matched.")
        elif beam_on: st.error(f"BEAM ON — Gantry {gantry}° — Field {field_x} x {field_y} cm")
        if beam_off: st.info("Beam OFF — Pause")
        if st.button("EMERGENCY STOP",use_container_width=True): st.error("EMERGENCY STOP")
        st.markdown("---"); st.markdown("### LINAC QA — Daily Quality Assurance"); st.caption("QA = Quality Assurance. Daily verification before the first patient. Treatment is permitted only after QA passes.")
        qa_freq=st.selectbox("QA Type",["Daily QA","Weekly QA","Monthly QA"],key="linac_qa_type")
        q1=st.slider("Output — Measured Dose (cGy) for 100 MU",90,110,100,1,key="linac_output"); q2=st.slider("Flatness (%) — Beam should be flat",0.,5.,1.5,.1,key="linac_flat"); q3=st.slider("Symmetry (%) — Left and Right should be equal",0.,5.,1.,.1,key="linac_sym"); q4=st.slider("Laser vs Isocenter Shift (mm)",0.,3.,.5,.1,key="linac_laser"); q5=st.slider("Light Field vs Radiation Field Mismatch (mm)",0.,3.,.5,.1,key="linac_light")
        q6=st.checkbox("Door Interlock Working?",True,key="linac_door"); q7=st.checkbox("Emergency Stop Working?",True,key="linac_emg"); q8=st.checkbox("Gantry / Couch Movement OK?",True,key="linac_move")
        qa_table([("Output",f"{q1} cGy","98–102 cGy",98<=q1<=102),("Flatness",f"{q2}%","< 3%",q2<=3),("Symmetry",f"{q3}%","< 2%",q3<=2),("Laser Alignment",f"{q4} mm","< 1 mm",q4<=1),("Light Field Match",f"{q5} mm","< 2 mm",q5<=2),("Door Interlock","OK" if q6 else "FAIL","Must be OK",q6),("Emergency Stop","OK" if q7 else "FAIL","Must be OK",q7),("Gantry / Couch","OK" if q8 else "FAIL","Must be OK",q8)],(98<=q1<=102) and q2<=3 and q3<=2 and q4<=1 and q5<=2 and q6 and q7 and q8,"LINAC",qa_freq)

    # ---- D: Cobalt ----
    else:
        st.subheader("D — Cobalt-60 Unit"); st.write("**Source: Co-60 | Half-Life 5.27 years | Energy 1.17 + 1.33 MeV | SSD 80 cm**")
        st.markdown("### Collimator Jaws — Field Setting (No MLC in Cobalt)")
        cx1,cx2,cy1,cy2,cfx,cfy,csx,csy=jaw_sliders("C")
        years=st.slider("Source Age (Years)",0,10,2,1); decayed=2.0*(0.5**(years/5.27))
        st.info(f"Calibration: 2.0 Gy/min → After {years} years: **{decayed:.2f} Gy/min** (Decay)")
        beams=st.selectbox("Beam Arrangement",["2 Beams — Lat + Lat","1 Beam — Direct","3 Beams"])
        dose_c=st.slider("Total Dose (Gy)",30,70,60,5); fx=st.slider("Fractions",10,35,30,1); per_fx=round(dose_c/fx,2)
        rate=st.slider("Current Dose Rate (Gy/min)",.5,2.,round(decayed,2),.05); t=round(per_fx/rate,2)
        st.success(f"Manual Calculation: {per_fx} Gy / {rate} Gy/min = **{t} min per Fraction** | Field {cfx} x {cfy} cm")
        s1,s2=st.columns(2)
        with s1: source_on=st.button("SOURCE ON",use_container_width=True)
        with s2: source_off=st.button("SOURCE OFF",use_container_width=True)
        fig,ax=plt.subplots(figsize=(6,6)); fig.patch.set_facecolor('#141414'); ax.set_facecolor('#0A0A0A'); ax.title.set_color('white')
        ax.add_patch(patches.Rectangle((-13,-13),26,26,facecolor="#111111",edgecolor="#2A2A2A")); ax.text(-12,12,"COBALT ROOM — SHIELDED WALLS",fontsize=8,color="#999999",fontweight="bold")
        ax.add_patch(patches.FancyBboxPatch((-3,5),6,5,boxstyle="round,pad=0.3",facecolor="#000000",edgecolor="white",linewidth=1.5))
        ax.text(0,9,"SOURCE HEAD",ha="center",va="center",fontsize=8,color="white",fontweight="bold"); ax.text(0,8,"(Lead Shield)",ha="center",va="center",fontsize=6,color="#D4AF37")
        ax.add_patch(patches.Circle((0,6.5),.9,facecolor="#DC2626" if source_on else "#666666",edgecolor="white",linewidth=1.2)); ax.text(0,6.5,"Co-60",ha="center",va="center",fontsize=7,color="white",fontweight="bold")
        cjw=max(cfx/2.5,.8); ax.add_patch(patches.Rectangle((-cjw/2,3.5),cjw,1.5,facecolor="#D4AF37",edgecolor="white")); ax.text(0,4.2,f"COLLIMATOR {cfx}x{cfy}",ha="center",va="center",fontsize=6,fontweight="bold",color="black")
        ax.text(5.5,4.2,f"X1 {cx1} | X2 {cx2}\nY1 {cy1} | Y2 {cy2}",fontsize=7,color="black",bbox=dict(facecolor="white",edgecolor="#D4AF37",boxstyle="round,pad=0.3"))
        if source_on: ax.plot([0,0],[3.5,0],color="#DC2626",linewidth=4,alpha=.85); ax.text(6,6,"SOURCE ON",fontsize=10,color="#DC2626",fontweight="bold",bbox=dict(facecolor="white",edgecolor="#DC2626",boxstyle="round,pad=0.3"))
        else: ax.plot([0,0],[3.5,0],color="#666666",linewidth=1,linestyle="--"); ax.text(6,6,"SOURCE OFF\n(In Shield)",fontsize=8,color="#AAAAAA",fontweight="bold",bbox=dict(facecolor="white",edgecolor="#666666",boxstyle="round,pad=0.3"))
        ax.add_patch(patches.Rectangle((-6,-1.5),12,2,facecolor="#333333",edgecolor="white")); ax.text(0,-.5,"COUCH",ha="center",va="center",fontsize=7,color="white",fontweight="bold")
        ax.add_patch(patches.Ellipse((0,0),5,2.5,facecolor=p["color"],alpha=.9,edgecolor="white")); ax.text(0,0,f"{patient}",ha="center",va="center",fontsize=7,fontweight="bold",color="black" if p["color"] in ["#D4AF37","#FFFFFF"] else "white")
        ax.add_patch(patches.Rectangle((csx-cfx/4,csy-cfy/4),cfx/2,cfy/2,facecolor="none",edgecolor="#DC2626",linewidth=2,linestyle="--")); ax.plot([0],[0],marker="+",color="#DC2626",markersize=16,markeredgewidth=2.2); ax.text(1.2,.8,"ISOCENTER",fontsize=7,color="#DC2626",fontweight="bold")
        ax.annotate("",xy=(-4,3.5),xytext=(-4,0),arrowprops=dict(arrowstyle="<->",color="#D4AF37")); ax.text(-5.5,1.7,"SSD\n80 cm",fontsize=7,color="#D4AF37",fontweight="bold",ha="center")
        ax.text(0,-8,f"Decay: After {years} years, Rate {decayed:.2f} Gy/min — Time {t} min",ha="center",fontsize=8,fontweight="bold",color="black",bbox=dict(facecolor="white",edgecolor="#D4AF37",boxstyle="round,pad=0.4"))
        ax.set_xlim(-13,13); ax.set_ylim(-13,13); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(f"Cobalt-60 — SSD 80 cm — {beams} — Field {cfx} x {cfy}",fontweight="bold"); st.pyplot(fig)
        if source_on: st.error(f"SOURCE ON — Co-60 — {beams} — {t} min — SSD 80 cm — Field {cfx} x {cfy}")
        if source_off: st.info("Source OFF — Source returned to shield.")
        st.markdown("---"); st.markdown("### Cobalt-60 QA — Daily Quality Assurance"); st.caption("QA = Quality Assurance. Daily verification before the first patient. Source movement and timer must be correct.")
        cqa=st.selectbox("QA Type",["Daily QA","Weekly QA","Monthly QA"],key="cobalt_qa_type")
        cq1=st.slider("Output — Measured Dose Rate (Gy/min)",.5,2.5,round(decayed,2),.05,key="cobalt_output"); cq2=st.slider("Timer Error (sec) — Set Time vs Actual Time",0.,5.,.5,.1,key="cobalt_timer"); cq3=st.slider("Light Field vs Radiation Field Mismatch (mm)",0.,3.,.5,.1,key="cobalt_light"); cq4=st.slider("Laser vs Isocenter Shift (mm)",0.,3.,.5,.1,key="cobalt_laser")
        cq5=st.checkbox("Source Moves ON and OFF Smoothly?",True,key="cobalt_source_move"); cq6=st.checkbox("Door Interlock Working?",True,key="cobalt_door"); cq7=st.checkbox("Emergency Stop Working?",True,key="cobalt_emg"); cq8=st.checkbox("Radiation Monitor in Room Working?",True,key="cobalt_monitor")
        qa_table([("Output / Dose Rate",f"{cq1} Gy/min",f"{decayed:.2f} ± 0.1 Gy/min",abs(cq1-decayed)<=.1),("Timer Accuracy",f"{cq2} sec","< 1 sec",cq2<=1),("Light Field Match",f"{cq3} mm","< 2 mm",cq3<=2),("Laser Alignment",f"{cq4} mm","< 2 mm",cq4<=2),("Source Movement","OK" if cq5 else "FAIL","Must be OK",cq5),("Door Interlock","OK" if cq6 else "FAIL","Must be OK",cq6),("Emergency Stop","OK" if cq7 else "FAIL","Must be OK",cq7),("Radiation Monitor","OK" if cq8 else "FAIL","Must be OK",cq8)],abs(cq1-decayed)<=.1 and cq2<=1 and cq3<=2 and cq4<=2 and cq5 and cq6 and cq7 and cq8,"Cobalt-60",cqa)

# ================= PART 2 =================
else:
    st.subheader("Part 2 — Optics Behind It"); st.write("The clinical workflow shown in Part 1 is explained here through fundamental optics.")
    GLOSS=[("Wavelength (λ)","The distance between two waves. Shorter wavelength means higher energy."),("Frequency (f)","How many waves pass in 1 second. Formula: f = c / λ"),("Energy (E)","The power of radiation. Formula: E = hf"),("Attenuation (μ)","How much radiation is absorbed in tissue. Bone has high μ, soft tissue has low μ."),("Beer-Lambert Law","The thicker the tissue, the less radiation comes out. Formula: I = I₀ e^(-μx)"),("Reflection","Light bouncing back from a mirror. Rule: i = r"),("Refraction","Bending of light when it goes from one medium to another."),("Coherent Light","All waves move together in same direction. Laser light is coherent."),("Interference","Two waves meeting each other. Adding up = Constructive, Cancelling = Destructive."),("Young's Double Slit","Light passes through 2 slits and makes bright and dark fringes. Bright = High Dose, Dark = Low Dose."),("Ray Tracing","Drawing each beam as a straight ray (line) to see where it goes."),("Penumbra","The blurred edge of a beam where dose is half. Bigger source = bigger penumbra."),("Umbra","The center of the beam where dose is full."),("Inverse Square Law","Dose decreases with distance. Formula: I ∝ 1/d². If distance is double, dose becomes 4 times less."),("Isocenter","The point where all beams meet. Tumor is placed at this point."),("SSD","Source to Skin Distance. In LINAC 100 cm, in Cobalt 80 cm."),("GTV","The tumor that is visible on the scan."),("PTV","GTV + small margin, so even if patient moves a little, tumor still gets dose."),("OAR","Normal organ that we must save, like Heart, Lung, Spinal Cord."),("DVH","A graph that shows how much volume received how much dose."),("Dose Wash","A color map. Red = High Dose, Blue = Low Dose."),("CBCT","A 3D scan taken before treatment to verify patient position."),("MLC","Small metal leaves that shape the beam to the tumor shape."),("Collimator Jaw (X1, X2, Y1, Y2)","Metal blocks that open and close to define field size. X1 = Left, X2 = Right, Y1 = Upper, Y2 = Lower. Field X = X1 + X2, Field Y = Y1 + Y2."),("Gantry","The rotating part of LINAC that moves around the patient."),("Couch","The treatment table where patient lies."),("Junction","The place where two fields meet. In CSI, Brain and Spine fields meet here."),("Hot Spot","Area where dose is too high because two fields overlapped."),("Cold Spot","Area where dose is too low because there was a gap between fields."),("Mobilization","Keeping the patient in the exact same position every day."),("Immobilization","Preventing the patient from moving during treatment."),("Supine","Patient lying straight, face up."),("Prone","Patient lying face down."),("Fraction","One daily treatment session. Example: 50 Gy in 25 fractions means 2 Gy daily."),("Prescription Dose","Total dose prescribed by doctor, in Gy."),("VMAT / IMRT / 3D-CRT","Beam delivery techniques. VMAT = rotating arcs, IMRT = many small fields, 3D-CRT = simple 3 fields."),("Contrast Scan","Scan after injecting contrast dye. Tumor becomes bright and its border becomes clear."),("Plain Scan","Scan without contrast. Only anatomy is visible."),("Post-Contrast Scan","Scan taken 60–90 seconds after contrast. Shows washout of tumor."),("Decay","Cobalt source becomes weaker with time. Half-life is 5.27 years."),("CSI","Cranio-Spinal Irradiation. Treatment of whole Brain + whole Spine together."),("QA","Quality Assurance. Daily check of machine before treatment to ensure it is safe and accurate.")]
    with st.expander("Glossary — All Difficult Terms Explained in English"):
        for k,v in GLOSS: st.write(f"**{k}:** {v}")
    optics=st.radio("Select Optics Module",["CT Sim","TPS","LINAC","Cobalt-60","CSI Junction"],horizontal=True)

    if optics=="CT Sim":
        st.markdown("### 1. CT Sim — Beer-Lambert Law + Wavelength"); st.write("**Definition:** Beer-Lambert Law states that radiation intensity decreases exponentially as it passes through tissue.")
        st.latex(r"I = I_0 e^{-\mu x}"); st.latex(r"c = f \lambda \quad , \quad E = hf = \frac{hc}{\lambda}")
        mu=st.slider("Attenuation Coefficient μ (cm⁻¹) — Tissue Density",.1,1.,.3,.05); xa=np.linspace(0,20,100); Ia=np.exp(-mu*xa)
        fig,ax=dark_fig(); style_ax(ax); ax.plot(xa,Ia,color="#D4AF37",linewidth=2.5,label=f"μ = {mu}"); ax.fill_between(xa,Ia,alpha=.15,color="#D4AF37"); ax.set_xlabel("Thickness x (cm)"); ax.set_ylabel("Intensity I / I0"); ax.set_title("Beer-Lambert Law — CT Sim",fontweight="bold"); ax.grid(True,alpha=.25,color="#333333"); ax.legend(facecolor="#141414",edgecolor="#333333",labelcolor="white"); st.pyplot(fig)
        st.write("**Plain Scan:** Low μ = Dark Image | **Contrast Scan:** High μ = Bright Image"); st.write("**Concept:** X-Ray Source → Patient (μ varies) → Detector. Where bone is present, absorption is high, image is bright.")
        fig,ax=dark_fig(5,2.5); ax.add_patch(patches.Rectangle((-4,.5),1,1,facecolor="#D4AF37",edgecolor="white")); ax.text(-3.5,1,"X-Ray",ha="center",fontsize=7,fontweight="bold",color="black")
        ax.add_patch(patches.Ellipse((0,1),4,2,facecolor="#1E1E1E",edgecolor="white")); ax.text(0,1,"PATIENT\nμ1 Bone / μ2 Soft",ha="center",fontsize=7,fontweight="bold",color="white")
        ax.add_patch(patches.Rectangle((3,.5),1,1,facecolor="#444444",edgecolor="white")); ax.text(3.5,1,"DETECTOR",ha="center",fontsize=7,fontweight="bold",color="white")
        ax.annotate("",xy=(-1.5,1),xytext=(-3,1),arrowprops=dict(arrowstyle="->",color="#DC2626",lw=2)); ax.annotate("",xy=(3,1),xytext=(1.5,1),arrowprops=dict(arrowstyle="->",color="#D4AF37",lw=2))
        ax.set_xlim(-5,5); ax.set_ylim(-.5,2.5); ax.axis("off"); ax.set_title("CT Sim — Ray Diagram",fontweight="bold"); st.pyplot(fig)

    elif optics=="TPS":
        st.markdown("### 2. TPS — Ray Tracing + Young's Interference"); st.write("**Definition:** Ray Tracing is drawing each beam as a ray. Interference is two rays meeting and adding up or cancelling.")
        st.latex(r"E = hf = \frac{hc}{\lambda}"); st.latex(r"I = I_1 + I_2 + 2\sqrt{I_1 I_2}\cos\delta")
        st.write("**Dose Wash = Interference Pattern:** Where rays overlap = Constructive = Red (High Dose). Where rays do not overlap = Destructive = Blue (Low Dose).")
        y=np.linspace(-5,5,500); Iy=(np.cos(y*2)**2)*np.exp(-y**2/8)*100
        fig,ax=dark_fig(); style_ax(ax); ax.plot(y,Iy,color="#D4AF37",linewidth=2.5); ax.fill_between(y,Iy,alpha=.15,color="#D4AF37"); ax.set_xlabel("Position (Like Young's Screen)"); ax.set_ylabel("Intensity / Dose"); ax.set_title("Young's Fringes = Dose Wash",fontweight="bold"); ax.grid(True,alpha=.25,color="#333333"); st.pyplot(fig)
        fig,ax=dark_fig(); ax.add_patch(patches.Circle((0,0),1,facecolor="#DC2626",alpha=.9)); ax.text(0,0,"TUMOR",ha="center",va="center",fontsize=7,color="white",fontweight="bold")
        for ang in [30,90,150,210,270,330]:
            a=math.radians(ang); ax.plot([0,math.cos(a)*3],[0,math.sin(a)*3],color="#D4AF37",linewidth=2,alpha=.85)
        ax.add_patch(patches.Ellipse((0,0),7,7,facecolor="none",edgecolor="white")); ax.text(0,3.8,"Ray Tracing — 6 Beams Meeting at Tumor",ha="center",fontsize=7,fontweight="bold",color="white")
        ax.set_xlim(-4,4); ax.set_ylim(-4,4); ax.set_aspect("equal"); ax.axis("off"); ax.set_title("TPS — Ray Tracing Diagram",fontweight="bold"); st.pyplot(fig)
        st.write("**DVH:** Analogous to Young's Intensity vs Position graph. PTV = Bright Fringe, OAR = Dark Fringe.")

    elif optics=="LINAC":
        st.markdown("### 3. LINAC — Mirror Reflection + Laser + Lens"); st.write("**Definition:** Reflection is light bouncing from a mirror. Laser is coherent light used for alignment. Collimator functions like an aperture / lens.")
        st.latex(r"i = r \quad \text{(Law of Reflection)}"); st.latex(r"c = f \lambda \quad , \quad E = \frac{hc}{\lambda}")
        lam=st.slider("Wavelength λ (nm)",.001,700.,635.); f=3e8/(lam*1e-9); E=6.626e-34*f
        c1,c2,c3=st.columns(3)
        with c1: st.metric("Wavelength λ",f"{lam} nm")
        with c2: st.metric("Frequency f",f"{f:.2e} Hz")
        with c3: st.metric("Energy E",f"{E:.2e} J")
        la=np.array([.001,.01,1,100,635,700]); Ea=6.626e-34*3e8/(la*1e-9)
        fig,ax=dark_fig(); style_ax(ax); ax.plot(la,Ea,marker="o",color="#D4AF37",linewidth=2.5,markersize=6); ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("Wavelength λ (nm) — Log"); ax.set_ylabel("Energy E (J) — Log"); ax.set_title("Small λ = High E",fontweight="bold"); ax.grid(True,alpha=.25,color="#333333"); ax.annotate("Gamma",xy=(.001,Ea[0]),fontsize=7,fontweight="bold",color="white"); ax.annotate("Laser 635nm",xy=(635,Ea[4]),fontsize=7,fontweight="bold",color="white"); st.pyplot(fig)
        fig,ax=dark_fig(); ax.plot([-2,2],[-1,1],color="#666666",linewidth=9,alpha=.9); ax.text(0,.5,"45° MIRROR",ha="center",fontsize=7,fontweight="bold",color="white")
        ax.annotate("",xy=(0,0),xytext=(-2,2),arrowprops=dict(arrowstyle="->",color="#DC2626",lw=2)); ax.text(-1.8,2.1,"Incident i",fontsize=7,color="#DC2626")
        ax.annotate("",xy=(2,0),xytext=(0,0),arrowprops=dict(arrowstyle="->",color="#D4AF37",lw=2)); ax.text(1.5,.4,"Reflected r",fontsize=7,color="#D4AF37")
        ax.text(0,-1.5,"i = r  |  Mirror Reflects Light Field on Patient",ha="center",fontsize=7,fontweight="bold",color="black",bbox=dict(facecolor="white",edgecolor="#D4AF37",boxstyle="round,pad=0.4"))
        ax.set_xlim(-3,3); ax.set_ylim(-2,3); ax.set_aspect("equal"); ax.axis("off"); ax.set_title("LINAC Mirror — Reflection Diagram",fontweight="bold"); st.pyplot(fig)
        st.write("**Laser (635 nm):** Coherent — Sharp line, used for alignment. **Collimator:** Aperture / Lens type, shapes the beam."); st.success("Laser is visible only on skin. X-Ray reaches the tumor because its λ is very small, therefore its energy is high.")

    elif optics=="Cobalt-60":
        st.markdown("### 4. Cobalt-60 — Young's Double Slit + Penumbra + Inverse Square Law"); st.write("**Definition:** Penumbra is the blurred edge. Inverse Square Law states intensity falls with distance squared.")
        st.latex(r"\beta = \frac{\lambda D}{d}"); st.latex(r"I \propto \frac{1}{d^2}"); st.write("**Two Edges of Source = Two Slits of Young.** Where rays meet = Umbra (High Dose) = Bright Fringe. Where rays do not meet = Penumbra (Low Dose) = Dark Fringe.")
        d_src=st.slider("Source Size d (cm)",1.,3.,2.,.1); st.metric("Penumbra Width",f"{d_src*.8:.2f} cm",f"Source {d_src} cm")
        fig,ax=dark_fig(); ax.add_patch(patches.Rectangle((-1,2.5),2,.5,facecolor="#444444",edgecolor="white")); ax.text(0,2.75,f"Source d={d_src}cm",ha="center",fontsize=7,fontweight="bold",color="white")
        ax.plot([-d_src/2,-1],[2.5,-1],color="#DC2626",linewidth=2); ax.plot([d_src/2,1],[2.5,-1],color="#DC2626",linewidth=2); ax.plot([-d_src/2,1],[2.5,-1],color="#D4AF37",linewidth=1.5,linestyle="--"); ax.plot([d_src/2,-1],[2.5,-1],color="#D4AF37",linewidth=1.5,linestyle="--")
        ax.add_patch(patches.Rectangle((-1,-1.5),2,.5,facecolor="#DC2626",alpha=.85)); ax.text(0,-1.25,"UMBRA",ha="center",fontsize=7,fontweight="bold",color="white")
        ax.add_patch(patches.Rectangle((-1.8,-1.5),.8,.5,facecolor="#D4AF37",alpha=.9)); ax.add_patch(patches.Rectangle((1,-1.5),.8,.5,facecolor="#D4AF37",alpha=.9)); ax.text(-1.4,-1.9,"PENUMBRA",ha="center",fontsize=6,color="white"); ax.text(1.4,-1.9,"PENUMBRA",ha="center",fontsize=6,color="white")
        ax.set_xlim(-3,3); ax.set_ylim(-2.5,3.5); ax.axis("off"); ax.set_title("Cobalt Penumbra = Young's Fringes",fontweight="bold"); st.pyplot(fig)
        dist=np.linspace(50,150,100); inten=10000/(dist**2)*100
        fig,ax=dark_fig(); style_ax(ax); ax.plot(dist,inten,color="#D4AF37",linewidth=2.5)
