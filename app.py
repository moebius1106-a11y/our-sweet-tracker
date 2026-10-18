import streamlit as st
from datetime import date, timedelta
import json
import os

st.set_page_config(
    page_title="我的LU寶貝的專屬暖心週期手帳",
    page_icon="🌸",
    layout="centered"
)

st.markdown("""
    <style>
    .main {
        background-color: #FFFDFD;
    }
    .stButton>button {
        background-color: #FF8BA7;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 8px 20px;
        font-weight: bold;
    }
    .card {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(255, 139, 167, 0.15);
        margin-bottom: 20px;
        border-left: 6px solid #FF8BA7;
    }
    .status-badge {
        font-size: 1.15rem;
        font-weight: bold;
        color: #D83A56;
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

st.title("🌸 我的LU寶貝的暖心週期日記")
st.caption("專屬於我們的健康小天地・隨時互相守護")

with st.sidebar:
    st.header("⚙️ 記錄與更新")
    default_date = date.fromisoformat(data.get("last_period_start", "2026-09-21"))
    new_period_start = st.date_input("月經開始第一天", value=default_date)
    new_cycle_length = st.number_input("平均週期天數", min_value=21, max_value=45, value=data.get("cycle_length", 28))
    
    st.subheader("💌 今日給寶貝的專屬悄悄話")
    new_msg = st.text_area("留言板（留給彼此的暖心話）", value=data.get("sweet_message", ""))
    
    if st.button("💾 儲存並同步更新"):
        data["last_period_start"] = str(new_period_start)
        data["cycle_length"] = int(new_cycle_length)
        data["sweet_message"] = new_msg
        save_data(data)
        st.success("已成功儲存！")
        st.rerun()

period_start = date.fromisoformat(data["last_period_start"])
cycle_days = data["cycle_length"]
today = date.today()

next_period_start = period_start + timedelta(days=cycle_days)
ovulation_date = next_period_start - timedelta(days=14)
fertile_start = ovulation_date - timedelta(days=5)
fertile_end = ovulation_date + timedelta(days=1)

days_since_start = (today - period_start).days % cycle_days

if days_since_start < 5:
    phase = "🩸 月經期（生理期中）"
    care_tip = "這幾天肚子容易悶痛，嚴禁冰品冷飲！多喝溫水或黑糖茶，肚子跟腳底一定要做好保暖，累了就隨時躺著好好休息。"
elif fertile_start <= today <= fertile_end:
    phase = "🌸 排卵期 / 易孕期"
    care_tip = "這幾天代謝與活力很好，記得多補水與優質蛋白質，保持好心情！"
elif today < ovulation_date:
    phase = "🌱 濾泡期（卵泡期）"
    care_tip = "精神與狀態逐漸回到巔峰，好好享受輕鬆放鬆的時光～"
else:
    phase = "🌙 黃體期 / 經前前夕 (PMS)"
    care_tip = "月經快要來報到了，身體容易水腫或下腹悶脹，情緒也可能比較敏感脆弱。這幾天要放慢腳步，好好放鬆被哄著～"

if data.get("sweet_message"):
    st.markdown(f"""
    <div class="card" style="border-left-color: #FF6584; background-color: #FFF5F7;">
        <b>💌 今日暖心留言：</b><br>
        <span style="font-size: 1.05rem; color: #555;">{data['sweet_message']}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="card">
    <div class="status-badge">{phase}</div>
    <p style="margin-top: 10px; color: #666; font-size: 0.95rem;">
        今天是週期第 <b>{days_since_start + 1}</b> 天
    </p>
    <div style="background: #FDF4F5; padding: 12px; border-radius: 10px; margin-top: 10px; color: #444;">
        💡 <b>貼心小指引：</b> {care_tip}
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="🎯 推算排卵日", value=ovulation_date.strftime("%m月%d日"))
    st.caption(f"易孕區間：{fertile_start.strftime('%m/%d')} ~ {fertile_end.strftime('%m/%d')}")

with col2:
    days_to_period = (next_period_start - today).days
    period_str = f"約 {days_to_period} 天後" if days_to_period >= 0 else "預計已報到"
    st.metric(label="🩸 預計下次月經", value=next_period_start.strftime("%m月%d日"), delta=period_str)
    st.caption("依排卵後 14 天黃體期推估")

progress_ratio = min(max((days_since_start + 1) / cycle_days, 0.0), 1.0)
st.write("週期進度：")
st.progress(progress_ratio)
