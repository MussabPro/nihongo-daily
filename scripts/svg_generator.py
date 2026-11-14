#!/usr/bin/env python3
"""
SVG Generator for Nihongo Daily.
Generates authentic, Japanese stationery-inspired vector graphics:
1. assets/today-date.svg (Japanese date, era, weekday, Hanko seal stamp)
2. assets/daily-kanji.svg (Featured Kanji, readings, meaning, JLPT tag, vocab)
"""

import xml.sax.saxutils as saxutils
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


def escape(text: Any) -> str:
    """Escape XML special characters."""
    return saxutils.escape(str(text)) if text is not None else ""


def generate_date_svg(date_info: Dict[str, Any], output_path: Path = ASSETS_DIR / "today-date.svg") -> str:
    """
    Generate an authentic Japanese-style date illustration SVG.
    Dimensions: 760 x 380, viewBox responsive.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    iso_date = escape(date_info["iso_date"])
    era_jp = escape(date_info["era_jp"])
    era_traditional = escape(date_info["era_traditional"])
    day_kanji = escape(date_info["day_kanji"])
    gregorian_en = escape(date_info["gregorian_en"])
    weekday_jp = escape(date_info["weekday_jp"])
    weekday_reading = escape(date_info["weekday_reading"])
    weekday_en = escape(date_info["weekday_en"])
    day_num = escape(date_info["day"])
    wafuu_month = escape(f"{date_info['wafuu_month_kanji']} ({date_info['wafuu_month_romaji']})")
    wafuu_meaning = escape(date_info["wafuu_month_meaning"])
    timezone_str = escape(date_info.get("timezone", "Asia/Karachi"))

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 380" width="100%" height="100%">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;600;900&amp;family=Noto+Sans+JP:wght@400;500&amp;family=Cormorant+Garamond:ital,wght@0,500;0,700;1,400&amp;display=swap');
      .washi-bg {{ fill: #F5F0E6; }}
      .border-line {{ stroke: #DDD5C7; stroke-width: 1.5; fill: none; }}
      .border-inner {{ stroke: #DDD5C7; stroke-width: 0.75; fill: none; stroke-dasharray: 4 2; }}
      .accent-red {{ fill: #B64032; stroke: #B64032; }}
      .accent-blue {{ fill: #45566B; }}
      .text-primary {{ fill: #25251F; font-family: 'Noto Serif JP', 'Hiragino Mincho ProN', 'Yu Mincho', serif; }}
      .text-muted {{ fill: #77736A; font-family: 'Noto Sans JP', 'Hiragino Sans', sans-serif; }}
      .text-roman {{ font-family: 'Cormorant Garamond', 'Times New Roman', serif; }}
    </style>
    <!-- Subtle washi texture pattern -->
    <pattern id="washi-grain" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 0,20 Q 10,15 20,20 T 40,20" fill="none" stroke="#EFE8D8" stroke-width="0.5" opacity="0.6"/>
      <path d="M 20,0 Q 25,10 20,20 T 20,40" fill="none" stroke="#EFE8D8" stroke-width="0.5" opacity="0.6"/>
      <circle cx="12" cy="12" r="0.6" fill="#DDD5C7" opacity="0.4"/>
      <circle cx="28" cy="34" r="0.6" fill="#DDD5C7" opacity="0.4"/>
    </pattern>
  </defs>

  <!-- Background with subtle paper tone -->
  <rect width="760" height="380" class="washi-bg"/>
  <rect width="760" height="380" fill="url(#washi-grain)"/>

  <!-- Outer Frame -->
  <rect x="24" y="24" width="712" height="332" class="border-line"/>
  <rect x="30" y="30" width="700" height="320" class="border-inner"/>

  <!-- Traditional Corner Accents -->
  <path d="M 24,44 L 44,44 L 44,24" fill="none" stroke="#B64032" stroke-width="2"/>
  <path d="M 736,44 L 716,44 L 716,24" fill="none" stroke="#B64032" stroke-width="2"/>
  <path d="M 24,336 L 44,336 L 44,356" fill="none" stroke="#B64032" stroke-width="2"/>
  <path d="M 736,336 L 716,336 L 716,356" fill="none" stroke="#B64032" stroke-width="2"/>

  <!-- Top Header Bar -->
  <text x="54" y="65" class="text-roman" font-size="13" letter-spacing="3" fill="#45566B" font-weight="700">NIHONGO DAILY · 日本語日録</text>
  <text x="696" y="65" class="text-muted" font-size="11" text-anchor="end" letter-spacing="1">{timezone_str} · {iso_date}</text>
  <line x1="54" y1="78" x2="696" y2="78" stroke="#DDD5C7" stroke-width="1"/>

  <!-- Left Column: Traditional Japanese Calendar -->
  <!-- Japanese Era (Reiwa) -->
  <text x="54" y="112" class="text-primary" font-size="20" font-weight="600" letter-spacing="2">{era_jp}</text>
  <text x="54" y="133" class="text-muted" font-size="12" letter-spacing="1">和風月名：{wafuu_month} · {wafuu_meaning}</text>

  <!-- Large Day Numeral & Traditional Day Kanji -->
  <g transform="translate(54, 140)">
    <!-- Big Day Number (elevated up for balanced vertical alignment) -->
    <text x="0" y="105" class="text-roman" font-size="115" font-weight="700" fill="#25251F">{day_num}</text>
    <!-- Traditional Day Kanji & English Date aligned beside the numeral -->
    <text x="165" y="58" class="text-primary" font-size="24" font-weight="600" letter-spacing="2" fill="#77736A">{day_kanji}</text>
    <text x="165" y="92" class="text-roman" font-size="18" fill="#45566B" font-style="italic">{gregorian_en}</text>
  </g>

  <!-- Middle Divider -->
  <line x1="430" y1="95" x2="430" y2="305" stroke="#DDD5C7" stroke-width="1" stroke-dasharray="3 3"/>

  <!-- Right Column: Weekday & Authentic Hanko Stamp -->
  <!-- Weekday display -->
  <g transform="translate(460, 105)">
    <text x="0" y="18" class="text-muted" font-size="11" letter-spacing="2">WEEKDAY · 曜日</text>
    <text x="0" y="66" class="text-primary" font-size="46" font-weight="900" letter-spacing="3" fill="#B64032">{weekday_jp}</text>
    <text x="2" y="92" class="text-muted" font-size="14" letter-spacing="2">（{weekday_reading}） · {weekday_en}</text>

    <!-- Traditional Hanko (Vermilion Seal Stamp) -->
    <g transform="translate(160, 110)">
      <!-- Outer rounded stamp box -->
      <rect x="0" y="0" width="70" height="70" rx="10" ry="10" fill="none" stroke="#B64032" stroke-width="2.5" opacity="0.9"/>
      <rect x="4" y="4" width="62" height="62" rx="7" ry="7" fill="none" stroke="#B64032" stroke-width="0.8" opacity="0.5"/>
      <!-- Hanko Kanji inside (本日 - Today) -->
      <text x="35" y="32" class="text-primary" font-size="20" font-weight="900" fill="#B64032" text-anchor="middle">本</text>
      <text x="35" y="56" class="text-primary" font-size="20" font-weight="900" fill="#B64032" text-anchor="middle">日</text>
    </g>

    <!-- Small traditional note -->
    <text x="0" y="155" class="text-muted" font-size="11" letter-spacing="1">日日是好日</text>
    <text x="0" y="172" class="text-muted" font-size="10" font-style="italic">"Every day is a good day"</text>
  </g>

  <!-- Bottom Accent Line -->
  <line x1="54" y1="315" x2="696" y2="315" stroke="#DDD5C7" stroke-width="1"/>
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return str(output_path)


def generate_kanji_svg(kanji_info: Dict[str, Any], date_info: Dict[str, Any], output_path: Path = ASSETS_DIR / "daily-kanji.svg") -> str:
    """
    Generate an authentic Japanese-style daily Kanji flashcard illustration SVG.
    Dimensions: 760 x 380, viewBox responsive.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    kanji_char = escape(kanji_info["kanji"])
    hiragana = escape(kanji_info["hiragana"])
    katakana = escape(kanji_info.get("katakana", ""))
    romaji = escape(kanji_info.get("romaji", ""))
    meaning = escape(kanji_info["meaning"])
    jlpt = escape(kanji_info.get("jlpt", "N5"))
    iso_date = escape(date_info["iso_date"])

    # Featured vocabulary sample
    examples = kanji_info.get("examples", [])
    ex1_form = escape(examples[0]["kanji_form"]) if len(examples) > 0 else kanji_char
    ex1_read = escape(examples[0]["reading"]) if len(examples) > 0 else hiragana
    ex1_mean = escape(examples[0]["meaning"]) if len(examples) > 0 else meaning

    ex2_form = escape(examples[1]["kanji_form"]) if len(examples) > 1 else ""
    ex2_read = escape(examples[1]["reading"]) if len(examples) > 1 else ""
    ex2_mean = escape(examples[1]["meaning"]) if len(examples) > 1 else ""

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 380" width="100%" height="100%">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;600;900&amp;family=Noto+Sans+JP:wght@400;500&amp;family=Cormorant+Garamond:ital,wght@0,500;0,700;1,400&amp;display=swap');
      .washi-bg {{ fill: #F5F0E6; }}
      .border-line {{ stroke: #DDD5C7; stroke-width: 1.5; fill: none; }}
      .border-inner {{ stroke: #DDD5C7; stroke-width: 0.75; fill: none; stroke-dasharray: 4 2; }}
      .text-primary {{ fill: #25251F; font-family: 'Noto Serif JP', 'Hiragino Mincho ProN', 'Yu Mincho', serif; }}
      .text-muted {{ fill: #77736A; font-family: 'Noto Sans JP', 'Hiragino Sans', sans-serif; }}
      .text-roman {{ font-family: 'Cormorant Garamond', 'Times New Roman', serif; }}
      .kanji-huge {{ font-family: 'Noto Serif JP', serif; font-weight: 900; fill: #25251F; }}
    </style>
    <!-- Paper texture grain -->
    <pattern id="kanji-grain" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 0,20 Q 10,15 20,20 T 40,20" fill="none" stroke="#EFE8D8" stroke-width="0.5" opacity="0.6"/>
      <path d="M 20,0 Q 25,10 20,20 T 20,40" fill="none" stroke="#EFE8D8" stroke-width="0.5" opacity="0.6"/>
      <circle cx="8" cy="8" r="0.6" fill="#DDD5C7" opacity="0.4"/>
      <circle cx="32" cy="24" r="0.6" fill="#DDD5C7" opacity="0.4"/>
    </pattern>
  </defs>

  <!-- Washi Background -->
  <rect width="760" height="380" class="washi-bg"/>
  <rect width="760" height="380" fill="url(#kanji-grain)"/>

  <!-- Outer Frame -->
  <rect x="24" y="24" width="712" height="332" class="border-line"/>
  <rect x="30" y="30" width="700" height="320" class="border-inner"/>

  <!-- Traditional Corner Accents -->
  <path d="M 24,44 L 44,44 L 44,24" fill="none" stroke="#45566B" stroke-width="2"/>
  <path d="M 736,44 L 716,44 L 716,24" fill="none" stroke="#45566B" stroke-width="2"/>
  <path d="M 24,336 L 44,336 L 44,356" fill="none" stroke="#45566B" stroke-width="2"/>
  <path d="M 736,336 L 716,336 L 716,356" fill="none" stroke="#45566B" stroke-width="2"/>

  <!-- Top Banner -->
  <text x="54" y="65" class="text-roman" font-size="13" letter-spacing="3" fill="#B64032" font-weight="700">DAILY KANJI · 本日の漢字</text>
  <text x="696" y="65" class="text-muted" font-size="11" text-anchor="end" letter-spacing="1">{iso_date}</text>
  <line x1="54" y1="78" x2="696" y2="78" stroke="#DDD5C7" stroke-width="1"/>

  <!-- Left Column: Prominent Kanji Character Presentation -->
  <g transform="translate(60, 100)">
    <!-- Traditional Calligraphy Framing Box -->
    <rect x="0" y="10" width="190" height="200" fill="#FAF7F2" stroke="#DDD5C7" stroke-width="1"/>
    <!-- Subtle interior cross guidelines for kanji balance (traditional calligraphy practice paper) -->
    <line x1="95" y1="10" x2="95" y2="210" stroke="#E6DEC9" stroke-width="0.75" stroke-dasharray="3 3"/>
    <line x1="0" y1="110" x2="190" y2="110" stroke="#E6DEC9" stroke-width="0.75" stroke-dasharray="3 3"/>

    <!-- Large Kanji -->
    <text x="95" y="160" class="kanji-huge" font-size="120" text-anchor="middle">{kanji_char}</text>

    <!-- JLPT Level Seal Badge -->
    <rect x="15" y="18" width="68" height="22" rx="4" fill="#B64032"/>
    <text x="49" y="34" class="text-roman" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle" letter-spacing="1">JLPT {jlpt}</text>
  </g>

  <!-- Right Column: Kanji Readings, Meaning, and Vocabulary -->
  <g transform="translate(290, 110)">
    <!-- Primary Meaning (English) -->
    <text x="0" y="24" class="text-roman" font-size="34" font-weight="700" fill="#25251F">{meaning}</text>

    <!-- Readings -->
    <g transform="translate(0, 48)">
      <text x="0" y="16" class="text-muted" font-size="11" letter-spacing="1">READINGS · 読み方</text>
      <!-- Hiragana & Romaji -->
      <text x="0" y="44" class="text-primary" font-size="24" font-weight="700" fill="#B64032">{hiragana}</text>
      <text x="130" y="44" class="text-roman" font-size="18" fill="#45566B" font-style="italic">({romaji})</text>
      <text x="250" y="44" class="text-primary" font-size="18" fill="#77736A">カタカナ: {katakana}</text>
    </g>

    <!-- Divider -->
    <line x1="0" y1="110" x2="410" y2="110" stroke="#DDD5C7" stroke-width="0.75"/>

    <!-- Featured Vocabulary Cards -->
    <g transform="translate(0, 126)">
      <text x="0" y="12" class="text-muted" font-size="11" letter-spacing="1">VOCABULARY STUDY · 関連語彙</text>

      <!-- Word 1 -->
      <g transform="translate(0, 24)">
        <text x="0" y="20" class="text-primary" font-size="18" font-weight="600">{ex1_form}</text>
        <text x="110" y="20" class="text-muted" font-size="13">[{ex1_read}]</text>
        <text x="210" y="20" class="text-roman" font-size="14" fill="#25251F" font-weight="600">{ex1_mean}</text>
      </g>
"""

    if ex2_form:
        svg_content += f"""
      <!-- Word 2 -->
      <g transform="translate(0, 52)">
        <text x="0" y="20" class="text-primary" font-size="18" font-weight="600">{ex2_form}</text>
        <text x="110" y="20" class="text-muted" font-size="13">[{ex2_read}]</text>
        <text x="210" y="20" class="text-roman" font-size="14" fill="#25251F" font-weight="600">{ex2_mean}</text>
      </g>
"""

    svg_content += f"""    </g>

    <!-- Hanko Seal Stamp (Kanji stamp) -->
    <g transform="translate(350, 128)">
      <rect x="0" y="0" width="54" height="54" rx="8" ry="8" fill="none" stroke="#B64032" stroke-width="2" opacity="0.85"/>
      <rect x="3" y="3" width="48" height="48" rx="5" ry="5" fill="none" stroke="#B64032" stroke-width="0.6" opacity="0.5"/>
      <text x="27" y="24" class="text-primary" font-size="15" font-weight="900" fill="#B64032" text-anchor="middle">漢</text>
      <text x="27" y="44" class="text-primary" font-size="15" font-weight="900" fill="#B64032" text-anchor="middle">字</text>
    </g>
  </g>

  <!-- Bottom Accent Line -->
  <line x1="54" y1="335" x2="696" y2="335" stroke="#DDD5C7" stroke-width="1"/>
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return str(output_path)


if __name__ == "__main__":
    from date_generator import get_current_date
    from kanji_generator import get_daily_kanji

    d_info = get_current_date("2026-11-14")
    k_info = get_daily_kanji("2026-11-14")

    date_svg_path = generate_date_svg(d_info)
    kanji_svg_path = generate_kanji_svg(k_info, d_info)

    print(f"Generated Date SVG: {date_svg_path}")
    print(f"Generated Kanji SVG: {kanji_svg_path}")

