import streamlit as st
import sqlite3
import pandas as pd
import datetime
import google.generativeai as genai
import json
from PIL import Image
import io

# --- ページ設定 ---
st.set_page_config(
    page_title="食生活アドバイザー",
    page_icon="💧",
    layout="wide"
)

# --- Google Gemini APIキーの設定 ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except (KeyError, FileNotFoundError):
    st.error("⚠️ Google APIキーが設定されていません。")
    st.info("デプロイガイドに従って、Streamlitのシークet管理で `GOOGLE_API_KEY` を設定してください。")
    st.stop()


# --- データベース設定 (SQLite) ---
DB_FILE = "diet_records.db"

def get_db_connection():
    """データベースへの接続を取得"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """データベースのテーブルを初期化"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
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
    ''')
    conn.commit()
    conn.close()

# --- データベース操作関数 ---
def add_record(date, meal_type, food_name, nutrients):
    """記録をデータベースに追加"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO meals (date, meal_type, food_name, calories, protein, carbohydrates, fat, vitamin_d, salt, zinc, folic_acid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        date.strftime('%Y-%m-%d'), meal_type, food_name,
        nutrients.get('calories'), nutrients.get('protein'), nutrients.get('carbohydrates'),
        nutrients.get('fat'), nutrients.get('vitaminD'), nutrients.get('salt'),
        nutrients.get('zinc'), nutrients.get('folic_acid')
    ))
    conn.commit()
    conn.close()

def get_all_records():
    """全ての記録を取得"""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM meals ORDER BY date DESC, id DESC", conn)
    conn.close()
    return df

def get_records_by_period(start_date, end_date):
    """指定期間の記録を取得"""
    conn = get_db_connection()
    query = "SELECT * FROM meals WHERE date BETWEEN ? AND ? ORDER BY date DESC, id DESC"
    df = pd.read_sql_query(query, conn, params=(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    conn.close()
    return df

def delete_record(record_id):
    """指定IDの記録を削除"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM meals WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

# --- AI (Gemini) 関連の関数 ---
def analyze_image_with_gemini(image_bytes):
    """画像から栄養素を分析"""
    model = genai.GenerativeModel('gemini-pro-vision')
    image_pil = Image.open(io.BytesIO(image_bytes))
    prompt = """
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
    try:
        response = model.generate_content([prompt, image_pil])
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except Exception as e:
        st.error(f"画像分析中にエラーが発生しました: {e}")
        return None

def get_advice_from_gemini(prompt):
    """テキストプロンプトからアドバイスを生成"""
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"アドバイス生成中にエラーが発生しました: {e}")
        return "アドバイスの生成に失敗しました。"

# --- アプリのメイン処理 ---
init_db()

st.title("🥗 食生活アドバイザー")

menu = st.sidebar.radio("メニューを選択", ["記録する", "相談する"], label_visibility="collapsed")

if menu == "記録する":
    st.header("🖊️ 今日の記録")

    with st.expander("記録フォームを開く", expanded=True):
        meal_type = st.selectbox(
            "記録の種類",
            ["朝食", "昼食", "夕食", "間食", "サプリ", "水分補給"]
        )
        record_date = st.date_input("日付", datetime.date.today())

        # --- フォーム定義 ---
        if meal_type == "サプリ":
            with st.form(key="supplement_form", clear_on_submit=True):
                supplements = {
                    'マルチビタミン': {'displayName': 'マルチビタミン', 'foodName': 'サプリ: スーパーマルチビタミン&ミネラル', 'nutrients': {'calories': 5, 'protein': 0.02, 'carbohydrates': 0.6, 'fat': 0.05, 'vitaminD': 10.0, 'salt': 0, 'zinc': 6.0, 'folic_acid': 240}},
                    '葉酸': {'displayName': '葉酸', 'foodName': 'サプリ: 葉酸', 'nutrients': {'calories': 1, 'protein': 0, 'carbohydrates': 0.23, 'fat': 0.004, 'vitaminD': 0, 'salt': 0, 'zinc': 0, 'folic_acid': 480}},
                    'ビタミンD': {'displayName': 'ビタミンD', 'foodName': 'サプリ: ビタミンD', 'nutrients': {'calories': 1, 'protein': 0, 'carbohydrates': 0, 'fat': 0.12, 'vitaminD': 30.0, 'salt': 0, 'zinc': 0, 'folic_acid': 0}},
                    '亜鉛': {'displayName': '亜鉛', 'foodName': 'サプリ: 亜鉛', 'nutrients': {'calories': 1, 'protein': 0, 'carbohydrates': 0.17, 'fat': 0.005, 'vitaminD': 0, 'salt': 0, 'zinc': 14.0, 'folic_acid': 0}}
                }
                selected_sup = st.selectbox("サプリを選択", list(supplements.keys()))
                if st.form_submit_button("サプリを記録する"):
                    sup_data = supplements[selected_sup]
                    add_record(record_date, "サプリ", sup_data['foodName'], sup_data['nutrients'])
                    st.success(f"{sup_data['displayName']}を記録しました！")

        elif meal_type == "水分補給":
            with st.form(key="water_form", clear_on_submit=True):
                amount_ml = st.number_input("飲んだ量 (ml)", min_value=0, step=50, value=200)
                if st.form_submit_button("水分補給を記録する"):
                    nutrients = {'calories': 0, 'protein': 0, 'carbohydrates': 0, 'fat': 0, 'vitamin_d': 0, 'salt': 0, 'zinc': 0, 'folic_acid': 0}
                    add_record(record_date, "水分補給", f"{amount_ml} ml", nutrients)
                    st.success(f"水分補給 {amount_ml}ml を記録しました！")

        else: # 食事の場合
            input_method = st.radio("記録方法", ["テキスト入力", "画像から入力"], horizontal=True)
            if input_method == "テキスト入力":
                with st.form(key="text_input_form", clear_on_submit=True):
                    food_name = st.text_input("食事名")
                    cols = st.columns(2)
                    calories = cols[0].number_input("カロリー (kcal)", value=0.0, format="%.1f")
                    protein = cols[1].number_input("たんぱく質 (g)", value=0.0, format="%.1f")
                    carbohydrates = cols[0].number_input("炭水化物 (g)", value=0.0, format="%.1f")
                    fat = cols[1].number_input("脂質 (g)", value=0.0, format="%.1f")
                    vitamin_d = cols[0].number_input("ビタミンD (μg)", value=0.0, format="%.1f")
                    salt = cols[1].number_input("食塩相当量 (g)", value=0.0, format="%.1f")
                    zinc = cols[0].number_input("亜鉛 (mg)", value=0.0, format="%.1f")
                    folic_acid = cols[1].number_input("葉酸 (μg)", value=0.0, format="%.1f")
                    if st.form_submit_button("食事を記録する"):
                        if food_name:
                            nutrients = {'calories': calories, 'protein': protein, 'carbohydrates': carbohydrates, 'fat': fat, 'vitaminD': vitamin_d, 'salt': salt, 'zinc': zinc, 'folic_acid': folic_acid}
                            add_record(record_date, meal_type, food_name, nutrients)
                            st.success(f"{food_name}を記録しました！")
                        else:
                            st.warning("食事名を入力してください。")

            elif input_method == "画像から入力":
                uploaded_file = st.file_uploader("食事の画像をアップロード", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    st.image(uploaded_file, caption="アップロードされた画像", use_column_width=True)
                    if st.button("画像を分析する"):
                        with st.spinner("AIが画像を分析中です..."):
                            analysis_result = analyze_image_with_gemini(uploaded_file.getvalue())
                        if analysis_result: st.session_state.analysis_result = analysis_result
                        else: st.error("分析に失敗しました。テキストで入力してください。")
                
                if 'analysis_result' in st.session_state:
                    st.info("AIによる分析結果です。必要に応じて修正して記録してください。")
                    result = st.session_state.analysis_result
                    with st.form(key="image_confirm_form"):
                        food_name = st.text_input("食事名", value=result.get('foodName', ''))
                        nut = result.get('nutrients', {})
                        cols = st.columns(2)
                        calories = cols[0].number_input("カロリー (kcal)", value=float(nut.get('calories', 0)), format="%.1f")
                        protein = cols[1].number_input("たんぱく質 (g)", value=float(nut.get('protein', 0)), format="%.1f")
                        # ... 他の栄養素も同様 ...
                        if st.form_submit_button("この内容で食事を記録する"):
                            if food_name:
                                nutrients = {'calories': calories, 'protein': protein, 'carbohydrates': nut.get('carbohydrates',0), 'fat': nut.get('fat',0), 'vitaminD': nut.get('vitaminD',0), 'salt': nut.get('salt',0), 'zinc': nut.get('zinc',0), 'folic_acid': nut.get('folic_acid',0)}
                                add_record(record_date, meal_type, food_name, nutrients)
                                st.success(f"{food_name}を記録しました！")
                                del st.session_state.analysis_result
                                st.rerun()
                            else:
                                st.warning("食事名を入力してください。")

    st.header("📖 記録一覧")
    all_records_df = get_all_records()
    if all_records_df.empty:
        st.info("まだ記録がありません。")
    else:
        display_df = all_records_df.copy()
        display_df['削除'] = [False] * len(display_df)
        
        # カロリー表示を整形
        def format_calories(row):
            if row['meal_type'] in ["水分補給", "サプリ"]:
                return "ー"
            return f"{int(row['calories'])} kcal" if pd.notna(row['calories']) else "ー"
        display_df['カロリー'] = display_df.apply(format_calories, axis=1)

        edited_df = st.data_editor(
            display_df[['date', 'meal_type', 'food_name', 'カロリー', '削除']],
            column_config={
                "date": "日付", "meal_type": "種類", "food_name": "内容", 
                "カロリー": "カロリー/量", "削除": st.column_config.CheckboxColumn("削除？")
            },
            hide_index=True, key="data_editor"
        )
        
        if edited_df['削除'].any():
            if st.button("選択した記録を削除", type="primary"):
                ids_to_delete = edited_df[edited_df['削除']].index
                original_ids = all_records_df.loc[ids_to_delete, 'id']
                for record_id in original_ids:
                    delete_record(record_id)
                st.success("選択した記録を削除しました。")
                st.rerun()

elif menu == "相談する":
    st.header("💬 AIに相談する")

    all_records_df = get_all_records()
    if all_records_df.empty:
        st.warning("アドバイスには最低1件の記録が必要です。まずは食事を記録してみましょう。")
        st.stop()

    # ★修正点: プライバシー情報を削除
    user_profile = """
    - 年齢: 35歳女性
    - 悩み: 痩せにくく太りやすい(特に、お腹まわりと顎)。筋肉量が少なく、下半身中心に筋肉をつけたい。
    - 希望: アンチエイジング
    - 苦手な食べ物: 生のトマト、納豆
    """
    base_prompt = f"あなたは経験豊富な食生活アドバイザーです。以下のクライアント情報と記録に基づき、優しく励ますトーンで、具体的なアドバイスをMarkdown形式でお願いします。\n\n# クライアント情報\n{user_profile}\n\n"
    prompt_to_send = ""

    # ★修正点: タブで相談方法を選択
    tab1, tab2, tab3 = st.tabs(["✍️ テキストで相談", "📊 全記録から分析", "🗓️ 期間で分析"])

    with tab1:
        question = st.text_area("相談内容を入力してください", height=150, placeholder="例：最近疲れやすいのですが、食事で改善できますか？")
        if st.button("AIに相談する", key="text_consult"):
            if question:
                record_history = all_records_df.head(30).to_string(index=False)
                prompt_to_send = f"{base_prompt}# 記録（参考）\n{record_history}\n\n# 相談内容\n{question}\n\n上記相談内容に対して、記録を参考にしつつ回答してください。"
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
                    prompt_to_send = f"{base_prompt}# 記録 ({start_date} ~ {end_date})\n{record_history}\n\n上記の指定期間の記録を評価し、アドバイスをしてください。"

    if prompt_to_send:
        with st.spinner("AIがアドバイスを生成中です..."):
            advice = get_advice_from_gemini(prompt_to_send)
            # ★修正点: チャット形式で表示
            with st.chat_message("ai", avatar="🥗"):
                st.markdown(advice)
