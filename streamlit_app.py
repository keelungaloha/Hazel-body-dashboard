import streamlit as st
import pandas as pd
import numpy as np

# 1. 核心設定
st.set_page_config(page_title="Hazel's 黃金體態", page_icon="🍊", layout="wide")

# 🎨 注入 CSS：設定 Mate SC 與 Georgia 字體
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Mate+SC&display=swap');
    
    /* 英文字體用 Mate SC，數字與內容優先用 Georgia */
    html, body, [class*="css"] {
        font-family: 'Georgia', 'Microsoft JhengHei', serif;
    }
    
    .mate-font {
        font-family: 'Mate SC', serif;
        text-transform: uppercase;
    }
    
    h1, h2, h3 {
        font-family: 'Mate SC', serif;
        color: #FF8C00;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Georgia', serif;
    }

    [data-testid="stMetric"] {
        background-color: #FFF5EE;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF8C00;
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
        # 轉換日期
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        return df
    except:
        return None

# 3. 側邊欄：目標設定與功能切換
with st.sidebar:
    st.markdown("<h2 class='mate-font'>Settings</h2>", unsafe_allow_html=True)
    target_weight = st.number_input("目標體重 (kg)", value=50.0)
    target_fat = st.number_input("目標體脂 (%)", value=22.0)
    
    st.markdown("---")
    st.write("💡 **小撇步**：拍照給我（Gemini），我幫你算完後，請記得填入 Google Sheet 的『飲食備註』欄位喔！")

# 4. 主程式介面
st.markdown("<h1 class='mate-font'>Hazel's War Room</h1>", unsafe_allow_html=True)

df_lemon = load_data()

if df_lemon is not None:
    # --- 指標區 ---
    latest = df_lemon.iloc[-1]
    previous = df_lemon.iloc[-2]
    
    curr_w = float(latest.iloc[4])
    prev_w = float(previous.iloc[4])
    
    # 計算達成率 (以體重為例)
    # 假設起始體重是 60 (這部分之後可以改為自動抓取)
    start_w = 60.0 
    progress = min(100, int(((start_w - curr_w) / (start_w - target_weight)) * 100))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Weight", value=f"{curr_w} kg", delta=f"{round(curr_w - prev_w, 2)} kg", delta_color="inverse")
    with col2:
        st.write(f"**目標達成率**")
        st.progress(max(0, progress/100))
        st.write(f"🔥 已完成 {progress}%！再接再厲！")
    with col3:
        # 生理期邏輯預留 (目前先放日期)
        st.metric(label="Record Date", value=str(latest.iloc[0]).split()[0])

    # --- 趨勢與多選區 ---
    st.markdown("---")
    st.subheader("📊 數據追蹤")
    
    # 讓使用者選要看哪些數值
    all_cols = df_lemon.columns.tolist()
    selected_metrics = st.multiselect("勾選想要顯示的數值", options=all_cols, default=[all_cols[4]])
    
    if selected_metrics:
        # 繪製自定義圖表 (顏色統一用橘色系)
        st.line_chart(df_lemon, x=all_cols[0], y=selected_metrics, color="#FF8C00")

    # --- 備註與飲食內容 ---
    st.markdown("---")
    st.subheader("🍎 飲食與睡眠備註")
    # 假設你的備註在最後幾欄，我們顯示最近三天的
    for i in range(1, 4):
        row = df_lemon.iloc[-i]
        with st.chat_message("user"):
            st.write(f"**{str(row.iloc[0]).split()[0]}**")
            # 假設備註在最後一欄，請根據實際調整索引
            st.write(f"飲食內容：{row.iloc[-1]}")
            # 這裡可以根據你 Sheets 裡的睡眠時數顯示
            st.write(f"😴 睡眠時數：{row.iloc[12]} 小時")

else:
    st.error("連線失敗")
