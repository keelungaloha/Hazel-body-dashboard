import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import altair as alt

# ---------------------------------------------------------
# 1. 核心設定
# ---------------------------------------------------------
st.set_page_config(page_title="Hazel's 黃金體態", page_icon="🍊", layout="wide")

# ★★★ 你的 Google Sheet ID ★★★
LEMON_SHEET_ID = "1o-_Xr7wlisU7Wo0eLY_m2sWocptJC9poMxrUSkOMCNo"
DIAMOND_SHEET_ID = "1Iok7RIO1y4ggbcpVja0yoO0J2Cox04Y3WJjufBpOAus"

# ---------------------------------------------------------
# 2. 資料讀取函式 (搬運工)
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    # 使用你修正後的分頁名稱 allDatas
    url_lemon = f"https://docs.google.com/spreadsheets/d/{LEMON_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=allDatas"
    url_diamond = f"https://docs.google.com/spreadsheets/d/{DIAMOND_SHEET_ID}/gviz/tq?tqx=out:csv"
    
    try:
        df_lemon = pd.read_csv(url_lemon)
        df_workout = pd.read_csv(url_diamond)
        return df_lemon, df_workout
    except Exception as e:
        return None, None

# ---------------------------------------------------------
# 3. 主程式 (開始蓋房子)
# ---------------------------------------------------------
st.title("🍊 Hazel's 黃金體態")
st.write("正在連線到 Google Sheet 讀取最新數據...")

df_lemon, df_workout = load_data()

if df_lemon is not None:
    st.success("✅ 資料讀取成功！")
    
    # 📊 數據預覽 - 顯示最近 7 筆，並把最新的放最上面
    st.subheader("📊 最近 7 天數據預覽")
    
    # 先過濾掉完全空白的列，再抓最後 7 筆並反轉順序
    df_clean = df_lemon.dropna(how='all').tail(7).iloc[::-1]
    
    # 這裡只顯示 df_clean，確保不會再出現 NameError
    st.dataframe(df_clean, use_container_width=True)
    
    # 📈 圖表區
    try:
        # 確保第一欄（通常是時間戳記）被正確辨識為日期
        date_col = df_lemon.columns[0] 
        df_lemon[date_col] = pd.to_datetime(df_lemon[date_col], errors='coerce')
        
        # 排除掉日期轉換失敗的空白列
        df_plot = df_lemon.dropna(subset=[date_col])
        
        st.subheader("📈 體重趨勢圖")
        # 這裡假設第
