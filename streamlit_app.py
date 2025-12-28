import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. 核心設定
st.set_page_config(page_title="Hazel's War Room", page_icon="🍊", layout="wide")

# 🎨 注入最強 CSS (修正露餡問題 + 強制覆蓋進度條)
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Mate+SC&display=swap" rel="stylesheet">
    <style>
    /* 修正程式碼露餡：確保 style 標籤內沒有任何非 CSS 內容 */
    html, body, [class*="css"] {
        font-family: 'Georgia', 'Microsoft JhengHei', serif !important;
    }
    h1 {
        font-family: 'Cinzel', serif !important;
        color: #FF8C00 !important;
        font-size: 3.5rem !important;
        text-align: center;
        letter-spacing: 4px;
        margin: 20px 0;
    }
    h2, h3, .mate-font {
        font-family: 'Mate SC', serif !important;
        color: #B8860B !important;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        color: #1A1A1A;
    }
    /* 強制修改進度條為暗黃色 (Goldenrod) */
    .stProgress > div > div > div > div {
        background: #B8860B !important;
    }
    .period-box {
        background-color: #FFF9F2;
        padding: 25px;
        border-radius: 20px;
        border-left: 12px solid #FF8C00;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05);
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 資料讀取
@st.cache_data(ttl=300)
def load_data():
    lemon_id = "1o-_Xr7wlisU7Wo0eLY_m2sWocptJC9poMxrUSkOMCNo"
    url = f"https://docs.google.com/spreadsheets/d/{lemon_id}/gviz/tq?tqx=out:csv&sheet=allDatas"
    try:
        df = pd.read_csv(url)
        df = df.dropna(how='all')
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        return df
    except:
        return None

# 3. 生理期判斷邏輯 (增加判斷基準)
def get_period_advice(record_date):
    # 這裡目前模擬週期，建議之後在 Sheet 設定經期第一天
    day_in_cycle = record_date.day % 28 
    if 1 <= day_in_cycle <= 5:
        return "🌸 月經期 (MENSTRUAL)", "賀爾蒙低谷，代謝緩慢。建議：補充紅肉、自泡鮮奶茶（150ml牛奶+200ml熱紅茶）、輕度伸展。"
    elif 6 <= day_in_cycle <= 13:
        return "🔥 濾泡期 (FOLLICULAR)", "雌激素上升，體力巔峰！建議：挑戰重訓 PR、嘗試高強度運動，飲食可稍微增加蛋白質。"
    elif 14 <= day_in_cycle <= 15:
        return "⚡ 排卵期 (OVULATORY)", "代謝加快，體溫微升。建議：注意水分補充，此時是增肌黃金期。"
    else:
        return "🍂 黃體期 (LUTEAL)", "孕酮飆升，水分易滯留。建議：低鈉飲食、減少精緻糖，心情起伏正常，適合帶氧運動。"

# 4. 主程式介面
st.markdown("<h1>HAZEL'S WAR ROOM</h1>", unsafe_allow_html=True)

df_lemon = load_data()

if df_lemon is not None:
    # --- 側邊欄 ---
    with st.sidebar:
        st.markdown("<h2 class='mate-font'>Control Center</h2>", unsafe_allow_html=True)
        target_w = st.number_input("GOAL WEIGHT", value=50.0)
        days_opt = st.radio("TIME RANGE", ["7D", "30D", "ALL"], index=0)
        
        all_cols = df_lemon.columns.tolist()
        # 預設選體重(4)、體脂(5)、骨骼肌(6)
        selected = st.multiselect("SELECT METRICS", all_cols, default=[all_cols[4], all_cols[5]])

    # --- 生理期提醒 (視覺優化) ---
    latest_date = df_lemon.iloc[-1, 0]
    p_title, p_advice = get_period_advice(latest_date)
    st.markdown(f"""
        <div class="period-box">
            <h3 style='margin:0;'>{p_title}</h3>
            <p style='margin:10px 0 0 0; font-size:1.1rem; color:#444;'>{p_advice}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 核心指標放大區 ---
    latest = df_lemon.iloc[-1]
    prev = df_lemon.iloc[-2]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("WEIGHT", f"{latest.iloc[4]} kg", f"{round(latest.iloc[4]-prev.iloc[4],2)} kg", delta_color="inverse")
    with col2:
        st.metric("BODY FAT", f"{latest.iloc[5]} %", f"{round(latest.iloc[5]-prev.iloc[5],2)} %", delta_color="inverse")
    with col3:
        st.metric("MUSCLE", f"{latest.iloc[6]} kg", f"{round(latest.iloc[6]-prev.iloc[6],2)} kg")

    # --- 達成百分比 (暗黃色) ---
    st.markdown("<br>", unsafe_allow_html=True)
    # 起始體重假設 60
    progress = min(100, int(((60.0 - float(latest.iloc[4])) / (60.0 - target_w)) * 100))
    st.markdown(f"<p style='color:#B8860B; font-family:\"Mate SC\"; font-size:1.5rem;'>GOAL PROGRESS: {progress}%</p>", unsafe_allow_html=True)
    st.progress(progress/100)

    # --- 圖表區 (使用 Plotly 解決縱軸扁平問題) ---
    st.markdown("<h2 class='mate-font'>Visual Trends</h2>", unsafe_allow_html=True)
    if selected:
        df_plot = df_lemon.copy()
        if days_opt == "7D": df_plot = df_plot.tail(7)
        elif days_opt == "30D": df_plot = df_plot.tail(30)
        
        # Plotly 繪圖：這會讓 Y 軸自動根據數據動態縮放，不會看到直線
        fig = px.line(df_plot, x=df_lemon.columns[0], y=selected, 
                      color_discrete_sequence=["#FF8C00", "#D4AF37", "#8B4513"])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text='Metrics',
            hovermode="x unified",
            yaxis=dict(autorange=True, fixedrange=False) # 關鍵：強制縱軸自動縮放
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- 飲食與備註 ---
    with st.expander("DETAILS LOG (CLICK TO VIEW)"):
        st.dataframe(df_plot.iloc[::-1], use_container_width=True)

else:
    st.error("Connection Error. Please check your Google Sheet Link.")
