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
  .stTextInput>div, .stNumberInput>div, .stDateInput>div, .stSelectbox>div {
    background:#FFFFFF !important; border:1px solid var(--border) !important; border-radius:12px !important; box-shadow:none !important; overflow:hidden !important;
  }
  .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox>div>div {
    background:#FFFFFF !important; border:none !important; border-radius:0 !important; box-shadow:none !important; color: var(--text) !important;
  }
  .stTextInput>div:focus-within, .stNumberInput>div:focus-within, .stDateInput>div:focus-within, .stSelectbox>div:focus-within { border-color: var(--primary) !important; box-shadow:none !important; }

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
    """画像を解析し、{ foodName, calories, nutrients{...} } を返す。
    まず gemini-2.5-flash を試し、ダメなら 1.5 系にフォールバック。
    """
    model_candidates = [
        "gemini-2.5-flash",  # マルチモーダル対応（利用可なら最優先）
        "gemini-1.5-flash",  # 旧来の高速・画像対応
        "gemini-1.5-pro",    # 高精度・画像対応
    ]

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

    last_err = None
    for model_name in model_candidates:
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content([prompt, image_pil])
            txt = (resp.text or "").strip().replace("```json", "").replace("```", "")
            data = json.loads(txt)
            # 期待キーの存在を軽くチェック
            if not isinstance(data, dict) or "nutrients" not in data:
                raise ValueError("unexpected response schema")
            return data
        except Exception as e:
            last_err = e
            continue

    st.error(f"画像分析に失敗しました（フォールバックも不可）: {last_err}")
    return None


def get_advice_from_gemini(prompt):
    model = genai.GenerativeModel("gemini-2.5-flash")
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"アドバイス生成中にエラーが発生しました: {e}")
        return "アドバイスの生成に失敗しました。"


# =============================
# Image-chat helpers (portion & Q&A)
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
    """『半分』『3分の1』『1/3』『1.5倍』『30%』などを係数に変換（正規表現なしの簡易版）。"""
    if not text:
        return None
    t = str(text).strip()
    # 半分
    if "半分" in t:
        return 0.5
    # ○分の△
    if "分の" in t:
        parts = t.split("分の")
        if len(parts) == 2:
            try:
                den = float(parts[0].strip())
                num = float(parts[1].strip())
                if den > 0:
                    return num / den
            except Exception:
                pass
    # a/b 形式
    if "/" in t:
        a_b = t.split("/")
        if len(a_b) == 2:
            try:
                a = float(a_b[0].strip()); b = float(a_b[1].strip())
                if b != 0:
                    return a / b
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
            return float(t.replace("%", "").strip()) / 100.0
        except Exception:
            pass
    return None


def _answer_about_meal(food_name: str, nutrients: dict, question: str) -> str:
    """栄養の特色などを簡潔に返す。"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    context = f"""
