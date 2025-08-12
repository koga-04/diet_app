import streamlit as st
import sqlite3
import pandas as pd
import datetime
import google.generativeai as genai
import json
from PIL import Image
import io

# =============================
# Page / Theme
# =============================
st.set_page_config(
    page_title="ウェルネスダイアリー",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Global Styles (accessible, minimal, modern) ----
st.markdown(
    """
    <style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@400');

  :root {
    --bg: #F7FAFC;
    --panel: #FFFFFF;
    --text: #111827;
    --muted: #6B7280;
    --border: #E5E7EB;
    --primary: #3B82F6;
    --primary-600: #2563EB;
    --primary-700: #1D4ED8;
    --warn: #EF4444;
    --radius: 12px;
  }

  html, body, [class*="st-"], [class*="css-"] {
    font-family: 'Noto Sans JP', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', sans-serif;
    color: var(--text);
  }
  .stApp { background: var(--bg); }

  /* Ensure material icon font renders glyphs instead of raw text */
  [class^="material-icons"], [class*=" material-icons"],
  [class^="material-symbols"], [class*=" material-symbols"] {
    font-family: 'Material Symbols Outlined' !important;
    font-weight: 400; font-style: normal;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  }

  /* ===== Hero ===== */
  .hero { background: linear-gradient(135deg, rgba(59,130,246,.10), rgba(34,211,238,.10)); border: 1px solid var(--border); border-radius: 16px; padding: 24px 28px; margin: 8px 0 18px 0; }
  .hero-title { font-size: 28px; font-weight: 700; letter-spacing: .2px; }
  .hero-sub { color: var(--muted); margin-top: 6px; }

  /* ===== Card ===== */
  .card { background: var(--panel); border-radius: 16px; border: 1px solid var(--border); padding: 24px; box-shadow: 0 8px 28px rgba(17,24,39,0.06); margin-bottom: 18px; }

  /* ===== Buttons ===== */
  .stButton>button { border-radius: 10px; border: 1px solid transparent !important; padding: .7rem 1.1rem; font-weight: 600; background: var(--primary) !important; color: #fff !important; box-shadow:none !important; }
  .stButton>button:hover { background: var(--primary-600) !important; }
  .stButton>button:active { transform: none; }

  /* ===== Inputs: identical to Selectbox (flat) ===== */
  .stTextInput>div, .stNumberInput>div, .stDateInput>div, .stSelectbox>div, .stTextArea>div {
    background:#FFFFFF !important; border:1px solid var(--border) !important; border-radius:12px !important; box-shadow:none !important; overflow:hidden !important;
  }
  .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox>div>div, .stTextArea textarea {
    background:#FFFFFF !important; border:none !important; border-radius:0 !important; box-shadow:none !important; color: var(--text) !important;
    caret-color: var(--primary) !important; /* ★改修要望2: カーソルを表示 */
  }
  .stTextInput>div:focus-within, .stNumberInput>div:focus-within, .stDateInput>div:focus-within, .stSelectbox>div:focus-within, .stTextArea>div:focus-within { 
      border-color: var(--primary) !important; box-shadow:none !important; 
  }

  /* >>> DateInput: remove any dark end-cap/inner enhancers */
  .stDateInput * { background:#FFFFFF !important; border-color: var(--border) !important; box-shadow:none !important; }
  .stDateInput input { height:42px !important; padding:0 12px !important; }

  /* NumberInput steppers: readable */
  .stNumberInput [data-baseweb="button"], .stNumberInput [data-baseweb="button"] * { background: transparent !important; color: #374151 !important; fill: #374151 !important; border:none !important; }
  .stNumberInput [data-baseweb="button"]:hover { background:#F3F4F6 !important; }

  /* ===== Tabs ===== */
  .stTabs [data-baseweb="tab-list"] { gap: 18px; border-bottom: 1px solid var(--border); }
  .stTabs [data-baseweb="tab"] { font-weight: 600; color: var(--muted); }
  .stTabs [aria-selected="true"] { color: var(--primary); border-bottom: 2px solid var(--primary); }

  /* ===== Sidebar ===== */
  [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid var(--border); }

  /* ===== Datepicker / Popover (full light) ===== */
  [data-baseweb="popover"] { background: #FFFFFF !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
  [data-baseweb="popover"] * { background:#FFFFFF !important; color: var(--text) !important; }
  [role="dialog"], [data-baseweb="datepicker"], [data-baseweb="calendar"] { background: #FFFFFF !important; color: var(--text) !important; }
  [data-baseweb="calendar"] [role="row"] [role="columnheader"],
  [data-baseweb="calendar"] [role="heading"],
  [data-baseweb="datepicker"] [class*="header"],
  [data-baseweb="datepicker"] [class*="Header"] { background:#FFFFFF !important; color:#111827 !important; }
  [data-baseweb="calendar"] [aria-selected="true"] { background: var(--primary) !important; color: #fff !important; border-radius: 8px; }
  [data-baseweb="calendar"] [aria-disabled="true"] { color: #9CA3AF !important; }

  /* ===== Sidebar collapse: hide raw text; keep button visible ===== */
  [data-testid="stSidebarNavCollapseButton"] span { visibility:hidden !important; }
  [data-testid="stSidebarNavCollapseButton"] { position:relative; width:28px !important; height:28px !important; }
  [data-testid="stSidebarNavCollapseButton"]::after { content:'≡'; position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size:18px; color:#6B7280; }

  /* Data editor tweaks */
  [data-testid="stDataFrame"] header, [data-testid="stDataFrame"] thead { background: #FBFDFF; }
</style>
    """,
    unsafe_allow_html=True,
)

# =============================
# API Key (Gemini)
# =============================
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except (KeyError, FileNotFoundError):
    st.error("⚠️ Google APIキーが設定されていません。")
    st.info("Streamlit の Secrets に `GOOGLE_API_KEY` を設定してください。")
    st.stop()

# =============================
# Database (SQLite)
# =============================
DB_FILE = "diet_records.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # 食事記録テーブル
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            food_name TEXT NOT NULL,
            calories REAL,
            protein REAL,
            carbohydrates REAL,
            fat REAL,
            vitamin_d REAL,
            salt REAL,
            zinc REAL,
            folic_acid REAL
        )
        """
    )
    # 運動記録テーブル
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            exercise_name TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


# CRUD helpers for Meals

def add_record(date, meal_type, food_name, nutrients):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO meals (date, meal_type, food_name, calories, protein, carbohydrates, fat, vitamin_d, salt, zinc, folic_acid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            date.strftime("%Y-%m-%d"),
            meal_type,
            food_name,
            nutrients.get("calories"),
            nutrients.get("protein"),
            nutrients.get("carbohydrates"),
            nutrients.get("fat"),
            nutrients.get("vitaminD"),
            nutrients.get("salt"),
            nutrients.get("zinc"),
            nutrients.get("folic_acid"),
        ),
    )
    conn.commit()
    conn.close()


def get_all_records():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM meals ORDER BY date DESC, id DESC", conn)
    conn.close()
    return df


def get_records_by_period(start_date, end_date):
    conn = get_db_connection()
    query = "SELECT * FROM meals WHERE date BETWEEN ? AND ? ORDER BY date DESC, id DESC"
    df = pd.read_sql_query(
        query,
        conn,
        params=(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
    )
    conn.close()
    return df


def delete_record(record_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM meals WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

# CRUD helpers for Exercises
def add_exercise_record(date, exercise_name, duration_minutes):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO exercises (date, exercise_name, duration_minutes) VALUES (?, ?, ?)",
        (date.strftime("%Y-%m-%d"), exercise_name, duration_minutes)
    )
    conn.commit()
    conn.close()

def get_all_exercise_records():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM exercises ORDER BY date DESC, id DESC", conn)
    conn.close()
    return df

def delete_exercise_record(record_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM exercises WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


# =============================
# Gemini helpers
# =============================

def get_advice_from_gemini(prompt: str) -> str:
    """テキストプロンプトからアドバイスを生成（gemini-2.5-flash）。"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        resp = model.generate_content(prompt)
        return (resp.text or "").strip()
    except Exception as e:
        st.error(f"アドバイス生成中にエラーが発生しました: {e}")
        return "アドバイスの生成に失敗しました。"

def analyze_image_with_gemini(image_bytes):
    """画像を解析し、料理ごとの内訳と合計値を含むJSONを返す。"""
    model_candidates = ["gemini-2.5-flash", "gemini-1.5-pro-latest"]
    image_pil = Image.open(io.BytesIO(image_bytes))
    prompt = (
        """
        あなたは栄養管理の専門家です。この食事の画像を分析してください。
        食事に含まれる料理を**すべて**特定し、**料理ごと**に栄養素を推定してください。
        結果は必ず以下のJSON形式で、数値のみを返してください。説明や```json```は不要です。

        {
          "summary": "食事全体の短い要約（例：焼き魚定食とビール）",
          "totalNutrients": { "calories": 0.0, "protein": 0.0, "carbohydrates": 0.0, "fat": 0.0, "vitaminD": 0.0, "salt": 0.0, "zinc": 0.0, "folic_a
