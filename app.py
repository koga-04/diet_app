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
    caret-color: var(--primary) !important;
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

  code {
    background-color: #F3F4F6;
    color: #374151;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
  }
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
            folic_acid REAL,
            is_favorite INTEGER NOT NULL DEFAULT 0
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
    
    c.execute("PRAGMA table_info(meals)")
    columns = [row['name'] for row in c.fetchall()]
    if 'is_favorite' not in columns:
        c.execute("ALTER TABLE meals ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0")

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

def get_favorite_meals():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM meals WHERE is_favorite = 1 ORDER BY food_name ASC", conn)
    conn.close()
    return df

def update_favorite_status(meal_id, is_favorite):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE meals SET is_favorite = ? WHERE id = ?", (1 if is_favorite else 0, meal_id))
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

def get_unique_exercise_names():
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT DISTINCT exercise_name FROM exercises ORDER BY exercise_name", conn)
        return df['exercise_name'].tolist()
    finally:
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
          "totalNutrients": { "calories": 0.0, "protein": 0.0, "carbohydrates": 0.0, "fat": 0.0, "vitaminD": 0.0, "salt": 0.0, "zinc": 0.0, "folic_acid": 0.0 },
          "dishes": [
            {
              "name": "料理名1",
              "rationale": "推定の簡単な根拠（例：鮭の切り身80gを基準）",
              "nutrients": { "calories": 0.0, "protein": 0.0, "carbohydrates": 0.0, "fat": 0.0, "vitaminD": 0.0, "salt": 0.0, "zinc": 0.0, "folic_acid": 0.0 }
            }
          ]
        }
        """
    )
    last_err = None
    for model_name in model_candidates:
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content([prompt, image_pil])
            txt = (resp.text or "").strip().replace("```json", "").replace("```", "")
            data = json.loads(txt)
            if isinstance(data, dict) and "dishes" in data and "totalNutrients" in data:
                return data
        except Exception as e:
            last_err = e
            continue
    st.error(f"画像分析に失敗しました（フォールバックも不可）: {last_err}")
    return None

def analyze_text_with_gemini(description: str):
    """フリーテキストを解析し、料理ごとの内訳と合計値を含むJSONを返す。"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = (
        f"""
        あなたは栄養管理の専門家です。以下の食事内容の記述を分析してください。
        食事に含まれる料理を**すべて**特定し、**料理ごと**に栄養素を推定してください。
        結果は必ず以下のJSON形式で、数値のみを返してください。説明や```json```は不要です。

        食事内容: "{description}"

        {{
          "summary": "食事全体の短い要約（例：飲み会での食事）",
          "totalNutrients": {{ "calories": 0.0, "protein": 0.0, "carbohydrates": 0.0, "fat": 0.0, "vitaminD": 0.0, "salt": 0.0, "zinc": 0.0, "folic_acid": 0.0 }},
          "dishes": [
            {{
              "name": "料理名1",
              "rationale": "推定の簡単な根拠（例：焼き鳥タレ5本を基準）",
              "nutrients": {{ "calories": 0.0, "protein": 0.0, "carbohydrates": 0.0, "fat": 0.0, "vitaminD": 0.0, "salt": 0.0, "zinc": 0.0, "folic_acid": 0.0 }}
            }}
          ]
        }}
        """
    )
    try:
        resp = model.generate_content(prompt)
        txt = (resp.text or "").strip().replace("```json", "").replace("```", "")
        data = json.loads(txt)
        if isinstance(data, dict) and "dishes" in data and "totalNutrients" in data:
            return data
    except Exception as e:
        st.error(f"テキスト分析中にエラーが発生しました: {e}")
    return None

def parse_exercise_from_text(text: str):
    """自由入力の運動記録を解析してJSONを返す"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""
    以下のテキストから運動名と時間（分）を抽出し、JSONで返してください。
    時間は必ず整数にしてください。説明や```json```は不要です。
    テキスト: "{text}"
    
    {{
      "name": "運動名",
      "duration": 60
    }}
    """
    try:
        resp = model.generate_content(prompt)
        txt = (resp.text or "").strip().replace("```json", "").replace("```", "")
        data = json.loads(txt)
        if isinstance(data, dict) and "name" in data and "duration" in data:
            return data
    except Exception:
        return None

def correct_exercise_from_text(original_data: dict, correction_text: str):
    """AIが提案した運動記録をユーザーの指示で修正する"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""
    以下の現在の運動記録を、ユーザーの修正指示に従って修正し、新しいJSONを返してください。
    時間は必ず整数にしてください。説明や```json```は不要です。
    
    現在の記録: {json.dumps(original_data, ensure_ascii=False)}
    修正指示: "{correction_text}"
    
    {{
      "name": "修正後の運動名",
      "duration": 90
    }}
    """
    try:
        resp = model.generate_content(prompt)
        txt = (resp.text or "").strip().replace("```json", "").replace("```", "")
        data = json.loads(txt)
        if isinstance(data, dict) and "name" in data and "duration" in data:
            return data
    except Exception:
        return None

