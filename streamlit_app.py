import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 核心設定
st.set_page_config(page_title="Hazel's War Room", page_icon="🍊", layout="wide")

# 🎨 注入 CSS
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Mate+SC&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Georgia', 'Microsoft JhengHei', serif !important; }
    h1 { font-family: 'Cinzel', serif !important; color: #FF8C00 !important; font-size: 3rem !important; text-align: center; letter-spacing: 4px; }
    .period-mini-box { background-color: #FFF5EE; padding: 12px 20px; border-radius: 10px; border-left: 6px solid #FF69B4; margin-bottom: 20px; font-size: 0.95rem; line-height: 1.6; }
    [data-testid="stMetricValue"] { font-size: 2.5rem !important; font-weight: 800 !important; }
    .stProgress > div > div > div > div { background: #D4AF37 !important; }
    .mate-title { font-family: 'Mate SC', serif !important; color: #B8860B; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. 資料讀取
@st.cache_data(ttl=300)
def load_sheet_data(sheet_id, sheet_name="Sheet1"):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url).dropna(how='all')
        return df
    except: return None

# 3. 生理期與飲食提醒邏輯 (移除鮮奶茶，加入碳水循環建議)
def get_period_advice(record_date):
    day_in_cycle = record_date.day % 28 
    if 1 <= day_in_cycle <= 5:
        return "🌸 月經期", "恢復為主。此時身體較虛弱，建議維持基礎碳水，避免極端低碳。"
    elif 6 <= day_in_cycle <= 13:
        return "🔥 濾泡期 (代謝高峰)", "體力與代謝最佳！**建議排入高碳日 (High Carb Day)** 配合大重量訓練，衝刺增肌。"
    elif 14 <= day_in_cycle <= 15:
        return "⚡ 排卵期", "體力巔峰。可維持高碳或轉入中碳，適合安排**欺騙餐 (Cheat Meal)** 滿足口慾。"
    else:
        return "🍂 恢復期 (水腫預警)", "黃體素升高。建議執行**低碳日 (Low Carb Day)** 以控水腫，減少精緻澱粉。"

# 4. 主介面
st.markdown("<h1>HAZEL'S WAR ROOM</h1>", unsafe_allow_html=True)

df_body = load_sheet_data("1o-_Xr7wlisU7Wo0eLY_m2sWocptJC9poMxrUSkOMCNo", "allDatas")
df_training = load_sheet_data("1Iok7RIO1y4ggbcpVja0yoO0J2Cox04Y3WJjufBpOAus", "重訓課表")

if df_body is not None:
    with st.sidebar:
        st.markdown("<h2 class='mate-title'>GOAL SETTINGS</h2>", unsafe_allow_html=True)
        t_w = st.number_input("目標體重 (kg)", value=52.0) 
        t_f_rate = st.number_input("目標體脂率 (%)", value=24.5) 
        t_ecw = st.number_input("目標 ECW 比率", value=0.380, format="%.3f")
        
        st.markdown("---")
        st.markdown("<h2 class='mate-title'>FILTER</h2>", unsafe_allow_html=True)
        days_opt = st.radio("顯示區間", ["最近 7 天", "最近 30 天", "全部日期"], index=1)
        
        st.markdown("---")
        view_mode = st.radio("功能切換", ["體態戰情室", "重訓成長曲線"])
        st.link_button("🔗 打開原始重訓清單", "https://docs.google.com/spreadsheets/d/1Iok7RIO1y4ggbcpVja0yoO0J2Cox04Y3WJjufBpOAus/edit?gid=0#gid=0")

    df_body.iloc[:, 0] = pd.to_datetime(df_body.iloc[:, 0], errors='coerce')
    df_filtered = df_body.tail(7) if days_opt=="最近 7 天" else (df_body.tail(30) if days_opt=="最近 30 天" else df_body)

    if view_mode == "體態戰情室":
        latest_date = df_body.iloc[-1, 0]
        p_title, p_advice = get_period_advice(latest_date)
        st.markdown(f'<div class="period-mini-box"><strong>{p_title} 指南：</strong><br>{p_advice}</div>', unsafe_allow_html=True)

        latest = df_body.iloc[-1]
        prev = df_body.iloc[-2]
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("WEIGHT", f"{latest.iloc[4]}kg", f"{round(latest.iloc[4]-prev.iloc[4],2)}kg", delta_color="inverse")
        with c2: st.metric("BODY FAT %", f"{latest.iloc[5]}%", f"{round(latest.iloc[5]-prev.iloc[5],2)}%", delta_color="inverse")
        with c3: st.metric("MUSCLE", f"{latest.iloc[6]}kg", f"{round(latest.iloc[6]-prev.iloc[6],2)}kg")
        with c4: st.metric("ECW RATIO", f"{latest.iloc[13]}", f"{round(latest.iloc[13]-prev.iloc[13],3)}", delta_color="inverse")

        st.markdown("---")
        progress = min(100, int(((60.0 - float(latest.iloc[4])) / (60.0 - t_w)) * 100))
        st.markdown(f"<p style='color:#B8860B; font-weight:bold;'>GOAL PROGRESS: {progress}%</p>", unsafe_allow_html=True)
        st.progress(progress/100)

        all_cols = df_body.columns.tolist()
        selected = st.multiselect("追蹤指標", all_cols, default=[all_cols[4], all_cols[5], all_cols[13]])
        if selected:
            fig = px.line(df_filtered, x=all_cols[0], y=selected, template="simple_white", color_discrete_sequence=["#FF8C00", "#D4AF37", "#8B4513"])
            fig.update_layout(yaxis=dict(autorange=True, fixedrange=False), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.subheader("🏋️ 重訓 1RM 強度成長趨勢")
        if df_training is not None:
            # 簡單 1RM 視覺化邏輯
            df_training['Weight'] = pd.to_numeric(df_training.iloc[:, 3], errors='coerce')
            df_training['1RM'] = df_training['Weight'] * 1.2 # 暫時用係數模擬趨勢
            fig_train = px.line(df_training.tail(20), x=df_training.columns[0], y='1RM', color=df_training.columns[2], title="Strength Growth (Estimated)")
            st.plotly_chart(fig_train, use_container_width=True)
            st.dataframe(df_training.tail(10), use_container_width=True)