あなたは管理栄養士です。以下の食品とその推定栄養（1食あたり、食べた量でスケール済み）を踏まえて、ユーザーの質問に簡潔に答えてください。
- 料理名: {food_name}
- 栄養: calories={nutrients.get('calories',0)} kcal, protein={nutrients.get('protein',0)} g, carbs={nutrients.get('carbohydrates',0)} g, fat={nutrients.get('fat',0)} g, vitaminD={nutrients.get('vitaminD',0)} μg, salt={nutrients.get('salt',0)} g, zinc={nutrients.get('zinc',0)} mg
出力ルール:
- 余計な前置きは不要
- 2〜4行の箇条書きで要点のみ
- 不確実な点は推定であることを一言添える
"""
    try:
        resp = model.generate_content([context, "質問: " + question])
        return resp.text
    except Exception as e:
        return f"回答生成に失敗しました: {e}"

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
                        "vitaminD": 0,  # \n
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

                    if st.form_submit_button("食事を記録する", use_container_width=True, type="primary"):
                        if food_name:
                            nutrients = {
                                "calories": calories,
                                "protein": protein,
                                "carbohydrates": carbohydrates,
                                "fat": fat,
                                "vitaminD": vitamin_d,
                                "salt": salt,
                                "zinc": zinc,                            }
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
                    st.info("AIの推定値を確認し、必要に応じて量を調整してから記録してください。")
                    result = st.session_state.analysis_result
                    base_food = result.get("foodName", "")
                    base_nut = result.get("nutrients", {})
                    base_pack = {"calories": float(result.get("calories", 0) or 0.0), **base_nut}

                    if "serve_factor" not in st.session_state:
                        st.session_state.serve_factor = 1.0

                    fc1, fc2 = st.columns([2, 1])
                    with fc2:
                        st.caption("食べた量（係数）")
                        bcols = st.columns(7)
                        if bcols[0].button("1/4"): st.session_state.serve_factor = 0.25
                        if bcols[1].button("1/3"): st.session_state.serve_factor = 1/3
                        if bcols[2].button("1/2"): st.session_state.serve_factor = 0.5
                        if bcols[3].button("2/3"): st.session_state.serve_factor = 2/3
                        if bcols[4].button("1x"):  st.session_state.serve_factor = 1.0
                        if bcols[5].button("1.5x"): st.session_state.serve_factor = 1.5
                        if bcols[6].button("2x"):  st.session_state.serve_factor = 2.0
                        st.session_state.serve_factor = st.slider("係数", 0.1, 2.0, float(st.session_state.serve_factor), 0.05)
                        instr = st.text_input("自然言語で量を指定（例：半分、3分の1、1.5倍、30%）", key="serve_text")
                        if st.button("反映", key="serve_apply") and instr.strip():
                            f = _parse_fraction_jp(instr)
                            if f is not None:
                                st.session_state.serve_factor = float(f)
                                st.success(f"係数 {f} を反映しました。")
                            else:
                                st.warning("係数を解釈できませんでした。")

                    factor = float(st.session_state.serve_factor)
                    scaled = _scale_nutrients(base_pack, factor)

                    with fc1:
                        st.caption("プレビュー（食べた量で自動スケール）")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("カロリー", f"{scaled['calories']:.0f} kcal")
                        m2.metric("たんぱく質", f"{scaled['protein']:.1f} g")
                        m3.metric("炭水化物", f"{scaled['carbohydrates']:.1f} g")
                        m4.metric("脂質", f"{scaled['fat']:.1f} g")

                    st.divider()
                    st.caption("この料理について質問（例：『他に特徴的な栄養素ある？』『塩分は控えめ？』など）")
                    q2 = st.text_input("質問を入力", key="meal_q")
                    if st.button("質問する", key="meal_q_btn"):
                        with st.spinner("回答中..."):
                            ans = _answer_about_meal(base_food or "料理", scaled, q2)
                        st.markdown(ans)

                    with st.form(key="image_confirm_form"):
                        food_name = st.text_input("食事名", value=base_food)
                        cols = st.columns(2)
                        calories = cols[0].number_input("カロリー (kcal)", value=float(scaled.get("calories", 0.0)), format="%.1f")
                        protein = cols[1].number_input("たんぱく質 (g)", value=float(scaled.get("protein", 0.0)), format="%.1f")
                        carbohydrates = cols[0].number_input("炭水化物 (g)", value=float(scaled.get("carbohydrates", 0.0)), format="%.1f")
                        fat = cols[1].number_input("脂質 (g)", value=float(scaled.get("fat", 0.0)), format="%.1f")
                        vitamin_d = cols[0].number_input("ビタミンD (μg)", value=float(scaled.get("vitaminD", 0.0)), format="%.1f")
                        salt = cols[1].number_input("食塩相当量 (g)", value=float(scaled.get("salt", 0.0)), format="%.1f")
                        zinc = cols[0].number_input("亜鉛 (mg)", value=float(scaled.get("zinc", 0.0)), format="%.1f")

                        if st.form_submit_button("この内容で食事を記録する", use_container_width=True, type="primary"):
                            if food_name:
                                nutrients = {
                                    "calories": calories,
                                    "protein": protein,
                                    "carbohydrates": carbohydrates,
                                    "fat": fat,
                                    "vitaminD": vitamin_d,
                                    "salt": salt,
                                    "zinc": zinc,                                }
                                add_record(record_date, meal_type, food_name, nutrients)
                                st.success(f"{food_name}を記録しました！")
                                del st.session_state.analysis_result
                                st.session_state.pop("serve_factor", None)
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

    # ---- Data chat under list ----
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧠 記録データに質問する")
        st.caption("例：『先週のたんぱく質の合計』『今日の朝食』『水分補給の合計』『7/1~7/7のカロリー推移』『今日のたんぱく質の内訳』など")
        q = st.text_input("質問", key="data_chat_q")
        use_llm = st.toggle("自由モード（LLMにSQLを作らせる）", value=True, help="あいまい表現や内訳表現に強い。安全性ガードの上でSELECTのみ実行します。")
        if st.button("送信", key="data_chat_send"):
            if not q.strip():
                st.warning("質問を入力してください。")
            else:
                if use_llm:
                    try:
                        with st.spinner("SQLを作成中..."):
                            plan = llm_to_sql(q)
                        st.caption(f"抽出方針(SQL): {json.dumps(plan, ensure_ascii=False)}")
                        df = _safe_run_sql(plan.get("sql", ""), plan.get("params") or [])
                        if df.empty:
                            st.info("該当データがありません。質問の条件を少し変えてみてください。")
                        else:
                            st.dataframe(df, use_container_width=True)
                    except Exception as e:
                        st.error(f"実行エラー: {e}")
                else:
                    with st.spinner("解析中..."):
                        plan = _nl_to_plan(q)
                        plan = _postprocess_plan(q, plan)
                        out_df, summary = _execute_plan(all_records_df, plan)
                    st.caption(f"抽出方針: {json.dumps(plan, ensure_ascii=False)}")
                    st.write(summary)
                    if not out_df.empty:
                        st.dataframe(out_df, use_container_width=True)
                    else:
                        st.info("該当データがありません。キーワードや期間を変えてみてください。")
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
        prompt_qna = f"""
