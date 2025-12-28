import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 核心設定
st.set_page_config(page_title="Hazel's 黃金體態", page_icon="🍊", layout="wide")

# 2. 資料讀取 (讀取 Google Sheet CSV)
@st.cache_data(ttl=600)
def load_data():
    lemon_id = "1o-_Xr7wlisU7Wo0eLY_m2sWocptJC9poMxrUSkOMCNo"
    # 使用你修正後的分頁名稱 allDatas
    url = f"https://docs.google.com/spreadsheets/d/{lemon_id}/gviz/tq?tqx=out:csv&sheet=allDatas"
    try:
        df = pd.read_csv(url)
        return df
    except:
        return None

# 3. 主程式介面
st.title("🍊 Hazel's 黃金體態戰情室")

df_lemon = load_data()

if df_lemon is not None:
    st.success("✅ 資料讀取成功！")
    
    # 📊 數據預覽：先丟掉空白行，抓最後 7 筆，最新在前
    st.subheader("📊 最近 7 天數據預覽")
    df_clean = df_lemon.dropna(how='all').tail(7).iloc[::-1]
    st.dataframe(df_clean, use_container_width=True)

    # 📈 簡易體重趨勢圖
    try:
        # 假設第一欄是日期，第四欄是體重 (請根據你的 Sheet 欄位順序調整索引)
        df_lemon['Date'] = pd.to_datetime(df_lemon.iloc[:, 0], errors='coerce')
        df_plot = df_lemon.dropna(subset=['Date'])
        
        st.subheader("📈 體重趨勢")
        # 抓取「體重」那一欄的名字自動畫圖
        weight_col = df_lemon.columns[4] 
        st.line_chart(df_plot, x='Date', y=weight_col)
    except:
        st.warning("提醒：圖表目前無法自動辨識欄位，但數據表格已正常顯示。")

else:
    st.error("❌ 無法連線到資料表，請檢查 Google Sheet 是否開啟「知道連結的人皆可檢視」。")

# 結尾：確保沒有遺漏任何程式碼塊
