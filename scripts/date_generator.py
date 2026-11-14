#!/usr/bin/env python3
"""
Date Generator for Nihongo Daily.
Handles timezone-aware date calculations (Asia/Karachi), Japanese era (Reiwa),
traditional calendar terms, and formatted output.
"""

from datetime import datetime, timezone, timedelta
import zoneinfo
from typing import Dict, Any, Optional

TIMEZONE_NAME = "Asia/Karachi"

WEEKDAYS = [
    {"jp": "月曜日", "short": "月", "reading": "げつようび", "en": "Monday"},
    {"jp": "火曜日", "short": "火", "reading": "かようび", "en": "Tuesday"},
    {"jp": "水曜日", "short": "水", "reading": "すいようび", "en": "Wednesday"},
    {"jp": "木曜日", "short": "木", "reading": "もくようび", "en": "Thursday"},
    {"jp": "金曜日", "short": "金", "reading": "きんようび", "en": "Friday"},
    {"jp": "土曜日", "short": "土", "reading": "どようび", "en": "Saturday"},
    {"jp": "日曜日", "short": "日", "reading": "にちようび", "en": "Sunday"},
]

WAFUU_MONTHS = [
    {"kanji": "睦月", "romaji": "Mutsuki", "meaning": "Month of Harmony"},
    {"kanji": "如月", "romaji": "Kisaragi", "meaning": "Month of Layering Clothes"},
    {"kanji": "弥生", "romaji": "Yayoi", "meaning": "Month of Spring Growth"},
    {"kanji": "卯月", "romaji": "Uzuki", "meaning": "Month of Deutzia Flowers"},
    {"kanji": "皐月", "romaji": "Satsuki", "meaning": "Month of Early Rice Planting"},
    {"kanji": "水無月", "romaji": "Minazuki", "meaning": "Month of Water"},
    {"kanji": "文月", "romaji": "Fumizuki", "meaning": "Month of Letters & Poetry"},
    {"kanji": "葉月", "romaji": "Hazuki", "meaning": "Month of Falling Leaves"},
    {"kanji": "長月", "romaji": "Nagatsuki", "meaning": "Month of Long Autumn Nights"},
    {"kanji": "神無月", "romaji": "Kannazuki", "meaning": "Month of the Gods"},
    {"kanji": "霜月", "romaji": "Shimotsuki", "meaning": "Month of Frost"},
    {"kanji": "師走", "romaji": "Shiwasu", "meaning": "Month of Busy Masters"},
]

KANJI_DIGITS = {
    0: "〇", 1: "一", 2: "二", 3: "三", 4: "四",
    5: "五", 6: "六", 7: "七", 8: "八", 9: "九", 10: "十"
}


def number_to_kanji(n: int) -> str:
    """Convert an integer (1-99) into traditional Japanese kanji numerals."""
    if n <= 10:
        return KANJI_DIGITS.get(n, str(n))
    elif n < 20:
        remainder = n - 10
        return f"十{KANJI_DIGITS.get(remainder, '')}"
    elif n < 100:
        tens = n // 10
        remainder = n % 10
        tens_str = f"{KANJI_DIGITS.get(tens, '')}十"
        rem_str = KANJI_DIGITS.get(remainder, "") if remainder > 0 else ""
        return f"{tens_str}{rem_str}"
    return str(n)


def get_current_date(target_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve date info for today in Asia/Karachi, or for an optional target_date (YYYY-MM-DD).
    Returns a dictionary with comprehensive Gregorian and Japanese date representations.
    """
    if target_date:
        parts = [int(p) for p in target_date.split("-")]
        dt = datetime(parts[0], parts[1], parts[2], 12, 0, 0, tzinfo=zoneinfo.ZoneInfo(TIMEZONE_NAME))
    else:
        try:
            tz = zoneinfo.ZoneInfo(TIMEZONE_NAME)
            dt = datetime.now(tz)
        except Exception:
            # Fallback if tzdata missing
            tz = timezone(timedelta(hours=5))
            dt = datetime.now(tz)

    year = dt.year
    month = dt.month
    day = dt.day
    iso_date = dt.strftime("%Y-%m-%d")

    # Reiwa calculation: started on 2019-05-01
    reiwa_year_num = year - 2018
    if reiwa_year_num == 1:
        era_year_str = "元年"
        era_kanji_year = "元年"
    else:
        era_year_str = f"{reiwa_year_num}年"
        era_kanji_year = f"{number_to_kanji(reiwa_year_num)}年"

    era_full_jp = f"令和{era_year_str}{month}月{day}日"
    era_traditional = f"令和{era_kanji_year} {number_to_kanji(month)}月{number_to_kanji(day)}日"

    # Weekday
    wd_idx = dt.weekday()  # 0 = Monday, 6 = Sunday
    wd_info = WEEKDAYS[wd_idx]

    # Traditional month
    wafuu = WAFUU_MONTHS[month - 1]

    # English formatted
    gregorian_en = dt.strftime("%B %d, %Y")
    japanese_date = f"{year}年{month}月{day}日"

    return {
        "iso_date": iso_date,
        "year": year,
        "month": month,
        "day": day,
        "gregorian_en": gregorian_en,
        "japanese_date": japanese_date,
        "weekday_jp": wd_info["jp"],
        "weekday_short": wd_info["short"],
        "weekday_reading": wd_info["reading"],
        "weekday_en": wd_info["en"],
        "era_name": "令和",
        "era_year": reiwa_year_num,
        "era_jp": era_full_jp,
        "era_traditional": era_traditional,
        "wafuu_month_kanji": wafuu["kanji"],
        "wafuu_month_romaji": wafuu["romaji"],
        "wafuu_month_meaning": wafuu["meaning"],
        "day_kanji": f"{number_to_kanji(day)}日",
        "month_kanji": f"{number_to_kanji(month)}月",
        "timezone": TIMEZONE_NAME,
        "updated_at": dt.isoformat(),
    }


if __name__ == "__main__":
    import pprint
    today_info = get_current_date()
    pprint.pprint(today_info)

