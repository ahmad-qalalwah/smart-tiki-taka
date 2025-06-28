import streamlit as st
import os
import base64

# Set Streamlit page configuration
st.set_page_config(page_title="Smart Tiki-Taka", layout="wide", initial_sidebar_state="collapsed")

# Load and encode background image
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

bg_base64 = get_base64_image("bg.jpg")  # تأكد من وجود bg.jpg في نفس المجلد

# Inject custom CSS
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
    }}
    .tile-button {{
        background-color: rgba(0, 0, 0, 0.75);
        color: white;
        padding: 25px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5);
        margin: 15px;
        transition: 0.3s;
        border: 2px solid #ffffff33;
    }}
    .tile-button:hover {{
        background-color: rgba(255, 255, 255, 0.1);
        color: #00ffcc;
        transform: scale(1.05);
    }}
    .dashboard-title {{
        font-size: 40px;
        font-weight: 900;
        text-align: center;
        margin-top: 40px;
        margin-bottom: 40px;
        color: white;
        text-shadow: 2px 2px 10px black;
    }}
    </style>
""", unsafe_allow_html=True)

# Main title
st.markdown("<div class='dashboard-title'>⚽ Smart Tiki-Taka: Football Intelligence Hub</div>", unsafe_allow_html=True)

# Create tile layout
cols1 = st.columns(3)
cols2 = st.columns(3)

# First row
with cols1[0]:
    if st.button("Match Shot Analysis", use_container_width=True):
        st.switch_page("pages/1_Match_Shot_Analysis.py")
with cols1[1]:
    if st.button("Passing Analysis", use_container_width=True):
        st.switch_page("pages/2_Passing_Analysis.py")
with cols1[2]:
    if st.button("Top Scorer Analysis", use_container_width=True):
        st.switch_page("pages/3_Top_Scorer_Analysis.py")

# Second row
with cols2[0]:
    if st.button("Formation Analysis", use_container_width=True):
        st.switch_page("pages/4_Formation_Analysis.py")
with cols2[1]:
    if st.button("Tactical Pattern", use_container_width=True):
        st.switch_page("pages/5_Tactical_Pattern.py")