あなたは経験豊富な食生活アドバイザーです。ユーザーの問いに対してのみ簡潔に回答してください。
出力ルール:
- 挨拶・導入・締めの定型文は不要
- 年齢・性別などの呼称を本文に含めない
- 回答は必要な要点のみ（最大5項目の箇条書き中心）
- 記録に基づく引用は最小限の数値のみ

参考情報（出力に含めない）:
{user_profile}
"""

        prompt_full = f"""
あなたは経験豊富な食生活アドバイザーです。以下のクライアント情報と記録に基づき、**包括的な分析レポート**を日本語で作成してください。
出力はMarkdownで、次の構成を必ず含めてください:
## 概要
## 良かった点
## 改善ポイント
## 栄養・摂取傾向（カロリー/たんぱく質/炭水化物/脂質/ビタミンD/食塩/亜鉛）
## パターン分析（食事回数・時間帯・朝/昼/夜の偏り）
## 具体的アクションプラン（食事例3〜5・買い物リスト）
## 次の7日間の目標
注意: 挨拶や呼称は不要。必要な数値のみ簡潔に引用。

参考情報（出力に含めない）:
{user_profile}
        """
        prompt_to_send = ""

        tab1, tab2, tab3 = st.tabs(["✍️ テキストで相談", "📊 全記録から分析", "🗓️ 期間で分析"])

        with tab1:
            question = st.text_area("相談内容を入力してください", height=150, placeholder="例：最近疲れやすいのですが、食事で改善できますか？")
            if st.button("AIに相談する", key="text_consult"):
                if question:
                    record_history = all_records_df.head(30).to_string(index=False)
                    prompt_to_send = (
                        f"{prompt_qna}# 記録（参考）\n{record_history}\n\n# 相談内容\n{question}\n\n上記相談内容に対して、記録を参考にしつつ回答してください。"
                    )
                else:
                    st.warning("相談内容を入力してください。")

        with tab2:
            st.info("今までの全ての記録を総合的に分析し、アドバイスをします。")
            if st.button("アドバイスをもらう", key="all_consult"):
                record_history = all_records_df.to_string(index=False)
                prompt_to_send = f"""{prompt_full}# 全ての記録
{record_history}

記録データに即した網羅的な分析レポートを出力してください。
"""

        if prompt_to_send:
            with st.spinner("AIがアドバイスを生成中です..."):
                advice = get_advice_from_gemini(prompt_to_send)
                with st.chat_message("ai", avatar="💬"):
                    st.markdown(advice)

        st.markdown('</div>', unsafe_allow_html=True)
