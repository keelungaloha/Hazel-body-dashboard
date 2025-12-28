import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import altair as alt

# ---------------------------------------------------------
# 1. 核心設定
# ---------------------------------------------------------
st.set_page_config(page_title="Hazel's 黃金體態", page_icon="🍊", layout="wide")

# ★★★ 請在這裡貼上你的 ID ★★★
# 如果你有多個表單，請分別填入。如果只有一個，兩個填一樣的也可以測試。
LEMON_SHEET_ID = "1o-_Xr7wlisU7Wo0eLY_m2sWocptJC9poMxrUSkOMCNo"  # 請替換成你剛剛複製的那串
DIAMOND_SHEET_ID = "1Iok7RIO1y4ggbcpVja0yoO0J2Cox04Y3WJjufBpOAus"

# ---------------------------------------------------------
# 2. 資料讀取函式 (搬運工)
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    # 注意：這裡的 sheet=Daily%20Data%20🍒 代表分頁名稱是 "Daily Data 🍒"
    # 如果你的分頁名稱不同，請務必修改 sheet= 後面的名字
    url_lemon = f"https://docs.google.com/spreadsheets/d/{LEMON_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=allDatas"

    
    # 如果第二個表不需要指定分頁，就不用加 sheet=...
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
    
  # 📊 數據預覽 - 改為顯示最近 7 筆，並把最新的放最上面
    st.subheader("📊 最近 7 天數據預覽")
    
   # 先把完全空白的列丟掉 (dropna)，再抓最後 7 筆
    df_clean = df_lemon.dropna(how='all').tail(7).iloc[::-1]
    
    st.dataframe(df_clean, use_container_width=True)
    
    st.dataframe(latest_7_days, use_container_width=True)
    # 嘗試畫一個簡單的體重折線圖 (假設你有 'Date' 和 '體重' 欄位)
    # 如果欄位名稱不一樣，這裡可能會報錯，但沒關係，我們先求有
    try:
        # 這裡做一點簡單的清洗，確保日期是日期格式
        # 假設第一欄是日期，我們自動抓第一欄當日期
        date_col = df_lemon.columns[0] 
        df_lemon[date_col] = pd.to_datetime(df_lemon[date_col], errors='coerce')
        
        st.subheader("📈 體重趨勢圖")
        st.line_chart(df_lemon, x=date_col, y=df_lemon.columns[1]) # 假設第二欄是體重
    except:
        st.warning("無法自動畫圖，請檢查 Excel 的欄位名稱是否包含特殊符號，但資料讀取是正常的！")

else:
    st.error("❌ 資料讀取失敗。")
    st.info("""
    請檢查以下幾點：
    1. Google Sheet 是否已開啟「知道連結者皆可檢視」。
    2. SHEET_ID 是否填寫正確。
    3. 分頁名稱 (Sheet Name) 是否真的是 'Daily Data 🍒'？如果不是，程式碼裡面的網址要改。
    """)
