import os
from lunar_python import Lunar
from openai import OpenAI

class ZiweiBrain:
    def __init__(self, api_key=None):
        self.api_key = api_key
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
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
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7 # 稍微降低一點溫度，讓邏輯更穩定，但語氣保留
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"哎唷喂呀，阿姨的天線訊號不好（AI Error）：{e}"