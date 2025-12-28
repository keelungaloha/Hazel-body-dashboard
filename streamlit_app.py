import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 核心設定
st.set_page_config(page_title="Hazel's War Room", page_icon="🍊", layout="wide")

# 🎨 注入 CSS：精緻化字體比例
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Mate+SC&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] {
        font-family: 'Georgia', 'Microsoft JhengHei', serif !important;
    }
    h1 {
        font-family: 'Cinzel', serif !important;
        color: #FF8C00 !important;
        font-size: 3rem !important;
        text-align: center;
        letter-spacing: 4px;
        margin: 10px 0;
    }
    .period-mini-box {
        background-color: #FFF5EE;
        padding: 12px 20px;
        border-radius: 10px;
        border-left: 6px solid #FF69B4;
        margin-bottom: 20px;
        font-size: 0.9rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    .stProgress > div > div > div > div {
        background: #D4AF37 !important;
    }
    .mate-title {
        font-family: 'Mate SC', serif !important;
        color: #B8860B;
        font-size: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 資料讀取
@st.cache_data(ttl=300)
def load_data():
    lemon_id = "1o-_Xr7wlisU7Wo0eLY_m2sWocptJC9poMxrUSkOMCNo"
    url = f"https://docs.google.com/spreadsheets/d/{lemon_id}/gviz/tq?tqx=out:csv&sheet=allDatas"
    try:
        df = pd.read_csv(url).dropna(how='all')
        if not df.empty:
            df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        return df
    except:
        return None

# 3. 生理期判斷邏輯
def get_period_advice(record_date):
    day_in_cycle = record_date.day % 28 
    if 1 <= day_in_cycle <= 5:
        return "🌸 月經期", "輕度運動。建議：自泡鮮奶茶（150ml全脂牛奶+200ml無糖熱紅茶）。"
    elif 6 <= day_in_cycle <= 13:
        return "🔥 濾泡期", "代謝高峰！適合大重量重訓期，挑戰 PR。"
    elif 14 <= day_in_cycle <= 15:
        return "⚡ 排卵期", "體力巔峰。注意水分補充。"
    else:
        return "🍂 黃體期", "易水腫。建議低鈉飲食，適合低強度帶氧。"

# 4. 主程式介面
st.markdown("<h1>HAZEL'S WAR ROOM</h1>", unsafe_allow_html=True)

df_lemon = load_data()

if df_lemon is not None:
    # --- 側邊欄：目標設定 (已鎖定 52kg) ---
    with st.sidebar:
        st.markdown("<h2 class='mate-title'>GOAL SETTINGS</h2>", unsafe_allow_html=True)
        t_w = st.number_input("目標體重 (kg)", value=52.0) # 已校正為 52.0
        t_f_rate = st.number_input("目標體脂率 (%)", value=24.5) 
        t_f_weight = st.number_input("目標體脂肪量 (kg)", value=13.0)
        t_m = st.number_input("目標骨骼肌 (kg)", value=21.0)
        t_v = st.number_input("目標內臟脂肪", value=3.0)
        t_ecw = st.number_input("目標 ECW 比率", value=0.380, format="%.3f")
        
        st.markdown("---")
        view_mode = st.radio("功能切換", ["體態戰情室", "重訓課表分析"])

    if view_mode == "體態戰情室":
        latest_date = df_lemon.iloc[-1, 0]
        p_title, p_advice = get_period_advice(latest_date)
        st.markdown(f'<div class="period-mini-box"><strong>{p_title} 指南：</strong> {p_advice}</div>', unsafe_allow_html=True)

        latest = df_lemon.iloc[-1]
        prev = df_lemon.iloc[-2]
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("WEIGHT", f"{latest.iloc[4]}kg", f"{round(latest.iloc[4]-prev.iloc[4],2)}kg", delta_color="inverse")
        with c2: st.metric("BODY FAT %", f"{latest.iloc[5]}%", f"{round(latest.iloc[5]-prev.iloc[5],2)}%", delta_color="inverse")
        with c3: st.metric("MUSCLE", f"{latest.iloc[6]}kg", f"{round(latest.iloc[6]-prev.iloc[6],2)}kg")
        with c4: st.metric("ECW RATIO", f"{latest.iloc[13]}", f"{round(latest.iloc[13]-prev.iloc[13],3)}", delta_color="inverse")

        st.markdown("---")
        progress = min(100, int(((60.0 - float(latest.iloc[4])) / (60.0 - t_w)) * 100))
        st.markdown(f"<p style='color:#B8860B; font-weight:bold;'>GOAL PROGRESS: {progress}%</p>", unsafe_allow_html=True)
        st.progress(progress/100)

        # 圖表
        all_cols = df_lemon.columns.tolist()
        selected = st.multiselect("選擇追蹤趨勢", all_cols, default=[all_cols[4], all_cols[5], all_cols[13]])
        if selected:
            fig = px.line(df_lemon.tail(30), x=all_cols[0], y=selected, template="simple_white",
                          color_discrete_sequence=["#FF8C00", "#D4AF37", "#8B4513"])
            fig.update_layout(yaxis=dict(autorange=True, fixedrange=False), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.subheader("🏋️ 訓練週期分析")
        st.dataframe(df_lemon.tail(10), use_container_width=True)

else:
    st.error("無法連線，請檢查資料來源。")
