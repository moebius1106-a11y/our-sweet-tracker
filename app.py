import streamlit as st
from datetime import date, timedelta
import json
import os
import urllib.parse
import requests

# 1. 頁面基本配置
st.set_page_config(
    page_title="🌸 我的LU寶貝專屬手帳",
    page_icon="🌸",
    layout="centered"
)

# 2. 強力 CSS：消除頂部留白、防止文字折行斷句、隱藏官方雜項
st.markdown("""
<style>
.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 2rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
}

#MainMenu, footer, header {
    visibility: hidden !important;
    display: none !important;
}
[data-testid="manage-app-button"],
.viewerBadge_container__1QSob,
.viewerBadge_link__1S137,
div[class*="viewerBadge_"],
div[class*="Profile"],
div[class*="toolbar"],
div[class*="StatusWidget"],
div[data-testid="stStatusWidget"],
div[data-testid="stDecoration"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

body {
    -webkit-font-smoothing: antialiased;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang TC", "Helvetica Neue", sans-serif;
    color: #4A3B40 !important;
}
.stApp {
    background: linear-gradient(180deg, #FFF5F7 0%, #FFFFFF 100%) !important;
}

.pink-card {
    background: #FFFFFF !important;
    padding: 16px 18px !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 15px rgba(255, 175, 189, 0.25) !important;
    margin-bottom: 14px !important;
    border-left: 6px solid #FF8FA3 !important;
}
.pink-title {
    color: #D6336C !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px !important;
}
.status-badge {
    font-size: 1.15rem !important;
    font-weight: bold !important;
    color: #C2255C !important;
}

p, span, label, div {
    color: #4A3B40;
}
.hint-text {
    color: #8C6D77 !important;
    font-size: 0.85rem !important;
    text-align: center !important;
    margin-top: 6px !important;
    display: block !important;
    line-height: 1.4 !important;
}

.btn-line {
    display: block !important;
    background: linear-gradient(135deg, #06C755 0%, #00B900 100%) !important;
    color: #FFFFFF !important;
    text-align: center !important;
    padding: 12px 14px !important;
    border-radius: 22px !important;
    font-weight: bold !important;
    text-decoration: none !important;
    margin: 6px 0 !important;
    box-shadow: 0 4px 10px rgba(6, 199, 85, 0.3) !important;
    font-size: 0.98rem !important;
    white-space: nowrap !important;
}
.btn-cal {
    display: block !important;
    background: #FFF0F5 !important;
    color: #D6336C !important;
    border: 1px solid #FFCCD5 !important;
    text-align: center !important;
    padding: 10px 14px !important;
    border-radius: 18px !important;
    font-weight: bold !important;
    text-decoration: none !important;
    font-size: 0.95rem !important;
    white-space: nowrap !important;
}

.stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%) !important;
    color: #5C2D3B !important;
    border-radius: 22px !important;
    border: none !important;
    padding: 10px 24px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(255, 154, 158, 0.4) !important;
    white-space: nowrap !important;
}

div[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #FFE3E8 !important;
    border-radius: 16px !important;
}
div[data-testid="stExpander"] summary {
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    color: #5C2D3B !important;
    padding: 10px 12px !important;
}
div[data-testid="stExpander"] summary p {
    font-size: 0.92rem !important;
    margin: 0 !important;
}
</style>
""", unsafe_allow_html=True)

NTFY_TOPIC = "lu-care-moebius-alert"

def send_push_notification(title, message, priority="default"):
    try:
        headers = {
            "Title": title.encode("utf-8"),
            "Priority": priority,
            "Tags": "cherry_blossom,heart"
        }
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers=headers,
            timeout=5
        )
    except Exception:
        pass

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
        "sweet_message": "今天也要多喝溫水、肚子暖暖的喔！最愛妳了 🥰",
        "my_line_url": "https://line.me/ti/p/3u_xwcKRUB"
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

st.markdown("""
<div style="text-align: center; margin-top: 5px; margin-bottom: 15px;">
    <div style="font-size: 2rem;">🌸</div>
    <div class="pink-title">我的 LU 寶貝專屬手帳</div>
    <div style="color: #A37081; font-size: 0.88rem; margin-top: 3px;">隨時守護妳的身體與好心情・專屬紀錄</div>
</div>
""", unsafe_allow_html=True)

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

