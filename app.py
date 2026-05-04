import streamlit as st
import sqlite3
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Gym App", layout="wide")

DB_PATH = "Gym.db3"

# -----------------------------
# DB CONNECTION
# -----------------------------
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_connection()
cursor = conn.cursor()

# -----------------------------
# CREATE LOGIN TABLE
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Login (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT UNIQUE,
    Password TEXT
)
""")
conn.commit()

# -----------------------------
# AUTH FUNCTIONS
# -----------------------------
def register_user(username, password):
    try:
        cursor.execute("INSERT INTO Login (Username, Password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    cursor.execute("SELECT * FROM Login WHERE Username=? AND Password=?", (username, password))
    return cursor.fetchone()

# -----------------------------
# SESSION STATE
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -----------------------------
# HERO UI (LIKE IMAGE)
# -----------------------------
def hero_section():
    st.markdown("""
    <style>
    .hero {
        position: relative;
        height: 450px;
        background-image: url("https://images.unsplash.com/photo-1558611848-73f7eb4001a1");
        background-size: cover;
        background-position: center;
        border-radius: 10px;
    }

    .overlay {
        position: absolute;
        top:0;left:0;width:100%;height:100%;
        background: rgba(0,0,0,0.7);
        border-radius: 10px;
    }

    .hero-text {
        position:absolute;
        top:50%;left:50%;
        transform:translate(-50%,-50%);
        color:white;
        text-align:center;
    }

    .hero-text h1 {
        font-size:50px;
        font-weight:800;
    }

    .hero-text span { color:#ff4b2b; }

    .btn {
        background:#ff4b2b;
        padding:10px 20px;
        border-radius:5px;
        margin-top:10px;
        display:inline-block;
    }
    </style>

    <div class="hero">
        <div class="overlay"></div>
        <div class="hero-text">
            <p>WORK HARDER, GET STRONGER</p>
            <h1>EASY WITH OUR <span>GYM</span></h1>
            <div class="btn">BECOME A MEMBER</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# LOGIN PAGE
# -----------------------------
def login_page():
    hero_section()

    st.subheader("Login / Register")

    menu = st.radio("", ["Login", "Register"], horizontal=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Login":
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid Credentials")

    else:
        if st.button("Register"):
            if register_user(username, password):
                st.success("User Registered")
            else:
                st.error("Username exists")

# -----------------------------
# GET TABLES
# -----------------------------
def get_tables():
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
    return tables["name"].tolist()

# -----------------------------
# CRUD UI
# -----------------------------
def table_ui(table):
    st.subheader(f"📋 {table}")

    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.dataframe(df, use_container_width=True)

    columns = df.columns.tolist()

    # ADD
    with st.expander("➕ Add Record"):
        inputs = {}
        for col in columns:
            if col.lower().endswith("id"):
                continue
            inputs[col] = st.text_input(f"{col}", key=f"add_{col}")

        if st.button("Submit", key=f"add_btn_{table}"):
            cols = ",".join(inputs.keys())
            vals = tuple(inputs.values())
            query = f"INSERT INTO {table} ({cols}) VALUES ({','.join(['?']*len(vals))})"
            cursor.execute(query, vals)
            conn.commit()
            st.success("Added")
            st.rerun()

    # DELETE
    with st.expander("❌ Delete Record"):
        del_id = st.number_input("Enter ID", 0)
        if st.button("Delete"):
            cursor.execute(f"DELETE FROM {table} WHERE rowid=?", (del_id,))
            conn.commit()
            st.success("Deleted")
            st.rerun()

# -----------------------------
# MAIN APP
# -----------------------------
def main_app():
    st.sidebar.title("🏋️ Gym App")

    tables = get_tables()
    menu = st.sidebar.selectbox("Select Table", tables)

    hero_section()

    if menu:
        table_ui(menu)

# -----------------------------
# FLOW
# -----------------------------
if not st.session_state.logged_in:
    login_page()
else:
    main_app()