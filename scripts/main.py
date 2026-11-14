#!/usr/bin/env python3
"""
Main Orchestration Script for Nihongo Daily.
Handles the 5 automated generation steps:
  Step 1 / csv:       Append/update data/dates.csv using Pandas (no duplicates)
  Step 2 / json:      Update data/today.json
  Step 3 / html:      Generate static index.html with Japanese editorial aesthetic
  Step 4 / date-svg:  Generate assets/today-date.svg
  Step 5 / kanji-svg: Generate assets/daily-kanji.svg and update README.md
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd

from date_generator import get_current_date
from kanji_generator import get_daily_kanji, get_kanji_bank
from svg_generator import generate_date_svg, generate_kanji_svg

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
DATES_CSV = DATA_DIR / "dates.csv"
TODAY_JSON = DATA_DIR / "today.json"
JOURNAL_JSON = DATA_DIR / "journal.json"
INDEX_HTML = BASE_DIR / "index.html"
README_MD = BASE_DIR / "README.md"


def get_dates_dataframe() -> pd.DataFrame:
    """Load or initialize the dates history DataFrame."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    columns = [
        "date", "gregorian", "japanese_date", "weekday_jp",
        "weekday_reading", "weekday_en", "era_jp",
        "kanji", "kanji_reading", "kanji_meaning", "jlpt",
        "updated_at"
    ]
    if DATES_CSV.exists() and DATES_CSV.stat().st_size > 0:
        try:
            df = pd.read_csv(DATES_CSV, dtype=str)
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=columns)


def step_1_csv(date_info: Dict[str, Any], kanji_info: Dict[str, Any]) -> bool:
    """
    Step 1: Update data/dates.csv using Pandas.
    Avoids duplicate entries if executed multiple times on the same date.
    Returns True if file was changed/created.
    """
    df = get_dates_dataframe()
    iso_date = date_info["iso_date"]

    new_row = {
        "date": iso_date,
        "gregorian": date_info["gregorian_en"],
        "japanese_date": date_info["japanese_date"],
        "weekday_jp": date_info["weekday_jp"],
        "weekday_reading": date_info["weekday_reading"],
        "weekday_en": date_info["weekday_en"],
        "era_jp": date_info["era_jp"],
        "kanji": kanji_info["kanji"],
        "kanji_reading": kanji_info["reading_raw"],
        "kanji_meaning": kanji_info["meaning"],
        "jlpt": kanji_info.get("jlpt", "N5"),
        "updated_at": date_info.get("updated_at_formatted", date_info["updated_at"])
    }

    if not df.empty and (df["date"] == iso_date).any():
        idx = df.index[df["date"] == iso_date][0]
        for col, val in new_row.items():
            df.at[idx, col] = val
        print(f"[Step 1: CSV] Updated existing record for {iso_date}.")
    else:
        new_df = pd.DataFrame([new_row])
        df = pd.concat([df, new_df], ignore_index=True)
        print(f"[Step 1: CSV] Appended new record for {iso_date}.")

    df = df.sort_values(by="date")
    df.to_csv(DATES_CSV, index=False, encoding="utf-8")
    return True


