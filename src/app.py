import streamlit as st
from dotenv import load_dotenv
import os, random, smtplib
from email.message import EmailMessage

load_dotenv()

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("design.css")

# Hide Streamlit menu and footer globally
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

valid_email = os.getenv("LOGIN_EMAIL")
valid_password = os.getenv("LOGIN_PASSWORD")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Initialize session_state keys
for key, val in {
    "page": "login",            # Tracks current UI page: login, otp, home
    "generated_otp": None,
    "verified_email": None,
    "login_error": "",
    "logged_in": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(receiver_email, otp):
    msg = EmailMessage()
    msg["Subject"] = "Your OTP Code"
    msg["From"] = SMTP_USER
    msg["To"] = receiver_email
    msg.set_content(f"Your OTP is {otp}. It expires in 5 minutes.")
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

# st.markdown('<div class="header-glass"><h2>Welcome to Automation</h2></div>', unsafe_allow_html=True)

if st.session_state.page == "login":
    st.markdown('<div class="header-glass"><h2>Welcome to Automation</h2></div>', unsafe_allow_html=True)
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", placeholder="Enter your password", type="password")
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            verify = st.form_submit_button("Send OTP")

    st.session_state.login_error = ""

    if verify:
        if email == valid_email and password == valid_password:
            otp = generate_otp()
            st.session_state.generated_otp = otp
            st.session_state.verified_email = email
            resp = send_email_otp(email, otp)
            if resp.get("success"):
                st.session_state.page = "otp"
                st.rerun()
            else:
                st.session_state.login_error = f"❌ Email failed: {resp.get('error')}"
        else:
            st.session_state.login_error = "❌ Invalid credentials."

    if st.session_state.login_error:
        st.error(st.session_state.login_error)

elif st.session_state.page == "otp":
    st.markdown("<h2>Enter OTP</h2>", unsafe_allow_html=True)
    with st.form("otp_form"):
        user_otp = st.text_input("Enter OTP", max_chars=6)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            submit = st.form_submit_button("Send OTP")
    st.session_state.login_error = ""

    if submit:
        if user_otp == st.session_state.generated_otp:
            st.session_state.logged_in = True
            st.session_state.page = "home"
            st.rerun()
        else:
            st.session_state.login_error = "❌ Invalid OTP."

    if st.session_state.login_error:
        st.error(st.session_state.login_error)

elif st.session_state.page == "home":
    # st.markdown('<div class="center-box">', unsafe_allow_html=True)
    st.markdown('<div class="header-glass"><h2>🏠 Home Page</h2></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    overview_clicked = col1.button("Overview")
    listeners_clicked = col2.button("Listeners")

    if "page_section" not in st.session_state:
        st.session_state.page_section = "Overview"

    if overview_clicked:
        st.session_state.page_section = "Overview"
    if listeners_clicked:
        st.session_state.page_section = "Listeners"

    if st.session_state.page_section == "Overview":
        st.markdown("""
        <p style="color: white;">
        The <strong>Standard Tier</strong> provides a balanced level of cybersecurity controls designed for organizations seeking reliable protection without the complexity of advanced enterprise frameworks. It focuses on building a baseline of defense that covers essential threats, regulatory compliance, and business continuity.
        </p>
        """, unsafe_allow_html=True)

        import pandas as pd
         # Randomly pick a tier type
        tier_types = ["standard", "non-standard", "weak"]
        chosen_tier = random.choice(tier_types)

        data = {"abc": [f"tier:{chosen_tier}"]}
        st.table(pd.DataFrame(data))

    elif st.session_state.page_section == "Listeners":
        st.markdown('<p style="color: white;">Listeners section content goes here. Customize as needed.</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = "login"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
