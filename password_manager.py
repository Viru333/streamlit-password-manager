import streamlit as st
import pandas as pd
import os
from cryptography.fernet import Fernet

# Constants
CSV_FILE = "passwords.csv"
KEY_FILE = "secret.key"

# Generate or load encryption key
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

# Encrypt and decrypt functions
def encrypt_password(password, fernet):
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password, fernet):
    return fernet.decrypt(encrypted_password.encode()).decode()

# Initialize CSV if not present
def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["Website", "Username", "EncryptedPassword"])
        df.to_csv(CSV_FILE, index=False)

# Add new entry
def add_entry(website, username, password, fernet):
    encrypted_password = encrypt_password(password, fernet)
    new_entry = pd.DataFrame([[website, username, encrypted_password]],
                             columns=["Website", "Username", "EncryptedPassword"])
    new_entry.to_csv(CSV_FILE, mode='a', header=False, index=False)

# Retrieve entry
def get_entry(website, fernet):
    df = pd.read_csv(CSV_FILE)
    result = df[df["Website"].str.lower() == website.lower()]
    if not result.empty:
        result["DecryptedPassword"] = result["EncryptedPassword"].apply(lambda x: decrypt_password(x, fernet))
    return result

# App starts here
st.title("🔐 Encrypted Password Manager")

# Load encryption key and create Fernet object
key = load_key()
fernet = Fernet(key)

# Initialize CSV
init_csv()

# UI
menu = st.sidebar.radio("Choose an action:", ["Add Password", "Retrieve Password"])

if menu == "Add Password":
    st.subheader("➕ Add a New Password Entry")
    website = st.text_input("Website")
    username = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

    if st.button("Save Password"):
        if website and username and password:
            add_entry(website, username, password, fernet)
            st.success("✅ Password encrypted and saved!")
        else:
            st.warning("⚠️ Please fill out all fields.")

elif menu == "Retrieve Password":
    st.subheader("🔍 Retrieve Stored Password")
    website_search = st.text_input("Enter Website Name")

    if st.button("Search"):
        if website_search:
            result = get_entry(website_search, fernet)
            if not result.empty:
                st.success(f"🔑 Retrieved {len(result)} record(s):")
                st.dataframe(result[["Website", "Username", "DecryptedPassword"]])
            else:
                st.error("❌ No entry found.")
        else:
            st.warning("⚠️ Please enter a website name.")