def step_2_json(date_info: Dict[str, Any], kanji_info: Dict[str, Any]) -> bool:
    """
    Step 2: Update data/today.json with rich structured daily data.
    Returns True if file was written.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    today_data = {
        "date": date_info["iso_date"],
        "gregorian": date_info["gregorian_en"],
        "japanese_date": date_info["japanese_date"],
        "weekday": date_info["weekday_jp"],
        "weekday_reading": date_info["weekday_reading"],
        "weekday_en": date_info["weekday_en"],
        "era_date": date_info["era_jp"],
        "era_traditional": date_info["era_traditional"],
        "wafuu_month": {
            "kanji": date_info["wafuu_month_kanji"],
            "romaji": date_info["wafuu_month_romaji"],
            "meaning": date_info["wafuu_month_meaning"]
        },
        "selected_kanji": {
            "id": kanji_info["id"],
            "kanji": kanji_info["kanji"],
            "reading_raw": kanji_info["reading_raw"],
            "hiragana": kanji_info["hiragana"],
            "katakana": kanji_info["katakana"],
            "romaji": kanji_info["romaji"],
            "meaning": kanji_info["meaning"],
            "jlpt": kanji_info["jlpt"],
            "examples": kanji_info.get("examples", []),
            "featured_word": kanji_info.get("featured_word", {}),
            "cycle_day": kanji_info.get("cycle_day", 1),
            "cycle_total": kanji_info.get("cycle_total", 93)
        },
        "updated_at": date_info["updated_at"]
    }

    with open(TODAY_JSON, "w", encoding="utf-8") as f:
        json.dump(today_data, f, ensure_ascii=False, indent=2)

    print(f"[Step 2: JSON] Updated {TODAY_JSON}")
    return True


def step_3_html(date_info: Dict[str, Any], kanji_info: Dict[str, Any]) -> bool:
    """
    Step 3: Generate the index.html website content.
    Includes date hero, daily kanji, vocabulary, calendar, journal, and stats.
    """
    df = get_dates_dataframe()
    total_days_recorded = len(df)
    unique_kanji_count = df["kanji"].nunique() if not df.empty else 1
    total_kanji_bank = len(get_kanji_bank())

    # Build vocab HTML
    vocab_html_items = []
    for ex in kanji_info.get("examples", []):
        form = ex.get("kanji_form", "")
        reading = ex.get("reading", "")
        romaji = ex.get("romaji", "")
        meaning = ex.get("meaning", "")
        vocab_html_items.append(f"""
          <div class="vocab-item">
            <div class="vocab-kanji">{form}</div>
            <div class="vocab-reading">{reading} <small style="color:var(--text-muted);">({romaji})</small></div>
            <div class="vocab-meaning">{meaning}</div>
            <button class="btn-audio" onclick="playJapaneseAudio('{form or reading}')" title="Pronounce">🔊 朗読</button>
          </div>
        """)
    vocab_html = "\n".join(vocab_html_items)

    # Build History cards HTML
    history_cards_html = []
    if not df.empty:
        # Show most recent records in reverse
        recent_records = df.tail(12).to_dict("records")[::-1]
        for r in recent_records:
            history_cards_html.append(f"""
              <div class="history-card" title="{r.get('gregorian','')} - {r.get('kanji_meaning','')}">
                <div class="history-kanji">{r.get('kanji','')}</div>
                <div class="history-reading">{r.get('kanji_reading','')}</div>
                <div class="history-date">{r.get('date','')}</div>
              </div>
            """)
    history_html = "\n".join(history_cards_html) if history_cards_html else "<p style='color:var(--text-muted);'>最初の記録を作成中…</p>"

    # Preload journal note if data/journal.json exists
    journal_notes_json_str = "{}"
    if JOURNAL_JSON.exists():
        try:
            with open(JOURNAL_JSON, "r", encoding="utf-8") as f:
                j_data = json.load(f)
                journal_notes_json_str = json.dumps(j_data, ensure_ascii=False)
        except Exception:
            pass

    # Calendar historical dates JSON
    recorded_dates_list = df["date"].tolist() if not df.empty else [date_info["iso_date"]]
    recorded_dates_json = json.dumps(recorded_dates_list)

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>日本語日録 · Nihongo Daily ({date_info['gregorian_en']})</title>
  <meta name="description" content="Automated Japanese daily calendar, daily Kanji learning, vocabulary study, and reflection journal.">
  <link rel="stylesheet" href="assets/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🇯🇵</text></svg>">
</head>
<body>
  <div class="page-container">
    <!-- Editorial Masthead -->
    <header class="masthead">
      <div class="masthead-inner">
        <div class="masthead-titles">
          <span class="publication-badge">Aesthetically Curated Japanese Journal · 日刊</span>
          <h1 class="main-title">日本語日録</h1>
          <p class="subtitle">Nihongo Daily — Daily Calendar, Kanji &amp; Reflection Journal</p>
        </div>
        <div class="masthead-meta">
          <div class="hanko-stamp">
            <span>日</span>
            <span>録</span>
          </div>
          <div class="vertical-accent">一日一文字</div>
          <div class="meta-edition">Vol. {date_info['year']} · No. {total_days_recorded} · 更新 {date_info['time_str']}</div>
        </div>
      </div>
    </header>

    <!-- Main Editorial 2-Column Grid -->
    <main class="editorial-grid">
      <!-- Left Column: Date & Kanji Primary Features -->
      <section class="grid-col-primary">
        <!-- Section A: Today's Date -->
        <article class="editorial-section">
          <div class="section-header">
            <div class="section-title-group">
              <h2 class="section-title-jp">本日の日付</h2>
              <span class="section-title-en">Today's Date</span>
            </div>
            <span class="section-tag">{date_info['timezone']}</span>
          </div>

          <div class="date-hero-grid">
            <div class="big-day-display">{date_info['day']}</div>
            <div class="date-details">
              <div class="date-era-kanji">{date_info['era_jp']}</div>
              <div class="date-gregorian-text">{date_info['gregorian_en']}</div>
              <div class="date-weekday-text">{date_info['weekday_jp']}（{date_info['weekday_reading']}）· {date_info['weekday_en']}</div>
              <div class="wafuu-badge">和風月名：{date_info['wafuu_month_kanji']}（{date_info['wafuu_month_romaji']} — {date_info['wafuu_month_meaning']}）</div>
            </div>
          </div>

          <!-- Embedded Vector Date Illustration -->
          <div class="svg-wrapper" title="Japanese Date Illustration">
            <img src="assets/today-date.svg" alt="Today's Date Illustration" loading="lazy">
          </div>
        </article>

        <!-- Section B: Daily Kanji Feature -->
        <article class="editorial-section">
          <div class="section-header">
            <div class="section-title-group">
              <h2 class="section-title-jp">本日の漢字</h2>
              <span class="section-title-en">Daily Kanji Study</span>
            </div>
            <span class="section-tag">Cycle {kanji_info.get('cycle_day', 1)} / {kanji_info.get('cycle_total', 93)}</span>
          </div>

          <div class="kanji-feature-card">
            <div class="kanji-char-box">
              <span class="jlpt-badge">JLPT {kanji_info['jlpt']}</span>
              <span class="kanji-huge-text">{kanji_info['kanji']}</span>
            </div>
            <div class="kanji-info-col">
              <div class="kanji-meaning">{kanji_info['meaning']}</div>
              <div class="readings-row">
                <span class="kana-pill">{kanji_info['hiragana']}</span>
                <span class="romaji-pill">({kanji_info['romaji']})</span>
                <span class="katakana-pill">カタカナ: {kanji_info['katakana']}</span>
              </div>
              <p style="color:var(--text-muted); font-size:0.9rem;">
                基本の読み方：<strong>{kanji_info['reading_raw']}</strong>
              </p>
              <button class="btn-audio" onclick="playJapaneseAudio('{kanji_info['kanji']}')" style="align-self: flex-start;">
                🔊 漢字の発音を聴く
              </button>
            </div>
          </div>

          <!-- Embedded Vector Kanji Illustration -->
          <div class="svg-wrapper" title="Daily Kanji Vector Art">
            <img src="assets/daily-kanji.svg" alt="Daily Kanji Flashcard" loading="lazy">
          </div>

          <!-- Vocabulary Study List -->
          <h3 style="font-family:var(--font-serif-jp); font-size:1.1rem; margin-top:24px; color:var(--text-primary); border-bottom: 1px solid var(--border-delicate); padding-bottom:6px;">
            関連語彙 · Featured Vocabulary
          </h3>
          <div class="vocab-list">
            {vocab_html}
          </div>
        </article>
      </section>

      <!-- Right Column: Calendar, Daily Journal & History -->
      <section class="grid-col-sidebar">
        <!-- Section C: Interactive Japanese Calendar -->
        <article class="editorial-section calendar-card">
          <div class="section-header">
            <div class="section-title-group">
              <h2 class="section-title-jp">暦 · カレンダー</h2>
              <span class="section-title-en">Calendar</span>
            </div>
            <span class="section-tag">{date_info['year']}年</span>
          </div>

          <div class="calendar-header">
            <button class="calendar-nav-btn" onclick="changeMonth(-1)">◀ 前月</button>
            <div class="calendar-month-title" id="calendarMonthTitle">{date_info['month']}月</div>
            <button class="calendar-nav-btn" onclick="changeMonth(1)">翌月 ▶</button>
          </div>

          <table class="calendar-grid-table">
            <thead>
              <tr>
                <th class="cal-sunday">日</th>
                <th>月</th>
                <th>火</th>
                <th>水</th>
                <th>木</th>
                <th>金</th>
                <th class="cal-saturday">土</th>
              </tr>
            </thead>
            <tbody id="calendarGridBody">
              <!-- Rendered via JS -->
            </tbody>
          </table>
          <p style="font-size:0.75rem; color:var(--text-muted); margin-top:12px; text-align:right;">
            ● 記録日 | 赤枠：本日
          </p>
        </article>

        <!-- Section D: Daily Journal (Persists & Non-overwriting) -->
        <article class="editorial-section">
          <div class="section-header">
            <div class="section-title-group">
              <h2 class="section-title-jp">日々の日記</h2>
              <span class="section-title-en">Daily Journal</span>
            </div>
            <span class="section-tag" id="journalDateLabel">{date_info['iso_date']}</span>
          </div>
          <div class="journal-box">
            <p style="font-size:0.85rem; color:var(--text-muted);">
              本日の学びや感想を書き留めておきましょう（自動更新で上書きされません）。
            </p>
            <textarea id="journalInput" class="journal-textarea" placeholder="今日の漢字について学んだこと、メモ、日記をここに記入…"></textarea>
            <div class="journal-toolbar">
              <button class="btn-editorial" onclick="saveJournalNote()">保存する (Save)</button>
              <button class="btn-secondary" onclick="exportJournalNotes()">書き出し (Export)</button>
              <span id="journalSavedHint" class="journal-saved-hint">✓ 保存完了</span>
            </div>
          </div>
        </article>

        <!-- Section E: Learning History & Stats -->
        <article class="editorial-section">
          <div class="section-header">
            <div class="section-title-group">
              <h2 class="section-title-jp">学習記録</h2>
              <span class="section-title-en">Progress &amp; Archives</span>
            </div>
          </div>

          <div class="stats-banner">
            <div class="stat-item">
              <div class="stat-number">{total_days_recorded}</div>
              <div class="stat-label">記録日数</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{unique_kanji_count}</div>
              <div class="stat-label">習得漢字</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{total_kanji_bank}</div>
              <div class="stat-label">総収録数</div>
            </div>
          </div>

          <h3 style="font-family:var(--font-serif-jp); font-size:1rem; margin-bottom:12px; color:var(--text-primary);">
            最近の漢字履歴 (Recent Kanji)
          </h3>
          <div class="history-cards-grid">
            {history_html}
          </div>
        </article>
      </section>
    </main>

    <!-- Editorial Footer -->
    <footer class="editorial-footer">
      <div>
        <p class="footer-kanji-quote">日日是好日（にちにちこれこうじつ）— Every day is a fine day.</p>
        <p style="margin-top:4px;">Nihongo Daily · Automated Japanese Journal · Powered by GitHub Actions &amp; Pages</p>
      </div>
      <div>
        <a href="data/dates.csv" download style="color:var(--accent-indigo); text-decoration:none; margin-right:16px;">📥 dates.csv</a>
        <a href="data/today.json" target="_blank" style="color:var(--accent-indigo); text-decoration:none;">📄 today.json</a>
      </div>
    </footer>
  </div>

  <!-- Interactive JavaScript Logic -->
  <script>
    const TODAY_ISO = "{date_info['iso_date']}";
    const RECORDED_DATES = new Set({recorded_dates_json});
    const INITIAL_JOURNAL_STORE = {journal_notes_json_str};

    let currentCalYear = {date_info['year']};
    let currentCalMonth = {date_info['month']}; // 1-12

    // Audio Pronunciation using Web Speech API
    function playJapaneseAudio(text) {{
      if (!('speechSynthesis' in window)) {{
        alert("お使いのブラウザは音声合成に対応していません。");
        return;
      }}
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'ja-JP';
      utterance.rate = 0.85; // Natural learning pace
      window.speechSynthesis.speak(utterance);
    }}

    // Calendar Generation
    function renderCalendar(year, month) {{
      const monthTitle = document.getElementById("calendarMonthTitle");
      const gridBody = document.getElementById("calendarGridBody");
      
      const monthNames = ["睦月 · 1月", "如月 · 2月", "弥生 · 3月", "卯月 · 4月", "皐月 · 5月", "水無月 · 6月",
                          "文月 · 7月", "葉月 · 8月", "長月 · 9月", "神無月 · 10月", "霜月 · 11月", "師走 · 12月"];
      monthTitle.textContent = `${{year}}年 ${{monthNames[month - 1]}}`;

      gridBody.innerHTML = "";
      const firstDay = new Date(year, month - 1, 1).getDay(); // 0 is Sun
      const daysInMonth = new Date(year, month, 0).getDate();

      let row = document.createElement("tr");
      for (let i = 0; i < firstDay; i++) {{
        const emptyCell = document.createElement("td");
        emptyCell.className = "empty";
        row.appendChild(emptyCell);
      }}

      for (let day = 1; day <= daysInMonth; day++) {{
        if (row.children.length === 7) {{
          gridBody.appendChild(row);
          row = document.createElement("tr");
        }}

        const cell = document.createElement("td");
        cell.textContent = day;

        const padM = String(month).padStart(2, '0');
        const padD = String(day).padStart(2, '0');
        const cellDate = `${{year}}-${{padM}}-${{padD}}`;

        if (cellDate === TODAY_ISO) {{
          cell.classList.add("today");
        }}
        if (RECORDED_DATES.has(cellDate)) {{
          cell.classList.add("has-record");
          cell.title = `記録あり: ${{cellDate}}`;
        }}

        row.appendChild(cell);
      }}

      while (row.children.length < 7) {{
        const emptyCell = document.createElement("td");
        emptyCell.className = "empty";
        row.appendChild(emptyCell);
      }}
      gridBody.appendChild(row);
    }}

    function changeMonth(delta) {{
      currentCalMonth += delta;
      if (currentCalMonth < 1) {{
        currentCalMonth = 12;
        currentCalYear--;
      }} else if (currentCalMonth > 12) {{
        currentCalMonth = 1;
        currentCalYear++;
      }}
      renderCalendar(currentCalYear, currentCalMonth);
    }}

    // Daily Journal Persistence (LocalStorage + Preloaded Store)
    const JOURNAL_KEY = "nihongo_daily_journal_notes";

    function getJournalStorage() {{
      try {{
        const local = localStorage.getItem(JOURNAL_KEY);
        const data = local ? JSON.parse(local) : {{}};
        return Object.assign({{}}, INITIAL_JOURNAL_STORE, data);
      }} catch (e) {{
        return INITIAL_JOURNAL_STORE || {{}};
      }}
    }}

    function loadJournalNoteForToday() {{
      const store = getJournalStorage();
      const input = document.getElementById("journalInput");
      if (store[TODAY_ISO]) {{
        input.value = store[TODAY_ISO];
      }}
    }}

    function saveJournalNote() {{
      const input = document.getElementById("journalInput");
      const store = getJournalStorage();
      store[TODAY_ISO] = input.value;
      try {{
        localStorage.setItem(JOURNAL_KEY, JSON.stringify(store));
      }} catch (e) {{}}

      const hint = document.getElementById("journalSavedHint");
      hint.classList.add("visible");
      setTimeout(() => hint.classList.remove("visible"), 2500);
    }}

    function exportJournalNotes() {{
      const store = getJournalStorage();
      const blob = new Blob([JSON.stringify(store, null, 2)], {{ type: "application/json" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `nihongo-daily-journal-${{TODAY_ISO}}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }}

    // Initialization
    document.addEventListener("DOMContentLoaded", () => {{
      renderCalendar(currentCalYear, currentCalMonth);
      loadJournalNoteForToday();
    }});
  </script>
</body>
</html>
"""

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[Step 3: HTML] Generated {INDEX_HTML}")
    return True


