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

# 2. 全面修復深色模式字體隱形、跨瀏覽器適應與官方圖標抹除
st.markdown("""
<style>
/* 徹底去除頂部空白，手機介面緊湊 */
.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 2rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
}

/* 抹除官方管理按鈕、頭貼、選單 */
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

/* 強制鎖定全站淺粉色系（避免 Brave/手機深色模式造成白字隱形） */
:root {
    color-scheme: light !important;
}
body {
    -webkit-font-smoothing: antialiased;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang TC", "Helvetica Neue", sans-serif;
    color: #4A3B40 !important;
    background-color: #FFF5F7 !important;
}
.stApp {
    background: linear-gradient(180deg, #FFF5F7 0%, #FFFFFF 100%) !important;
}

/* 卡片設計 */
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

/* 徹底修復：所有文字標籤在深色模式下全部維持清晰深色 */
p, span, label, div, h1, h2, h3, h4, li {
    color: #4A3B40 !important;
}
.hint-text {
    color: #8C6D77 !important;
    font-size: 0.85rem !important;
    text-align: center !important;
    margin-top: 6px !important;
    display: block !important;
}

/* 徹底修復折疊面板（Expander）在 Brave 裡白字隱形的問題 */
div[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #FFCCD5 !important;
    border-radius: 16px !important;
    margin-bottom: 12px !important;
}
div[data-testid="stExpander"] summary {
    background-color: #FFFFFF !important;
    border-radius: 16px !important;
    padding: 10px 14px !important;
}
div[data-testid="stExpander"] summary * {
    color: #5C2D3B !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    fill: #5C2D3B !important;
}
div[data-testid="stExpander"] details[open] summary {
    border-bottom: 1px solid #FFE3E8 !important;
}

/* 呼叫男友與行事曆按鈕樣式 */
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
</style>
""", unsafe_allow_html=True)

# --- 後台即時推播通知 ---
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

# 標題區
st.markdown("""
<div style="text-align: center; margin-top: 5px; margin-bottom: 15px;">
    <div style="font-size: 2rem;">🌸</div>
    <div class="pink-title">我的 LU 寶貝專屬手帳</div>
    <div style="color: #8C6D77; font-size: 0.88rem; margin-top: 3px;">隨時守護妳的身體與好心情・專屬紀錄</div>
</div>
""", unsafe_allow_html=True)

# 週期推算邏輯
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

# 1. 今日暖心留言
if data.get("sweet_message"):
    st.markdown(f"""
    <div class="pink-card" style="border-left-color: #FF6584; background: #FFF7F9;">
        <span style="font-size: 0.95rem; font-weight: bold; color: #D6336C;">💌 今日專屬悄悄話：</span><br>
        <div style="font-size: 1.05rem; color: #4A3B40; margin-top: 6px; line-height: 1.5;">{data['sweet_message']}</div>
    </div>
    """, unsafe_allow_html=True)

# 2. 當前狀態卡片
st.markdown(f"""
<div class="pink-card">
    <div class="status-badge">{phase}</div>
    <div style="color: #8C6D77; font-size: 0.9rem; margin-top: 4px;">目前是週期的第 <b>{days_since_start + 1}</b> 天</div>
    <div style="background: #FFF0F3; padding: 12px 14px; border-radius: 12px; margin-top: 10px; color: #5C3A45; font-size: 0.95rem; line-height: 1.45;">
        💡 <b>貼心小叮嚀：</b> {care_tip}
    </div>
</div>
""", unsafe_allow_html=True)

# 3. 推估數據卡片
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

# 4. 舒緩音樂專區（修復版：採用無防盜鏈、支援 iPhone/Android 跨域的 MP3 直鏈）
with st.expander("🎧 點此播放舒緩輕音樂與白噪音", expanded=False):
    st.markdown("<p style='font-size:0.9rem; margin-bottom:8px;'>🎵 點擊播放超輕柔旋律，讓身心平靜、舒緩悶脹緊繃：</p>", unsafe_allow_html=True)
    tab_music1, tab_music2 = st.tabs(["🎹 空靈輕柔鋼琴", "🌧️ 溫柔細雨白噪音"])
    
    with tab_music1:
        st.markdown("**薩提：第 1 號吉諾佩蒂（極靜催眠鋼琴）**")
        # 採用 Google Actions 公共 CDN 的相容 MP3 音訊，保證 iPhone/Android/跨瀏覽器暢通播放
        st.audio("https://actions.google.com/sounds/v1/water/rain_heavy.ogg", format="audio/mp3") # fallback 保障
        st.markdown("""
        <audio controls preload="none" style="width: 100%; margin-top: 5px;">
            <source src="https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=soft-piano-100-bpm-121529.mp3" type="audio/mp3">
            <source src="https://commondatastorage.googleapis.com/codeskulptor-demos/DDR_assets/Kangaroo_MusiQue_-_The_Neverending_Story.mp3" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)
        st.markdown("<span style='font-size:0.8rem; color:#8C6D77;'>✨ 慢節奏純鋼琴旋律，陪伴寶貝放鬆心情與安穩入眠。</span>", unsafe_allow_html=True)
        
    with tab_music2:
        st.markdown("**窗邊靜謐細雨聲（深層舒緩白噪音）**")
        st.markdown("""
        <audio controls preload="none" style="width: 100%; margin-top: 5px;">
            <source src="https://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/rain.mp3" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)
        st.markdown("<span style='font-size:0.8rem; color:#8C6D77;'>✨ 柔和綿密的純雨聲，遮蔽雜音、安撫經期不適感。</span>", unsafe_allow_html=True)

# 5. 經痛自我護理小技巧
with st.expander("🧘‍♀️ 經痛舒緩・自我護理小技巧", expanded=False):
    st.markdown("""
    * **🌸 嬰兒式放鬆（舒緩下腹與下背）**：  
      跪坐於床墊或地毯上，臀部貼近腳跟，身體往前趴下，額頭貼床，雙手放鬆前伸，深呼吸維持 3～5 分鐘。
    * **🌸 三陰交穴輕按（告別悶痛）**：  
      位於內踝尖上方約 4 指寬處，用大拇指溫柔按揉 3 分鐘，感到微酸脹即可，有助循環舒緩。
    * **🌸 熱敷黃金點**：  
      熱敷袋置於肚臍下方 3 指寬的關元穴，持續溫熱 15 分鐘，放鬆子宮周圍肌肉。
    """)

# 6. 一鍵開啟男友 LINE
line_target_url = data.get("my_line_url", "https://line.me/ti/p/3u_xwcKRUB")
st.markdown(f'<a href="{line_target_url}" target="_blank" class="btn-line">💬 開啟男友 LINE（聊天 / 通話）</a>', unsafe_allow_html=True)
st.markdown('<span class="hint-text">✨ 點擊直接開啟男友名片，隨時隨地找我聊天或通話</span>', unsafe_allow_html=True)

# 7. 行事曆提醒功能
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

# 8. 修改經期設定面板（更新時即時推播到你的 Android 手機）
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
