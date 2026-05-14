import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

def generate_banner():
    st.set_page_config(page_title="Medical Banner Generator", layout="wide")
    st.title("Medical Banner Generator")

    # サイドバーでの入力
    st.sidebar.header("入力設定")
    title = st.sidebar.text_area("学会名 / タイトル", "第1回 メディカルトリビューン学会\n〜最新の医療技術〜")
    details = st.sidebar.text_area("詳細（日時・場所）", "2026年5月14日（木） 19:00〜20:30\nZoomウェビナー配信")
    
    # フォントと背景の設定
    font_path = "NotoSansJP-Bold.ttf"
    
    # サイズ定義
    sizes = {
        "1440x300": {"size": (1440, 300), "bg": "background_1440.png", "title_size": 52, "detail_size": 32},
        "880x820": {"size": (880, 820), "bg": "background_880.png", "title_size": 60, "detail_size": 36},
        "800x500": {"size": (800, 500), "bg": "background_800.png", "title_size": 48, "detail_size": 28}
    }

    for size_key, config in sizes.items():
        st.write("---")
        st.subheader(f"サイズ: {size_key}")
        
        # 背景の読み込み
        try:
            img = Image.open(config["bg"]).convert("RGBA")
        except:
            img = Image.new('RGBA', config["size"], color=(240, 240, 240, 255))
        
        draw = ImageDraw.Draw(img)
        
        # フォント設定
        try:
            font_title = ImageFont.truetype(font_path, config["title_size"])
            font_details = ImageFont.truetype(font_path, config["detail_size"])
        except:
            st.error(f"{size_key}: フォントファイルが見つかりません。")
            continue

        # --- 学会名（タイトル）のロジック ---
        display_title = title
        if size_key == "1440x300":
            # 1440は常に1行
            display_title = title.replace("\n", " ")
        elif size_key == "800x500":
            # 800は「1行にした時の幅」をチェック
            single_line_title = title.replace("\n", " ")
            title_width = draw.textlength(single_line_title, font=font_title)
            # 左右余白を考慮して収まるなら1行、収まらないなら改行指示に従う
            if title_width < (config["size"][0] - 100):
                display_title = single_line_title
            else:
                display_title = title
        elif size_key == "880x820":
            # 880は改行指示を尊重
            display_title = title

        # --- 詳細（日時・場所）のロジック ---
        display_details = details
        if size_key == "1440x300":
            # 1440サイズのみ、詳細は常に1行
            display_details = details.replace("\n", " ")
        else:
            # 880と800は改行指示を尊重
            display_details = details

        # 描画位置の計算（簡易中央揃え）
        # ここでは固定位置または計算ロジックを入れます
        w, h = config["size"]
        draw.text((w/2, h/2 - 20), display_title, font=font_title, fill=(0, 0, 0), anchor="mm")
        draw.text((w/2, h/2 + 60), display_details, font=font_details, fill=(50, 50, 50), anchor="mm")

        # 表示
        st.image(img, caption=f"Preview: {size_key}")
        
        # ダウンロードボタン
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button(
            label=f"{size_key}をダウンロード",
            data=buf.getvalue(),
            file_name=f"banner_{size_key}.png",
            mime="image/png",
            key=f"btn_{size_key}"
        )

if __name__ == "__main__":
    generate_banner()
