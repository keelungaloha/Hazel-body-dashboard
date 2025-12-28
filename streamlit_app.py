import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 核心設定
st.set_page_config(page_title="Hazel's War Room", page_icon="🍊", layout="wide")

# 🎨 注入 CSS：解決露餡並強化字體份量感
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Mate+SC&display=swap" rel="stylesheet">
    <style>
    /* 修正露餡：確保 style 標籤內純淨 */
    html, body, [class*="css"] {
        font-family: 'Georgia', 'Microsoft JhengHei', serif !important;
    }
    h1 {
        font-family: 'Cinzel', serif !important;
        color: #FF8C00 !important;
        font-size: 3rem !important;
        text-align: center;
        letter-spacing: 4px;
        margin: 5px 0;
    }
    /* 精簡生理期提示 */
    .period-mini {
        background-color: #FFF5EE;
        padding: 10px 20px;
        border-radius: 10px;
        border-left: 6px solid #FF69B4;
        margin-bottom: 15px;
        font-size: 0.95rem;
    }
    /* 數據卡片放大 */
    [data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
    }
    /* 進度條暗黃色 */
    .stProgress > div > div > div > div {
        background: #B8860B !important;
    }
    .mate-font {
        font-family: 'Mate SC', serif !important;
        color: #B8860B;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 資料讀取 (讀取兩個不同的 Sheet)
@st.cache_data(ttl=300)
def load_all_data():
    lemon_id = "1o-_Xr7wlisU7Wo0eLY_m2sWocptJC9poMxrUSkOMCNo"
    diamond_id = "1Iok7RIO1y4ggbcpVja0yoO0J2Cox04Y3WJjufBpOAus"
    
    # 讀取體態數據
    url_l = f"https://docs.google.com/spreadsheets/d/{lemon_id}/gviz/tq?tqx=out:csv&sheet=allDatas"
    # 讀取重訓數據 (假設分頁名稱為 Sheet1)
    url_d = f"https://docs.google.com/spreadsheets/d/{diamond_id}/gviz/tq?tqx=out:csv"
    
    try:
        df_l = pd.read_csv(url_l).dropna(how='all')
        df_l.iloc[:, 0] = pd.to_datetime(df_l.iloc[:, 0], errors='coerce')
        df_d = pd.read_csv(url_d).dropna(how='all')
        return df_l, df_d
    except:
        return None, None

# 3. 生理期判斷
def get_period_advice(record_date):
    day = record_date.day % 28
    if 1 <= day <= 5: return "🌸 月經期", "低強度運動，建議補充鐵質與鮮奶茶。"
    elif 6 <= day <= 13: return "🔥 濾泡期", "體力巔峰！適合大重量重訓期。"
    elif 14 <= day <= 15: return "⚡ 排卵期", "代謝加快，注意水分補充。"
    else: return "🍂 黃體期", "易水腫，建議中低強度帶氧運動。"

# 4. 主介面
st.markdown("<h1>HAZEL'S WAR ROOM</h1>", unsafe_allow_html=True)
df_l, df_d = load_all_data()

if df_l is not None:
    # --- 側邊欄：全指標目標設定 ---
    with st.sidebar:
        st.markdown("<h3 class='mate-font'>GOAL SETTINGS</h3>", unsafe_allow_html=True)
        t_w = st.number_input("Weight Goal (kg)", value=50.0)
        t_f = st.number_input("Body Fat Goal (%)", value=22.0)
        t_m = st.number_input("Muscle Goal (kg)", value=24.0)
        t_v = st.number_input("V-Fat Goal", value=3.0)
        
        st.markdown("---")
        view_mode = st.radio("VIEW MODE", ["Body Analysis", "Training Strength"])

    if view_mode == "Body Analysis":
        # 生理期精簡提示
        title, advice = get_period_advice(df_l.iloc[-1, 0])
        st.markdown(f'<div class="period-mini"><strong>{title}：</strong>{advice}</div>', unsafe_allow_html=True)

        # 核心數據
        latest = df_l.iloc[-1]
        prev = df_l.iloc[-2]
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("WEIGHT", f"{latest.iloc[4]}kg", f"{round(latest.iloc[4]-prev.iloc[4],2)}kg", delta_color="inverse")
        with c2: st.metric("FAT", f"{latest.iloc[5]}%", f"{round(latest.iloc[5]-prev.iloc[5],2)}%", delta_color="inverse")
        with c3: st.metric("MUSCLE", f"{latest.iloc[6]}kg", f"{round(latest.iloc[6]-prev.iloc[6],2)}kg")
        with c4: st.metric("V-FAT", f"{latest.iloc[8]}", f"{int(latest.iloc[8]-prev.iloc[8])}", delta_color="inverse")

        # 進度條 (暗黃色)
        st.markdown("---")
        progress = min(100, int(((60.0 - float(latest.iloc[4])) / (60.0 - t_w)) * 100))
        st.markdown(f"<span style='color:#B8860B; font-weight:bold;'>PROGRESS: {progress}%</span>", unsafe_allow_html=True)
        st.progress(progress/100)

        # 趨勢圖 (動態縮放)
        cols = df_l.columns.tolist()
        selected = st.multiselect("Select Trends", cols, default=[cols[4], cols[5]])
        if selected:
            fig = px.line(df_l.tail(30), x=cols[0], y=selected, template="simple_white", color_discrete_sequence=["#FF8C00", "#D4AF37"])
            fig.update_layout(yaxis=dict(autorange=True, fixedrange=False), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

    else:
        # --- 重訓數據分析 (Training Mode) ---
        st.subheader("🏋️ 訓練總量與強度分析")
        if df_d is not None:
            # 這裡我們利用 Plotly 做一個複合圖表
            # 顯示你的 1RM 趨勢或是訓練重量分布
            st.dataframe(df_d.tail(10), use_container_width=True)
            st.info("💡 系統正在分析你的訓練週期... 目前顯示為『最大肌力期』數據。")
            
            # 範例圖表：訓練強度分布
            fig_d = px.bar(df_d.tail(20), x=df_d.columns[2], y=df_d.columns[0], color=df_d.columns[1],
                           title="Training Load Analysis", color_discrete_sequence=["#B8860B"])
            st.plotly_chart(fig_d, use_container_width=True)
        else:
            st.warning("無法載入重訓數據，請確認 Diamond Sheet 連結。")

else:
    st.error("Data Connection Failed.")
