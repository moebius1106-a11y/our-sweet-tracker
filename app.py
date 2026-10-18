import streamlit as st
from datetime import date, timedelta
import json
import os
import urllib.parse
import requests

# 1. 頁面配置
st.set_page_config(
    page_title="🌸 LU寶貝的專屬暖心手帳 (Pro)",
    page_icon="🌸",
    layout="centered"
)

# 2. 進階視覺 CSS（仿原生 App 質感、漸層卡片與陰影）
st.markdown("""
<style>
.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 2.5rem !important;
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
}

body {
    -webkit-font-smoothing: antialiased;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang TC", "Helvetica Neue", sans-serif;
    color: #4A3B40 !important;
}
.stApp {
    background: linear-gradient(180deg, #FFF0F3 0%, #FAF0F4 50%, #FFFFFF 100%) !important;
}

.pink-card {
    background: #FFFFFF !important;
    padding: 16px 18px !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 18px rgba(255, 175, 189, 0.22) !important;
    margin-bottom: 14px !important;
    border-left: 6px solid #FF8FA3 !important;
}

.pink-title {
    color: #D6336C !important;
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px !important;
}

/* 仿坊間 App 多色週期進度條 */
.cycle-timeline-box {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 4px 15px rgba(255, 182, 193, 0.2);
    margin-bottom: 16px;
}
.cycle-bar-wrap {
    height: 14px;
    width: 100%;
    background: #F1E5E8;
    border-radius: 10px;
    overflow: hidden;
    display: flex;
    margin-top: 10px;
    margin-bottom: 6px;
}
.bar-period { background-color: #FF6B8B; }
.bar-follicular { background-color: #B5EAD7; }
.bar-ovulation { background-color: #FFD166; }
.bar-luteal { background-color: #C7CEEA; }

.timeline-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #8C6D77;
    margin-top: 4px;
}

/* 按鈕美化 */
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
}

div[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #FFE3E8 !important;
    border-radius: 16px !important;
}
</style>
""", unsafe_allow_html=True)

# --- 後台通知配置 ---
NTFY_TOPIC = "lu-care-moebius-alert"