# ★改修要望1: 栄養素の対話型修正用ヘルパー
def refine_nutrition_with_ai(chat_history: list, current_data: dict):
    """栄養素の対話履歴と現在のデータから、修正案を生成する"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""
あなたは栄養管理の専門家です。以下の対話履歴と現在の栄養素データを基に、ユーザーの最新の修正依頼に回答してください。
- ユーザーの指示が妥当であれば、栄養素データを修正した新しいJSONを返します。
- ユーザーの指示が不正確、またはAIの当初の推定が妥当だと思われる場合は、その理由を説明し、栄養素データは修正せずに返します。
- 回答は必ず以下のJSON形式で、説明や```json```は不要です。

現在の栄養素データ:
{json.dumps(current_data, ensure_ascii=False, indent=2)}

対話履歴:
{json.dumps(chat_history, ensure_ascii=False, indent=2)}

{{
  "response_text": "ユーザーへの返答メッセージ（例：ご指摘ありがとうございます。たんぱく質を修正しました。）",
  "updated_data": {{
    "summary": "食事全体の短い要約",
    "dishes": [
      {{
        "name": "料理名1",
        "rationale": "推定の簡単な根拠",
        "nutrients": {{ "calories": 0.0, "protein": 0.0, "carbohydrates": 0.0, "fat": 0.0, "vitaminD": 0.0, "salt": 0.0, "zinc": 0.0, "folic_acid": 0.0 }}
      }}
    ]
  }}
}}
"""
    try:
        resp = model.generate_content(prompt)
        txt = (resp.text or "").strip().replace("```json", "").replace("```", "")
        data = json.loads(txt)
        if isinstance(data, dict) and "response_text" in data and "updated_data" in data:
            return data
    except Exception as e:
        st.error(f"AIによる修正案の作成中にエラーが発生しました: {e}")
    return None


# =============================
# Image-chat helpers (portion / supplement refine)
# =============================

def _scale_nutrients(nut: dict, factor: float) -> dict:
    keys = ["calories", "protein", "carbohydrates", "fat", "vitaminD", "salt", "zinc", "folic_acid"]
    out = {}
    for k in keys:
        v = (nut or {}).get(k, 0)
        try:
            out[k] = round(float(v) * float(factor), 2)
        except Exception:
            out[k] = 0.0
    return out


def _parse_fraction_jp(text: str):
    """『半分』『3分の1』『1/3』『1.5倍』『30%』などを係数に変換。"""
    if not text:
        return None
    t = str(text).strip()
    if "半分" in t:
        return 0.5
    # 3分の1 など
    if "分の" in t:
        try:
            den, num = t.split("分の")
            den = float(den.strip()); num = float(num.strip())
            if den > 0:
                return num/den
        except Exception:
            pass
    # 1/3 など
    if "/" in t:
        try:
            a, b = t.split("/")
            a = float(a.strip()); b = float(b.strip())
            if b != 0:
                return a/b
        except Exception:
            pass
    # 倍
    if "倍" in t:
        try:
            return float(t.replace("倍", "").strip())
        except Exception:
            pass
    # %
    if "%" in t:
        try:
            return float(t.replace("%", "").strip())/100.0
        except Exception:
            pass
    return None


def _refine_by_note(food_name: str, nutrients: dict, note: str):
    """補足説明を反映して、料理名/栄養値の上書き案を返す。失敗時は None。"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    base_json = json.dumps({"foodName": food_name, "nutrients": nutrients}, ensure_ascii=False)
    schema = """
以下のJSONのみを返してください。説明不要。コードフェンス不要。
{
  "foodName": "料理名（変更不要ならそのまま）",
  "nutrients": {
    "calories": 0.0, "protein": 0.0, "carbohydrates": 0.0, "fat": 0.0,
    "vitaminD": 0.0, "salt": 0.0, "zinc": 0.0, "folic_acid": 0.0
  },
  "note": "補正内容の要約（20字以内）"
}
"""
    prompt_parts = [
        "あなたは管理栄養士です。ユーザーの補足説明を反映して、現在の推定値を必要に応じて上書きしてください。単位: calories(kcal), protein/carbohydrates/fat(g), vitaminD(μg), salt(g), zinc(mg), folic_acid(μg)。可能な範囲で妥当な値に丸めてください（1〜2桁）。",
        "現在の推定: " + base_json + "\n補足: " + (note or ""),
        schema,
    ]
    try:
        resp = model.generate_content(prompt_parts)
        txt = (resp.text or "").strip().replace("```json", "").replace("```", "")
        data = json.loads(txt)
        if isinstance(data, dict) and data.get("nutrients"):
            return data
    except Exception:
        return None
    return None

# =============================
# Utils: NL → DataFrame query planner
# =============================

def _nl_to_plan(question: str) -> dict:
    """Geminiで自然文→クエリJSONに変換。失敗時は空dictを返す。"""
    schema = """
