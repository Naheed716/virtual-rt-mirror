import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Virtual RT Mirror - Jaws", layout="centered")
st.title("☢️ Virtual RT Mirror - JAWS")
st.markdown("**X1, X2, Y1, Y2 hi asal Field banate hain**")
st.markdown("> **Field X = X1 + X2**  |  **Field Y = Y1 + Y2**")

# --- Patient Presets ---
st.subheader("👩‍⚕️ Patient Select Karo")
preset = st.selectbox("Patient", ["Custom", "Brain", "Breast", "Pelvis", "Head & Neck", "Esophagus"])

presets = {
    "Brain": (7.5, 7.5, 7.5, 7.5),
    "Breast": (9, 9, 8, 8),
    "Pelvis": (7.5, 7.5, 7.5, 7.5),
    "Head & Neck": (6, 10, 6, 6),
    "Esophagus": (6, 6, 7.5, 7.5),
}

if preset != "Custom":
    d_x1, d_x2, d_y1, d_y2 = presets[preset]
else:
    d_x1, d_x2, d_y1, d_y2 = 7.5, 7.5, 7.5, 7.5

# --- Jaws Sliders ---
st.subheader("↔️ JAWS - X1 X2 Y1 Y2")
col1, col2 = st.columns(2)
with col1:
    x1 = st.slider("X1 Left Jaw (cm)", 0.0, 15.0, d_x1, 0.5)
    y1 = st.slider("Y1 Upper Jaw (cm)", 0.0, 15.0, d_y1, 0.5)
with col2:
    x2 = st.slider("X2 Right Jaw (cm)", 0.0, 15.0, d_x2, 0.5)
    y2 = st.slider("Y2 Lower Jaw (cm)", 0.0, 15.0, d_y2, 0.5)

fx = x1 + x2
fy = y1 + y2

# --- Result ---
st.markdown(f"### Field X = {x1} + {x2} = **{fx} cm** | Field Y = {y1} + {y2} = **{fy} cm**")

if x1 == x2 and y1 == y2:
    st.success("✅ Symmetric - Dono side barabar")
    st.write("Dono Jaws barabar khule hain.")
else:
    st.warning("⚠️ Asymmetric - Ek side zyada khula hai, OAR bachane ke liye")
    if preset == "Head & Neck":
        st.write("Jaise Head & Neck me X2 zyada hai, taake Cord bach jaye.")

# --- Graph / Field Light ---
st.subheader("💡 Field Light - Graph")
fig, ax = plt.subplots(figsize=(5, 5))

# Center cross
ax.axhline(0, color="black", linewidth=0.8)
ax.axvline(0, color="black", linewidth=0.8)

# Field rectangle: left = -X1, right = +X2, top = +Y1, bottom = -Y2
rect = patches.Rectangle((-x1, -y2), fx, fy, linewidth=2, edgecolor="#FFD700", facecolor="#FFF9C4", alpha=0.9)
ax.add_patch(rect)

# Jaws labels
ax.text(-x1, fy/2, f"X1={x1}", ha="right", va="center", fontsize=10, fontweight="bold")
ax.text(x2, fy/2, f"X2={x2}", ha="left", va="center", fontsize=10, fontweight="bold")
ax.text(0, y1, f"Y1={y1}", ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.text(0, -y2, f"Y2={y2}", ha="center", va="top", fontsize=10, fontweight="bold")
ax.text(0, 0, f"{fx} x {fy} cm", ha="center", va="center", fontsize=12, fontweight="bold")

ax.set_xlim(-16, 16)
ax.set_ylim(-16, 16)
ax.set_xlabel("X - Left / Right (cm)")
ax.set_ylabel("Y - Up / Down (cm)")
ax.set_title(f"Field Light: {fx} x {fy} cm")
ax.set_aspect("equal")
ax.grid(True, linestyle="--", alpha=0.4)
st.pyplot(fig)

# --- Viva Line ---
st.subheader("🎤 Ma'am Ko Kya Bolna Hai - Viva Line")
st.info("Ma'am, X1/X2 left-right jaws hain, Y1/Y2 up-down jaws hain. Field X = X1+X2 hota hai. Agar hum X1=6, X2=10 rakhein to ye Asymmetric Field hai, isse hum Cord ko bacha lete hain. Field Light ON karke hum pehle patient pe field dekhte hain, phir Beam ON karte hain.")

# --- Table ---
st.subheader("📋 Har Patient Ke Liye Setting")
st.table({
    "Patient": ["Brain", "Breast", "Pelvis", "Head & Neck", "Esophagus"],
    "X1": [7.5, 9, 7.5, 6, 6],
    "X2": [7.5, 9, 7.5, 10, 6],
    "Y1": [7.5, 8, 7.5, 6, 7.5],
    "Y2": [7.5, 8, 7.5, 6, 7.5],
    "Field": ["15x15", "18x16", "15x15", "16x12", "12x15"],
})
