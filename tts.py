import os
import tempfile
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import save

# 載入 .env
load_dotenv()

# 初始化 ElevenLabs Client
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# ⚠️⚠️⚠️ 請確認這裡填入的是正確的 Voice ID (約20碼亂碼)
VOICE_ID = "x6KzocdNJ8OF2NPKpTaW" 

def get_audio_filepath(text):
    """
    將文字轉為廖麗芳的語音 (MP3) - 適用於 ElevenLabs SDK v1.0+
    """
    try:
        # 1. 使用 text_to_speech.convert (這是新版 SDK 的正確寫法)
        # 注意：參數名稱變成了 voice_id 和 model_id
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,             # 參數名改了：是 voice_id
            model_id="eleven_multilingual_v2" # 參數名改了：是 model_id
        )
        
        # 2. 建立臨時檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            output_path = fp.name
            
        # 3. 存檔 (save 函數會自動處理 generator)
        save(audio_generator, output_path)
        
        print(f"✅ 阿姨語音生成完畢：{output_path}")
        return output_path

    except Exception as e:
        print(f"❌ ElevenLabs Error: {e}")
        # 如果是額度不足，可以在這裡印出來
        if "quota_exceeded" in str(e):
            print("⚠️ 額度用完了！請檢查 ElevenLabs 帳號。")
        return None