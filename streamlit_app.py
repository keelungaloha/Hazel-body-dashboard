import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 核心設定
st.set_page_config(page_title="Hazel's War Room", page_icon="🍊", layout="wide")

# 🎨 注入 CSS：強化字體與精準感
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Mate+SC&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Georgia', 'Microsoft JhengHei', serif !important; }
    h1 { font-family: 'Cinzel', serif !important; color: #FF8C00 !important; font-size: 3rem !important; text-align: center; letter-spacing: 4px; }
    .period-mini-box { background-color: #FFF5EE; padding: 15px 20px; border-radius: 12px; border-left: 8px solid #FF69B4; margin-bottom: 25px; }
    [data-testid="stMetricValue"] { font-size: 2.5rem !important; font-weight: 800 !important; }
    .mate-title { font-family: 'Mate SC', serif !important; color: #B8860B; font-size: 1.2rem; }
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
    except: return None

# 3. 生理期飲食戰術 (直接根據表格中的 Cycle Day)
def get_period_strategy(cycle_day):
    try:
        cd = int(cycle_day)
    except: return "數據讀取中", "請確認表格中 Cycle Day 欄位是否有值。"
    
    if 1 <= cd <= 5:
        return f"🌸 月經期 (Day {cd})", "恢復為主。建議維持基礎碳水，避免極端低碳，注意保暖。"
    elif 6 <= cd <= 13:
        return f"🔥 濾泡期 (Day {cd} - 代謝高峰)", "體力最佳！**建議排入高碳日 (High Carb Day)** 配合重訓衝刺。"
    elif 14 <= cd <= 17:
        return f"⚡ 排卵期 (Day {cd})", "體力巔峰。適合安排**欺騙餐 (Cheat Meal)** 滿足口慾。"
    else:
        return f"🍂 恢復/黃體期 (Day {cd} - 水腫預警)", "黃體素升高。建議執行**低碳日 (Low Carb Day)** 以控水腫。"

# 4. 主介面
st.markdown("<h1>HAZEL'S WAR ROOM</h1>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # 側邊欄設定
    with st.sidebar:
        st.markdown("<h2 class='mate-title'>GOAL SETTINGS</h2>", unsafe_allow_html=True)
        t_w = st.number_input("目標體重 (kg)", value=52.0)
        t_ecw = st.number_input("目標 ECW", value=0.380, format="%.3f")
        st.markdown("---")
        days_opt = st.radio("顯示區間", ["最近 7 天", "最近 30 天", "全部日期"], index=1)
        st.link_button("🔗 打開原始重訓清單", "https://docs.google.com/spreadsheets/d/1Iok7RIO1y4ggbcpVja0yoO0J2Cox04Y3WJjufBpOAus/edit?gid=0#gid=0")

    # 取得最新一筆數據
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 生理期提醒 (從表格第 15 欄抓取 Cycle Day)
    # 根據 allDatas 結構，Cycle Day 通常在最後幾個欄位，請確認索引
    # 假設是第 15 欄 (index 14)，如果位置不同請調整索引值
    cycle_day_val = latest.iloc[14] 
    p_title, p_advice = get_period_strategy(cycle_day_val)
    st.markdown(f'<div class="period-mini-box"><strong>{p_title} 指南：</strong><br>{p_advice}</div>', unsafe_allow_html=True)

    # 數據卡片
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("WEIGHT", f"{latest.iloc[4]}kg", f"{round(latest.iloc[4]-prev.iloc[4],2)}kg", delta_color="inverse")
    with c2: st.metric("FAT %", f"{latest.iloc[5]}%", f"{round(latest.iloc[5]-prev.iloc[5],2)}%", delta_color="inverse")
    with c3: st.metric("MUSCLE", f"{latest.iloc[6]}kg", f"{round(latest.iloc[6]-prev.iloc[6],2)}kg")
    with c4: st.metric("ECW RATIO", f"{latest.iloc[13]}", f"{round(latest.iloc[13]-prev.iloc[13],3)}", delta_color="inverse")

    # 高精度圖表
    st.markdown("---")
    df_plot = df.tail(7) if days_opt=="最近 7 天" else (df.tail(30) if days_opt=="最近 30 天" else df)
    
    all_cols = df.columns.tolist()
    selected = st.multiselect("追蹤指標", all_cols, default=[all_cols[4], all_cols[5], all_cols[13]])
    
    if selected:
        fig = go.Figure()
        colors = ["#FF8C00", "#D4AF37", "#8B4513", "#2F4F4F"]
        for i, col in enumerate(selected):
            fig.add_trace(go.Scatter(x=df_plot.iloc[:, 0], y=df_plot[col], name=col,
                                     line=dict(color=colors[i % len(colors)], width=3), mode='lines+markers'))
        
        # 強制縱軸緊貼數據範圍，顯示小數點兩位
        fig.update_layout(
            yaxis=dict(autorange=True, fixedrange=False, tickformat=".2f", showgrid=True),
            hovermode="x unified", template="simple_white", height=500
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.error("無法載入數據，請檢查 Google Sheet 權限。")