以下のJSONだけを返してください。説明不要。```は付けない。
{
  "action": "aggregate|filter|trend|top_n",
  "date_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"} | null,
  "meal_types": ["朝食","昼食","夕食","間食","サプリ","水分補給"] | [],
  "name_contains": "任意のキーワード" | null,
  "metrics": ["calories","protein","carbohydrates","fat","vitamin_d","salt","zinc","folic_acid"],
  "agg": "sum|avg|count" | null,
  "group_by": "date|meal_type|food_name" | null,
  "top_n": 整数 | null,
  "sort_by": 指標名 | null,
  "sort_order": "desc|asc" | null
}
"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""ユーザーの質問:
{question}

上の質問を、指定スキーマのJSONに変換してください。
{schema}
"""
        resp = model.generate_content(prompt)
        txt = resp.text.strip().replace("```json", "").replace("```", "")
        return json.loads(txt)
    except Exception:
        return {}


def _postprocess_plan(question: str, plan: dict) -> dict:
    """質問文から相対日付や内訳リクエストを解釈し、計画を補正する。"""
    pr = (plan or {}).copy()
    q = (question or "")

    # --- 相対日付の補正 ---
    today = datetime.date.today()
    if any(k in q for k in ["今日", "本日", "today"]):
        ds = today.strftime("%Y-%m-%d")
        pr["date_range"] = {"start": ds, "end": ds}
    if any(k in q for k in ["昨日", "きのう", "yesterday"]):
        d = today - datetime.timedelta(days=1)
        ds = d.strftime("%Y-%m-%d")
        pr["date_range"] = {"start": ds, "end": ds}

    # --- "どの/内訳/どれくらい/食材" → 食品別の内訳を求めていると解釈 ---
    if any(k in q for k in ["どの", "内訳", "どれくらい", "どれぐらい", "食材"]):
        pr["action"] = "aggregate"
        pr["group_by"] = "food_name"
        pr.setdefault("agg", "sum")
        pr.setdefault("metrics", ["protein"])  # 明示されてなければタンパク質

    return pr


def _execute_plan(df: pd.DataFrame, plan: dict):
    """計画に従ってDataFrameを抽出/集計し、(結果DF, サマリ文字列)を返す。"""
    if df.empty:
        return pd.DataFrame(), "記録がありません。"

    work = df.copy()
    # 型整形
    work["date"] = pd.to_datetime(work["date"], errors="coerce")
    num_cols = ["calories", "protein", "carbohydrates", "fat", "vitamin_d", "salt", "zinc", "folic_acid"]
    for c in num_cols:
        if c in work.columns:
            work[c] = pd.to_numeric(work[c], errors="coerce")

    # フィルタ
    pr = plan or {}
    dr = pr.get("date_range") or {}
    if dr.get("start"):
        start = pd.to_datetime(dr.get("start"), errors="coerce")
        work = work[work["date"] >= start]
    if dr.get("end"):
        end = pd.to_datetime(dr.get("end"), errors="coerce")
        work = work[work["date"] <= end]

    mts = pr.get("meal_types") or []
    if mts:
        work = work[work["meal_type"].isin(mts)]

    kw = pr.get("name_contains")
    if kw:
        work = work[work["food_name"].str.contains(str(kw), case=False, na=False)]

    action = (pr.get("action") or "filter").lower()
    metrics = pr.get("metrics") or ["calories"]

    if work.empty:
        return pd.DataFrame(), "条件に一致する記録がありません。"

    if action == "filter":
        cols = ["date", "meal_type", "food_name"] + [c for c in metrics if c in work.columns]
        out = work[cols].sort_values("date", ascending=False)
        return out, f"{len(out)}件ヒット"

    if action in ("aggregate", "trend"):
        gb = pr.get("group_by")
        agg = pr.get("agg") or "sum"
        agg_map = {m: agg for m in metrics if m in work.columns}
        if gb in ("date", "meal_type", "food_name"):
            out = work.groupby(gb).agg(agg_map).reset_index()
            if gb == "date":
                out = out.sort_values("date")
            return out, f"{gb}別の{agg}"
        else:
            out = work[metrics].agg(agg)
            out = out.to_frame(name=agg).reset_index().rename(columns={"index": "metric"})
            return out, f"全体の{agg}"

    if action == "top_n":
        sort_by = pr.get("sort_by") or metrics[0]
        order = (pr.get("sort_order") or "desc").lower() == "desc"
        n = int(pr.get("top_n") or 5)
        cols = ["date", "meal_type", "food_name", sort_by]
        cols = [c for c in cols if c in work.columns]
        out = work.sort_values(sort_by, ascending=not order)[cols].head(n)
        return out, f"{sort_by}の上位{n}件"

    # default
    out = work[["date", "meal_type", "food_name"] + [c for c in metrics if c in work.columns]].sort_values("date", ascending=False)
    return out, f"{len(out)}件ヒット"

# =============================
# LLM-to-SQL (自由モード)
# =============================

ALLOWED_COLS = {"id","date","meal_type","food_name","calories","protein","carbohydrates","fat","vitamin_d","salt","zinc","folic_acid"}


def llm_to_sql(question: str) -> dict:
    """自然文から安全なSQL(JSON)を生成する。Gemini 2.5 Flash を使用。"""
    today_jst = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).date().strftime("%Y-%m-%d")
    model = genai.GenerativeModel("gemini-2.5-flash")
    schema_tmpl = """
あなたはSQLite用のSQLアシスタントです。次の制約を必ず守ってください:
- SELECT文のみ。INSERT/UPDATE/DELETE/ALTER/DROP は禁止（セミコロン含む）。
- FROM は必ず meals のみ。
- 相対日付（今日/昨日/先週など）は日本時間(__TODAY__)基準で具体的なYYYY-MM-DDに解決。
- 可能なら ? プレースホルダと params を使う。
- 結果行は最大500行（LIMIT を付ける）。

テーブル: meals(
  id INTEGER, date TEXT(YYYY-MM-DD), meal_type TEXT, food_name TEXT,
  calories REAL, protein REAL, carbohydrates REAL, fat REAL, vitamin_d REAL, salt REAL, zinc REAL, folic_acid REAL
)

JSONのみを返してください（説明不要・コードフェンス不要）:
{
  "sql": "SELECT ... FROM meals WHERE ... LIMIT 500",
  "params": [],
  "intent": "日本語での簡単な説明"
}
"""
    schema = schema_tmpl.replace("__TODAY__", today_jst)
    prompt = f"""ユーザー質問: {question}

上記の制約でSQL JSONを返してください。
{schema}
"""
    resp = model.generate_content(prompt)
    txt = (resp.text or "").strip().replace("```json", "").replace("```", "")
    try:
        return json.loads(txt)
    except Exception:
        return {"sql": "", "params": [], "intent": "parse_error"}


def _safe_run_sql(sql: str, params: list):
    """最低限のサニタイズを行ってからSQLを実行してDataFrameを返す。"""
    if not sql:
        raise ValueError("SQLが空です")
    s = sql.strip().lower()
    if not s.startswith("select"):
        raise ValueError("SELECTのみ許可")
    for bad in ["insert", "update", "delete", "drop", "alter", "attach", "pragma", ";"]:
        if bad in s:
            raise ValueError("禁止キーワードを検出しました")
    if " from " not in s or "meals" not in s:
        raise ValueError("FROM は meals のみ許可")
    if " limit " not in s:
        sql = sql.strip() + " LIMIT 500"
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(sql, conn, params=params or [])
    finally:
        conn.close()
    return df

# =============================
# App
# =============================
init_db()

# --- Sidebar ---
with st.sidebar:
    st.markdown("### メニュー")
    menu = st.radio("選択", ["食事記録", "運動記録", "相談する"], index=0, label_visibility="collapsed")

# --- Dynamic Header ---
if menu == "食事記録":
    title = "🍽️ 食事記録"
    subtitle = "日々の食事やサプリ・水分補給をシンプルに記録しましょう。"
elif menu == "運動記録":
    title = "💪 運動記録"
    subtitle = "日々の運動を記録して、活動の習慣を可視化しましょう。"
else: # 相談する
    title = "💬 AIに相談する"
    subtitle = "食事と運動の記録を基に、AIがパーソナルなアドバイスをします。"

st.markdown(
    f"""
    <div class="hero">
      <div class="hero-title">{title}</div>
      <div class="hero-sub">{subtitle}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Quick glance (today) ---
if menu != "相談する": # 相談ページでは非表示
    all_df = get_all_records()

    def _sum_today(df: pd.DataFrame):
        if df.empty:
            return {"cal": 0, "p": 0, "c": 0, "f": 0}
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        t = df[df["date"] == today_str]
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
if menu == "食事記録":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("食事の記録")
        
        left, right = st.columns([1, 1])
        with left:
            meal_type = st.selectbox(
                "記録の種類",
                ["朝食", "昼食", "夕食", "間食", "プロテイン", "サプリ", "水分補給"],
                index=0,
            )
        with right:
            record_date = st.date_input("日付", datetime.date.today())
        
        if meal_type == "プロテイン":
            with st.form(key="protein_form", clear_on_submit=True):
                protein_amount = st.number_input("たんぱく質の量 (g)", min_value=0.0, step=0.1, value=20.0, format="%.1f")
                if st.form_submit_button("プロテインを記録する", use_container_width=True):
                    nutrients = { "protein": protein_amount, "calories": protein_amount * 4 } 
                    add_record(record_date, "プロテイン", f"プロテイン {protein_amount}g", nutrients)
                    st.success(f"プロテイン {protein_amount}g を記録しました！")

        elif meal_type == "サプリ":
            with st.form(key="supplement_form", clear_on_submit=True):
                supplements = {
                    "マルチビタミン": { "displayName": "マルチビタミン", "foodName": "サプリ: スーパーマルチビタミン&ミネラル", "nutrients": { "calories": 5, "protein": 0.02, "carbohydrates": 0.6, "fat": 0.05, "vitaminD": 10.0, "salt": 0, "zinc": 6.0, "folic_acid": 240, }, },
                    "葉酸": { "displayName": "葉酸", "foodName": "サプリ: 葉酸", "nutrients": { "calories": 1, "protein": 0, "carbohydrates": 0.23, "fat": 0.004, "vitaminD": 0, "salt": 0, "zinc": 0, "folic_acid": 480, }, },
                    "ビタミンD": { "displayName": "ビタミンD", "foodName": "サプリ: ビタミンD", "nutrients": { "calories": 1, "protein": 0, "carbohydrates": 0, "fat": 0.12, "vitaminD": 30.0, "salt": 0, "zinc": 0, "folic_acid": 0, }, },
                    "亜鉛": { "displayName": "亜鉛", "foodName": "サプリ: 亜鉛", "nutrients": { "calories": 1, "protein": 0, "carbohydrates": 0.17, "fat": 0.005, "vitaminD": 0, "salt": 0, "zinc": 14.0, "folic_acid": 0, }, },
                }
                selected_sup = st.selectbox("サプリを選択", list(supplements.keys()))
                if st.form_submit_button("サプリを記録する", use_container_width=True):
                    sup_data = supplements[selected_sup]
                    add_record(record_date, "サプリ", sup_data["foodName"], sup_data["nutrients"])
                    st.success(f"{sup_data['displayName']}を記録しました！")

        elif meal_type == "水分補給":
            with st.form(key="water_form", clear_on_submit=True):
                amount_ml = st.number_input("飲んだ量 (ml)", min_value=0, step=50, value=200)
                if st.form_submit_button("水分補給を記録する", use_container_width=True):
                    nutrients = { "calories": 0, "protein": 0, "carbohydrates": 0, "fat": 0, "vitaminD": 0, "salt": 0, "zinc": 0, "folic_acid": 0, }
                    add_record(record_date, "水分補給", f"{amount_ml} ml", nutrients)
                    st.success(f"水分補給 {amount_ml}ml を記録しました！")

        else: 
            input_method = st.radio("記録方法", ["栄養素手入力", "フリー記述入力", "画像から入力"], horizontal=True)

            if input_method == "栄養素手入力":
                favorite_meals_df = get_favorite_meals()
                favorite_options = {"新規入力": None}
                for index, row in favorite_meals_df.iterrows():
                    favorite_options[row['food_name']] = row.to_dict()

                selected_favorite_key = st.selectbox(
                    "お気に入りから選択",
                    options=list(favorite_options.keys()),
                    index=0
                )
                
                selected_favorite_data = favorite_options.get(selected_favorite_key)

                with st.form(key="text_input_form", clear_on_submit=True):
                    food_name = st.text_input("食事名", value=selected_favorite_data['food_name'] if selected_favorite_data else "", placeholder="例）鮭の塩焼き定食 など")
                    cols = st.columns(2)
                    calories = cols[0].number_input("カロリー (kcal)", value=float(selected_favorite_data['calories'] or 0.0) if selected_favorite_data else 0.0, format="%.1f")
                    protein = cols[1].number_input("たんぱく質 (g)", value=float(selected_favorite_data['protein'] or 0.0) if selected_favorite_data else 0.0, format="%.1f")
                    carbohydrates = cols[0].number_input("炭水化物 (g)", value=float(selected_favorite_data['carbohydrates'] or 0.0) if selected_favorite_data else 0.0, format="%.1f")
                    fat = cols[1].number_input("脂質 (g)", value=float(selected_favorite_data['fat'] or 0.0) if selected_favorite_data else 0.0, format="%.1f")
                    vitamin_d = cols[0].number_input("ビタミンD (μg)", value=float(selected_favorite_data['vitamin_d'] or 0.0) if selected_favorite_data else 0.0, format="%.1f")
                    salt = cols[1].number_input("食塩相当量 (g)", value=float(selected_favorite_data['salt'] or 0.0) if selected_favorite_data else 0.0, format="%.1f")
                    zinc = cols[0].number_input("亜鉛 (mg)", value=float(selected_favorite_data['zinc'] or 0.0) if selected_favorite_data else 0.0, format="%.1f")

                    if st.form_submit_button("食事を記録する", use_container_width=True, type="primary"):
                        if food_name:
                            nutrients = { "calories": calories, "protein": protein, "carbohydrates": carbohydrates, "fat": fat, "vitaminD": vitamin_d, "salt": salt, "zinc": zinc, }
                            add_record(record_date, meal_type, food_name, nutrients)
                            st.success(f"{food_name}を記録しました！")
                        else:
                            st.warning("食事名を入力してください。")
            
            elif input_method == "フリー記述入力":
                description = st.text_area("食事の内容を自由に入力してください", placeholder="例：飲み会で、焼き鳥を5本（タレ）、ビールを2杯、枝豆を食べた")
                if st.button("AIで栄養素を推定する", use_container_width=True):
                    if description.strip():
                        with st.spinner("AIが記述内容を分析中です..."):
                            analysis_result = analyze_text_with_gemini(description)
                        if analysis_result:
                            st.session_state.analysis_result = analysis_result
                            # ★改修要望1: 対話履歴を初期化
                            st.session_state.nutrition_chat_history = []
                        else:
                            st.error("分析に失敗しました。もう少し具体的に記述してください。")
                    else:
                        st.warning("食事の内容を入力してください。")

            elif input_method == "画像から入力":
                uploaded_file = st.file_uploader("食事の画像をアップロード", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    st.image(uploaded_file, caption="アップロードされた画像", use_column_width=True)
                    if st.button("画像を分析する", use_container_width=True):
                        with st.spinner("AIが画像を分析中です..."):
                            analysis_result = analyze_image_with_gemini(uploaded_file.getvalue())
                        if analysis_result:
                            st.session_state.analysis_result = analysis_result
                            # ★改修要望1: 対話履歴を初期化
                            st.session_state.nutrition_chat_history = []
                        else:
                            st.error("分析に失敗しました。テキストで入力してください。")
            
            if input_method in ["フリー記述入力", "画像から入力"] and "analysis_result" in st.session_state:
                st.info("AIの推定結果です。内容を確認し、必要に応じて修正してください。")
                result = st.session_state.analysis_result
                
                # ★改修要望1: 対話履歴の表示
                if "nutrition_chat_history" in st.session_state:
                    for msg in st.session_state.nutrition_chat_history:
                        with st.chat_message(msg["role"]):
                            st.markdown(msg["content"])
                
                st.markdown("##### AIによる現在の推定内訳")
                dishes_df = pd.DataFrame(result.get("dishes", []))
                if not dishes_df.empty:
                    nutrients_df = pd.json_normalize(dishes_df['nutrients'])
                    display_dishes = pd.concat([dishes_df[['name', 'rationale']], nutrients_df], axis=1)
                    st.dataframe(display_dishes.rename(columns={
                        "name": "料理名", "rationale": "推定根拠", "calories": "cal", "protein": "P",
                        "carbohydrates": "C", "fat": "F", "vitaminD": "VitD", "salt": "塩分", "zinc": "亜鉛"
                    }), use_container_width=True)
                
                st.divider()
                st.markdown("##### この内容で登録しますか？")
                
                col1, col2, col_spacer = st.columns([1,2,2])
                if col1.button("はい、この内容で記録する", type="primary"):
                    dishes = result.get("dishes", [])
                    if not dishes:
                        st.warning("記録する料理がありません。")
                    else:
                        recorded_dishes = []
                        with st.spinner("記録中..."):
                            for dish in dishes:
                                add_record(record_date, meal_type, dish.get("name"), dish.get("nutrients", {}))
                                recorded_dishes.append(dish.get("name"))
                        st.success(f"{len(recorded_dishes)}件の料理を記録しました: {', '.join(recorded_dishes)}")
                        
                        for key in list(st.session_state.keys()):
                            if key.startswith('analysis_') or key.startswith('nutrition_'):
                                del st.session_state[key]
                        st.rerun()

                if col2.button("修正を希望する"):
                    st.session_state.show_nutrition_correction = True

                if st.session_state.get("show_nutrition_correction"):
                    correction_text = st.text_area("修正点を自由に入力してください", placeholder="例：焼き鳥は5本じゃなくて3本です。あと、ビールは飲んでいません。", key="nut_correction_text")
                    if st.button("AIに修正を依頼する"):
                        if correction_text.strip():
                            st.session_state.nutrition_chat_history.append({"role": "user", "content": correction_text})
                            with st.spinner("AIが修正案を作成中です..."):
                                new_proposal = refine_nutrition_with_ai(st.session_state.nutrition_chat_history, result)
                            
                            if new_proposal:
                                st.session_state.nutrition_chat_history.append({"role": "assistant", "content": new_proposal["response_text"]})
                                st.session_state.analysis_result = new_proposal["updated_data"]
                                st.session_state.show_nutrition_correction = False
                                st.rerun()
                            else:
                                st.error("修正案の作成に失敗しました。")
                        else:
                            st.warning("修正内容を入力してください。")

        st.markdown('</div>', unsafe_allow_html=True)

    # ---- List ----
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("食事記録一覧")
        all_records_df = get_all_records()
        if all_records_df.empty:
            st.info("まだ記録がありません。")
        else:
            all_records_df['is_favorite'] = all_records_df['is_favorite'].astype(bool)
            
            edited_df = st.data_editor(
                all_records_df,
                column_config={
                    "id": None,
                    "date": "日付",
                    "meal_type": "種類",
                    "food_name": "内容",
                    "calories": st.column_config.NumberColumn("カロリー", format="%d kcal"),
                    "protein": st.column_config.NumberColumn("P(g)", format="%.1f"),
                    "carbohydrates": st.column_config.NumberColumn("C(g)", format="%.1f"),
                    "fat": st.column_config.NumberColumn("F(g)", format="%.1f"),
                    "vitamin_d": None, "salt": None, "zinc": None, "folic_acid": None,
                    "is_favorite": st.column_config.CheckboxColumn("プルダウン登録", width="small"),
                },
                use_container_width=True,
                hide_index=True,
                key="data_editor",
            )
            
            if not edited_df.equals(all_records_df):
                diff = edited_df[edited_df['is_favorite'] != all_records_df['is_favorite']]
                for index, row in diff.iterrows():
                    update_favorite_status(row['id'], row['is_favorite'])
                st.success("お気に入り設定を更新しました。")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "運動記録":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("運動の記録")
        st.caption("日々の運動を記録して、活動量を管理しましょう。")
        
        default_exercises = ["ヨガ", "エアロビクス", "Group Centergy"]
        try:
            past_exercises = get_unique_exercise_names()
            exercise_options = sorted(list(set(default_exercises + past_exercises)))
        except Exception:
            exercise_options = default_exercises
        exercise_options.append("その他（自由入力）")

        selected_exercise = st.selectbox(
            "運動メニュー",
            exercise_options
        )

        if selected_exercise != "その他（自由入力）":
            with st.form(key="exercise_form_select", clear_on_submit=True):
                duration = st.number_input("運動時間（分）", min_value=0, value=60, step=5)
                record_date_ex = st.date_input("日付", datetime.date.today())
                if st.form_submit_button("運動を記録する", use_container_width=True, type="primary"):
                    if duration > 0:
                        add_exercise_record(record_date_ex, selected_exercise, duration)
                        st.success(f"{selected_exercise} ({duration}分) を記録しました！")
                    else:
                        st.warning("運動時間を入力してください。")
        else:
            st.info("実施した運動内容と時間を自由に入力してください。AIが内容を整理します。")
            free_text_exercise = st.text_area("運動内容と時間", placeholder="例：ジムで筋トレを60分、そのあとランニングを30分")
            record_date_ex = st.date_input("日付", datetime.date.today())
            
            if st.button("内容を整理して確認", use_container_width=True):
                if free_text_exercise.strip():
                    with st.spinner("AIが内容を解析中..."):
                        parsed_exercise = parse_exercise_from_text(free_text_exercise)
                    if parsed_exercise:
                        st.session_state.exercise_proposal = parsed_exercise
                        st.session_state.record_date_ex = record_date_ex # 日付を保存
                    else:
                        st.error("内容を解析できませんでした。もう少し具体的に記述してください。")
                else:
                    st.warning("運動内容を入力してください。")

            if "exercise_proposal" in st.session_state:
                proposal = st.session_state.exercise_proposal
                st.write("---")
                st.write(f"AIは以下の内容と解釈しました。この内容で記録しますか？")
                st.markdown(f"**運動内容:** `{proposal['name']}`")
                st.markdown(f"**運動時間:** `{proposal['duration']}` 分")

                col1, col2, col_spacer = st.columns([1,1,2])
                if col1.button("はい、この内容で記録する", type="primary"):
                    record_date_to_save = st.session_state.get('record_date_ex', datetime.date.today())
                    add_exercise_record(record_date_to_save, proposal['name'], proposal['duration'])
                    st.success(f"{proposal['name']} ({proposal['duration']}分) を記録しました！")
                    # セッションステートをクリーンアップ
                    for key in list(st.session_state.keys()):
                        if key.startswith('exercise_') or key == 'record_date_ex':
                            del st.session_state[key]
                    st.rerun()

                if col2.button("修正する"):
                    st.session_state.show_exercise_correction = True
                
                if st.session_state.get("show_exercise_correction"):
                    correction_text = st.text_area("修正点を入力してください", placeholder="時間を90分に変更して", key="ex_correction_text")
                    if st.button("修正を反映"):
                        with st.spinner("AIが修正案を作成中..."):
                            new_proposal = correct_exercise_from_text(proposal, correction_text)
                        if new_proposal:
                            st.session_state.exercise_proposal = new_proposal
                            st.session_state.show_exercise_correction = False
                            st.rerun()
                        else:
                            st.error("修正内容を解析できませんでした。")

        st.markdown('</div>', unsafe_allow_html=True)
        
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("運動記録一覧")
        all_exercise_df = get_all_exercise_records()
        if all_exercise_df.empty:
            st.info("まだ運動の記録がありません。")
        else:
            display_ex_df = all_exercise_df.copy()
            display_ex_df["削除"] = [False] * len(display_ex_df)
            
            edited_ex_df = st.data_editor(
                display_ex_df[["date", "exercise_name", "duration_minutes", "削除"]],
                column_config={
                    "date": "日付",
                    "exercise_name": "運動内容",
                    "duration_minutes": "時間(分)",
                    "削除": st.column_config.CheckboxColumn("削除？"),
                },
                use_container_width=True,
                hide_index=True,
                key="ex_data_editor",
            )

            if edited_ex_df["削除"].any():
                btn_col1, btn_col2 = st.columns([1, 3])
                with btn_col1:
                    if st.container().button("選択した記録を削除", type="primary", use_container_width=True, key="delete_ex"):
                        ids_to_delete = edited_ex_df[edited_ex_df["削除"]].index
                        original_ids = all_exercise_df.loc[ids_to_delete, "id"]
                        for rid in original_ids:
                            delete_exercise_record(int(rid))
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
        all_exercise_df = get_all_exercise_records()

        if all_records_df.empty and all_exercise_df.empty:
            st.warning("アドバイスには最低1件の記録が必要です。まずは食事か運動を記録してみましょう。")
            st.stop()

        user_profile = (
            """
            - 年齢: 35歳女性
            - 身長: 153cm
            - 体重: 50kg
            - 悩み: 痩せにくく太りやすい(特に、お腹まわりと顎)。筋肉量が少なく、下半身中心に筋肉をつけたい。
            - 希望: アンチエイジング
            - 苦手な食べ物: 生のトマト、納豆
            - 運動補足: Group Centergyはヨガやピラティスをベースにした下半身の筋力強化に効果的なプログラム。
            """
        )
        prompt_qna = f"""
あなたは経験豊富な食生活と運動のパーソナルアドバイザーです。ユーザーの問いに対してのみ簡潔に回答してください。
出力ルール:
- 挨拶・導入・締めの定型文は不要
- 年齢・性別などの呼称を本文に含めない
- 回答は必要な要点のみ（最大5項目の箇条書き中心）
- 記録に基づく引用は最小限の数値のみ

参考情報（出力に含めない）:
{user_profile}
"""
        prompt_full = f"""
あなたは経験豊富な食生活と運動のパーソナルアドバイザーです。以下のユーザー情報と記録に基づき、**包括的な分析レポート**を日本語で作成してください。
出力はMarkdownで、次の構成を必ず含めてください:
## 概要
## 良かった点（食事・運動）
## 改善ポイント（食事・運動）
## 栄養・摂取傾向
## 運動の傾向（頻度・時間）
## 具体的アクションプラン（食事と運動の組み合わせ提案）
## 次の7日間の目標
注意: 挨拶や呼称は不要。必要な数値のみ簡潔に引用。

参考情報（出力に含めない）:
{user_profile}
"""

        prompt_to_send = ""

        tab1, tab2, tab3 = st.tabs(["✍️ テキストで相談", "📊 全記録から分析", "🗓️ 期間で分析"])

        with tab1:
            question = st.text_area("相談内容を入力してください", height=150, placeholder="例：最近疲れやすいのですが、食事や運動で改善できますか？")
            if st.button("AIに相談する", key="text_consult"):
                if question:
                    record_history = all_records_df.head(30).to_string(index=False)
                    exercise_history = all_exercise_df.head(15).to_string(index=False)
                    prompt_to_send = f"""{prompt_qna}# 食事記録（参考）
{record_history}
# 運動記録（参考）
{exercise_history}

# 相談内容
{question}

上記相談内容に対して、記録を参考にしつつ回答してください。
"""
                else:
                    st.warning("相談内容を入力してください。")

        with tab2:
            st.info("今までの全ての記録を総合的に分析し、アドバイスをします。")
            if st.button("アドバイスをもらう", key="all_consult"):
                record_history = all_records_df.to_string(index=False)
                exercise_history = all_exercise_df.to_string(index=False)
                prompt_to_send = f"""{prompt_full}# 全ての食事記録
{record_history}
# 全ての運動記録
{exercise_history}

記録データに即した網羅的な分析レポートを出力してください。
"""

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
                    period_exercise_df = get_all_exercise_records() # Simple filter for now
                    period_exercise_df['date'] = pd.to_datetime(period_exercise_df['date'])
                    period_exercise_df = period_exercise_df[(period_exercise_df['date'] >= pd.to_datetime(start_date)) & (period_exercise_df['date'] <= pd.to_datetime(end_date))]
                    
                    if period_records_df.empty and period_exercise_df.empty:
                        st.warning("指定された期間に記録がありません。")
                    else:
                        record_history = period_records_df.to_string(index=False)
                        exercise_history = period_exercise_df.to_string(index=False)
                        prompt_to_send = f"""{prompt_full}# 食事記録 ({start_date} ~ {end_date})
{record_history}
# 運動記録 ({start_date} ~ {end_date})
{exercise_history}

上記の指定期間の記録を評価し、アドバイスをしてください。
"""

        if prompt_to_send:
            with st.spinner("AIがアドバイスを生成中です..."):
                advice = get_advice_from_gemini(prompt_to_send)
                with st.chat_message("ai", avatar="💬"):
                    st.markdown(advice)
        st.markdown('</div>', unsafe_allow_html=True)
