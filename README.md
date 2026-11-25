# nihongo-daily 🇯🇵

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
| **Gregorian Date** | November 26, 2026 (`2026-11-26`) |
| **Japanese Date** | 2026年11月26日 |
| **Reiwa Era** | 令和8年11月26日 (令和八年 十一月二十六日) |
| **Weekday** | 木曜日（もくようび · Thursday） |
| **Traditional Month** | 霜月（Shimotsuki — Month of Frost） |

---

## 🈁 Daily Kanji · 本日の漢字

<div align="center">
  <img src="assets/daily-kanji.svg" alt="Today's Daily Kanji" width="680"/>
</div>

### 来 — Come

- **JLPT Level:** `N5` (Cycle Day 51 of 93)
- **Reading:** `くる (Kuru)`
- **Hiragana:** `くる`
- **Katakana:** `クル`
- **Romaji:** *Kuru*

#### 📖 Related Vocabulary &amp; Studied Forms
- **来る** (`くる` / *Kuru*): To come
- **来年** (`らいねん` / *Rainen*): Next year
- **来月** (`らいげつ` / *Raigetsu*): Next month

---

## 📊 Learning Statistics

- **Total Days Recorded:** `13`
- **Unique Kanji Studied:** `13`
- **Total Kanji Collection:** `93` (Foundation N5 Collection)
- **Timezone Anchor:** `Asia/Karachi` (Last synchronized: `2026-11-26 04:44:16 PKT`)

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
