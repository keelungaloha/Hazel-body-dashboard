import streamlit as st
import pandas as pd

# 1. 核心設定
st.set_page_config(page_title="Hazel's 黃金體態", page_icon="🍊", layout="wide")

# 2. 資料讀取
@st.cache_data(ttl=600)
def load_data():
    lemon_id = "1o-_Xr7wlisU7Wo0eLY_m2sWocptJC9poMxrUSkOMCNo"
    url = f"https://docs.google.com/spreadsheets/d/{lemon_id}/gviz/tq?tqx=out:csv&sheet=allDatas"
    try:
        df = pd.read_csv(url)
        # 清除完全空白的行
        df = df.dropna(how='all')
        return df
    except:
        return None

# 3. 主程式介面
st.title("🍊 Hazel's 黃金體態戰情室")

df_lemon = load_data()

if df_lemon is not None:
    # --- 美化區：大數字卡片 ---
    st.subheader("核心指標")
    col1, col2, col3 = st.columns(3)
    
    try:
        # 假設：第 5 欄是體重 (E)，第 6 欄是體脂 (F)
        # 抓取最後兩筆來計算變化
        latest = df_lemon.iloc[-1]
        previous = df_lemon.iloc[-2]
        
        curr_w = round(float(latest.iloc[4]), 1)
        prev_w = round(float(previous.iloc[4]), 1)
        w_delta = round(curr_w - prev_w, 1)

        curr_f = round(float(latest.iloc[5]), 1)
        prev_f = round(float(previous.iloc[5]), 1)
        f_delta = round(curr_f - prev_f, 1)

        with col1:
            st.metric(label="目前體重", value=f"{curr_w} kg", delta=f"{w_delta} kg", delta_color="inverse")
        with col2:
            st.metric(label="體脂肪率", value=f"{curr_f} %", delta=f"{f_delta} %", delta_color="inverse")
        with col3:
            st.metric(label="最後記錄日期", value=str(latest.iloc[0]).split()[0])
    except:
        st.info("指標計算中...請確保體重與體脂欄位有數值。")

    st.markdown("---") # 分隔線

    # --- 數據預覽 ---
    st.subheader("📊 最近 7 天數據預覽")
    df_clean = df_lemon.tail(7).iloc[::-1]
    st.dataframe(df_clean, use_container_width=True)

    # --- 圖表區 ---
    try:
        df_lemon['Date'] = pd.to_datetime(df_lemon.iloc[:, 0], errors='coerce')
        df_plot = df_lemon.dropna(subset=['Date'])
        
        st.subheader("📈 體重趨勢圖")
        weight_col = df_lemon.columns[4] 
        # 使用 Streamlit 內建圖表，簡約美觀
        st.area_chart(df_plot, x='Date', y=weight_col)
    except:
        st.warning("圖表暫時無法顯示。")

else:
    st.error("❌ 無法讀取資料。")
