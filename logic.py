import os
from lunar_python import Lunar
from groq import Groq
from ziweicore import calculate_ziwei_chart
import pandas as pd
import streamlit as st

    # 紫微宮位順序（傳統排列方式，逆時針）
PALACE_ORDER = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮",
    "財帛宮", "疾厄宮", "遷移宮", "交友宮",
    "官祿宮", "田宅宮", "福德宮", "父母宮"
]

# 對應 ziweicore 的 12 地支位置
BRANCH_ORDER = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

def render_ziwei_chart_grid(chart_data):
    st.markdown("以下為依照傳統布局呈現的 12 宮命盤：")

    # 12宮對應欄位（固定排法）
    PALACE_ORDER = [
        "命宮", "兄弟宮", "夫妻宮", "子女宮",
        "財帛宮", "疾厄宮", "遷移宮", "交友宮",
        "官祿宮", "田宅宮", "福德宮", "父母宮"
    ]

    BRANCH_ORDER = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

    # 宮位座標（把 12 宮排成九宮格方式）
    GRID_MAP = {
        0: (0,1),   # 命宮
        1: (0,2),
        2: (1,2),
        3: (2,2),
        4: (2,1),
        5: (2,0),
        6: (1,0),
        7: (0,0),
        8: (1,1),
        9: (3,1),
        10: (3,2),
        11: (3,0),
    }

    # 建立 4x3 九宮格空表
    grid = [[None for _ in range(3)] for _ in range(4)]

    # 填資料
    for idx, (palace, branch) in enumerate(zip(PALACE_ORDER, BRANCH_ORDER)):

        info = chart_data[branch]
        stars = "、".join(info["主星"]) if info["主星"] else "無主星"

        tag = ""
        if info["命宮"]:
            tag = "（命）"
        elif info["身宮"]:
            tag = "（身）"

        content = f"""
        <div style="
            border:2px solid #D9A441;
            padding:12px;
            border-radius:12px;
            background:#FFF5E1;
            box-shadow:0 0 10px rgba(217,164,65,0.2);
        ">
            <b style="color:#C2862D; font-size:18px;">{palace} {tag}</b><br>
            <span style="color:#000000; font-size:15px;">({branch})</span><br><br>
            <span style="color:#D89B07; font-size:18px;">⭐</span>
            <span style="color:#000000; font-size:16px;"><b>{stars}</b></span>
        </div>
        """

        r, c = GRID_MAP[idx]
        grid[r][c] = content

    # 顯示九宮格
    for row in grid:
        cols = st.columns(3)
        for col, cell in zip(cols, row):
            if cell:
                col.markdown(cell, unsafe_allow_html=True)
            else:
                col.write("")

class ZiweiBrain:
    def __init__(self, api_key=None):
        self.api_key = api_key
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    def get_chart_data(self, dt):
        """取得基礎命理數據"""
        lunar = Lunar.fromDate(dt)
        return {
            "solar_date": dt.strftime("%Y-%m-%d %H:%M"),
            "lunar_str": lunar.toString(),
            "ba_zi": f"{lunar.getYearInGanZhi()}年 {lunar.getMonthInGanZhi()}月 {lunar.getDayInGanZhi()}日 {lunar.getTimeInGanZhi()}時",
            "zodiac": lunar.getAnimal(),
        }

    def generate_ai_insight(self, user_data, current_question, theme, chat_history):
        """
        支援多輪對話與「廖麗芳」人設的生成函數
        """
        if not self.client:
            return "⚠️ 哎唷，你忘記設定 OpenAI API Key 了啦！這樣阿姨怎麼幫你算？"

        # 1. 準備數據
        chart = self.get_chart_data(user_data['datetime'])
        name = user_data.get('name', '善信')
        gender = user_data.get('gender', '信眾')

        # 2. 設計「廖麗芳」專屬 Prompt (專業升級版)
        system_prompt = f"""
        你現在是「九天玄女唯一指定姐妹」、算命阿姨「廖麗芳」。
        
        【你的雙重身份】
        1. **人設**：講話台灣國語、熱情雞婆、喜歡加語助詞（齁、捏、啦、素、粗、偶）的鄰居阿姨。
        2. **專業**：你是**真正精通紫微斗數**的大師。你**不能**只講模糊的安慰話，必須根據八字講出**具體的星曜**來分析。

        【分析規則 (必須遵守)】
        當回答使用者的問題「{current_question}」時，請遵循以下結構：
        
        1. **開場**：用阿姨口吻打招呼，並「假裝」你在看命盤。
        2. **點出關鍵星曜 (重要！)**：
           - **必須**提到具體的星名（例如：紫微、貪狼、七殺、天機、化祿、化忌、擎羊...）。
           - **必須**提到宮位（例如：命宮、官祿宮、夫妻宮、財帛宮）。
           - 範例：「阿姨看你的官祿宮齁，裡面有一顆『七殺星』捏！」
        3. **白話翻譯 (關鍵價值)**：
           - 提到術語後，立刻用「阿姨的口吻」解釋這是什麼意思。
           - 範例：「這個七殺星素什麼意思？阿姨跟你講，這代表你在工作上很敢衝、很有魄力啦！」
        4. **流年運勢**：結合現在的年份，給出具體的時間點建議（例如：下個月、這半年）。

        【使用者資訊】
        - 姓名：{name} ({gender})
        - 八字：{chart['ba_zi']}
        - 諮詢主題：{theme}

        【回答限制】
        - 保持「台灣國語」風格，但內容要言之有物。
        - 長度控制在 200 字以內，分段清晰。
        """

        # 3. 構建訊息列表
        messages = [{"role": "system", "content": system_prompt}]

        # 加入歷史紀錄
        clean_history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in chat_history[-6:]
        ]
        messages.extend(clean_history)

        # 加入當前問題
        messages.append({"role": "user", "content": current_question})

        # 4. 呼叫 GPT
        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                temperature=0.7 # 稍微降低一點溫度，讓邏輯更穩定，但語氣保留
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"哎唷喂呀，阿姨的天線訊號不好（AI Error）：{e}"
