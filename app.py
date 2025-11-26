import streamlit as st
import datetime
import speech_recognition as sr
import os
from dotenv import load_dotenv
from logic import ZiweiBrain
from tts import get_audio_filepath

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
    h1, h2, h3, h4, h5, h6, p, span, div, label {
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

    /* ================= 日曆 (Calendar) 萬用字元修復 ================= */
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
    div[data-baseweb="calendar"] button[aria-selected="true"] {
        background-color: #b71c1c !important;
    }
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

    section[data-testid="stSidebar"] {
        background-color: #1a0b2e !important;
        border-right: 1px solid #d4af37;
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid #5a3e7a;
        border-radius: 15px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. API Key 與大腦初始化 (純 .env 模式) ---
openai_key = os.getenv("OPENAI_API_KEY")
eleven_key = os.getenv("ELEVENLABS_API_KEY")

with st.sidebar:
    st.header("⚙️ 靈力設定")
    
    # 這裡改成純顯示狀態，不再提供輸入框
    if openai_key and eleven_key:
        st.success("✅ 系統靈力充沛 (已連線)")
    else:
        st.error("❌ 靈力不足！")
        if not openai_key:
            st.warning("⚠️ 缺 OpenAI Key\n請檢查 .env 檔案")
        if not eleven_key:
            st.warning("⚠️ 缺 語音 Key\n請檢查 .env 檔案")

    st.markdown("---")
    st.info("⚠️ **期末作業聲明**：\n語音採樣自網紅「阿翰po影片」角色廖麗芳，僅供學術展示。")

engine = ZiweiBrain(api_key=openai_key) if openai_key else None

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

def main():
    if st.session_state.step == 1:
        page_user_input()
    elif st.session_state.step == 2:
        page_theme_selection()
    elif st.session_state.step == 3:
        page_chat_room()
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 重新算別的"):
            st.session_state.step = 1
            st.session_state.chat_history = []
            st.session_state.last_audio = None
            st.session_state.input_key += 1
            st.rerun()

if __name__ == "__main__":
    main()