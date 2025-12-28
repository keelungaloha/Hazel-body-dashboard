import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. 核心設定
st.set_page_config(page_title="Hazel's War Room", page_icon="🍊", layout="wide")

# 🎨 注入 CSS：確保字體份量感與進度條顏色
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Mate+SC&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Georgia', 'Microsoft JhengHei', serif !important; }
    h1 { font-family: 'Cinzel', serif !important; color: #FF8C00 !important; font-size: 3rem !important; text-align: center; letter-spacing: 4px; }
    .period-mini-box { background-color: #FFF5EE; padding: 12px 20px; border-radius: 10px; border-left: 6px solid #FF69B4; margin-bottom: 20px; font-size: 0.95rem; }
    [data-testid="stMetricValue"] { font-size: 2.5rem !important; font-weight: 800 !important; }
    .stProgress > div > div > div > div { background: #D4AF37 !important; }
    .mate-title { font-family: 'Mate SC', serif !important; color: #B8860B; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. 資料讀取函式
@st.cache_data(ttl=300)
def load_data(sheet_id, sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url).dropna(how='all')
        return df
    except: return None

# 3. 生理期判斷邏輯
def get_period_advice(record_date):
    day = record_date.day % 28 
    if 6 <= day <= 13: return "🔥 濾泡期 (代謝高峰)", "體力最佳！**建議排入高碳日 (High Carb Day)** 配合重訓，衝刺增肌。"
    elif 20 <= day <= 28: return "🍂 恢復期 (水腫預警)", "黃體素升高。建議執行**低碳日 (Low Carb Day)** 以控水腫。"
    else: return "🌸 穩定/月經期", "維持基礎碳水，依照身體感受調整訓練強度。"

# 4. 主程式介面
st.markdown("<h1>HAZEL'S WAR ROOM</h1>", unsafe_allow_html=True)

df_body = load_data("1o-_Xr7wlisU7Wo0eLY_m2sWocptJC9poMxrUSkOMCNo", "allDatas")
df_train = load_data("1Iok7RIO1y4ggbcpVja0yoO0J2Cox04Y3WJjufBpOAus", "Sheet1") # 請確認重訓分頁名稱

if df_body is not None:
    with st.sidebar:
        st.markdown("<h2 class='mate-title'>GOAL SETTINGS</h2>", unsafe_allow_html=True)
        t_w = st.number_input("目標體重 (kg)", value=52.0) 
        t_ecw = st.number_input("目標 ECW 比率", value=0.380, format="%.3f")
        st.markdown("---")
        days_opt = st.radio("顯示區間", ["最近 7 天", "最近 30 天", "全部日期"], index=1)
        view_mode = st.radio("功能切換", ["體態戰情室", "重訓成長曲線"])
        st.link_button("🔗 打開原始重訓清單", "https://docs.google.com/spreadsheets/d/1Iok7RIO1y4ggbcpVja0yoO0J2Cox04Y3WJjufBpOAus/edit?gid=0#gid=0")

    # 日期預處理
    df_body.iloc[:, 0] = pd.to_datetime(df_body.iloc[:, 0], errors='coerce')
    df_plot = df_body.tail(7) if days_opt=="最近 7 天" else (df_body.tail(30) if days_opt=="最近 30 天" else df_body)

    if view_mode == "體態戰情室":
        # 生理期
        p_title, p_advice = get_period_advice(df_body.iloc[-1, 0])
        st.markdown(f'<div class="period-mini-box"><strong>{p_title} 指南：</strong><br>{p_advice}</div>', unsafe_allow_html=True)

        # 指標
        latest = df_body.iloc[-1]
        prev = df_body.iloc[-2]
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("WEIGHT", f"{latest.iloc[4]}kg", f"{round(latest.iloc[4]-prev.iloc[4],2)}kg", delta_color="inverse")
        with c2: st.metric("FAT %", f"{latest.iloc[5]}%", f"{round(latest.iloc[5]-prev.iloc[5],2)}%", delta_color="inverse")
        with c3: st.metric("MUSCLE", f"{latest.iloc[6]}kg", f"{round(latest.iloc[6]-prev.iloc[6],2)}kg")
        with c4: st.metric("ECW", f"{latest.iloc[13]}", f"{round(latest.iloc[13]-prev.iloc[13],3)}", delta_color="inverse")

        # 進度
        st.markdown("---")
        progress = min(100, int(((60.0 - float(latest.iloc[4])) / (60.0 - t_w)) * 100))
        st.markdown(f"<p style='color:#B8860B; font-weight:bold;'>GOAL PROGRESS: {progress}%</p>", unsafe_allow_html=True)
        st.progress(progress/100)

        # 高精度圖表
        st.subheader("高精度趨勢追蹤")
        all_cols = df_body.columns.tolist()
        selected = st.multiselect("追蹤指標", all_cols, default=[all_cols[4], all_cols[5], all_cols[13]])
        
        if selected:
            fig = go.Figure()
            colors = ["#FF8C00", "#D4AF37", "#8B4513", "#2F4F4F"]
            for i, col in enumerate(selected):
                fig.add_trace(go.Scatter(x=df_plot.iloc[:, 0], y=df_plot[col], name=col,
                                         line=dict(color=colors[i % len(colors)], width=3),
                                         mode='lines+markers'))
            
            # 關鍵：強制 Y 軸根據數據範圍自動縮放，並顯示到小數點兩位
            fig.update_layout(
                yaxis=dict(autorange=True, fixedrange=False, tickformat=".2f"),
                hovermode="x unified", template="simple_white",
                height=500, margin=dict(l=0, r=0, t=20, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        # 重訓模式
        st.subheader("🏋️ 1RM 強度成長 (高精度分析)")
        if df_train is not None:
            # 假設重訓表 D 欄重量, E 欄次數
            try:
                df_train['W'] = pd.to_numeric(df_train.iloc[:, 3], errors='coerce')
                df_train['R'] = pd.to_numeric(df_train.iloc[:, 4], errors='coerce')
                df_train['1RM'] = df_train['W'] * (1 + df_train['R'] / 30)
                
                fig_t = px.line(df_train.tail(20), x=df_train.columns[0], y='1RM', color=df_train.columns[2],
                                markers=True, template="simple_white")
                fig_t.update_layout(yaxis=dict(autorange=True, tickformat=".2f"))
                st.plotly_chart(fig_t, use_container_width=True)
            except:
                st.info("數據解析中...請確保重訓表格式正確。")
                st.dataframe(df_train.tail(10))

else:
    st.error("連線失敗")
