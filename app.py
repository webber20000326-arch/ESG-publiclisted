import io

import pandas as pd
import requests
import streamlit as st
import urllib3

# verify=False 會產生 InsecureRequestWarning，這裡關閉警告訊息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_URL = "https://mopsfin.twse.com.tw/opendata/t187ap46_L_1.csv"  # 換連結

st.set_page_config(page_title="CSV 資料檢視", page_icon="📊", layout="wide")
st.title("📊 公開資訊觀測站 CSV 資料檢視")


@st.cache_data(ttl=3600, show_spinner="下載資料中...")
def load_data(url: str, drop_na: bool) -> pd.DataFrame:
    response = requests.get(url, verify=False, timeout=30)
    response.raise_for_status()
    # 直接在記憶體中讀取，不需要先存成 data01.csv
    df = pd.read_csv(io.BytesIO(response.content), encoding="utf-8-sig")  # 繁體中文
    if drop_na:
        df = df.dropna()
    return df


# ---------------- 側邊欄 ----------------
with st.sidebar:
    st.header("設定")
    url = st.text_input("CSV 連結", value=DEFAULT_URL)
    drop_na = st.checkbox("移除含空值的列 (dropna)", value=True)
    if st.button("🔄 重新下載"):
        st.cache_data.clear()

# ---------------- 主畫面 ----------------
try:
    df = load_data(url, drop_na)
except requests.RequestException as e:
    st.error(f"下載失敗：{e}")
    st.stop()
except Exception as e:
    st.error(f"資料處理失敗：{e}")
    st.stop()

col1, col2 = st.columns(2)
col1.metric("資料筆數", f"{len(df):,}")
col2.metric("欄位數", len(df.columns))

keyword = st.text_input("🔍 關鍵字搜尋（搜尋所有欄位）")
if keyword:
    mask = df.astype(str).apply(
        lambda col: col.str.contains(keyword, case=False, na=False)
    ).any(axis=1)
    view_df = df[mask]
    st.caption(f"符合 {len(view_df):,} 筆")
else:
    view_df = df

st.dataframe(view_df, use_container_width=True, hide_index=True)

st.download_button(
    "⬇️ 下載 CSV",
    data=view_df.to_csv(index=False).encode("utf-8-sig"),
    file_name="data01.csv",
    mime="text/csv",
)
