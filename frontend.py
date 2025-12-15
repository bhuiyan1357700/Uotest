import streamlit as st
from PIL import Image
import io

# バックエンド関数をインポート
try:
    from backend import identify_and_check_fish
    from utils.location import prefecture_from_city
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    st.warning("バックエンドが見つかりません。backend.pyを作成してください。")

st.set_page_config(page_title="UOチェッカー", layout="centered")

# タイトルを中央揃えで表示
title = "UOチェッカー"

st.markdown(
    f"""<h1 style='text-align: center; 
            font-size: clamp(30px, 8vw, 100px);
            font-weight: bold;
            white-space: nowrap;'>{title}</h1>""",
    unsafe_allow_html=True,
)

st.button("設定", width="stretch", key="settings_button")

st.markdown("---")

# CSSスタイル
custom_css = """
    <style>
    [data-testid="stFileUploader"] section {
        visibility: hidden
    }
    [data-testid="stFileUploader"] button {
        visibility: visible;
        width:30vw;
        height: 180px;
        color: transparent !important;
        background-color: #ffffff;
        border: 2px dashed #cccccc;
        border-radius: 10px;
        font-size: 1.2rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-left: -17%;
        margin-right: auto;
    }

    @media (max-width: 600px) {
        [data-testid="stFileUploader"] button {
            width: 80vw;
            margin-top: -20px;
            margin-left: 0;
            margin-right: auto;
        }
    }

    [data-testid="stFileUploader"] button:hover {
        background-color: #f7f7f7;
        border-color: #aaaaaa;
    }

    [data-testid="stFileUploader"] button::before {
        content: '📷';
        font-size: 4rem;
        color: #555;
        display: block;
        margin-bottom: 0.5rem;
    }

    [data-testid="stFileUploader"] button::after {
        content: '画像を選択';
        font-size: 1.2rem;
        color: #333;
        display: block;
    }

    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .stImage {
        text-align: center;
    }
    </style>
"""

st.html(custom_css)

# セッション状態の初期化
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "fish_result" not in st.session_state:
    st.session_state.fish_result = None

# ファイルアップロード部分
if st.session_state.uploaded_file is None:
    col_uploader_left, col_uploader, col_uploader_right = st.columns([2, 5, 2])

    with col_uploader:
        uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            st.rerun()
else:
    # プレビュー表示
    col_preview_left, col_preview_center, col_preview_right = st.columns([2, 5, 2])

    with col_preview_center:
        try:
            image = Image.open(st.session_state.uploaded_file)
            st.image(
                image,
                caption=st.session_state.uploaded_file.name,
                use_container_width=True,
            )

        except Exception as e:
            st.error(f"読み込みエラー: {e}")
            st.session_state.uploaded_file = None

    # 別の画像を選択ボタン
    col_btn_picture_left, col_btn_picture, col_btn_picture_right = st.columns([2, 5, 2])

    with col_btn_picture:
        if st.button("別の画像を選択", width="stretch"):
            st.session_state.uploaded_file = None
            st.session_state.fish_result = None
            st.rerun()

# 現在地選択
suggestions = [
    "神戸", "姫路", "大阪", "京都", "奈良", "和歌山", "滋賀",
    "福井", "石川", "富山", "名古屋", "岐阜", "静岡", "浜松",
    "三重", "東京", "横浜", "川崎", "埼玉", "千葉", "茨城",
    "栃木", "群馬", "宇都宮", "水戸", "高崎", "仙台", "福島",
    "山形", "秋田", "盛岡", "青森", "弘前", "八戸", "新潟",
    "長野", "松本", "甲府", "山梨", "富士吉田", "静岡市",
]

st.write("\n\n")
st.divider()
selected = st.selectbox("現在地を入力", [""] + suggestions)

