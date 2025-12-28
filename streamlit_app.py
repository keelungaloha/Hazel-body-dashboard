import streamlit as st
import pandas as pd

# 1. 核心設定
st.set_page_config(page_title="Hazel's 黃金體態", page_icon="🍊", layout="wide")

# 🎨 注入自定義 CSS (美編控專屬)
st.markdown("""
    <style>
    /* 全域字體優化 */
    html, body, [class*="css"] {
        font-family: "Microsoft JhengHei", "PingFang TC", "Source Sans Pro", sans-serif;
    }
    /* 標題顏色 */
    h1 {
        color: #FF8C00;
    }
    /* 指標卡片外框美化 (選用) */
    [data-testid="stMetric"] {
        background-color: #FFF5EE;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF8C00;
    }
    </style>
    """, unsafe_allow_stdio=True)

# 2. 資料讀取
@st.cache_data(ttl=600)
def load_data():
    lemon_id = "1o-_Xr7wlisU7Wo0eLY_m2sWocptJC9poMxrUSkOMCNo"
    url = f"https://docs.google.com/spreadsheets/d/{lemon_id}/gviz/tq?tqx=out:csv&sheet=allDatas"
    try:
        df = pd.read_csv(url)
        df = df.dropna(how='all')
        return df
    except:
        return None

# 3. 主程式介面
st.title("🍊 Hazel's 黃金體態🍊")

df_lemon = load_data()

if df_lemon is not None:
    # --- 大數字卡片區 ---
    st.subheader("核心指標")
    col1, col2, col3 = st.columns(3)
    
    try:
        latest = df_lemon.iloc[-1]
        previous = df_lemon.iloc[-2]
        
        curr_w = round(float(latest.iloc[4]), 1) # 體重
        prev_w = round(float(previous.iloc[4]), 1)
        w_delta = round(curr_w - prev_w, 1)

        curr_f = round(float(latest.iloc[5]), 1) # 體脂
        prev_f = round(float(previous.iloc[5]), 1)
        f_delta = round(curr_f - prev_f, 1)

        with col1:
            st.metric(label="目前體重", value=f"{curr_w} kg", delta=f"{w_delta} kg", delta_color="inverse")
        with col2:
            st.metric(label="體脂肪率", value=f"{curr_f} %", delta=f"{f_delta} %", delta_color="inverse")
        with col3:
            st.metric(label="最後記錄日期", value=str(latest.iloc[0]).split()[0])
    except:
        st.info("指標計算中...")

    st.markdown("---")

    # --- 圖表區 (橘色系優化) ---
    try:
        df_lemon['Date'] = pd.to_datetime(df_lemon.iloc[:, 0], errors='coerce')
        df_plot = df_lemon.dropna(subset=['Date'])
        
        st.subheader("📈 體重趨勢 (橘色波段)")
        weight_col = df_lemon.columns[4] 
        
        # 使用 area_chart 並指定顏色
        # 注意：color 參數在較新版的 Streamlit 中可用
        st.area_chart(df_plot, x='Date', y=weight_col, color="#FFCC99") # 淡淡的橘色
    except:
        st.warning("圖表暫時無法顯示。")

    # --- 數據預覽 ---
    with st.expander("📂 查看最近 7 天詳細數據"):
        df_clean = df_lemon.tail(7).iloc[::-1]
        st.dataframe(df_clean, use_container_width=True)

else:
    st.error("❌ 無法讀取資料。")