def step_4_date_svg(date_info: Dict[str, Any]) -> bool:
    """
    Step 4: Generate assets/today-date.svg.
    """
    svg_path = generate_date_svg(date_info)
    print(f"[Step 4: Date SVG] Generated {svg_path}")
    return True


def step_5_kanji_svg_and_readme(date_info: Dict[str, Any], kanji_info: Dict[str, Any]) -> bool:
    """
    Step 5: Generate assets/daily-kanji.svg and update README.md.
    """
    # Generate SVG
    svg_path = generate_kanji_svg(kanji_info, date_info)
    print(f"[Step 5: Kanji SVG] Generated {svg_path}")

    # Load statistics
    df = get_dates_dataframe()
    total_days = len(df)
    unique_kanji = df["kanji"].nunique() if not df.empty else 1
    total_bank = len(get_kanji_bank())

    # Build README table of examples
    examples_md = []
    for ex in kanji_info.get("examples", []):
        form = ex.get("kanji_form", "")
        reading = ex.get("reading", "")
        romaji = ex.get("romaji", "")
        meaning = ex.get("meaning", "")
        examples_md.append(f"- **{form}** (`{reading}` / *{romaji}*): {meaning}")
    examples_str = "\n".join(examples_md)

    readme_content = f"""# nihongo-daily 🇯🇵

> An automated Japanese-inspired daily calendar, Kanji flashcard, vocabulary study, and learning journal. Updated every single day through GitHub Actions in `Asia/Karachi` time.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5"/>
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3"/>
  <img src="https://img.shields.io/badge/SVG-FFB13B?style=for-the-badge&logo=svg&logoColor=white" alt="SVG"/>
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git"/>
  <img src="https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white" alt="JSON"/>
  <img src="https://img.shields.io/badge/CSV-217346?style=for-the-badge&logo=apacheparquet&logoColor=white" alt="CSV"/>
  <img src="https://img.shields.io/badge/PDF-EC1C24?style=for-the-badge&logo=adobeacrobatreader&logoColor=white" alt="PDF"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas"/>
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions"/>
</p>

[![Daily Update](https://github.com/mussab/nihongo-daily/actions/workflows/daily.yml/badge.svg)](https://github.com/mussab/nihongo-daily/actions/workflows/daily.yml)
[![Pages Deployment](https://img.shields.io/badge/GitHub_Pages-Active-success?logo=github)](index.html)
[![Timezone](https://img.shields.io/badge/Timezone-Asia%2FKarachi-45566B)](https://time.is/Karachi)
[![JLPT Level](https://img.shields.io/badge/JLPT-N5-B64032)](materials/kanji.md)

---

## 📅 Today's Date · 本日の日付

<div align="center">
  <img src="assets/today-date.svg" alt="Today's Japanese Date" width="680"/>
</div>

<br/>

| Attribute | Details |
| :--- | :--- |
| **Gregorian Date** | {date_info['gregorian_en']} (`{date_info['iso_date']}`) |
| **Japanese Date** | {date_info['japanese_date']} |
| **Reiwa Era** | {date_info['era_jp']} ({date_info['era_traditional']}) |
| **Weekday** | {date_info['weekday_jp']}（{date_info['weekday_reading']} · {date_info['weekday_en']}） |
| **Traditional Month** | {date_info['wafuu_month_kanji']}（{date_info['wafuu_month_romaji']} — {date_info['wafuu_month_meaning']}） |

---

## 🈁 Daily Kanji · 本日の漢字

<div align="center">
  <img src="assets/daily-kanji.svg" alt="Today's Daily Kanji" width="680"/>
</div>

### {kanji_info['kanji']} — {kanji_info['meaning']}

- **JLPT Level:** `{kanji_info['jlpt']}` (Cycle Day {kanji_info.get('cycle_day', 1)} of {kanji_info.get('cycle_total', 93)})
- **Reading:** `{kanji_info['reading_raw']}`
- **Hiragana:** `{kanji_info['hiragana']}`
- **Katakana:** `{kanji_info['katakana']}`
- **Romaji:** *{kanji_info['romaji']}*

#### 📖 Related Vocabulary &amp; Studied Forms
{examples_str}

---

## 📊 Learning Statistics

- **Total Days Recorded:** `{total_days}`
- **Unique Kanji Studied:** `{unique_kanji}`
- **Total Kanji Collection:** `{total_bank}` (Foundation N5 Collection)
- **Timezone Anchor:** `Asia/Karachi` (Last synchronized: `{date_info.get('updated_at_formatted', date_info['iso_date'])}`)

---

## 🏛️ Authentic Japanese Editorial Design

The website and vector graphics are designed with a traditional Japanese stationery and editorial aesthetic:
- **Washi Paper Palette:** Warm washi ecru (`#F5F0E6`), sumi black ink (`#25251F`), cinnabar vermilion stamp red (`#B64032`), and indigo iron (`#45566B`).
- **Typography:** `Noto Serif JP`, `Noto Sans JP`, and `Cormorant Garamond`.
- **Hanko Stamps:** Authentic Japanese cinnabar seal stamps for daily authenticity.
- **Interactive Calendar:** Monthly navigation highlighting recorded history.
- **Non-Overwriting Journal:** LocalStorage and JSON-persisted daily notes.

---

## 📁 Repository Structure

```
nihongo-daily/
│
├── .github/
│   └── workflows/
│       └── daily.yml             # GitHub Actions workflow (5 daily commits)
│
├── materials/                    # Study source materials directory
│   ├── kanji.md                  # Complete 93-Kanji N5 curriculum guide
│   └── Under 100 Kanjis_v3.pdf   # Foundational Kanji study guide reference
│
├── scripts/
│   ├── main.py                   # Automated pipeline runner (--step, --all)
│   ├── date_generator.py         # Timezone & Japanese era calculations
│   ├── kanji_generator.py        # Kanji parser & deterministic daily selector
│   └── svg_generator.py          # Vector date & kanji stationery generators
│
├── data/
│   ├── dates.csv                 # Cumulative history of daily records (Pandas)
│   ├── today.json                # Today's structured JSON data
│   ├── kanji_bank.json           # Parsed 93-Kanji dictionary database
│   └── journal.json              # Preserved user reflections storage
│
├── assets/
│   ├── today-date.svg            # Vector Japanese date calendar card
│   ├── daily-kanji.svg           # Vector daily Kanji practice card
│   └── style.css                 # Authentic Japanese editorial styling
│
├── index.html                    # Live web journal & calendar application
├── README.md                     # Live repository dashboard
└── requirements.txt              # Python dependencies
```

---

## 🔄 Five Daily Commits Architecture

To maintain an authentic daily contribution history, the GitHub Actions workflow commits file updates across five independent stages:

1. **Commit 1 (CSV):** `data/dates.csv` — Appends today's record using Pandas (strictly avoids duplicates).
2. **Commit 2 (JSON):** `data/today.json` — Stores structured JSON for APIs and integrations.
3. **Commit 3 (HTML):** `index.html` — Rebuilds the static journal website with the latest date & kanji.
4. **Commit 4 (Date SVG):** `assets/today-date.svg` — Generates the vector date stationery illustration.
5. **Commit 5 (Kanji SVG & README):** `assets/daily-kanji.svg` and `README.md` — Renders the daily kanji flashcard and dashboard.

---

## 🚀 Setup & Automation

### Running Locally

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run all generation steps
python scripts/main.py --all

# Or run individual stages:
python scripts/main.py --step csv
python scripts/main.py --step json
python scripts/main.py --step html
python scripts/main.py --step date-svg
python scripts/main.py --step kanji-svg
```

### Enabling GitHub Pages, Actions & Personal Account Commits

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit of nihongo-daily"
   git push -u origin main
   ```
2. **Configure Repository Secrets (for your personal commit credit):**
   Go to your repository **Settings** > **Secrets and variables** > **Actions** and add:
   * `GIT_USER_NAME`: Your GitHub username or name (e.g., `Mussab`)
   * `GIT_USER_EMAIL`: Your GitHub account email address (e.g., your primary or `@users.noreply.github.com` email)
   * `GH_PAT`: A Personal Access Token (classic with `repo` scope, or fine-grained with Contents read/write) so the commits are attributed to your personal account and contribute to your activity graph.
3. **Enable Workflow Permissions:**
   - Go to **Settings** > **Actions** > **General** > **Workflow permissions**.
   - Select **Read and write permissions** and check **Allow GitHub Actions to create and approve pull requests**.
4. **Enable GitHub Pages:**
   - Go to **Settings** > **Pages**.
   - Under **Build and deployment**, select **Deploy from a branch**.
   - Set Branch to `main`, folder to `/ (root)`, and click **Save**.
"""

    with open(README_MD, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"[Step 5: README] Updated {README_MD}")
    return True


