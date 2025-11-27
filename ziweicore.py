# ziwei_core.py

from lunar_python import Lunar
from datetime import datetime

# 地支
BRANCHES = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

# 天干
STEMS = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]

# 五行局 (依命宮 + 年干決定)
FIVE_ELEMENTS = ["木", "火", "土", "金", "水"]

# 紫微 14 主星
MAIN_STARS = [
    "紫微","天機","太陽","武曲","天同","廉貞","天府",
    "太陰","貪狼","巨門","天相","天梁","七殺","破軍"
]

# 14 主星的排盤表（簡化後的 Python 版）
# 來源：專業紫微斗數表格（JS 版本的 Star_A14）
# 每個主星依照「紫微星所在宮」推算位置
# 這裡用 12 宮（0~11）表達
STAR_A14 = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # 紫微星
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0],  # 天機
    [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1],  # 太陽
    [3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2],  # 武曲
    [4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3],  # 天同
    [5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4],  # 廉貞
    [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],  # 天府
    [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6],  # 太陰
    [8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7],  # 貪狼
    [9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8],  # 巨門
    [10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],  # 天相
    [11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # 天梁
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # 七殺
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0]   # 破軍
]


# ---------------------------------------------------------------------
# ⭐ Step 1：計算命宮
# ---------------------------------------------------------------------
def get_ming_gong(lunar_month, hour_branch_index):
    return (lunar_month + hour_branch_index) % 12


# ---------------------------------------------------------------------
# ⭐ Step 2：計算身宮
# ---------------------------------------------------------------------
def get_shen_gong(lunar_month, hour_branch_index):
    return (lunar_month + hour_branch_index + 5) % 12


# ---------------------------------------------------------------------
# ⭐ Step 3：五行局計算（年干 + 命宮）
# ---------------------------------------------------------------------
def get_five_element(stem_index, ming_gong):
    # 傳統五行局公式：
    # 五行局 = (年干 % 5 + 命宮%6) % 5
    return FIVE_ELEMENTS[(stem_index % 5 + (ming_gong % 6)) % 5]


# ---------------------------------------------------------------------
# ⭐ Step 4：排主星（依「紫微所在地」為基準）
# 紫微星的位置由五行局 + 農曆生日（簡化版）
# ---------------------------------------------------------------------
def place_main_stars(ziwei_pos):
    places = [[] for _ in range(12)]
    for i, star in enumerate(MAIN_STARS):
        pos = STAR_A14[i][ziwei_pos]
        places[pos].append(star)
    return places


# ---------------------------------------------------------------------
# ⭐ 主函式：傳入出生西元時間 → 回傳命盤資料
# ---------------------------------------------------------------------
def calculate_ziwei_chart(dt: datetime, gender: str):
    lunar = Lunar.fromDate(dt)

    # 年干支
    year_gan = (dt.year - 4) % 10
    year_zhi = (dt.year - 4) % 12

    # 地支時辰 index（每兩小時為一支）
    hour_index = dt.hour // 2

    # 命宮
    ming_gong = get_ming_gong(lunar.getMonth(), hour_index)

    # 身宮
    shen_gong = get_shen_gong(lunar.getMonth(), hour_index)

    # 五行局
    five_ele = get_five_element(year_gan, ming_gong)

    # 紫微星所在宮（五行局 → 起紫微表）
    ziwei_pos = (lunar.getDay() + ming_gong) % 12

    # 排主星
    main_star_table = place_main_stars(ziwei_pos)

    # 組成完整命盤
    chart = {}
    for i in range(12):
        chart[BRANCHES[i]] = {
            "宮位": i,
            "主星": main_star_table[i],
            "命宮": (i == ming_gong),
            "身宮": (i == shen_gong),
            "五行局": five_ele if i == ming_gong else None,
        }

    return chart
