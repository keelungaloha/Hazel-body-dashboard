import streamlit as st
import pandas as pd
import numpy as np

# 1. 核心設定
st.set_page_config(page_title="Hazel's 黃金體態", page_icon="🍊", layout="wide")

# 🎨 注入 CSS：精細控制字體比例與顏色
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Mate+SC&display=swap" rel="stylesheet">
    <style>
    /* 英文字體 Mate SC，數字 Georgia */
    html, body, [class*="css"] {
        font-family: 'Georgia', 'Microsoft JhengHei', serif;
    }
    
    /* 強制標題使用 Mate SC */
    h1, h2, h3, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2 {
        font-family: 'Mate SC', serif !important;
        color: #FF8C00 !important;
        text-transform: uppercase;
    }

    /* 調整 Metric 數據大小 */
    [data-testid="stMetricValue"] {
        font-size: 2.8rem !important; /* 放大重點數據 */
        font-family: 'Georgia', serif;
    }
    [data-testid="stMetricDelta"] {
        font-size: 1.2rem !important; /* 增減比例稍大 */
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
    }

    /* 縮小 Record Date 的 Metric 顯示 */
    div[data-testid="column"]:nth-child(3) [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: #888;
    }

    /* 更改進度條顏色為暗黃色 */
    .stProgress > div > div > div > div {
        background-color: #D4AF37 !important;
    }

    /* 指標卡片美化 */
    [data-testid="stMetric"] {
        background-color: #FFF5EE;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #FF8C00;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
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

# 3. 側邊欄控制
df_lemon = load_data()

with st.sidebar:
    st.markdown("## SETTINGS")
    target_weight = st.number_input("目標體重 (kg)", value=50.0)
    
    st.markdown("---")
    st.markdown("## CHART FILTER")
    # 預設選 7 天，但可以選「全部」
    days_to_show = st.radio("顯示區間", options=["最近 7 天", "最近 30 天", "全部日期"], index=0)
    
    # 趨勢數據下拉多選
    all_cols = df_lemon.columns.tolist() if df_lemon is not None else []
    # 預設勾選：體重(4), 體脂(5), 骨骼肌(6)
    selected_metrics = st.multiselect("選擇圖表顯示項目", options=all_cols, default=[all_cols[4], all_cols[5]])

# 4. 主程式介面
st.title("Hazel's War Room")

if df_lemon is not None:
    # 數據過濾邏輯
    df_filtered = df_lemon.copy()
    if days_to_show == "最近 7 天":
        df_filtered = df_lemon.tail(7)
    elif days_to_show == "最近 30 天":
        df_filtered = df_lemon.tail(30)

    # --- 重點數據指標區 ---
    latest = df_lemon.iloc[-1]
    prev = df_lemon.iloc[-2]
    
    # 這裡選取你指定的重點數據
    col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 1])
    
    with col1:
        # 體重
        val = round(float(latest.iloc[4]), 1)
        diff = round(val - float(prev.iloc[4]), 1)
        st.metric(label="Weight", value=f"{val} kg", delta=f"{diff} kg", delta_color="inverse")
    
    with col2:
        # 體脂肪 (假設索引 5)
        val = round(float(latest.iloc[5]), 1)
        diff = round(val - float(prev.iloc[5]), 1)
        st.metric(label="Body Fat", value=f"{val} %", delta=f"{diff} %", delta_color="inverse")

    with col3:
        # 骨骼肌 (假設索引 6)
        val = round(float(latest.iloc[6]), 1)
        diff = round(val - float(prev.iloc[6]), 1)
        st.metric(label="Skeletal Muscle", value=f"{val} kg", delta=f"{diff} kg")

    with col4:
        # 小小的日期
        st.metric(label="Date", value=str(latest.iloc[0]).split()[0])

    # 細胞內外水 (額外一列)
    c1, c2, c3 = st.columns(3)
    with c1:
        val = round(float(latest.iloc[13]), 3) # ECW比率
        diff = round(val - float(prev.iloc[13]), 3)
        st.metric(label="ECW Ratio", value=val, delta=diff, delta_color="inverse")

    # --- 成功百分比 (暗黃色) ---
    st.markdown("---")
    start_w = 60.0 # 起始體重
    progress = min(100, int(((start_w - float(latest.iloc[4])) / (start_w - target_weight)) * 100))
    st.markdown(f"**Goal Progress: {progress}%**")
    st.progress(max(0, progress/100))

    # --- 趨勢圖 (解決多變數報錯) ---
    st.subheader("Trends Analysis")
    if selected_metrics:
        # 不使用內建 line_chart 改用 area_chart 或更穩定的處理方式
        # 為了支援多顏色，我們不強制設定單一 color 參數
        st.line_chart(df_filtered.set_index(df_lemon.columns[0])[selected_metrics])
    
    # --- 飲食備註 ---
    with st.expander("Notes Log"):
        st.dataframe(df_filtered.iloc[::-1], use_container_width=True)

else:
    st.error("Data connection failed.")
