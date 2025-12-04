# 🔮 九天玄女指定姐妹 - 紫微語音互動平台

這是一個結合 **傳統紫微斗數** 與 **生成式 AI** 的互動算命平台。
我們復刻了網紅角色「廖麗芳」的語音與人設，讓使用者能透過語音直接與 AI 算命師對談，獲得關於運勢、事業、愛情的個人化解析。

> **⚠️ 聲明**：本專案為學術/期末作業展示用途(2025_TAICA_智慧人機互動_主導課程)。語音模型採樣自網紅「阿翰po影片」之角色廖麗芳，版權歸原創作者所有，請勿用於商業用途。

## ✨ 核心功能

* **🎙️ 全語音互動**：支援語音輸入 (STT) 與 擬真語音輸出 (TTS)。
* **🧙‍♀️ 廖麗芳人設**：AI 完美模仿台灣算命阿姨的口吻（台灣國語、語助詞）。
* **🧠 智能解盤**：結合 `lunar_python` 排盤演算法與 Groq API - gpt-oss-120b 模型進行深度命理分析。
* **🎨 沉浸式 UI**：宮廟風格的暗黑紫金配色與直覺的日曆選擇介面。

## 🛠️ 技術棧 (Tech Stack)

* **Frontend**: [Streamlit](https://streamlit.io/)
* **Logic & Reasoning**: OpenAI API (GPT-4o-mini)
* **Voice Synthesis**: ElevenLabs API (Multilingual v2)
* **Speech to Text**: Google SpeechRecognition
* **Astrology Engine**: lunar-python

## 🚀 快速開始 (Installation)

請依照以下步驟在您的電腦上啟動專案。

### 1. 下載專案

```bash
# 請將下方網址換成您實際的 GitHub Repository 網址
git clone [https://github.com/您的帳號/ziwei-voice-bot.git](https://github.com/您的帳號/ziwei-voice-bot.git)
cd ziwei-voice-bot
```

### 2.建立虛擬環境 & 安裝依賴
為了避免套件衝突，強烈建議使用虛擬環境。請依據您的作業系統執行對應指令：

macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

```
### 3. 設定環境變數
由於資安考量，API Key 不會包含在程式碼中。 請在專案根目錄下建立一個名為 .env 的檔案，並填入以下資訊:
```bash
# .env 檔案內容範例
GROQ_API_KEY=gsk-xxxxxxxxxxxxxxxxxxxxxxxx
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. 啟動應用程式
```bash
python -m streamlit run app.py
```
啟動後，瀏覽器將自動開啟 http://localhost:8501。

### 5. 專案結構說明
```bash
ziwei-voice-bot/
├── app.py           # [主程式] Streamlit 前端介面與流程控制
├── logic.py         # [大腦] 負責紫微排盤運算與 OpenAI Prompt 處理
├── tts.py           # [語音] 負責呼叫 ElevenLabs 生成廖麗芳聲音
├── requirements.txt # [設定] 專案依賴庫列表
├── .env             # [設定] API Key (此檔案不應上傳)
└── .gitignore       # [設定] Git 忽略清單

```
