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
    page_title="食生活アドバイザー",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Global Styles (accessible, minimal, modern) ----
st.markdown(
    """
    <style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');

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
  .stTextInput>div, .stNumberInput>div, .stDateInput>div, .stSelectbox>div {
    background:#FFFFFF !important; border:1px solid var(--border) !important; border-radius:12px !important; box-shadow:none !important; overflow:hidden !important;
  }
  .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox>div>div {
    background:#FFFFFF !important; border:none !important; border-radius:0 !important; box-shadow:none !important; color: var(--text) !important;
  }
  .stTextInput>div:focus-within, .stNumberInput>div:focus-within, .stDateInput>div:focus-within, .stSelectbox>div:focus-within { border-color: var(--primary) !important; box-shadow:none !important; }

  /* >>> DateInput: force all inner slots to white (remove dark end-cap) */
  .stDateInput>div>div, .stDateInput>div>div * { background:#FFFFFF !important; border:none !important; box-shadow:none !important; }
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

  /* ===== Sidebar collapse: hide fallback text only (keep button visible) ===== */
  [data-testid="stSidebarNavCollapseButton"] span { font-size:0 !important; line-height:0 !important; }
  [data-testid="stSidebarNavCollapseButton"] { position:relative; }
  [data-testid="stSidebarNavCollapseButton"]::after { content:'☰'; font-size:18px; color:#6B7280; }

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
    conn.commit()
    conn.close()


# CRUD helpers

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
            # DB column is vitamin_d (snake); normalize here
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


# =============================
# Gemini helpers
# =============================

def analyze_image_with_gemini(image_bytes):
    """画像を解析し、{ foodName, calories, nutrients{...} } を返す"""
    # NOTE: 'gemini-pro-vision' でも使えますが、画像解析は 1.5 系でも動作します
    model = genai.GenerativeModel("gemini-pro-vision")
    image_pil = Image.open(io.BytesIO(image_bytes))
    prompt = (
        """
        あなたは栄養管理の専門家です。この食事の画像を分析してください。
        食事に含まれる料理名を特定し、全体の総カロリー(kcal)、たんぱく質(g)、炭水化物(g)、脂質(g)、ビタミンD(μg)、食塩相当量(g)、亜鉛(mg)、葉酸(μg)を推定してください。
        結果は必ず以下のJSON形式で、数値のみを返してください。説明や```json ```は不要です。
        {
            "foodName": "料理名",
            "calories": 123.0,
            "nutrients": {
                "protein": 12.3, "carbohydrates": 12.3, "fat": 12.3,
                "vitaminD": 1.2, "salt": 1.2, "zinc": 1.5, "folic_acid": 20.0
            }
        }
        """
    )
    try:
        response = model.generate_content([prompt, image_pil])
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except Exception as e:
        st.error(f"画像分析中にエラーが発生しました: {e}")
        return None


def get_advice_from_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"アドバイス生成中にエラーが発生しました: {e}")
        return "アドバイスの生成に失敗しました。"


# =============================
# App
# =============================
init_db()

# --- Header (Hero) ---
st.markdown(
    """
    <div class="hero">
      <div class="hero-title">💧 食生活アドバイザー</div>
      <div class="hero-sub">日々の食事やサプリ・水分補給をシンプルに記録し、AIがやさしくアドバイスします。</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### メニュー")
    menu = st.radio("選択", ["記録する", "相談する"], index=0, label_visibility="collapsed")

# --- Quick glance (today) ---
all_df = get_all_records()

def _sum_today(df: pd.DataFrame):
    if df.empty:
        return {"cal": 0, "p": 0, "c": 0, "f": 0}
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    t = df[df["date"] == today_str]
    # 除外: 水分補給
    t = t[t["meal_type"] != "水分補給"]
    return {
        "cal": float(t["calories"].fillna(0).sum()),
        "p": float(t["protein"].fillna(0).sum()),
        "c": float(t["carbohydrates"].fillna(0).sum()),
        "f": float(t["fat"].fillna(0).sum()),
    }

sum_today = _sum_today(all_df)
col1, col2, col3, col4 = st.columns(4)
col1.metric("本日のカロリー", f"{int(sum_today['cal'])} kcal")
col2.metric("たんぱく質", f"{sum_today['p']:.1f} g")
col3.metric("炭水化物", f"{sum_today['c']:.1f} g")
col4.metric("脂質", f"{sum_today['f']:.1f} g")

# =============================
# RECORD
# =============================
if menu == "記録する":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("今日の記録")
        st.caption("食事・サプリ・水分補給を記録しましょう。")

        # type + date
        left, right = st.columns([1, 1])
        with left:
            meal_type = st.selectbox(
                "記録の種類",
                ["朝食", "昼食", "夕食", "間食", "サプリ", "水分補給"],
                index=0,
            )
        with right:
            record_date = st.date_input("日付", datetime.date.today())

        # ---- サプリ ----
        if meal_type == "サプリ":
            with st.form(key="supplement_form", clear_on_submit=True):
                supplements = {
                    "マルチビタミン": {
                        "displayName": "マルチビタミン",
                        "foodName": "サプリ: スーパーマルチビタミン&ミネラル",
                        "nutrients": {
                            "calories": 5,
                            "protein": 0.02,
                            "carbohydrates": 0.6,
                            "fat": 0.05,
                            "vitaminD": 10.0,
                            "salt": 0,
                            "zinc": 6.0,
                            "folic_acid": 240,
                        },
                    },
                    "葉酸": {
                        "displayName": "葉酸",
                        "foodName": "サプリ: 葉酸",
                        "nutrients": {
                            "calories": 1,
                            "protein": 0,
                            "carbohydrates": 0.23,
                            "fat": 0.004,
                            "vitaminD": 0,
                            "salt": 0,
                            "zinc": 0,
                            "folic_acid": 480,
                        },
                    },
                    "ビタミンD": {
                        "displayName": "ビタミンD",
                        "foodName": "サプリ: ビタミンD",
                        "nutrients": {
                            "calories": 1,
                            "protein": 0,
                            "carbohydrates": 0,
                            "fat": 0.12,
                            "vitaminD": 30.0,
                            "salt": 0,
                            "zinc": 0,
                            "folic_acid": 0,
                        },
                    },
                    "亜鉛": {
                        "displayName": "亜鉛",
                        "foodName": "サプリ: 亜鉛",
                        "nutrients": {
                            "calories": 1,
                            "protein": 0,
                            "carbohydrates": 0.17,
                            "fat": 0.005,
                            "vitaminD": 0,
                            "salt": 0,
                            "zinc": 14.0,
                            "folic_acid": 0,
                        },
                    },
                }
                selected_sup = st.selectbox("サプリを選択", list(supplements.keys()))
                if st.form_submit_button("サプリを記録する", use_container_width=True):
                    sup_data = supplements[selected_sup]
                    add_record(record_date, "サプリ", sup_data["foodName"], sup_data["nutrients"])
                    st.success(f"{sup_data['displayName']}を記録しました！")

        # ---- 水分 ----
        elif meal_type == "水分補給":
            with st.form(key="water_form", clear_on_submit=True):
                amount_ml = st.number_input("飲んだ量 (ml)", min_value=0, step=50, value=200)
                if st.form_submit_button("水分補給を記録する", use_container_width=True):
                    nutrients = {
                        "calories": 0,
                        "protein": 0,
                        "carbohydrates": 0,
                        "fat": 0,
                        "vitaminD": 0,  # \n<< FIXED: key was vitamin_d >>
                        "salt": 0,
                        "zinc": 0,
                        "folic_acid": 0,
                    }
                    add_record(record_date, "水分補給", f"{amount_ml} ml", nutrients)
                    st.success(f"水分補給 {amount_ml}ml を記録しました！")

        # ---- 食事 ----
        else:
            input_method = st.radio("記録方法", ["テキスト入力", "画像から入力"], horizontal=True)

            # manual
            if input_method == "テキスト入力":
                with st.form(key="text_input_form", clear_on_submit=True):
                    food_name = st.text_input("食事名", placeholder="例）鮭の塩焼き定食 など")
                    cols = st.columns(2)
                    calories = cols[0].number_input("カロリー (kcal)", value=0.0, format="%.1f")
                    protein = cols[1].number_input("たんぱく質 (g)", value=0.0, format="%.1f")
                    carbohydrates = cols[0].number_input("炭水化物 (g)", value=0.0, format="%.1f")
                    fat = cols[1].number_input("脂質 (g)", value=0.0, format="%.1f")
                    vitamin_d = cols[0].number_input("ビタミンD (μg)", value=0.0, format="%.1f")
                    salt = cols[1].number_input("食塩相当量 (g)", value=0.0, format="%.1f")
                    zinc = cols[0].number_input("亜鉛 (mg)", value=0.0, format="%.1f")
                    folic_acid = cols[1].number_input("葉酸 (μg)", value=0.0, format="%.1f")

                    if st.form_submit_button("食事を記録する", use_container_width=True, type="primary"):
                        if food_name:
                            nutrients = {
                                "calories": calories,
                                "protein": protein,
                                "carbohydrates": carbohydrates,
                                "fat": fat,
                                "vitaminD": vitamin_d,
                                "salt": salt,
                                "zinc": zinc,
                                "folic_acid": folic_acid,
                            }
                            add_record(record_date, meal_type, food_name, nutrients)
                            st.success(f"{food_name}を記録しました！")
                        else:
                            st.warning("食事名を入力してください。")

            # image
            elif input_method == "画像から入力":
                uploaded_file = st.file_uploader("食事の画像をアップロード", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    st.image(uploaded_file, caption="アップロードされた画像", use_column_width=True)
                    if st.button("画像を分析する", use_container_width=True):
                        with st.spinner("AIが画像を分析中です..."):
                            analysis_result = analyze_image_with_gemini(uploaded_file.getvalue())
                        if analysis_result:
                            st.session_state.analysis_result = analysis_result
                        else:
                            st.error("分析に失敗しました。テキストで入力してください。")

                if "analysis_result" in st.session_state:
                    st.info("AIの推定値を確認し、必要に応じて修正してから記録してください。")
                    result = st.session_state.analysis_result

                    with st.form(key="image_confirm_form"):
                        food_name = st.text_input("食事名", value=result.get("foodName", ""))
                        nut = result.get("nutrients", {})
                        cols = st.columns(2)
                        # << FIXED: calories is top-level in result >>
                        calories = cols[0].number_input("カロリー (kcal)", value=float(result.get("calories", 0) or 0.0), format="%.1f")
                        protein = cols[1].number_input("たんぱく質 (g)", value=float(nut.get("protein", 0) or 0.0), format="%.1f")
                        carbohydrates = cols[0].number_input("炭水化物 (g)", value=float(nut.get("carbohydrates", 0) or 0.0), format="%.1f")
                        fat = cols[1].number_input("脂質 (g)", value=float(nut.get("fat", 0) or 0.0), format="%.1f")
                        vitamin_d = cols[0].number_input("ビタミンD (μg)", value=float(nut.get("vitaminD", 0) or 0.0), format="%.1f")
                        salt = cols[1].number_input("食塩相当量 (g)", value=float(nut.get("salt", 0) or 0.0), format="%.1f")
                        zinc = cols[0].number_input("亜鉛 (mg)", value=float(nut.get("zinc", 0) or 0.0), format="%.1f")
                        folic_acid = cols[1].number_input("葉酸 (μg)", value=float(nut.get("folic_acid", 0) or 0.0), format="%.1f")

                        if st.form_submit_button("この内容で食事を記録する", use_container_width=True, type="primary"):
                            if food_name:
                                nutrients = {
                                    "calories": calories,
                                    "protein": protein,
                                    "carbohydrates": carbohydrates,
                                    "fat": fat,
                                    "vitaminD": vitamin_d,
                                    "salt": salt,
                                    "zinc": zinc,
                                    "folic_acid": folic_acid,
                                }
                                add_record(record_date, meal_type, food_name, nutrients)
                                st.success(f"{food_name}を記録しました！")
                                del st.session_state.analysis_result
                                st.rerun()
                            else:
                                st.warning("食事名を入力してください。")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- List ----
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("記録一覧")
        all_records_df = get_all_records()
        if all_records_df.empty:
            st.info("まだ記録がありません。")
        else:
            display_df = all_records_df.copy()
            display_df["削除"] = [False] * len(display_df)

            def fmt_meal_chip(meal):
                if meal == "水分補給":
                    return '<span class="chip water">水分補給</span>'
                if meal == "サプリ":
                    return '<span class="chip sup">サプリ</span>'
                return f'<span class="chip meal">{meal}</span>'

            def format_calories(row):
                if row["meal_type"] in ["水分補給", "サプリ"]:
                    return "ー"
                return f"{int(row['calories'])} kcal" if pd.notna(row["calories"]) else "ー"

            display_df["種類"] = display_df["meal_type"]
            display_df["カロリー/量"] = display_df.apply(format_calories, axis=1)

            edited_df = st.data_editor(
                display_df[["date", "種類", "food_name", "カロリー/量", "削除"]],
                column_config={
                    "date": st.column_config.Column("日付"),
                    "種類": st.column_config.Column("種類", help="記録タイプ"),
                    "food_name": st.column_config.Column("内容"),
                    "カロリー/量": st.column_config.Column("カロリー/量"),
                    "削除": st.column_config.CheckboxColumn("削除？"),
                },
                use_container_width=True,
                hide_index=True,
                key="data_editor",
            )

            # map back to original indices
            if edited_df["削除"].any():
                btn_col1, btn_col2 = st.columns([1, 3])
                with btn_col1:
                    if st.container().button("選択した記録を削除", type="primary", use_container_width=True):
                        ids_to_delete = edited_df[edited_df["削除"]].index
                        original_ids = all_records_df.loc[ids_to_delete, "id"]
                        for rid in original_ids:
                            delete_record(int(rid))
                        st.success("選択した記録を削除しました。")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# =============================
# ADVICE
# =============================
elif menu == "相談する":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("AIに相談する")

        all_records_df = get_all_records()
        if all_records_df.empty:
            st.warning("アドバイスには最低1件の記録が必要です。まずは食事を記録してみましょう。")
            st.stop()

        user_profile = (
            """
            - 年齢: 35歳女性
            - 悩み: 痩せにくく太りやすい(特に、お腹まわりと顎)。筋肉量が少なく、下半身中心に筋肉をつけたい。
            - 希望: アンチエイジング
            - 苦手な食べ物: 生のトマト、納豆
            """
        )
        base_prompt = (
            f"あなたは経験豊富な食生活アドバイザーです。以下のクライアント情報と記録に基づき、優しく励ますトーンで、具体的なアドバイスをMarkdown形式でお願いします。\n\n# クライアント情報\n{user_profile}\n\n"
        )
        prompt_to_send = ""

        tab1, tab2, tab3 = st.tabs(["✍️ テキストで相談", "📊 全記録から分析", "🗓️ 期間で分析"])

        with tab1:
            question = st.text_area("相談内容を入力してください", height=150, placeholder="例：最近疲れやすいのですが、食事で改善できますか？")
            if st.button("AIに相談する", key="text_consult"):
                if question:
                    record_history = all_records_df.head(30).to_string(index=False)
                    prompt_to_send = (
                        f"{base_prompt}# 記録（参考）\n{record_history}\n\n# 相談内容\n{question}\n\n上記相談内容に対して、記録を参考にしつつ回答してください。"
                    )
                else:
                    st.warning("相談内容を入力してください。")

        with tab2:
            st.info("今までの全ての記録を総合的に分析し、アドバイスをします。")
            if st.button("アドバイスをもらう", key="all_consult"):
                record_history = all_records_df.to_string(index=False)
                prompt_to_send = f"{base_prompt}# 全ての記録\n{record_history}\n\n上記の記録全体を評価し、総合的なアドバイスをしてください。"

        with tab3:
            today = datetime.date.today()
            one_week_ago = today - datetime.timedelta(days=7)
            cols = st.columns(2)
            start_date = cols[0].date_input("開始日", one_week_ago)
            end_date = cols[1].date_input("終了日", today)
            if st.button("指定期間のアドバイスをもらう", key="period_consult"):
                if start_date > end_date:
                    st.error("終了日は開始日以降に設定してください。")
                else:
                    period_records_df = get_records_by_period(start_date, end_date)
                    if period_records_df.empty:
                        st.warning("指定された期間に記録がありません。")
                    else:
                        record_history = period_records_df.to_string(index=False)
                        prompt_to_send = (
                            f"{base_prompt}# 記録 ({start_date} ~ {end_date})\n{record_history}\n\n上記の指定期間の記録を評価し、アドバイスをしてください。"
                        )

        if prompt_to_send:
            with st.spinner("AIがアドバイスを生成中です..."):
                advice = get_advice_from_gemini(prompt_to_send)
                with st.chat_message("ai", avatar="💬"):
                    st.markdown(advice)

        st.markdown('</div>', unsafe_allow_html=True)
