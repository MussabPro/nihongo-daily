#!/usr/bin/env python3
"""
Kanji Generator for Nihongo Daily.
Parses the supplied kanji.md dataset, builds/caches data/kanji_bank.json,
and provides deterministic, non-repeating daily Kanji selection.
"""

import os
import re
import json
import random
from datetime import date
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
KANJI_MD_PATH = BASE_DIR / "kanji.md"
KANJI_BANK_JSON = DATA_DIR / "kanji_bank.json"

# Fixed reference epoch for deterministic day offset
REFERENCE_DATE = date(2026, 1, 1)
# Fixed seed ensures stable, reproducible permutation across all runs
SELECTION_SEED = 1205


def hiragana_to_katakana(text: str) -> str:
    """Convert Hiragana characters into Katakana."""
    result = []
    for char in text:
        code = ord(char)
        if 0x3041 <= code <= 0x3096:
            result.append(chr(code + 0x60))
        else:
            result.append(char)
    return "".join(result)


def parse_related_readings(rel_str: str, form_str: str) -> List[Dict[str, str]]:
    """
    Extract vocabulary items from Related readings and Studied kanji form lines.
    Preserves authentic forms, kana readings, romaji, and English meanings.
    """
    # Split items by comma
    rel_items = [x.strip() for x in rel_str.split(",") if x.strip()]
    form_items = [x.strip() for x in form_str.split(",") if x.strip()]

    parsed_items = []
    for idx, item in enumerate(rel_items):
        clean_item = re.sub(r"</?u>", "", item).strip()
        form_kanji = ""
        if idx < len(form_items):
            fm = re.match(r"^(.*?)\s*\(", form_items[idx])
            form_kanji = fm.group(1).strip() if fm else form_items[idx].strip()

        # Format: <reading> (<romaji> - <meaning>)
        m = re.match(r"^(.*?)\s*\((.*?)\s*-\s*(.*?)\)$", clean_item)
        if m:
            reading = m.group(1).strip()
            romaji = m.group(2).strip()
            meaning = m.group(3).strip()
            parsed_items.append({
                "kanji_form": form_kanji or reading,
                "reading": reading,
                "katakana": hiragana_to_katakana(reading),
                "romaji": romaji,
                "meaning": meaning
            })
        else:
            # Format: <reading> (<romaji>)
            m2 = re.match(r"^(.*?)\s*\((.*?)\)$", clean_item)
            if m2:
                reading = m2.group(1).strip()
                romaji = m2.group(2).strip()
                parsed_items.append({
                    "kanji_form": form_kanji or reading,
                    "reading": reading,
                    "katakana": hiragana_to_katakana(reading),
                    "romaji": romaji,
                    "meaning": ""
                })
            else:
                parsed_items.append({
                    "kanji_form": form_kanji or clean_item,
                    "reading": clean_item,
                    "katakana": hiragana_to_katakana(clean_item),
                    "romaji": "",
                    "meaning": ""
                })

    return parsed_items


def parse_kanji_markdown(md_path: Path = KANJI_MD_PATH) -> List[Dict[str, Any]]:
    """Parse the provided kanji.md file into structured entries."""
    if not md_path.exists():
        raise FileNotFoundError(f"Kanji dataset not found at: {md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Pattern for entries
    pattern = (
        r"###\s+(\d+)\.\s*([^\n]+)\n"
        r"-\s*\*\*Reading:\*\*\s*([^\n]+)\n"
        r"-\s*\*\*Meaning:\*\*\s*([^\n]+)\n"
        r"-\s*\*\*Related readings:\*\*\s*([^\n]+)\n"
        r"-\s*\*\*Studied kanji form:\*\*\s*([^\n]+)"
    )

    matches = re.findall(pattern, text)
    kanji_bank = []

    for item in matches:
        kid = int(item[0])
        kanji_char = item[1].strip()
        reading_raw = item[2].strip()
        meaning = item[3].strip()
        related_raw = item[4].strip()
        studied_raw = item[5].strip()

        # Parse primary reading: e.g. "にち (Nichi)" or "たべる (Taberu)"
        hiragana = ""
        romaji = ""
        read_match = re.match(r"^(.*?)\s*\((.*?)\)$", reading_raw)
        if read_match:
            hiragana = read_match.group(1).strip()
            romaji = read_match.group(2).strip()
        else:
            hiragana = reading_raw
            romaji = ""

        katakana = hiragana_to_katakana(hiragana)
        examples = parse_related_readings(related_raw, studied_raw)

        # Primary vocabulary item for featured word of the day
        featured_word = examples[0] if examples else {
            "kanji_form": kanji_char,
            "reading": hiragana,
            "katakana": katakana,
            "romaji": romaji,
            "meaning": meaning
        }

        kanji_bank.append({
            "id": kid,
            "kanji": kanji_char,
            "reading_raw": reading_raw,
            "hiragana": hiragana,
            "katakana": katakana,
            "romaji": romaji,
            "meaning": meaning,
            "jlpt": "N5",  # All 93 entries correspond to the foundation N5 syllabus
            "examples": examples,
            "featured_word": featured_word,
            "raw_related": related_raw,
            "raw_studied": studied_raw
        })

    return kanji_bank


def get_kanji_bank(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Retrieve kanji bank from JSON cache or parse from markdown."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not force_refresh and KANJI_BANK_JSON.exists():
        try:
            with open(KANJI_BANK_JSON, "r", encoding="utf-8") as f:
                bank = json.load(f)
                if bank and len(bank) >= 90:
                    return bank
        except Exception:
            pass

    bank = parse_kanji_markdown()
    with open(KANJI_BANK_JSON, "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=2)

    return bank


def get_daily_kanji(target_date_iso: str, jlpt_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Deterministically select one Kanji for the specified date (YYYY-MM-DD).
    Uses a seeded shuffle so that all kanji in the bank are visited once
    without repeats before repeating.
    """
    bank = get_kanji_bank()

    if jlpt_filter:
        bank = [k for k in bank if k.get("jlpt") == jlpt_filter]

    total_count = len(bank)
    if total_count == 0:
        raise ValueError("Kanji bank is empty!")

    # Parse date
    d_parts = [int(p) for p in target_date_iso.split("-")]
    d_obj = date(d_parts[0], d_parts[1], d_parts[2])

    day_offset = (d_obj - REFERENCE_DATE).days

    # Deterministic permutation of indices
    rng = random.Random(SELECTION_SEED)
    permutation = list(range(total_count))
    rng.shuffle(permutation)

    cycle_index = day_offset % total_count
    selected_idx = permutation[cycle_index]
    selected_kanji = bank[selected_idx]

    # Return a copy enriched with selection metadata
    res = dict(selected_kanji)
    res["cycle_day"] = cycle_index + 1
    res["cycle_total"] = total_count
    return res


if __name__ == "__main__":
    import pprint
    bank = get_kanji_bank(force_refresh=True)
    print(f"Loaded {len(bank)} kanji into {KANJI_BANK_JSON}")
    today_kanji = get_daily_kanji("2026-11-14")
    print("\nSelected Kanji for 2026-11-14:")
    pprint.pprint(today_kanji)
