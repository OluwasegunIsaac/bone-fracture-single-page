import streamlit as st
from ultralytics import YOLO
from PIL import Image
import io
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import bcrypt
import os

st.set_page_config(layout="wide")


logo_path = "assets/logo.png"  # Path to your logo
logo = Image.open(logo_path)
logo = logo.resize((700, 140))  # Resize the logo
_, col1,_ = st.columns([1,2.5,1.3])
with col1:
    st.image(logo, use_column_width=True)

# Load the YOLOv8 model using your trained weights
model = YOLO('assets/model_best.pt')

def init_firebase():
    """Initialize firebase using credentials from Streamlit secrets."""
    if not firebase_admin._apps:  # Check if firebase is already initialized
        firebase_creds = {
            "type": st.secrets["firebase"]["type"],
            "project_id": st.secrets["firebase"]["project_id"],
            "private_key_id": st.secrets["firebase"]["private_key_id"],
            "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),  # Ensure proper formatting of the key
            "client_email": st.secrets["firebase"]["client_email"],
            "client_id": st.secrets["firebase"]["client_id"],
            "auth_uri": st.secrets["firebase"]["auth_uri"],
            "token_uri": st.secrets["firebase"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
        }

        # Initialize firebase with the credentials from secrets
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
def get_firestore_client():
    """Initialize and return Firestore client."""
    init_firebase()  # Ensure firebase is initialized before accessing Firestore
    db = firestore.client()
    return db


def add_user_to_firestore(username, data):
    """Add or update user data in Firestore."""
    db = get_firestore_client()
    db.collection("users").document(username).set(data)
    return f"User '{username}' data added/updated in Firestore."

def fetch_user_from_firestore(username):
    """Fetch user data from Firestore."""
    db = get_firestore_client()
    user_doc = db.collection("users").document(username).get()
    return user_doc.to_dict() if user_doc.exists else None

def hash_password(password):
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()  # Generate a salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)  # Hash the password
    return hashed_password.decode('utf-8')  # Return as string

def check_password(hashed_password, user_password):
    """Check if the provided password matches the hashed password."""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))



# Function to detect fracture
def detect_disease(img_path):
    results = model(img_path)
    if len(results) > 0:
        results_img = results[0].plot()
        results_img_path = "temp_results.png"
        img = Image.fromarray(results_img)
        img.save(results_img_path)
        return results_img_path, img
    else:
        return None, None

# Function to handle login UI
def login_ui():
    st.markdown("""
        <style>
        .app-spacing { margin-top: -70px; margin-bottom: -30px; }
        </style>
        """, unsafe_allow_html=True)

    app_name = """
        <div class='app-spacing' style="padding:4px">
        <h1 style='text-align: center; color: #22686E; font-size: 50px;'>Bone Fracture Detection System</h1>
        </div>
        """
    st.markdown(app_name, unsafe_allow_html=True)
    
    _, col1, _ = st.columns([0.9, 2, 1])
    with col1:
        st.divider()
        st.markdown("""
        <style>
        .app-spacing { margin-top: -30px; margin-bottom: -30px; }
        </style>
        """, unsafe_allow_html=True)

        header = """
            <div class='app-spacing' style="padding:4px">
            <h1 style='text-align: center; color: #22686E; font-size: 30px;'>Login</h1>
            </div>
            """
        st.markdown(header, unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                user_data = fetch_user_from_firestore(username)
                if user_data:
                    if check_password(user_data['password'], password):
                        st.success("Login successful!")
                        st.session_state.user = username
                        st.session_state.user_data = user_data
                        st.rerun()  # Rerun the app to transition to main content
                    else:
                        st.error("Incorrect password. Please try again.")
                else:
                    new_user_data = {"username": username, "password": hash_password(password)}
                    add_user_to_firestore(username, new_user_data)
                    st.success("New user created and logged in!")
                    st.session_state.user = username
                    st.rerun()  # Rerun after new user creation
            else:
                st.error("Please enter both username and password")
    
    with col1:
        st.markdown("""
        <style>
        .app-spacing { margin-top: -30px; margin-bottom: -30px; }
        </style>
        """, unsafe_allow_html=True)

        if st.button("Continue without login", type="secondary", use_container_width=True):
            st.session_state.user = "guest"
            st.rerun()  # Rerun to transition to main content

# Main content: Bone Fracture Detection App
def main_app():
    st.markdown("""
        <style>
        .app-spacing { margin-top: -70px; margin-bottom: -30px; }
        </style>
        """, unsafe_allow_html=True)

    app_name = """
        <div class='app-spacing' style="padding:4px">
        <h1 style='text-align: center; color: #22686E; font-size: 62px;'>Bone Fracture Detection System</h1>
        </div>
        """
    st.markdown(app_name, unsafe_allow_html=True)
    
    _, col1, _ = st.columns([1, 3, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            temp_img_path = "temp_uploaded_img.png"
            image.save(temp_img_path)

            if st.button("Detect Fracture", type="primary", use_container_width=True):
                results_img_path, result_img = detect_disease(temp_img_path)
                if results_img_path:
                    result_img_resized = result_img.resize((350, 350))
                    st.image(result_img_resized, caption="Detection Results", use_column_width=True)

                    buf = io.BytesIO()
                    result_img.save(buf, format="PNG")
                    byte_img = buf.getvalue()

                    st.download_button(
                        label="Download Detection Image",
                        data=byte_img,
                        file_name="detection_results.png",
                        mime="image/png"
                    )
                else:
                    st.write("No detections found.")
            else:
                st.image(image, caption="Uploaded Image", use_column_width=True)

# Check session state for user login status
if "user" not in st.session_state:
    login_ui()  # Display login page if user is not logged in
else:
    main_app()  # Display the main app after login
