import streamlit as st
import pandas as pd
import numpy as np

# 1. 核心設定
st.set_page_config(page_title="Hazel's War Room", page_icon="🍊", layout="wide")

# 🎨 注入設計師級 CSS
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Mate+SC&display=swap" rel="stylesheet">
    <style>
    /* 標題：Cinzel (份量感十足) */
    h1 {
        font-family: 'Cinzel', serif !important;
        color: #FF8C00 !important;
        font-size: 3.5rem !important;
        letter-spacing: 3px;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* 副標題與側邊欄 */
    h2, h3, .mate-font {
        font-family: 'Mate SC', serif !important;
        color: #B8860B !important;
    }

    /* 數字與一般文字：Georgia */
    html, body, [class*="css"] {
        font-family: 'Georgia', 'Microsoft JhengHei', serif;
    }

    /* 指標數據放大 */
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 700;
        color: #2F4F4F;
    }

    /* 強制修改進度條顏色為暗黃色 (Goldenrod) */
    .stProgress > div > div > div > div {
        background-color: #B8860B !important;
    }

    /* 生理期提醒區塊 */
    .period-box {
        background-color: #FFF0F5;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #FF69B4;
        margin-bottom: 25px;
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

# 3. 生理週期邏輯判斷 (假設以 28 天為一週期)
def get_period_advice(record_date):
    # 這裡需要一個基準日，目前先以日期天數做模擬，建議你在 Sheet 加一欄「經期開始日」
    day_in_cycle = record_date.day % 28 
    if 1 <= day_in_cycle <= 5:
        return "🌸 **月經期 (Menstrual)**", "賀爾蒙低谷，容易疲勞。建議：輕度伸展、補充鐵質、多熱飲自泡鮮奶茶。"
    elif 6 <= day_in_cycle <= 13:
        return "🔥 **濾泡期 (Follicular)**", "雌激素上升，代謝極佳！建議：挑戰大重量重訓、高強度運動，食慾較穩定。"
    elif 14 <= day_in_cycle <= 15:
        return "⚡ **排卵期 (Ovulatory)**", "體溫上升，體力巔峰。建議：破 PR 的好時機，但要注意分泌物變化。"
    else:
        return "🍂 **黃體期 (Luteal)**", "孕酮升高，水分易滯留（水腫）。建議：多喝水消腫、心情易波動、食慾增加，適合低強度帶氧。"

# 4. 主程式
st.markdown("<h1>Hazel's War Room</h1>", unsafe_allow_html=True)

df_lemon = load_data()

if df_lemon is not None:
    # --- 側邊欄控制 ---
    with st.sidebar:
        st.markdown("<h2 class='mate-font'>Control Center</h2>", unsafe_allow_html=True)
        target_w = st.number_input("Goal Weight", value=50.0)
        days_opt = st.radio("Time Range", ["7D", "30D", "ALL"], index=0)
        
        all_cols = df_lemon.columns.tolist()
        selected = st.multiselect("Select Metrics", all_cols, default=[all_cols[4], all_cols[5]])

    # --- 生理期提醒區 ---
    latest_date = df_lemon.iloc[-1, 0]
    phase_title, phase_advice = get_period_advice(latest_date)
    st.markdown(f"""
        <div class="period-box">
            <h3 style='margin:0; color:#FF69B4;'>{phase_title}</h3>
            <p style='margin:10px 0 0 0; color:#555;'>{phase_advice}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 重點指標 ---
    latest = df_lemon.iloc[-1]
    prev = df_lemon.iloc[-2]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Weight", f"{latest.iloc[4]} kg", f"{round(latest.iloc[4]-prev.iloc[4],2)} kg", delta_color="inverse")
    with c2:
        st.metric("Body Fat", f"{latest.iloc[5]} %", f"{round(latest.iloc[5]-prev.iloc[5],2)} %", delta_color="inverse")
    with c3:
        st.metric("Skeletal Muscle", f"{latest.iloc[6]} kg", f"{round(latest.iloc[6]-prev.iloc[6],2)} kg")

    # --- 達成率 (暗黃色) ---
    st.markdown("---")
    progress = min(100, int(((60.0 - float(latest.iloc[4])) / (60.0 - target_w)) * 100))
    st.markdown(f"<p style='color:#B8860B; font-weight:bold;'>GOAL PROGRESS: {progress}%</p>", unsafe_allow_html=True)
    st.progress(progress/100)

    # --- 趨勢圖 (優化縱軸) ---
    st.subheader("Visual Analysis")
    if selected:
        df_plot = df_lemon.copy()
        if days_opt == "7D": df_plot = df_plot.tail(7)
        elif days_opt == "30D": df_plot = df_plot.tail(30)
        
        # 使用動態縮放：讓縱軸不要從 0 開始，而是根據數據範圍顯示
        chart_data = df_plot.set_index(df_lemon.columns[0])[selected]
        st.line_chart(chart_data, use_container_width=True) 
        # 註：Streamlit 的 line_chart 預設會根據數據縮放。
        # 如果你覺得還不夠，我們可以改用 Plotly 來精確控制 y-axis 範圍。

    # --- 睡眠與備註 ---
    with st.expander("Details Log"):
        st.dataframe(df_plot.iloc[::-1])

else:
    st.error("Sheet Connection Error")