if data.get("sweet_message"):
    st.markdown(f"""
    <div class="pink-card" style="border-left-color: #FF6584; background: #FFF7F9;">
        <span style="font-size: 0.95rem; font-weight: bold; color: #D6336C;">💌 今日專屬悄悄話：</span><br>
        <div style="font-size: 1.05rem; color: #4A3B40; margin-top: 6px; line-height: 1.5;">{data['sweet_message']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="pink-card">
    <div class="status-badge">{phase}</div>
    <div style="color: #8C6D77; font-size: 0.9rem; margin-top: 4px;">目前是週期的第 <b>{days_since_start + 1}</b> 天</div>
    <div style="background: #FFF0F3; padding: 12px 14px; border-radius: 12px; margin-top: 10px; color: #5C3A45; font-size: 0.95rem; line-height: 1.45;">
        💡 <b>貼心小叮嚀：</b> {care_tip}
    </div>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"""
    <div class="pink-card" style="border-left-color: #FFB3C1; text-align: center; padding: 12px;">
        <div style="font-size: 0.85rem; color: #8A6570;">🎯 推算排卵日</div>
        <div style="font-size: 1.3rem; font-weight: bold; color: #D6336C; margin: 3px 0;">{ovulation_date.strftime("%m月%d日")}</div>
        <div style="font-size: 0.75rem; color: #B08D97;">易孕：{fertile_start.strftime("%m/%d")}~{fertile_end.strftime("%m/%d")}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    days_left = (next_period_start - today).days
    delta_text = f"約 {days_left} 天後" if days_left >= 0 else "預計報到中"
    st.markdown(f"""
    <div class="pink-card" style="border-left-color: #FF8FA3; text-align: center; padding: 12px;">
        <div style="font-size: 0.85rem; color: #8A6570;">🩸 下次月經預估</div>
        <div style="font-size: 1.3rem; font-weight: bold; color: #D6336C; margin: 3px 0;">{next_period_start.strftime("%m月%d日")}</div>
        <div style="font-size: 0.75rem; color: #E64980; font-weight: bold;">{delta_text}</div>
    </div>
    """, unsafe_allow_html=True)

line_target_url = data.get("my_line_url", "https://line.me/ti/p/3u_xwcKRUB")
st.markdown(f'<a href="{line_target_url}" target="_blank" class="btn-line">💬 開啟男友 LINE（聊天 / 通話）</a>', unsafe_allow_html=True)
st.markdown('<span class="hint-text">✨ 點擊直接開啟男友名片，隨時隨地找我聊天或通話</span>', unsafe_allow_html=True)

event_title = "🌸 LU寶貝生理期呵護提醒"
event_details = "記得多喝溫水、肚子保暖、放鬆心情～有另一半隨時疼妳哄妳 🥰"
gcal_start = next_period_start.strftime("%Y%m%d")
gcal_end = (next_period_start + timedelta(days=1)).strftime("%Y%m%d")
gcal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote(event_title)}&dates={gcal_start}/{gcal_end}&details={urllib.parse.quote(event_details)}"

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
    st.markdown(f'<a href="{gcal_url}" target="_blank" class="btn-cal">📅 Google 日曆</a>', unsafe_allow_html=True)
with col_cal2:
    st.download_button(
        label="🍏 Apple 行事曆",
        data=ics_content,
        file_name="lu_care_reminder.ics",
        mime="text/calendar",
        use_container_width=True
    )

with st.expander("⚙️ 點此修改經期設定與悄悄話", expanded=False):
    default_date = date.fromisoformat(data.get("last_period_start", "2026-09-21"))
    new_period_start = st.date_input("月經開始第一天", value=default_date)
    new_cycle_length = st.number_input("平均週期天數", min_value=21, max_value=45, value=data.get("cycle_length", 28))
    new_msg = st.text_area("寫給寶貝的專屬悄悄話", value=data.get("sweet_message", ""))
    
    if st.button("💾 儲存並同步更新手帳"):
        data["last_period_start"] = str(new_period_start)
        data["cycle_length"] = int(new_cycle_length)
        data["sweet_message"] = new_msg
        save_data(data)
        
        send_push_notification(
            title="🌸 LU寶貝的手帳有新更新！",
            message=f"寶貝更新了手帳！\n最後經期開始日設為：{new_period_start}\n週期：{new_cycle_length}天",
            priority="high"
        )
        
        st.success("手帳已成功同步更新！已發送通知提醒男友 🥰")
        st.rerun()
