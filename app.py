import streamlit as st
from datetime import date, timedelta
import json
import os
import urllib.parse

# 1. 頁面基本配置
st.set_page_config(
    page_title="🌸 我的LU寶貝專屬手帳",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. iPhone 介面優化、隱藏 Streamlit 水印與頭貼、極致粉嫩風格
st.markdown("""
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <style>
    /* 隱藏 Streamlit 頂部與底部所有官方雜項、大頭貼、皇冠按鈕 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob, .viewerBadge_link__1S137, [data-testid="manage-app-button"] {
        display: none !important;
    }
    div[class^="viewerBadge_"] {
        display: none !important;
    }

    /* iPhone 沉浸式粉嫩背景與字體 */
    body {
        -webkit-font-smoothing: antialiased;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .stApp {
        background: linear-gradient(180deg, #FFF6F8 0%, #FFFFFF 100%);
    }

    /* 卡片設計：柔美圓角與粉紅微光陰影 */
    .pink-card {
        background: #FFFFFF;
        padding: 18px 20px;
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(255, 182, 193, 0.25);
        margin-bottom: 16px;
        border-left: 6px solid #FF8FA3;
    }
    .pink-title {
        color: #D6336C;
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .status-badge {
        font-size: 1.15rem;
        font-weight: bold;
        color: #C2255C;
    }

    /* 日曆與操作按鈕美化 */
    .cal-btn {
        display: inline-block;
        padding: 10px 16px;
        margin: 6px 4px;
        border-radius: 25px;
        text-decoration: none;
        font-weight: bold;
        font-size: 0.95rem;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    }
    .btn-google {
        background-color: #FFF0F5;
        color: #D6336C !important;
        border: 1px solid #FFCCD5;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%);
        color: #5C2D3B;
        border-radius: 22px;
        border: none;
        padding: 10px 24px;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(255, 154, 158, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "cycle_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_period_start": "2026-09-21",
        "cycle_length": 28,
        "sweet_message": "今天也要多喝溫水、肚子暖暖的喔！最愛妳了 🥰"
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# 標題區
st.markdown("""
<div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
    <div style="font-size: 2.2rem;">🌸</div>
    <div class="pink-title">我的 LU 寶貝專屬手帳</div>
    <div style="color: #A37081; font-size: 0.9rem; margin-top: 4px;">隨時守護妳的身體與好心情・專屬紀錄</div>
</div>
""", unsafe_allow_html=True)

# --- 側邊欄：記錄與更新 ---
with st.sidebar:
    st.header("⚙️ 週期設置與留悄悄話")
    default_date = date.fromisoformat(data.get("last_period_start", "2026-09-21"))
    new_period_start = st.date_input("月經開始第一天", value=default_date)
    new_cycle_length = st.number_input("平均週期天數", min_value=21, max_value=45, value=data.get("cycle_length", 28))
    
    st.subheader("💌 今日給 LU 寶貝的悄悄話")
    new_msg = st.text_area("寫下暖心留言", value=data.get("sweet_message", ""))
    
    if st.button("💾 儲存並同步更新"):
        data["last_period_start"] = str(new_period_start)
        data["cycle_length"] = int(new_cycle_length)
        data["sweet_message"] = new_msg
        save_data(data)
        st.success("已更新！")
        st.rerun()

# --- 週期推算邏輯 ---
period_start = date.fromisoformat(data["last_period_start"])
cycle_days = data["cycle_length"]
today = date.today()

next_period_start = period_start + timedelta(days=cycle_days)
ovulation_date = next_period_start - timedelta(days=14)
fertile_start = ovulation_date - timedelta(days=5)
fertile_end = ovulation_date + timedelta(days=1)

days_since_start = (today - period_start).days % cycle_days

if days_since_start < 5:
    phase = "🩸 生理期中・好好休息"
    care_tip = "這幾天肚子容易悶脹，冰品冷飲先放一邊喔～多喝溫熱開水，肚子跟腳腳一定要保暖，累了就乖乖躺好讓我哄妳 🥰"
elif fertile_start <= today <= fertile_end:
    phase = "🌸 排卵期・活力滿滿"
    care_tip = "這幾天氣色最好、代謝快，記得多喝水補足水分，今天也是最迷人耀眼的一天！"
elif today < ovulation_date:
    phase = "🌱 卵泡期・心情舒暢"
    care_tip = "身體活力逐漸回升，精神跟心情都很棒，今天想吃什麼好料就好好享受吧～"
else:
    phase = "🌙 經前前夕 (PMS)・溫柔守護"
    care_tip = "這兩天月經快報到了，容易水腫或下腹悶悶的，心情敏感都是正常的～別給自己壓力，凡事都有我陪著妳喔！"

# --- 1. 今日暖心留言 ---
if data.get("sweet_message"):
    st.markdown(f"""
    <div class="pink-card" style="border-left-color: #FF6584; background: #FFF7F9;">
        <span style="font-size: 0.95rem; font-weight: bold; color: #D6336C;">💌 今日專屬悄悄話：</span><br>
        <div style="font-size: 1.05rem; color: #4A3B40; margin-top: 6px; line-height: 1.5;">{data['sweet_message']}</div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 當前狀態與暖心指引 ---
st.markdown(f"""
<div class="pink-card">
    <div class="status-badge">{phase}</div>
    <div style="color: #8C6D77; font-size: 0.9rem; margin-top: 4px;">目前是週期的第 <b>{days_since_start + 1}</b> 天</div>
    <div style="background: #FFF0F3; padding: 12px 14px; border-radius: 12px; margin-top: 10px; color: #5C3A45; font-size: 0.95rem; line-height: 1.45;">
        💡 <b>貼心小叮嚀：</b> {care_tip}
    </div>
</div>
""", unsafe_allow_html=True)

# --- 3. 關鍵推估數據 ---
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"""
    <div class="pink-card" style="border-left-color: #FFB3C1; text-align: center; padding: 14px;">
        <div style="font-size: 0.85rem; color: #8A6570;">🎯 推算排卵日</div>
        <div style="font-size: 1.35rem; font-weight: bold; color: #D6336C; margin: 4px 0;">{ovulation_date.strftime("%m月%d日")}</div>
        <div style="font-size: 0.75rem; color: #B08D97;">易孕：{fertile_start.strftime("%m/%d")}~{fertile_end.strftime("%m/%d")}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    days_left = (next_period_start - today).days
    delta_text = f"約 {days_left} 天後" if days_left >= 0 else "預計報到中"
    st.markdown(f"""
    <div class="pink-card" style="border-left-color: #FF8FA3; text-align: center; padding: 14px;">
        <div style="font-size: 0.85rem; color: #8A6570;">🩸 下次月經預估</div>
        <div style="font-size: 1.35rem; font-weight: bold; color: #D6336C; margin: 4px 0;">{next_period_start.strftime("%m月%d日")}</div>
        <div style="font-size: 0.75rem; color: #E64980; font-weight: bold;">{delta_text}</div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. 一鍵加入日曆與 iPhone 自動提醒 ---
st.markdown("""
<div style="text-align: center; margin-top: 10px; margin-bottom: 8px;">
    <span style="font-weight: bold; color: #D6336C; font-size: 0.95rem;">⏰ 點擊下方加入手機自動提醒</span>
</div>
""", unsafe_allow_html=True)

# 產生 Google 日曆連結
event_title = "🌸 LU寶貝生理期呵護提醒"
event_details = "記得多喝溫水、肚子保暖、放鬆心情～有另一半隨時疼妳哄妳 🥰"
gcal_start = next_period_start.strftime("%Y%m%d")
gcal_end = (next_period_start + timedelta(days=1)).strftime("%Y%m%d")
gcal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote(event_title)}&dates={gcal_start}/{gcal_end}&details={urllib.parse.quote(event_details)}"

# 產生 Apple 行事曆 (.ics 檔案)
ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//LU Baby Care//TW
BEGIN:VEVENT
SUMMARY:{event_title}
DESCRIPTION:{event_details}
DTSTART;VALUE=DATE:{next_period_start.strftime('%Y%m%d')}
DTEND;VALUE=DATE:{(next_period_start + timedelta(days=1)).strftime('%Y%m%d')}
BEGIN:VALARM
TRIGGER:-PT12H
ACTION:DISPLAY
DESCRIPTION:提醒寶貝注意保暖與多喝熱水
END:VALARM
END:VEVENT
END:VCALENDAR"""

col_cal1, col_cal2 = st.columns(2)
with col_cal1:
    st.markdown(f'<a href="{gcal_url}" target="_blank" class="cal-btn btn-google" style="display:block;">📅 Google 日曆</a>', unsafe_allow_html=True)
with col_cal2:
    st.download_button(
        label="🍏 Apple 行事曆提醒",
        data=ics_content,
        file_name="lu_care_reminder.ics",
        mime="text/calendar",
        use_container_width=True
    )

st.caption("✨ iPhone 用戶點擊「Apple 行事曆提醒」即可自動匯入行事曆並設定鬧鐘提醒。")
