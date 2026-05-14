import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageChops
import io
import os

# --- 共通設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "NotoSansJP-Bold.ttf")

SIZES = {
    "880x550": (880, 550),
    "1440x300": (1440, 300),
    "800x418": (800, 418)
}

# --- 自動折り返し関数 ---
def wrap_text(text, font, max_width, draw, newline_mode="all"):
    if not text: return []
    
    # 1. 1行に収まるかチェックする判定（新規追加ロジック）
    # 「すべて1行」モードの場合、または「1行で収まるなら1行にする」判定用
    single_line_text = text.replace("\n", " ").replace("\r", "")
    bbox = draw.textbbox((0, 0), single_line_text, font=font)
    text_w = bbox[2] - bbox[0]
    
    # スペースに余裕がある（max_width以下）かつ newline_mode が強制改行でない場合
    if newline_mode == "none" or (newline_mode == "auto_single" and text_w <= max_width):
        return [single_line_text]

    # 2. 通常の改行・折り返し処理
    lines = text.splitlines()
    paragraphs = []
    if newline_mode == "all":
        paragraphs = lines
    elif newline_mode == "first_only":
        paragraphs.append(lines[0])
        if len(lines) > 1:
            remaining = "".join(lines[1:])
            if remaining: paragraphs.append(remaining)
    
    final_lines = []
    for p in paragraphs:
        if not p:
            final_lines.append("")
            continue
        line = ""
        for char in p:
            test_line = line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                line = test_line
            else:
                if line: final_lines.append(line)
                line = char
        if line: final_lines.append(line)
    return final_lines

# --- 画像生成メイン ---
def create_banner(size_key, n_txt, t_txt, i_txt, color):
    width, height = SIZES[size_key]
    final_image = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(final_image)
    
    # 各サイズごとの詳細設定
    configs = {
        "880x550": {
            "n_fs": 40, "t_fs": 58, "i_fs": 34,
            "t_y": 240, "i_y": 420, "max_w": 780,
            "line_space": 15, "info_line_space": 10,
            "newline_mode": "all", "filename_format": "880x550"
        },
        "1440x300": {
            "n_fs": 34, "t_fs": 54, "i_fs": 30,
            "t_y": 125, "i_y": 210, "max_w": 1300,
            "line_space": 10, "info_line_space": 8,
            "newline_mode": "none", "filename_format": "1440x300"
        },
        "800x418": {
            "n_fs": 36, "t_fs": 48, "i_fs": 28,
            "t_y": 180, "i_y": 320, "max_w": 720,
            "line_space": 12, "info_line_space": 8,
            "newline_mode": "auto_single", "filename_format": "fb_link"
        }
    }
    
    conf = configs[size_key]
    
    # フォント読み込み
    try:
        font_n_base = ImageFont.truetype(FONT_PATH, conf["n_fs"])
        font_t_base = ImageFont.truetype(FONT_PATH, conf["t_fs"])
        font_i_base = ImageFont.truetype(FONT_PATH, conf["i_fs"])
    except:
        st.error("フォントファイルが見つかりません。")
        return None, ""

    # デザイン描画（アクセントバーなど）
    draw.rectangle([0, 0, width, 15], fill=color)
    
    r_margin = 50
    # 回数
    draw.text((width - r_margin, 60), n_txt, fill=color, font=font_n_base, anchor="ra")

    # 学会名（タイトル）
    wrapped_title = wrap_text(t_txt, font_t_base, conf["max_w"], draw, newline_mode=conf["newline_mode"])
    title_y_pos = conf["t_y"]
    for t_line in wrapped_title:
        draw.text((width - r_margin, title_y_pos), t_line, fill=\"#000000\", font=font_t_base, anchor=\"ra\")
        title_y_pos += conf[\"t_fs\"] + conf[\"line_space\"]

    # 詳細 (日時・場所)
    # 1440と800で余裕があれば1行にするため newline_mode を設定
    info_newline_mode = \"all\"
    if size_key == \"1440x300\":
        info_newline_mode = \"none\"
    elif size_key == \"800x418\":
        info_newline_mode = \"auto_single\"

    wrapped_info = wrap_text(i_txt, font_i_base, conf[\"max_w\"], draw, newline_mode=info_newline_mode)
    info_y_pos = conf[\"i_y\"]
    for i_line in wrapped_info:
        draw.text((width - r_margin, info_y_pos), i_line, fill=\"#000000\", font=font_i_base, anchor=\"ra\")
        info_y_pos += conf[\"i_fs\"] + conf[\"info_line_space\"]

    return final_image, conf[\"filename_format\"]

# --- UI ---
st.set_page_config(page_title=\"学会バナー一括生成\", layout=\"wide\")
with st.sidebar:
    st.header(\"🎨 デザイン設定\")
    accent_color = st.color_picker(\"テーマカラー\", \"#1A448E\")
    n_in = st.text_input(\"回数\", \"第○○回\")
    t_in = st.text_area(\"学会名\", \"日本○○○○学会\\n〜サブタイトル〜\")
    i_in = st.text_area(\"詳細 (日時・場所)\", \"2026.1.30〜2.10\\n東京・ウェブ併催\")
    st.divider()
    slug_input = st.text_input(\"英語ファイル名用キーワード\", \"jsm\").lower().strip()
    slug = slug_input.replace(\" \", \"_\")

st.title(\"🎓 学会バナー 3サイズ一括生成\")
cols = st.columns(3)
size_list = [\"880x550\", \"1440x300\", \"800x418\"]

for idx, skey in enumerate(size_list):
    with cols[idx]:
        st.subheader(skey)
        img, f_suffix = create_banner(skey, n_in, t_in, i_in, accent_color)
        if img:
            st.image(img, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format=\"PNG\")
            st.download_button(
                label=f\"{skey}を保存\",
                data=buf.getvalue(),
                file_name=f\"{slug}_{f_suffix}.png\",
                mime=\"image/png\",
                key=f\"dl_{skey}\"
            )