def send_push_notification(title, message, priority="default"):
    try:
        headers = {
            "Title": title.encode("utf-8"),
            "Priority": priority,
            "Tags": "cherry_blossom,sparkles"
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

# 標題
st.markdown("""
<div style="text-align: center; margin-top: 5px; margin-bottom: 12px;">
    <div style="font-size: 2rem;">🌸</div>
    <div class="pink-title">我的 LU 寶貝專屬手帳</div>
    <div style="color: #A37081; font-size: 0.88rem; margin-top: 3px;">隨時守護妳的身體與好心情・專屬紀錄</div>
</div>
""", unsafe_allow_html=True)

# 週期數據核心運算
period_start = date.fromisoformat(data["last_period_start"])
cycle_days = data["cycle_length"]
today = date.today()

next_period_start = period_start + timedelta(days=cycle_days)
ovulation_date = next_period_start - timedelta(days=14)
fertile_start = ovulation_date - timedelta(days=5)
fertile_end = ovulation_date + timedelta(days=1)

days_since_start = (today - period_start).days % cycle_days
day_in_cycle = days_since_start + 1

# 階段狀態判定
if days_since_start < 5:
    phase = "🩸 生理期中・好好休息"
    care_tip = "肚子容易悶痛，嚴禁冰品冷飲！多喝溫開水或黑糖薑茶，肚子跟腳部保暖做好，累了就乖乖躺好讓我哄妳 🥰"
    status_color = "#FF6B8B"
elif fertile_start <= today <= fertile_end:
    phase = "🌸 排卵期・活力滿滿"
    care_tip = "這幾天氣色最好、代謝旺盛，多補充溫水與優質蛋白質，心情愉悅度滿分！"
    status_color = "#FFD166"
elif today < ovulation_date:
    phase = "🌱 卵泡期・神清氣爽"
    care_tip = "體力與精神逐漸回到最佳狀態，想吃什麼好料就好好享受吧～"
    status_color = "#06D6A0"
else:
    phase = "🌙 經前前夕 (PMS)・溫柔守護"
    care_tip = "這兩天月經快來了，身體容易水腫或微悶，情緒敏感都是正常的～別給自己壓力，凡事都有我陪著！"
    status_color = "#9B5DE5"

# --- 亮點功能 1：仿坊間 App 的圖形化色彩週期軸 ---
pct_period = (5 / cycle_days) * 100
pct_ovulation = (6 / cycle_days) * 100
days_follicular = max((ovulation_date - (period_start + timedelta(days=5))).days, 1)
pct_follicular = (days_follicular / cycle_days) * 100
pct_luteal = 100 - (pct_period + pct_follicular + pct_ovulation)

st.markdown(f"""
<div class="cycle-timeline-box">
    <div style="display: flex; justify-content: space-between; align-items: baseline;">
        <span style="font-size: 1.15rem; font-weight: bold; color: {status_color};">{phase}</span>
        <span style="font-size: 0.88rem; color: #8A6570;">第 <b>{day_in_cycle}</b> / {cycle_days} 天</span>
    </div>
    <div class="cycle-bar-wrap">
        <div class="bar-period" style="width: {pct_period}%;" title="月經期"></div>
        <div class="bar-follicular" style="width: {pct_follicular}%;" title="濾泡期"></div>
        <div class="bar-ovulation" style="width: {pct_ovulation}%;" title="排卵易孕期"></div>
        <div class="bar-luteal" style="width: {pct_luteal}%;" title="黃體期"></div>
    </div>
    <div class="timeline-labels">
        <span>🩸 月經期</span>
        <span>🌱 濾泡期</span>
        <span>🌸 排卵期</span>
        <span>🌙 黃體期</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 暖心悄悄話
if data.get("sweet_message"):
    st.markdown(f"""
    <div class="pink-card" style="border-left-color: #FF6584; background: #FFF7F9;">
        <span style="font-size: 0.95rem; font-weight: bold; color: #D6336C;">💌 今日專屬悄悄話：</span><br>
        <div style="font-size: 1.05rem; color: #4A3B40; margin-top: 6px; line-height: 1.5;">{data['sweet_message']}</div>
    </div>
    """, unsafe_allow_html=True)

# 貼心叮嚀
st.markdown(f"""
<div class="pink-card" style="border-left-color: {status_color};">
    <div style="background: #FFF0F3; padding: 12px 14px; border-radius: 12px; color: #5C3A45; font-size: 0.95rem; line-height: 1.45;">
        💡 <b>貼心小叮嚀：</b> {care_tip}
    </div>
</div>
""", unsafe_allow_html=True)

# 關鍵日期卡片
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

# --- 亮點功能 2：聲音景觀・極度舒緩輕音樂與白噪音（後端快取直出，保證能播） ---
@st.cache_data(show_spinner=False)
def load_audio_stream(url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            return res.content
    except Exception:
        pass
    return None

with st.expander("🎧 點此播放舒緩輕音樂與白噪音", expanded=False):
    st.caption("🎵 點擊播放超輕柔旋律，讓身心平靜、舒緩悶脹緊繃：")
    tab_music1, tab_music2 = st.tabs(["🎹 空靈輕柔鋼琴", "🌧️ 溫柔細雨白噪音"])
    
    # 經由 Wikimedia Commons 開放授權且支援公共分發的高音質來源
    PIANO_URL = "https://upload.wikimedia.org/wikipedia/commons/e/eb/Gymnopedie_No._1_%28ISRC_USUAN1100787%29.mp3"
    RAIN_URL = "https://actions.google.com/sounds/v1/weather/rain_heavy.ogg"
    
    with tab_music1:
        st.markdown("**薩提：第1號吉諾佩蒂（極靜慢板鋼琴）**")
        piano_data = load_audio_stream(PIANO_URL)
        if piano_data:
            st.audio(piano_data, format="audio/mp3")
        else:
            st.audio(PIANO_URL, format="audio/mp3")
        st.caption("✨ 節奏緩慢、音色清澈純淨，陪伴寶貝深層放鬆與入眠。")
        
    with tab_music2:
        st.markdown("**靜謐自然細雨聲（深層舒緩）**")
        rain_data = load_audio_stream(RAIN_URL)
        if rain_data:
            st.audio(rain_data, format="audio/ogg")
        else:
            st.audio(RAIN_URL, format="audio/ogg")
        st.caption("✨ 柔和綿密的白噪音頻率，安撫經期不適與緊張神經。")
# --- 亮點功能 3：經痛舒緩與自我護理指南 ---
with st.expander("🧘‍♀️ 經痛舒緩・自我護理小技巧", expanded=False):
    st.markdown("""
    * **🌸 嬰兒式放鬆（舒緩下腹與下背）**：
      跪坐於床墊或地毯上，臀部貼近腳跟，身體往前趴下，額頭貼床，雙手放鬆前伸，深呼吸維持 3～5 分鐘。
    * **🌸 三陰交穴輕按（告別悶痛）**：
      位於內踝尖上方約 4 指寬處，用大拇指溫柔按揉 3 分鐘，感到微酸脹即可，有助下焦循環。
    * **🌸 熱敷黃金點**：
      熱敷袋置於肚臍下方 3 指寬的關元穴，持續溫熱 15 分鐘，放鬆子宮周圍肌肉。
    """)

# 一鍵找男友
line_target_url = data.get("my_line_url", "https://line.me/ti/p/3u_xwcKRUB")
st.markdown(f'<a href="{line_target_url}" target="_blank" class="btn-line">💬 開啟男友 LINE（聊天 / 通話）</a>', unsafe_allow_html=True)

# 日曆提醒
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

# 修改設定
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
