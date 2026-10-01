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
        return response.data[0]
    else:
        default_data = {
            "email": email,
            "level": 1,
            "exp": 0,
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
    </style>
""", unsafe_allow_html=True)


# --- ❄️ 滑鼠互動式下雪特效 ---
st.markdown("""
    <div id="snow-container" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 99999;">
        <canvas id="snowCanvas"></canvas>
    </div>
    <script>
    const canvas = document.getElementById('snowCanvas');
    const ctx = canvas.getContext('2d');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    let mouseX = width / 2;
    let mouseY = height / 2;

    // 即時追蹤滑鼠位置
    window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    const numFlakes = 120;
    const flakes = [];

    for (let i = 0; i < numFlakes; i++) {
        flakes.push({
            x: Math.random() * width,
            y: Math.random() * height,
            r: Math.random() * 2.5 + 0.8, // 雪花大小
            d: Math.random() * numFlakes,
            speedY: Math.random() * 1.2 + 0.4 // 下落速度
        });
    }

    function drawSnow() {
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = "rgba(255, 255, 255, 0.75)"; // 半透明白雪
        ctx.beginPath();
        for (let i = 0; i < numFlakes; i++) {
            let f = flakes[i];
            ctx.moveTo(f.x, f.y);
            ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2, true);
        }
        ctx.fill();
        updateSnow();
    }

    let angle = 0;
    function updateSnow() {
        angle += 0.01;
        // 根據滑鼠在畫面上的左右位置，計算風向偏移（滑鼠在右側，雪往右飄；滑鼠在左側，雪往左飄）
        let wind = (mouseX - width / 2) / (width / 2) * 1.8;

        for (let i = 0; i < numFlakes; i++) {
            let f = flakes[i];
            
            // 向下掉落
            f.y += f.speedY;
            // 結合自然搖晃與滑鼠風向
            f.x += Math.sin(angle + f.d) * 0.4 + wind * 0.6;

            // 邊界循環：掉到畫面底部或超出左右側時重置
            if (f.y > height) {
                f.y = 0;
                f.x = Math.random() * width;
            }
            if (f.x > width) {
                f.x = 0;
            } else if (f.x < 0) {
                f.x = width;
            }
        }
    }

    // 每 25 毫秒更新一次畫面
    setInterval(drawSnow, 25);
    </script>
""", unsafe_allow_html=True)
# --- ❄️ 滑鼠互動式下雪特效 ---
snow_html = """
<div id="snow-container" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 99999;">
    <canvas id="snowCanvas"></canvas>
</div>
<script>
const canvas = document.getElementById('snowCanvas');
const ctx = canvas.getContext('2d');

let width = canvas.width = window.innerWidth;
let height = canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
});

let mouseX = width / 2;
let mouseY = height / 2;

// 即時追蹤滑鼠位置
window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

const numFlakes = 120;
const flakes = [];

for (let i = 0; i < numFlakes; i++) {
    flakes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        r: Math.random() * 2.5 + 0.8, // 雪花大小
        d: Math.random() * numFlakes,
        speedY: Math.random() * 1.2 + 0.4 // 下落速度
    });
}

function drawSnow() {
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "rgba(255, 255, 255, 0.75)"; // 半透明白雪
    ctx.beginPath();
    for (let i = 0; i < numFlakes; i++) {
        let f = flakes[i];
        ctx.moveTo(f.x, f.y);
        ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2, true);
    }
    ctx.fill();
    updateSnow();
}

let angle = 0;
function updateSnow() {
    angle += 0.01;
    // 根據滑鼠在畫面上的左右位置，計算風向偏移
    let wind = (mouseX - width / 2) / (width / 2) * 1.8;

    for (let i = 0; i < numFlakes; i++) {
        let f = flakes[i];
        
        // 向下掉落
        f.y += f.speedY;
        // 結合自然搖晃與滑鼠風向
        f.x += Math.sin(angle + f.d) * 0.4 + wind * 0.6;

        // 邊界循環
        if (f.y > height) {
            f.y = 0;
            f.x = Math.random() * width;
        }
        if (f.x > width) {
            f.x = 0;
        } else if (f.x < 0) {
            f.x = width;
        }
    }
}

// 每 25 毫秒更新一次畫面
setInterval(drawSnow, 25);
</script>
"""

# 透過元件安全載入特效（設定 height=0 避免佔用頁面空間）
components.html(snow_html, height=0, width=0)

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

# --- 4. 主畫面內容 ---
with st.sidebar:
    st.subheader("Background Style")
    
    # 讓使用者選擇背景風格（選項與對應名稱保持一致）
    theme_choice = st.selectbox(
        "Theme Selection",
        ["Dark Abyss", "Pixel Forest", "Magma Castle"]
    )

# 根據使用者的選擇動態切換 CSS 樣式
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
else:  # Magma Castle
    bg_css = """
    .stApp {
        background-color: #1a0f0f;
        background-image: linear-gradient(to bottom, #1a0f0f, #2e1313);
    }
    section[data-testid="stSidebar"] { background-color: #240e0e; }
    """

# 將動態背景樣式套用到畫面上
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
    
    # 計算百分比 (0 ~ 100)
    progress_pct = int(progress_ratio * 100)

    # 自訂 RPG 風格的亮綠色經驗條 experience bar 動態效果
    st.markdown(f"""
        <div style="font-family: 'Courier New', monospace; font-size: 0.9rem; margin-bottom: 4px; color: #fafafa;">
            Progress to Next Level: {current_data['exp']} / {needed_exp} EXP ({progress_pct}%)
        </div>
        <div style="width: 100%; background-color: #1a1c29; border: 1px solid rgba(250, 250, 250, 0.2); border-radius: 4px; overflow: hidden; padding: 2px; margin-bottom: 1rem;">
        <div>
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
                
                save_user_data_to_cloud(user_email, current_data["level"], current_data["exp"], current_data["tasks"])
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{index}"):
                current_data["tasks"].pop(index)
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
                save_user_data_to_cloud(user_email, current_data["level"], current_data["exp"], current_data["tasks"])
                st.success(f"New quest added: {new_task_name}!")
                st.rerun()
            else:
                st.warning("Please enter a valid quest name.")