# 決定ボタン
col_decide_left, col_decide_button, col_decide_right = st.columns([3, 4, 3])
with col_decide_button:
    if st.button("決定", width="stretch", type="primary"):
        if selected == "":
            st.warning("現在地を選択してください。")
        elif st.session_state.uploaded_file is None:
            st.warning("画像をアップロードしてください。")
        elif not BACKEND_AVAILABLE:
            st.error("バックエンドが利用できません。backend.pyを確認してください。")
        else:
            # バックエンド処理を実行
            with st.spinner('魚を識別中...'):
                try:
                    # 画像をバイト列に変換
                    st.session_state.uploaded_file.seek(0)
                    image_bytes = st.session_state.uploaded_file.read()
                    
                    # 都道府県に変換
                    prefecture = prefecture_from_city(selected)
                    
                    # バックエンド呼び出し
                    result = identify_and_check_fish(
                        image_bytes=image_bytes,
                        prefecture=prefecture,
                        city=selected
                    )
                    
                    st.session_state.fish_result = result
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    st.write("詳細:", e)

# 結果表示
if st.session_state.fish_result is not None:
    result = st.session_state.fish_result
    
    st.markdown("---")
    st.markdown("## 識別結果")
    
    if not result.get('success', False):
        st.error(result.get('error', '魚を特定できませんでした'))
        if 'message' in result:
            st.info(result['message'])
    else:
        data = result.get('data', {})
        
        # キャッシュ情報
        if result.get('fromCache', False):
            st.info("キャッシュから取得（高速）")
        else:
            st.info("AIが新しく生成しました")
        
        # 魚の名前
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {data.get('fishNameJa', '不明')} ({data.get('fishNameEn', 'Unknown')})")
        with col2:
            if data.get('scientificName'):
                st.caption(f"学名: {data['scientificName']}")
        
        # 法的ステータス（最も重要！）
        status = data.get('status', 'UNKNOWN')
        legal_explanation = data.get('legalExplanation', '情報なし')
        
        if status == 'OK':
            st.success(f"{legal_explanation}")
        elif status == 'RESTRICTED':
            st.warning(f"{legal_explanation}")
        elif status == 'PROHIBITED':
            st.error(f"{legal_explanation}")
        else:
            st.info(f"{legal_explanation}")
        
        # 規制情報
        st.markdown("### 規制情報")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            min_size = data.get('minSize', 0)
            if min_size > 0:
                st.metric("最小サイズ", f"{min_size}cm")
            else:
                st.metric("最小サイズ", "制限なし")
        
        with col2:
            daily_limit = data.get('dailyLimit')
            if daily_limit:
                st.metric("1日の漁獲量", f"{daily_limit}尾")
            else:
                st.metric("1日の漁獲量", "制限なし")
        
        with col3:
            seasonal_ban = data.get('seasonalBan', [])
            if seasonal_ban:
                st.metric("禁漁期", ", ".join(seasonal_ban))
            else:
                st.metric("禁漁期", "なし")
        
        with col4:
            is_edible = data.get('isEdible', None)
            if is_edible is True:
                st.metric("食用", "可能")
            elif is_edible is False:
                st.metric("食用", "不可")
            else:
                st.metric("食用", "不明")
        
        # 詳細情報
        with st.expander("詳細情報を見る"):
            if data.get('description'):
                st.write("**説明:**")
                st.write(data['description'])
            
            if data.get('cookingMethods'):
                st.write("**調理法:**")
                st.write(", ".join(data['cookingMethods']))
            
            if data.get('taste'):
                st.write("**味:**")
                st.write(data['taste'])
            
            if data.get('nutrition'):
                st.write("**栄養:**")
                st.write(data['nutrition'])
            
            if data.get('peakSeason'):
                st.write("**旬:**")
                st.write(data['peakSeason'])
            
            if data.get('habitat'):
                st.write("**生息地:**")
                st.write(data['habitat'])
            
            if data.get('edibilityNotes'):
                st.write("**食用に関する注意:**")
                st.write(data['edibilityNotes'])
            
            if data.get('preparationWarnings'):
                st.write("**調理時の注意:**")
                st.warning(data['preparationWarnings'])
        
        # 情報源
        st.markdown("---")
        st.caption(f"情報源: {data.get('regulationSource', '不明')}")
        st.caption(f"信頼度: {data.get('confidence', '不明')}")
        
        if data.get('sourceUrl'):
            st.caption(f"[公式サイトで確認]({data['sourceUrl']})")