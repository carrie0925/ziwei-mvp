import streamlit as st
import datetime
import speech_recognition as sr
import os
from dotenv import load_dotenv
from logic import ZiweiBrain, render_ziwei_chart_grid
from tts import get_audio_filepath
from ziweicore import calculate_ziwei_chart
import time
from pathlib import Path
import base64
import uuid
from streamlit.components.v1 import html



# 0. 載入環境變數
load_dotenv()

# --- 1. 設定頁面 ---
st.set_page_config(page_title="九天玄女指定姐妹 - 紫微語音室", layout="centered", page_icon="🔮")

# ⚠️ CSS 終極修復：維持之前的完美暗黑主題
st.markdown("""
<style>
    /* ================= 全域設定 ================= */
    .stApp {
        background: linear-gradient(180deg, #1a0b2e 0%, #2d1b4e 100%);
    }
    h1, h2, h3, h4, h5, h6, p, label {
        font-family: 'Noto Serif TC', 'Songti TC', serif !important;
        color: #f0e6d2 !important;
    }
    h1 {
        color: #ffd700 !important;
        text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.6);
        text-align: center;
        font-weight: 800 !important;
    }

    /* ================= 輸入框優化 ================= */
    .stTextInput label, .stSelectbox label, .stDateInput label, .stTimeInput label {
        color: #ffd700 !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: #ffffff !important;
        border: 1px solid #d4af37 !important;
    }

    /* ================= 日曆 (Calendar) ================= */
    div[data-baseweb="popover"], div[data-baseweb="calendar"] {
        background-color: #1a0b2e !important;
        border: 1px solid #d4af37 !important;
    }
    div[data-baseweb="calendar"] * {
        background-color: #1a0b2e !important; 
        color: #f0e6d2 !important;
    }
    div[data-baseweb="calendar"] button:hover {
        background-color: #4a148c !important;
        border-radius: 50%;
    }
    div[data-baseweb="calendar"] button:hover div {
        background-color: #4a148c !important;
    }
    div[data-baseweb="calendar"] button[aria-selected="true"],
    div[data-baseweb="calendar"] button[aria-selected="true"] div {
        background-color: #b71c1c !important;
        color: #ffffff !important;
    }
    div[data-baseweb="calendar"] svg {
        fill: #ffd700 !important;
        background-color: transparent !important;
    }
    
    /* ================= 其他元件 ================= */
    div[data-baseweb="select"] > div {
        background-color: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid #d4af37 !important;
        color: #ffffff !important;
    }
    div[data-baseweb="menu"] {
        background-color: #1a0b2e !important;
    }
    li[role="option"] {
        background-color: #1a0b2e !important;
        color: #f0e6d2 !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #b71c1c !important;
        color: #ffffff !important;
    }

    /* ================= 按鈕 ================= */
    .stButton button {
        background: linear-gradient(to bottom, #7b1fa2, #4a148c) !important;
        color: #ffd700 !important;
        border: 2px solid #d4af37 !important;
        border-radius: 12px !important;
        font-size: 18px !important;
    }
    .stButton button:hover {
        background: linear-gradient(to bottom, #9c27b0, #7b1fa2) !important;
        box-shadow: 0px 0px 15px #ffd700;
        color: #fff !important;
    }
    div[data-testid="stForm"] button p { color: #ffd700 !important; }

    /* ================= 側邊欄 ================= */
    section[data-testid="stSidebar"] {
        background-color: #1a0b2e !important;
        border-right: 1px solid #d4af37;
    }

    /* ================= Chat Message 氣泡 ================= */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid #5a3e7a;
        border-radius: 15px;
    }

    /* ====== ❗ 讓聊天字變淺色（關鍵修正） ====== */
    .stChatMessage p,
    .stChatMessage span,
    .stChatMessage div,
    .stChatMessage .stMarkdown,
    .stChatMessage pre {
        color: #f8f3e6 !important; /* 奶油白 */
    }

    /* 使用者訊息（User bubble） */
    .stChatMessage[data-testid="stChatMessageUser"] p {
        color: #ffffff !important;
    }

    /* ================= 隱藏 Streamlit logo ================= */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 2. API Key 與大腦初始化 (純 .env 模式) ---
groq_key = os.getenv("GROQ_API_KEY")
eleven_key = os.getenv("ELEVENLABS_API_KEY")

with st.sidebar:
    st.header("⚙️ 靈力設定")
    
    # 這裡改成純顯示狀態，不再提供輸入框
    if groq_key and eleven_key:
        st.success("✅ 系統靈力充沛 (已連線)")
    else:
        st.error("❌ 靈力不足！")
        if not groq_key:
            st.warning("⚠️ 缺 OpenAI Key\n請檢查 .env 檔案")
        if not eleven_key:
            st.warning("⚠️ 缺 語音 Key\n請檢查 .env 檔案")

    st.markdown("---")
    st.info("⚠️ **期末作業聲明**：\n語音採樣自網紅「阿翰po影片」角色廖麗芳，僅供學術展示。")

engine = ZiweiBrain(api_key=groq_key) if groq_key else None

# --- 3. 狀態管理 ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'user_data' not in st.session_state: st.session_state.user_data = {}
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'last_audio' not in st.session_state: st.session_state.last_audio = None
if 'current_theme' not in st.session_state: st.session_state.current_theme = "整體運勢"
if 'input_key' not in st.session_state: st.session_state.input_key = 0

# --- 4. STT ---
def transcribe_audio(audio_file_obj):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_obj) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="zh-TW")
            return text
    except sr.UnknownValueError:
        return None
    except Exception as e:
        return f"聽不懂捏 ({e})"

# --- 5. 頁面邏輯 ---
def page_user_input():
    st.markdown("<h1 style='font-size: 3.5rem;'>🔯 紫微天機閣 🔯</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #d4af37; font-size: 1.2rem;'>九天玄女指定姐妹 • 廖麗芳 親算</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.container():
        st.markdown("### 📝 請填寫生辰八字")
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("您的尊姓大名", placeholder="例如：阿美")
                date = st.date_input("出生日期", min_value=datetime.date(1950, 1, 1))
            with col2:
                gender = st.selectbox("性別", ["女", "男"])
                time_val = st.time_input("出生時間", step=900)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🙏 呈報八字，開始算命", use_container_width=True)
            if submitted:
                if not name:
                    st.error("哎唷，名字要寫啦！")
                else:
                    st.session_state.user_data = {
                        "name": name,
                        "datetime": datetime.datetime.combine(date, time_val),
                        "gender": gender
                    }
                    st.session_state.step = 4
                    st.rerun()

def page_chart_display():
    st.markdown("## 🔮 您的紫微命盤")
    st.session_state.ziwei_chart = calculate_ziwei_chart(
        st.session_state.user_data["datetime"],
        st.session_state.user_data["gender"]
    )

    # 🟣 九宮格 UI
    render_ziwei_chart_grid(st.session_state.ziwei_chart)

        # 上一頁（回到 step 1）
    if st.button("⬅️ 返回輸入頁"):
        st.session_state.step = 1
        st.rerun()

    if st.button("👉 看夠了，帶我去算命！", use_container_width=True):
        st.session_state.step = 2
        st.rerun()


def page_theme_selection():
    st.markdown("<h1>🔮 您想求什麼？</h1>", unsafe_allow_html=True)
    user_name = st.session_state.user_data.get('name')
    st.markdown(f"<p style='text-align: center; font-size: 1.3rem; color: #fff;'>善信 <b style='color:#ffd700'>{user_name}</b> 哩賀！我是廖麗芳。<br>來，心誠則靈，你想問哪方面？</p>", unsafe_allow_html=True)
    st.markdown("---")
    themes = ["💰 財富運勢", "🍎 健康平安", "🌸 愛情桃花", "🏆 事業工作"]
    cols = st.columns(2)
    for i, theme in enumerate(themes):
        clean_theme = theme.split(" ")[1]
        if cols[i % 2].button(theme, type="primary", use_container_width=True):
            st.session_state.current_theme = clean_theme
            opening_text = f"來，{user_name}，關於這個{clean_theme}齁，阿姨幫你看一下命盤..."
            st.session_state.chat_history.append({"role": "assistant", "content": opening_text})
            with st.spinner("阿姨正在請神..."):
                audio_path = get_audio_filepath(opening_text)
                st.session_state.last_audio = audio_path
            st.session_state.step = 3
            st.rerun()
        # 上一頁（回到 step 1）
    if st.button("⬅️ 返回命盤"):
        st.session_state.step = 4
        st.rerun()

def page_chat_room():
    st.markdown("<h1>🎙️ 廖麗芳紫微語音室</h1>", unsafe_allow_html=True)
    
    # 檢查 API Key 是否存在，若不存在顯示錯誤並停止
    if not engine:
        st.error("⚠️ 系統偵測不到 API Key！請確認您的 .env 檔案是否設定正確。")
        return

    for msg in st.session_state.chat_history:
        avatar = "🧙‍♀️" if msg["role"] == "assistant" else "🧑‍💼"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(f"<span style='font-size: 1.1rem;'>{msg['content']}</span>", unsafe_allow_html=True)
    
    if st.session_state.last_audio:
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
        st.session_state.last_audio = None

    st.markdown("---")
    st.markdown("### 👇 請按麥克風，直接用講的：")
    current_key = f"audio_{st.session_state.input_key}"
    audio_value = st.audio_input("錄製您的問題", key=current_key)

    if audio_value:
        with st.spinner("阿姨正在感應宇宙能量 (聽打與思考中)..."):
            user_text = transcribe_audio(audio_value)
            if user_text:
                ai_reply = engine.generate_ai_insight(
                    user_data=st.session_state.user_data, 
                    current_question=user_text, 
                    theme=st.session_state.current_theme,
                    chat_history=st.session_state.chat_history
                )
                st.session_state.chat_history.append({"role": "user", "content": user_text})
                st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
                audio_path = get_audio_filepath(ai_reply)
                st.session_state.last_audio = audio_path
                st.session_state.input_key += 1
                st.rerun()
            else:
                st.warning("阿姨聽不清楚捏，你大聲一點～")

    if st.button("⬅️ 返回主題頁"):
        st.session_state.step = 2
        st.rerun()

    if st.button("🪵 我要去敲木魚結緣"):
        st.session_state.step = 5
        st.rerun()

# --- 載入圖片 ---
def load_image_base64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()

muyu_base64 = load_image_base64("assets/wood_fish.png")

def page_final_blessing():
    if st.session_state.previous_step != 5:
        st.session_state.gongde = 0
        st.session_state.muyu_hit = False

    if "gongde" not in st.session_state:
        st.session_state.gongde = 0
    if "muyu_hit" not in st.session_state:
        st.session_state.muyu_hit = False

    st.markdown("<h1 style='text-align:center;'>🪵 紫微木魚功德頁</h1>", unsafe_allow_html=True)

    # --- CSS：木魚動畫 ---
    st.markdown(
        """
        <style>
        .muyu-wrap {
            text-align: center;
            margin-top: 10px;
        }
        .muyu-img {
            width: 320px;
            transition: transform 100ms ease-out;
            cursor: pointer;
        }
        .muyu-hit {
            animation: muyu-bonk 0.1s ease-out;
        }
        @keyframes muyu-bonk {
            0%   { transform: scale(1); }
            50%  { transform: scale(0.9); }
            100% { transform: scale(1); }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    img_class = "muyu-img muyu-hit" if st.session_state.muyu_hit else "muyu-img"

    st.markdown(
        f"""
        <div class="muyu-wrap">
            <img class="{img_class}" src="data:image/png;base64,{muyu_base64}">
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------------
    # 🔥 修正重點：改用 HTML Audio 標籤播放 (避開 st.audio 不支援 key 的問題)
    # -----------------------------------------------------------
    if st.session_state.muyu_hit:
        try:
            # 1. 讀取音檔並轉成 base64 (網頁只能讀字串)
            audio_file = open("assets/muyu.mp3", "rb")
            audio_bytes = audio_file.read()
            audio_b64 = base64.b64encode(audio_bytes).decode()
            
            # 2. 生成一個隨機 ID，強迫瀏覽器認為這是新的音效 (解決連點不播放問題)
            sound_id = f"muyu_sound_{uuid.uuid4()}"
            
            # 3. 寫入一段隱藏的 HTML 來播放
            # display:none -> 隱藏播放器
            # autoplay -> 自動播放
            st.markdown(
                f"""
                <audio autoplay="true" style="display:none;" id="{sound_id}">
                    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                </audio>
                """,
                unsafe_allow_html=True
            )
        except FileNotFoundError:
            st.warning("⚠️ 找不到音效檔 assets/muyu.mp3")
    # -----------------------------------------------------------

    # 按鈕
    if st.button("🪵 敲一下木魚", use_container_width=True):
        st.session_state.gongde += 1
        st.session_state.muyu_hit = True
        st.rerun()

    st.markdown(
        f"<h2 style='text-align:center; margin-top:10px;'>累積功德：{st.session_state.gongde}</h2>",
        unsafe_allow_html=True
    )

    st.session_state.muyu_hit = False

    if st.button("⬅️ 回首頁"):
        st.session_state.step = 1
        st.rerun()

def main():
    if "previous_step" not in st.session_state:
        st.session_state.previous_step = None

    current_step = st.session_state.step

    if current_step == 1:
        page_user_input()
    elif current_step == 4:
        page_chart_display()
    elif current_step == 2:
        page_theme_selection()
    elif current_step == 3:
        page_chat_room()
    elif current_step == 5:
        page_final_blessing()
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 重新算別的"):
        st.session_state.step = 1
        st.session_state.chat_history = []
        st.session_state.last_audio = None
        st.session_state.input_key += 1
        st.rerun()
    st.session_state.previous_step = current_step


if __name__ == "__main__":
    main()