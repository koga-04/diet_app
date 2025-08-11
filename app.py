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
    page_icon="🥗",
    layout="wide"
)

# --- Google Gemini APIキーの設定 ---
# Streamlitのシークレット管理機能を使ってAPIキーを設定します。
# ローカルで試す場合は、直接キーを文字列として入力してもOKです。
# 例: GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
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
    """食事記録をデータベースに追加"""
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
    """全ての食事記録を取得"""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM meals ORDER BY date DESC, id DESC", conn)
    conn.close()
    return df

def get_records_by_period(start_date, end_date):
    """指定期間の食事記録を取得"""
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
            "protein": 12.3,
            "carbohydrates": 12.3,
            "fat": 12.3,
            "vitaminD": 1.2,
            "salt": 1.2,
            "zinc": 1.5,
            "folic_acid": 20.0
        }
    }
    """
    try:
        response = model.generate_content([prompt, image_pil])
        # レスポンスからJSON部分を抽出
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except Exception as e:
        st.error(f"画像分析中にエラーが発生しました: {e}")
        return None

def get_advice_from_gemini(prompt):
    """テキストプロンプトからアドバイスを生成"""
    model = genai.GenerativeModel('gemini-pro')
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"アドバイス生成中にエラーが発生しました: {e}")
        return "アドバイスの生成に失敗しました。"

# --- アプリのメイン処理 ---

# データベースを初期化
init_db()

# --- タイトル ---
st.title("🥗 食生活アドバイザー")
st.write("日々の食事やサプリを記録し、AIからパーソナルなアドバイスを受けましょう。")

# --- サイドバー (記録と相談の切り替え) ---
menu = st.sidebar.radio("メニューを選択", ["記録する", "相談する"], label_visibility="collapsed")

# --- 食事記録ページ ---
if menu == "記録する":
    st.header("食事・サプリを記録する")

    # --- 記録フォーム ---
    with st.expander("記録フォームを開く", expanded=True):
        meal_type = st.selectbox(
            "記録の種類",
            ["朝食", "昼食", "夕食", "間食", "サプリ"]
        )
        
        record_date = st.date_input("日付", datetime.date.today())

        if meal_type == "サプリ":
            supplements = {
                'マルチビタミン': {'displayName': 'マルチビタミン', 'foodName': 'サプリ: スーパーマルチビタミン&ミネラル', 'nutrients': {'calories': 5, 'protein': 0.02, 'carbohydrates': 0.6, 'fat': 0.05, 'vitaminD': 10.0, 'salt': 0, 'zinc': 6.0, 'folic_acid': 240}},
                '葉酸': {'displayName': '葉酸', 'foodName': 'サプリ: 葉酸', 'nutrients': {'calories': 1, 'protein': 0, 'carbohydrates': 0.23, 'fat': 0.004, 'vitaminD': 0, 'salt': 0, 'zinc': 0, 'folic_acid': 480}},
                'ビタミンD': {'displayName': 'ビタミンD', 'foodName': 'サプリ: ビタミンD', 'nutrients': {'calories': 1, 'protein': 0, 'carbohydrates': 0, 'fat': 0.12, 'vitaminD': 30.0, 'salt': 0, 'zinc': 0, 'folic_acid': 0}},
                '亜鉛': {'displayName': '亜鉛', 'foodName': 'サプリ: 亜鉛', 'nutrients': {'calories': 1, 'protein': 0, 'carbohydrates': 0.17, 'fat': 0.005, 'vitaminD': 0, 'salt': 0, 'zinc': 14.0, 'folic_acid': 0}}
            }
            
            selected_sup = st.selectbox("サプリを選択", list(supplements.keys()))

            if st.button("サプリを記録する"):
                sup_data = supplements[selected_sup]
                add_record(record_date, "サプリ", sup_data['foodName'], sup_data['nutrients'])
                st.success(f"{sup_data['displayName']}を記録しました！")
                st.experimental_rerun()

        else: # 食事の場合
            input_method = st.radio("記録方法", ["テキスト入力", "画像から入力"])

            if input_method == "テキスト入力":
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

                if st.button("食事を記録する"):
                    if food_name:
                        nutrients = {
                            'calories': calories, 'protein': protein, 'carbohydrates': carbohydrates,
                            'fat': fat, 'vitaminD': vitamin_d, 'salt': salt, 'zinc': zinc, 'folic_acid': folic_acid
                        }
                        add_record(record_date, meal_type, food_name, nutrients)
                        st.success(f"{food_name}を記録しました！")
                        st.experimental_rerun()
                    else:
                        st.warning("食事名を入力してください。")

            elif input_method == "画像から入力":
                uploaded_file = st.file_uploader("食事の画像をアップロード", type=["jpg", "jpeg", "png"])

                if uploaded_file is not None:
                    image_bytes = uploaded_file.getvalue()
                    st.image(image_bytes, caption="アップロードされた画像", use_column_width=True)
                    
                    if st.button("画像を分析する"):
                        with st.spinner("AIが画像を分析中です..."):
                            analysis_result = analyze_image_with_gemini(image_bytes)
                        
                        if analysis_result:
                            st.session_state.analysis_result = analysis_result
                        else:
                            st.error("分析に失敗しました。テキストで入力してください。")
                
                if 'analysis_result' in st.session_state:
                    result = st.session_state.analysis_result
                    st.info("AIによる分析結果です。必要に応じて修正して記録してください。")
                    
                    food_name = st.text_input("食事名", value=result.get('foodName', ''))
                    nut = result.get('nutrients', {})
                    cols = st.columns(2)
                    calories = cols[0].number_input("カロリー (kcal)", value=float(nut.get('calories', 0)), format="%.1f")
                    protein = cols[1].number_input("たんぱく質 (g)", value=float(nut.get('protein', 0)), format="%.1f")
                    carbohydrates = cols[0].number_input("炭水化物 (g)", value=float(nut.get('carbohydrates', 0)), format="%.1f")
                    fat = cols[1].number_input("脂質 (g)", value=float(nut.get('fat', 0)), format="%.1f")
                    vitamin_d = cols[0].number_input("ビタミンD (μg)", value=float(nut.get('vitaminD', 0)), format="%.1f")
                    salt = cols[1].number_input("食塩相当量 (g)", value=float(nut.get('salt', 0)), format="%.1f")
                    zinc = cols[0].number_input("亜鉛 (mg)", value=float(nut.get('zinc', 0)), format="%.1f")
                    folic_acid = cols[1].number_input("葉酸 (μg)", value=float(nut.get('folic_acid', 0)), format="%.1f")

                    if st.button("この内容で食事を記録する"):
                        if food_name:
                            nutrients = {
                                'calories': calories, 'protein': protein, 'carbohydrates': carbohydrates,
                                'fat': fat, 'vitaminD': vitamin_d, 'salt': salt, 'zinc': zinc, 'folic_acid': folic_acid
                            }
                            add_record(record_date, meal_type, food_name, nutrients)
                            st.success(f"{food_name}を記録しました！")
                            del st.session_state.analysis_result
                            st.experimental_rerun()
                        else:
                            st.warning("食事名を入力してください。")


    st.header("記録一覧")
    
    # --- 記録の表示 ---
    all_records_df = get_all_records()

    if all_records_df.empty:
        st.info("まだ記録がありません。")
    else:
        # 削除ボタンのための列を追加
        all_records_df['削除'] = [False] * len(all_records_df)
        
        # 表示する列を選択・整形
        display_cols = ['date', 'meal_type', 'food_name', 'calories', 'protein', 'carbohydrates', 'fat', '削除']
        edited_df = st.data_editor(
            all_records_df[display_cols],
            column_config={
                "date": st.column_config.TextColumn("日付"),
                "meal_type": st.column_config.TextColumn("種類"),
                "food_name": st.column_config.TextColumn("内容"),
                "calories": st.column_config.NumberColumn("カロリー(kcal)", format="%.0f"),
                "protein": st.column_config.NumberColumn("たんぱく質(g)", format="%.1f"),
                "carbohydrates": st.column_config.NumberColumn("炭水化物(g)", format="%.1f"),
                "fat": st.column_config.NumberColumn("脂質(g)", format="%.1f"),
                "削除": st.column_config.CheckboxColumn("削除する", default=False),
            },
            hide_index=True,
            key="data_editor"
        )
        
        # 削除がチェックされた行を特定
        rows_to_delete = edited_df[edited_df['削除']]
        if not rows_to_delete.empty:
            if st.button("選択した記録を削除"):
                original_indices = rows_to_delete.index
                ids_to_delete = all_records_df.loc[original_indices, 'id']
                for record_id in ids_to_delete:
                    delete_record(record_id)
                st.success("選択した記録を削除しました。")
                st.experimental_rerun()

# --- 相談ページ ---
elif menu == "相談する":
    st.header("AI食生活アドバイザーに相談する")

    all_records_df = get_all_records()
    if all_records_df.empty:
        st.warning("アドバイスには最低1件の記録が必要です。まずは食事を記録してみましょう。")
        st.stop()

    consult_method = st.selectbox(
        "相談方法を選択してください",
        ["テキストで自由に相談する", "全記録から総合的なアドバイスをもらう", "期間を指定してアドバイスをもらう"]
    )

    user_profile = """
    - 年齢: 35歳女性
    - 悩み: 痩せにくく太りやすい(特に、お腹まわりと顎)。筋肉量が少なく、下半身中心に筋肉をつけたい。
    - 希望: アンチエイジング
    - 苦手な食べ物: 生のトマト、納豆
    """
    
    base_prompt = f"""
    あなたは経験豊富な食生活アドバイザーです。
    以下のクライアント情報と食事/サプリ記録に基づき、具体的で実行可能なアドバイスをしてください。
    クライアントの悩みを解決し、希望を叶えるための食事プランや、おすすめの食材、避けるべき習慣などを、専門的かつ優しく、励ますようなトーンで提案してください。
    苦手な食べ物は避け、代替案を提示してください。Markdown形式で、見出しやリストを使って分かりやすくまとめてください。

    # クライアント情報
    {user_profile}
    """

    prompt_to_send = ""

    if consult_method == "テキストで自由に相談する":
        question = st.text_area("相談内容を入力してください", height=150, placeholder="例：最近疲れやすいのですが、食事で改善できますか？")
        if st.button("AIに相談する"):
            if question:
                record_history = all_records_df.head(20).to_string(index=False)
                prompt_to_send = f"{base_prompt}\n\n# 食事・サプリ記録（参考）\n{record_history}\n\n# 相談内容\n{question}\n\n上記相談内容に対して、記録を参考にしつつ回答してください。"
            else:
                st.warning("相談内容を入力してください。")

    elif consult_method == "全記録から総合的なアドバイスをもらう":
        if st.button("アドバイスをもらう"):
            record_history = all_records_df.to_string(index=False)
            prompt_to_send = f"{base_prompt}\n\n# 食事・サプリ記録\n{record_history}\n\n上記の記録全体を評価し、総合的なアドバイスをしてください。"

    elif consult_method == "期間を指定してアドバイスをもらう":
        today = datetime.date.today()
        one_week_ago = today - datetime.timedelta(days=7)
        
        cols = st.columns(2)
        start_date = cols[0].date_input("開始日", one_week_ago)
        end_date = cols[1].date_input("終了日", today)

        if st.button("指定期間のアドバイスをもらう"):
            if start_date > end_date:
                st.error("終了日は開始日以降に設定してください。")
            else:
                period_records_df = get_records_by_period(start_date, end_date)
                if period_records_df.empty:
                    st.warning("指定された期間に記録がありません。")
                else:
                    record_history = period_records_df.to_string(index=False)
                    prompt_to_send = f"{base_prompt}\n\n# 食事・サプリ記録 ({start_date} ~ {end_date})\n{record_history}\n\n上記の指定期間の記録を評価し、アドバイスをしてください。"

    if prompt_to_send:
        with st.spinner("AIがアドバイスを生成中です..."):
            advice = get_advice_from_gemini(prompt_to_send)
            st.markdown(advice)


