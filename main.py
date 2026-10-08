import streamlit as st

from streamlit_oauth import OAuth2Component

from supabase import create_client, Client

import streamlit.components.v1 as components

# --- Supabase 設定 ---

SUPABASE_URL = st.secrets["SUPABASE_URL"]

SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

CLIENT_ID = st.secrets["CLIENT_ID"]

CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 雲端資料同步函數 ---
def load_user_data_from_cloud(email):
    response = supabase.table("profiles").select("*").eq("email", email).execute()
    if response.data and len(response.data) > 0:
        data = response.data[0]
        if not data.get("goal"):
            data["goal"] = "Become a Legendary Developer & Master Python!"
        return data
    else:
        default_data = {
            "email": email,
            "level": 1,
            "exp": 0,
            "goal": "Become a Legendary Developer & Master Python!",
            "tasks": [
                {"name": "Complete Main Quest: Study for 1 hour", "exp": 50},
                {"name": "Side Quest: Read 20 pages of a book", "exp": 20},
            ]
        }
        supabase.table("profiles").insert(default_data).execute()
        return default_data

# 修正：補上 goal 參數以便同步儲存大目標
def save_user_data_to_cloud(email, level, exp, tasks, goal):
    supabase.table("profiles").update({
        "level": level,
        "exp": exp,
        "tasks": tasks,
        "goal": goal
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
        padding-top: 3.5rem !important;
    }

    html, body, input, h3 {
        font-family: 'Courier New', monospace !important;
    }

    h1 {
        font-family: 'Press Start 2P', cursive !important;
        font-size: 1.6rem !important;
        color: #FF4B4B;
    }
    
    div[data-testid="column"] button {
        font-family: 'Courier New', monospace !important;
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
    /* 讓編輯按鈕變小、更精緻 */
    button[key="toggle_edit_goal"], div[data-testid="column"] button[kind="secondary"] {
        padding: 0rem 0.3rem !important;
        font-size: 0.7rem !important;
        min-height: 24px !important;
        max-height: 28px !important;
    }
   
    </style>
""", unsafe_allow_html=True)

# --- ❄️ 純 CSS 動態雪花特效 ---
st.markdown("""
    <style>
    .snow-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 999999;
        overflow: hidden;
    }
    .snowflake {
        position: absolute;
        top: -10px;
        background-color: #ffffff;
        border-radius: 50%;
        opacity: 0.8;
        animation: fall linear infinite;
    }
    @keyframes fall {
        0% { transform: translateY(-10px) translateX(0); }
        50% { transform: translateY(50vh) translateX(20px); }
        100% { transform: translateY(105vh) translateX(-20px); }
    }
    .snowflake:nth-of-type(1)  { left: 5%; width: 6px; height: 6px; animation-duration: 7s; animation-delay: 0s; }
    .snowflake:nth-of-type(2)  { left: 15%; width: 4px; height: 4px; animation-duration: 9s; animation-delay: 2s; }
    .snowflake:nth-of-type(3)  { left: 25%; width: 8px; height: 8px; animation-duration: 5s; animation-delay: 1s; }
    .snowflake:nth-of-type(4)  { left: 35%; width: 5px; height: 5px; animation-duration: 8s; animation-delay: 3s; }
    .snowflake:nth-of-type(5)  { left: 45%; width: 7px; height: 7px; animation-duration: 6s; animation-delay: 0.5s; }
    .snowflake:nth-of-type(6)  { left: 55%; width: 4px; height: 4px; animation-duration: 10s; animation-delay: 4s; }
    .snowflake:nth-of-type(7)  { left: 65%; width: 6px; height: 6px; animation-duration: 7s; animation-delay: 1.5s; }
    .snowflake:nth-of-type(8)  { left: 75%; width: 8px; height: 8px; animation-duration: 5s; animation-delay: 2.5s; }
    .snowflake:nth-of-type(9)  { left: 85%; width: 5px; height: 5px; animation-duration: 8s; animation-delay: 3.5s; }
    .snowflake:nth-of-type(10) { left: 95%; width: 6px; height: 6px; animation-duration: 6s; animation-delay: 1s; }
    .snowflake:nth-of-type(11) { left: 10%; width: 5px; height: 5px; animation-duration: 8s; animation-delay: 4s; }
    .snowflake:nth-of-type(12) { left: 20%; width: 7px; height: 7px; animation-duration: 6s; animation-delay: 1s; }
    .snowflake:nth-of-type(13) { left: 30%; width: 4px; height: 4px; animation-duration: 11s; animation-delay: 3s; }
    .snowflake:nth-of-type(14) { left: 40%; width: 6px; height: 6px; animation-duration: 7s; animation-delay: 2s; }
    .snowflake:nth-of-type(15) { left: 50%; width: 8px; height: 8px; animation-duration: 5s; animation-delay: 0s; }
    .snowflake:nth-of-type(16) { left: 60%; width: 5px; height: 5px; animation-duration: 9s; animation-delay: 2.5s; }
    .snowflake:nth-of-type(17) { left: 70%; width: 6px; height: 6px; animation-duration: 6s; animation-delay: 1.5s; }
    .snowflake:nth-of-type(18) { left: 80%; width: 4px; height: 4px; animation-duration: 10s; animation-delay: 3.5s; }
    .snowflake:nth-of-type(19) { left: 90%; width: 7px; height: 7px; animation-duration: 7s; animation-delay: 0.5s; }
    </style>

    <div class="snow-container">
        <div class="snowflake"></div><div class="snowflake"></div><div class="snowflake"></div>
        <div class="snowflake"></div><div class="snowflake"></div><div class="snowflake"></div>
        <div class="snowflake"></div><div class="snowflake"></div><div class="snowflake"></div>
        <div class="snowflake"></div><div class="snowflake"></div><div class="snowflake"></div>
        <div class="snowflake"></div><div class="snowflake"></div><div class="snowflake"></div>
        <div class="snowflake"></div><div class="snowflake"></div><div class="snowflake"></div>
        <div class="snowflake"></div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 初始化登入狀態 ---
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'is_editing_goal' not in st.session_state:
    st.session_state.is_editing_goal = False

# --- 3. 頂部導覽列：左側標題，右側登入/登出按鈕 ---
col_title, col_auth = st.columns([3, 1])

with col_title:
    st.title("Progression")

with col_auth:
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.token:
        current_url = "https://progression-kuo.streamlit.app"

        result = oauth2.authorize_button(
            name="Log in",
            icon=None,
            redirect_uri=current_url,
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
# --- 🎯 緊貼在頂部分隔線下方的 Grand Objective ---
if st.session_state.token and st.session_state.user_data:
    current_data = st.session_state.user_data
    user_email = current_data["email"]
    current_goal = current_data.get("goal", "Set your grand objective here...")

    if st.session_state.is_editing_goal:
        with st.form("update_goal_form"):
            new_goal = st.text_input("Edit Grand Objective", value=current_goal)
            col_save, _ = st.columns([1, 5])
            with col_save:
                submit_goal = st.form_submit_button("Save")
            
            if submit_goal:
                if new_goal.strip():
                    current_data["goal"] = new_goal
                    save_user_data_to_cloud(user_email, current_data["level"], current_data["exp"], current_data["tasks"], current_data["goal"])
                    st.session_state.is_editing_goal = False
                    st.success("Objective updated!")
                    st.rerun()
                else:
                    st.warning("Objective cannot be empty.")
    else:
        col_goal_text, col_goal_btn = st.columns([15, 1])
        with col_goal_text:
            st.markdown(f"""
                <div style="font-family: 'Courier New', monospace; font-size: 1.5rem; color: #a0a0a0; margin-top: -5px; margin-bottom: 4px;">
                      <span style="color: #fafafa;">{current_goal}</span>
                </div>
            """, unsafe_allow_html=True)
        with col_goal_btn:
            if st.button("✏️", key="toggle_edit_goal"):
                st.session_state.is_editing_goal = not st.session_state.is_editing_goal
                st.rerun()
    st.divider()

# --- 4. 主畫面內容 ---
with st.sidebar:
    st.subheader("Background Style")
    
    theme_choice = st.selectbox(
        "Theme Selection",
        ["Dark Abyss", "Pixel Forest", "Magma Castle"]
    )

if theme_choice == "Dark Abyss":
    bg_css = """
    .stApp {
        background-color: #0f111a;
        background-image: linear-gradient(to bottom, #0f111a, #1a1c29);
    }
    section[data-testid="stSidebar"] { background-color: #141622; }
    """
elif theme_choice == "Pixel Forest":
    bg_css = """
    .stApp {
        background-color: #0b1a12;
        background-image: linear-gradient(to bottom, #0b1a12, #132e20);
    }
    section[data-testid="stSidebar"] { background-color: #0e2419; }
    """
else:
    bg_css = """
    .stApp {
        background-color: #1a0f0f;
        background-image: linear-gradient(to bottom, #1a0f0f, #2e1313);
    }
    section[data-testid="stSidebar"] { background-color: #240e0e; }
    """

st.markdown(f"""
    <style>
    {bg_css}
    </style>
""", unsafe_allow_html=True)

if not st.session_state.token:
    st.subheader("Welcome to Progression!")
    st.markdown("Please click the **Log in** button in the top right corner to start your RPG journey.")

else:
    if st.session_state.user_data is None:
        email = st.session_state.user_info.get("email")
        st.session_state.user_data = load_user_data_from_cloud(email)

    current_data = st.session_state.user_data
    user_email = current_data["email"]

    

    needed_exp = current_data["level"] * 100
    progress_ratio = min(current_data["exp"] / needed_exp, 1.0)
    
    st.metric(label="Level", value=f"Lv. {current_data['level']}", delta=f"Total EXP: {current_data['exp']}")
    
    progress_pct = int(progress_ratio * 100)

    # 修正：移除多餘的 div 確保經驗條結構乾淨
    st.markdown(f"""
        <div style="font-family: 'Courier New', monospace; font-size: 0.9rem; margin-bottom: 4px; color: #fafafa;">
            Progress to Next Level: {current_data['exp']} / {needed_exp} EXP ({progress_pct}%)
        </div>
        <div style="width: 100%; background-color: #1a1c29; border: 1px solid rgba(250, 250, 250, 0.2); border-radius: 4px; overflow: hidden; padding: 2px; margin-bottom: 1rem;">
            <div style="width: {progress_pct}%; background-color: #00FF66; height: 16px; border-radius: 2px; box-shadow: 0 0 8px rgba(0, 255, 102, 0.6); transition: width 0.5s ease-in-out;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # 任務清單區塊
    st.subheader("Quest Log")
    for index, task in enumerate(current_data["tasks"]):
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"- {task['name']} (+{task['exp']} XP)", key=f"task_{index}"):
                current_data["exp"] += task['exp']
                
                while current_data["exp"] >= current_data["level"] * 100:
                    current_data["exp"] -= current_data["level"] * 100
                    current_data["level"] += 1
                    st.success(f"Level Up! You reached Lv. {current_data['level']}!")
                
                # 修正：補上 goal 參數
                save_user_data_to_cloud(user_email, current_data["level"], current_data["exp"], current_data["tasks"], current_data["goal"])
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{index}"):
                current_data["tasks"].pop(index)
                # 修正：補上 goal 參數
                save_user_data_to_cloud(user_email, current_data["level"], current_data["exp"], current_data["tasks"], current_data["goal"])
                st.rerun()

    st.divider()
    # --- ⏳ 內嵌 RPG 專注計時器 (Pomodoro Timer) ---
    st.subheader("⏳ Focus Timer")
    timer_mode = st.selectbox("Timer Mode", ["Pomodoro (25m)", "Short Break (5m)", "Deep Work (50m)"])
    
    # 根據選擇設定秒數
    if "25m" in timer_mode:
        default_seconds = 1500
    elif "5m" in timer_mode:
        default_seconds = 300
    else:
        default_seconds = 3000

    # 修正：將 JavaScript 獨立出來，避免 f-string 的大括號衝突
    timer_html = f"""
    <div style="font-family: 'Courier New', monospace; text-align: center; background-color: #141622; padding: 10px; border-radius: 6px; border: 1px solid rgba(250, 250, 250, 0.1);">
        <div id="timer-display" style="font-size: 1.8rem; font-weight: bold; color: #00FF66; margin-bottom: 8px;">25:00</div>
        <button id="start-btn" onclick="startTimer()" style="background-color: #0e1117; color: #fafafa; border: 1px solid rgba(250, 250, 250, 0.3); padding: 4px 12px; border-radius: 4px; cursor: pointer; font-family: 'Courier New', monospace;">Start</button>
        <button id="reset-btn" onclick="resetTimer()" style="background-color: #0e1117; color: #fafafa; border: 1px solid rgba(250, 250, 250, 0.3); padding: 4px 12px; border-radius: 4px; cursor: pointer; font-family: 'Courier New', monospace; margin-left: 5px;">Reset</button>
    </div>

    <script>
    let totalSeconds = {default_seconds};
    let timerInterval = null;
    let isRunning = false;

    function updateDisplay() {{
        let minutes = Math.floor(totalSeconds / 60);
        let seconds = totalSeconds % 60;
        document.getElementById('timer-display').innerText = 
            String(minutes).padStart(2, '0') + ":" + String(seconds).padStart(2, '0');
    }}

    function startTimer() {{
        if (!isRunning) {{
            isRunning = true;
            document.getElementById('start-btn').innerText = "Pause";
            timerInterval = setInterval(() => {{
                if (totalSeconds > 0) {{
                    totalSeconds--;
                    updateDisplay();
                }} else {{
                    clearInterval(timerInterval);
                    isRunning = false;
                    document.getElementById('start-btn').innerText = "Start";
                    alert("Quest Time Completed! Great job Adventurer!");
                }}
            }}, 1000);
        }} else {{
            isRunning = false;
            clearInterval(timerInterval);
            document.getElementById('start-btn').innerText = "Start";
        }}
    }}

    function resetTimer() {{
        clearInterval(timerInterval);
        isRunning = false;
        totalSeconds = {default_seconds};
        updateDisplay();
        document.getElementById('start-btn').innerText = "Start";
    }}

    updateDisplay();
    </script>
    """
    components.html(timer_html, height=110, width=0)
    # 新增任務區塊
    st.subheader("+ Create a New Quest")
    with st.form("add_task_form"):
        new_task_name = st.text_input("Quest Name", placeholder="e.g., Finish Python Homework")
        new_task_exp = st.number_input("EXP Reward", min_value=5, max_value=500, value=30, step=5)
        submit_button = st.form_submit_button("Add Quest")
        
        if submit_button:
            if new_task_name.strip():
                current_data["tasks"].append({"name": new_task_name, "exp": new_task_exp})
                # 修正：補上 goal 參數
                save_user_data_to_cloud(user_email, current_data["level"], current_data["exp"], current_data["tasks"], current_data["goal"])
                st.success(f"New quest added: {new_task_name}!")
                st.rerun()
            else:
                st.warning("Please enter a valid quest name.")