def run_pipeline(step: Optional[str] = None, target_date: Optional[str] = None):
    """Orchestrate the required generation step(s)."""
    date_info = get_current_date(target_date)
    kanji_info = get_daily_kanji(date_info["iso_date"])

    step_map = {
        "1": "csv",
        "csv": "csv",
        "2": "json",
        "json": "json",
        "3": "html",
        "html": "html",
        "4": "date-svg",
        "date-svg": "date-svg",
        "datesvg": "date-svg",
        "5": "kanji-svg",
        "kanji-svg": "kanji-svg",
        "kanjisvg": "kanji-svg",
        "all": "all"
    }

    action = step_map.get(step.lower() if step else "all", "all")

    if action in ("csv", "all"):
        step_1_csv(date_info, kanji_info)
    if action in ("json", "all"):
        step_2_json(date_info, kanji_info)
    if action in ("html", "all"):
        step_3_html(date_info, kanji_info)
    if action in ("date-svg", "all"):
        step_4_date_svg(date_info)
    if action in ("kanji-svg", "all"):
        step_5_kanji_svg_and_readme(date_info, kanji_info)


def main():
    parser = argparse.ArgumentParser(description="Nihongo Daily Generator")
    parser.add_argument(
        "--step",
        choices=["csv", "json", "html", "date-svg", "kanji-svg", "1", "2", "3", "4", "5", "all"],
        default="all",
        help="Specify which generation step to run (default: all)"
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Target date in YYYY-MM-DD format (defaults to current date in Asia/Karachi)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all 5 generation steps in sequence"
    )

    args = parser.parse_args()
    step = "all" if args.all else args.step
    run_pipeline(step=step, target_date=args.date)


if __name__ == "__main__":
    main()
