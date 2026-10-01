import streamlit as st
from streamlit_oauth import OAuth2Component
from supabase import create_client, Client

# --- Supabase 設定 ---

# --- 從 Streamlit Secrets 讀取設定 ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 雲端資料同步函數 ---
def load_user_data_from_cloud(email):
    response = supabase.table("profiles").select("*").eq("email", email).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    else:
        default_data = {
            "email": email,
            "level": 2,
            "exp": 150,
            "tasks": [
                {"name": "Complete Main Quest: Study for 1 hour", "exp": 50},
                {"name": "Side Quest: Read 20 pages of a book", "exp": 20},
            ]
        }
        supabase.table("profiles").insert(default_data).execute()
        return default_data

def save_user_data_to_cloud(email, level, exp, tasks):
    supabase.table("profiles").update({
        "level": level,
        "exp": exp,
        "tasks": tasks
    }).eq("email", email).execute()

# --- 1. Google OAuth 設定 ---


AUTHORIZE_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"

oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint=AUTHORIZE_ENDPOINT,
    token_endpoint=TOKEN_ENDPOINT
)

# --- 設定頁面寬度與樣式 ---
st.set_page_config(page_title="Progression", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    .block-container {
        padding-top: 1rem !important;
    }

    html, body, button, input, h3, span {
        font-family: 'Courier New', monospace !important;
    }

    h1 {
        font-family: 'Press Start 2P', cursive !important;
        font-size: 1.6rem !important;
        color: #FF4B4B;
    }
    
    div[data-testid="column"] button {
        background-color: #0e1117 !important;
        color: #fafafa !important;
        border: 1px solid rgba(250, 250, 250, 0.2) !important;
        padding: 0.15rem 0.6rem !important;
        font-size: 0.8rem !important;
        min-height: auto !important;
        border-radius: 4px !important;
    }

    div[data-testid="column"] button:hover {
        border-color: #FF4B4B !important;
        color: #FF4B4B !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 初始化登入狀態 ---
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# --- 3. 頂部導覽列：左側標題，右側登入/登出按鈕 ---
col_title, col_auth = st.columns([3, 1])

with col_title:
    st.title("Progression")

with col_auth:
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.token:
        result = oauth2.authorize_button(
            name="Log in",
            icon=None,
            redirect_uri="http://localhost:8501",
            scope="openid email profile",
            key="top_login_button"
        )
        if result:
            st.session_state.token = result.get("token")
            import jwt
            id_token = result.get("token", {}).get("id_token")
            if id_token:
                user_data_jwt = jwt.decode(id_token, options={"verify_signature": False})
                st.session_state.user_info = user_data_jwt
                
                # 🚀 關鍵優化：只在剛登入時向雲端抓取一次資料並放入 session_state 快取
                email = user_data_jwt.get("email")
                st.session_state.user_data = load_user_data_from_cloud(email)
                
            st.rerun()
    else:
        user_name = st.session_state.user_info.get("name", "Adventurer")
        st.markdown(f"👤 **{user_name}**")
        if st.button("Log out", key="top_logout_button"):
            st.session_state.token = None
            st.session_state.user_info = None
            st.session_state.user_data = None
            st.rerun()

st.divider()

# --- 4. 主畫面內容 ---
if not st.session_state.token:
    st.subheader("Welcome to Progression!")
    st.markdown("Please click the **Log in** button in the top right corner to start your RPG journey.")

else:
    # 如果重新整理但 session 裡剛好沒有快取，補抓一次
    if st.session_state.user_data is None:
        email = st.session_state.user_info.get("email")
        st.session_state.user_data = load_user_data_from_cloud(email)

    current_data = st.session_state.user_data
    user_email = current_data["email"]

   
    # --- 💡 升級門檻改為：級數 * 100 ---
    # 計算當前等級升下一級所需的總經驗值門檻 (例如 Lv.2 升 Lv.3 需要 2 * 100 = 200 點)
    needed_exp = current_data["level"] * 100
    progress_ratio = min(current_data["exp"] / needed_exp, 1.0)
    
    st.metric(label="Level", value=f"Lv. {current_data['level']}", delta=f"Total EXP: {current_data['exp']}")
    st.progress(progress_ratio, text=f"Progress to Next Level: {current_data['exp']} / {needed_exp} EXP")
    
    st.divider()

    # 任務清單區塊
    st.subheader("Quest Log")
    for index, task in enumerate(current_data["tasks"]):
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"- {task['name']} (+{task['exp']} XP)", key=f"task_{index}"):
                current_data["exp"] += task['exp']
                
                # 升級判定：若經驗值大於等於當前等級所需門檻，則升級並扣除該門檻（保留剩餘經驗值）
                while current_data["exp"] >= current_data["level"] * 100:
                    current_data["exp"] -= current_data["level"] * 100
                    current_data["level"] += 1
                    st.success(f"Level Up! You reached Lv. {current_data['level']}!")
                
                # 背景同步至雲端
                save_user_data_to_cloud(user_email, current_data["level"], current_data["exp"], current_data["tasks"])
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{index}"):
                current_data["tasks"].pop(index)
                
                # 背景同步至雲端
                save_user_data_to_cloud(user_email, current_data["level"], current_data["exp"], current_data["tasks"])
                st.rerun()

    st.divider()

    # 新增任務區塊
    st.subheader("+ Create a New Quest")
    with st.form("add_task_form"):
        new_task_name = st.text_input("Quest Name", placeholder="e.g., Finish Python Homework")
        new_task_exp = st.number_input("EXP Reward", min_value=5, max_value=500, value=30, step=5)
        submit_button = st.form_submit_button("Add Quest")
        
        if submit_button:
            if new_task_name.strip():
                current_data["tasks"].append({"name": new_task_name, "exp": new_task_exp})
                
                # 背景同步至雲端
                save_user_data_to_cloud(user_email, current_data["level"], current_data["exp"], current_data["tasks"])
                st.success(f"New quest added: {new_task_name}!")
                st.rerun()
            else:
                st.warning("Please enter a valid quest name.")