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
def wrap_text(text, font, max_width, draw, newline_mode="all", force_single_line=False):
    if not text: return []
    
    # 1440の詳細行など、強制1行モード
    if force_single_line:
        # 入力の全改行を削除し、スペース1つで結合して「1つの要素」として返す
        single_joined = " ".join(text.splitlines()).strip()
        return [single_joined] if single_joined else []

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

def generate_banner(size_key, n_txt, t_txt, i_txt, accent_color):
    width, height = SIZES[size_key]
    
    # --- サイズごとの個別設定 ---
    configs = {
        "880x550": {
            "bg": "background_880.png", "sd": "shadow_880.png",
            "f_size": [54, 80, 40], "y_pos": [10, 80], "max_w": 740,
            "right_margin": 40, "line_space": 95, "info_margin": 30, "info_line_space": 50,
            "filename_format": "com_{slug}_thum_w440h275.png", 
            "newline_mode": "all",
            "force_single_line": False
        },
        "1440x300": {
            "bg": "background_1440.png", "sd": "shadow_1440.png",
            "f_size": [54, 86, 40], "y_pos": [25, 3], "max_w": 1050,
            "right_margin": 40, "line_space": 100, "info_margin": 30, "info_line_space": 45,
            "filename_format": "com_{slug}_bn_w720h150.png", 
            "newline_mode": "first_only",
            "force_single_line": True     # ★1440の詳細行は強制1行
        },
        "800x418": {
            "bg": "background_800.png", "sd": "shadow_800s.png",
            "f_size": [41, 60, 30], "y_pos": [25, 80], "max_w": 710,
            "right_margin": 20, "line_space": 70, "info_margin": 25, "info_line_space": 42,
            "filename_format": "X_{slug}_thum_w800h418.png", 
            "newline_mode": "first_only",
            "force_single_line": False
        }
    }
    
    conf = configs[size_key]
    r_margin = conf["right_margin"]
    final_image = Image.new('RGB', (width, height), color=accent_color)
    
    # 背景・影合成
    for path_key, filename in [("sd", conf["sd"]), ("bg", conf["bg"])]:
        full_path = os.path.join(BASE_DIR, filename)
        if os.path.exists(full_path):
            overlay = Image.open(full_path).convert("RGBA").resize((width, height))
            if path_key == "sd":
                base = Image.new('RGBA', (width, height), color="#FFFFFF")
                base.paste(overlay, (0, 0), overlay)
                final_image = ImageChops.multiply(final_image, base.convert("RGB"))
            else:
                base = Image.new('RGBA', (width, height), color="#FFFFFF")
                base.paste(overlay, (0, 0), overlay)
                final_image.paste(base.convert("RGB"), (0, 0), overlay)

    draw = ImageDraw.Draw(final_image)
    
    try:
        font_n = ImageFont.truetype(FONT_PATH, conf["f_size"][0])
        font_t = ImageFont.truetype(FONT_PATH, conf["f_size"][1])
        # 詳細行のフォント（1440の場合は収まるまでリサイズ）
        i_f_size = conf["f_size"][2]
        if conf["force_single_line"]:
            i_text_flat = " ".join(i_txt.splitlines()).strip()
            temp_font = ImageFont.truetype(FONT_PATH, i_f_size)
            while i_f_size > 20:
                tw = draw.textbbox((0, 0), i_text_flat, font=temp_font)[2]
                if tw <= conf["max_w"]: break
                i_f_size -= 1
                temp_font = ImageFont.truetype(FONT_PATH, i_f_size)
        font_i = ImageFont.truetype(FONT_PATH, i_f_size)
    except:
        font_n = font_t = font_i = ImageFont.load_default()

    # --- 1. 学会名の描画 ---
    wrapped_title = wrap_text(t_txt, font_t, conf["max_w"], draw, newline_mode=conf["newline_mode"])
    
    if size_key == "1440x300":
        first_line = wrapped_title[0] if wrapped_title else ""
        draw.text((width - r_margin, conf["y_pos"][1]), first_line, fill=accent_color, font=font_t, anchor="ra")
        
        # 回数の位置調整
        t_w = draw.textbbox((0, 0), first_line, font=font_t)[2]
        draw.text((width - r_margin - t_w - 30, conf["y_pos"][0]), n_txt, fill="#000000", font=font_n, anchor="ra")
        
        curr_y = conf["y_pos"][1] + conf["line_space"]
        for line in wrapped_title[1:]:
            draw.text((width - r_margin, curr_y), line, fill=accent_color, font=font_t, anchor="ra")
            curr_y += conf["line_space"]
    else:
        draw.text((width - r_margin, conf["y_pos"][0]), n_txt, fill="#000000", font=font_n, anchor="ra")
        curr_y = conf["y_pos"][1]
        for line in wrapped_title:
            draw.text((width - r_margin, curr_y), line, fill=accent_color, font=font_t, anchor="ra")
            curr_y += conf["line_space"]

    # --- 2. 詳細行の描画 ---
    # 直前の学会名末尾から位置を算出
    info_y = curr_y - conf["line_space"] + conf["f_size"][1] + conf["info_margin"]
    
    # 1440の場合は force_single_line=True で呼び出し
    wrapped_info = wrap_text(i_txt, font_i, conf["max_w"], draw, 
                             newline_mode=conf["newline_mode"], 
                             force_single_line=conf["force_single_line"])
    
    for i_line in wrapped_info:
        draw.text((width - r_margin, info_y), i_line, fill="#000000", font=font_i, anchor="ra")
        info_y += conf["info_line_space"]

    return final_image, conf["filename_format"]

# --- UI ---
st.set_page_config(page_title="学会バナー一括生成", layout="wide")
with st.sidebar:
    st.header("🎨 デザイン設定")
    accent_color = st.color_picker("テーマカラー", "#1A448E")
    n_in = st.text_input("回数", "第○○回")
    t_in = st.text_area("学会名", "日本○○○○学会")
    i_in = st.text_area("詳細 (日時・場所)", "東京・ウェブ併催／2026.1.30〜2.10")
    st.divider()
    slug_input = st.text_input("英語ファイル名用キーワード", "jsm").lower().strip()
    slug = slug_input.replace(" ", "_")

st.title("🎓 学会バナー 3サイズ一括生成")
cols = st.columns(3)
size
