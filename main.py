import streamlit as st
import os
import base64
import shutil

# Prepare background image
src = "WhatsApp Image 2025-05-16 at 19.50.48_e69b5c15.jpg"
dst = "bg.jpg"
if os.path.exists(src) and not os.path.exists(dst):
    shutil.copy(src, dst)

st.set_page_config(page_title="Smart Tiki-Taka", layout="wide")

# Convert image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_base64 = get_base64_image("bg.jpg")

# Custom CSS styling
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: Arial, sans-serif;
        color: white;
    }}
    .tile {{
        display: inline-block;
        width: 250px;
        height: 150px;
        background: rgba(0, 0, 0, 0.7);
        border-radius: 20px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4);
        margin: 20px;
        text-align: center;
        vertical-align: top;
        transition: all 0.3s ease-in-out;
        cursor: default;
        padding: 30px;
        font-size: 20px;
        font-weight: bold;
        color: #ffffff;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/e/eb/Soccer_ball.svg');
        background-repeat: no-repeat;
        background-position: center 10px;
        background-size: 40px;
        padding-top: 70px;
        border: 2px solid #ffffff33;
    }}
    .tile:hover {{
        transform: scale(1.05);
        background-color: rgba(255, 255, 255, 0.1);
        color: #00ffcc;
    }}
    .dashboard-title {{
        font-size: 36px;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 20px;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
        text-align: center;
    }}
    </style>
""", unsafe_allow_html=True)

# Welcome title
st.markdown("<h2 class='dashboard-title'>⚽ Smart Tiki-Taka: Football Intelligence Hub</h2>", unsafe_allow_html=True)
st.markdown("### Use the sidebar on the left ⬅️ to select an analysis page.")

# Optional tip
st.markdown("##### 💡 If the sidebar isn't visible, click the ☰ icon in the top left corner.")
