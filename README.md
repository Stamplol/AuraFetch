# ⬢ AuraFetch — YouTube to MP3 / MP4

> Clean, fast, no-BS desktop app to download YouTube videos as **MP3 (320kbps)** or **MP4 (up to 4K)**. Playlists, Shorts, and chapter splitting included.

![License](https://img.shields.io/badge/license-MIT-green) ![Python](https://img.shields.io/badge/python-3.9%2B-blue) ![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey) ![yt-dlp](https://img.shields.io/badge/powered%20by-yt--dlp-red)

### ⚠️ Vibe-Coded Disclaimer

Yes, this was **vibe-coded** — built fast with AI assistance, late nights, and a lot of iteration. The code isn't trying to win awards for architecture. **Why? Because I suck at UI design** — so I let AI do the heavy lifting on the pretty parts while I focused on making it actually work. And it **works really well**: it's fast, looks good, has zero ads/limits, and solves a real problem. Feel free to judge the process, but try the app first. PRs to make it less vibey (or more pretty) are welcome.

---

## ✨ Features

- **MP3 & MP4** — MP3 at 128/192/256/320 kbps, MP4 at 360p / 480p / 720p / 1080p / Best (4K)
- **Playlists & Shorts** — toggle "Entire playlist" to batch-download
- **Chapter Split** — split podcasts / mixes by YouTube chapters (requires ffmpeg)
- **Preview** — thumbnail, title, channel, duration, views and upload year before downloading
- **Smart fallbacks** — never dies with "Requested format is not available"
- **Progress** — real speed, ETA, and progress bar (not a fake spinner)
- **Cross-platform** — Windows, macOS, Linux
- **No ads, no limits, no telemetry**

## 📸 Preview

> Dark modern UI built with CustomTkinter. Card layout, pill stats, segmented MP3/MP4 switch.

```
[ Paste YouTube link ] [ Paste ] [ Fetch ]
[  Thumbnail  3:42   ]  Title / Channel / ⏱ 👁 📅
[ FORMAT: MP3 | MP4 ] [ QUALITY ] [ SAVE TO: ~/Downloads ]
[ ☐ Entire playlist · ☐ Split chapters ]  Idle
[ Progress  42% ████████░░░░ ]  2.4 MiB/s  ETA 00:12
[ ⬇ Download MP3 • 320 kbps ]
```

## 🚀 Quick Start

### Option 1 — Run from source (recommended for dev)

```bash
git clone https://github.com/YOUR_USERNAME/aurafetch.git
cd aurafetch
pip install -r requirements.txt
python app.py
```

Windows double-click: `run.bat` · macOS/Linux: `bash run.sh`

### Option 2 — Binary (no Python needed)

Download from **Releases** (or build it yourself — see below):

- **Windows:** `AuraFetch.exe` — double click to run
- **macOS:** `AuraFetch.app` / `AuraFetch` — right-click → Open on first run
- **Linux:** `AuraFetch` — `chmod +x AuraFetch && ./AuraFetch`

> Binaries are ~40-60 MB (Python + Tk bundled). This is normal for PyInstaller.

## 📦 Installation

**Requirements:** Python 3.9+, ffmpeg (optional but strongly recommended)

```bash
# clone
git clone https://github.com/YOUR_USERNAME/aurafetch.git
cd aurafetch

# venv (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

**ffmpeg:**

| OS | Install |
|---|---|
| Windows | `winget install ffmpeg` or `choco install ffmpeg` or download from https://ffmpeg.org |
| macOS | `brew install ffmpeg` |
| Linux | `sudo apt install ffmpeg` / `sudo dnf install ffmpeg` / `sudo pacman -S ffmpeg` |

Verify: `ffmpeg -version` — app shows `● ffmpeg ready` when detected.

## 🖱️ Usage

1. Paste a YouTube link (video, Short, or playlist) → it auto-fetches
2. Check the preview, pick **MP3** or **MP4** and quality
3. Choose save folder (defaults to `~/Downloads`)
4. Toggle **Entire playlist** / **Split chapters** if needed
5. Hit **Download** — watch progress and find file in your folder

Tips: `Ctrl+V` pastes and fetches instantly. `Enter` in the URL bar also fetches.

## 🔨 Build a Binary

AuraFetch uses **PyInstaller** to compile to a single-file executable.

### Prerequisites

```bash
pip install -r requirements.txt  # includes pyinstaller now
```

### Build

**Windows:**
```bat
build.bat
:: output: dist\AuraFetch.exe
```

**macOS / Linux:**
```bash
bash build.sh
# output: dist/AuraFetch
```

**Manual (any OS):**
```bash
pyinstaller --noconfirm --clean --onefile --windowed --name AuraFetch --collect-all customtkinter app.py
# single file will be in dist/
```

> `--windowed` hides the console on Windows/macOS. Use `--console` if you want logs. On Linux, PyInstaller builds are not cross-compilable — build on the OS you target.

**Spec file:** `AuraFetch.spec` is included for reproducible builds. Edit it if you add icons or data files:
```bash
pyinstaller AuraFetch.spec
```

**App icon (optional):** Place `icon.ico` (Windows) / `icon.icns` (macOS) / `icon.png` (Linux) in the project root and rebuild — the spec auto-picks it up if present.

## 🛠️ Troubleshooting — YouTube vs. The Scraper

YouTube changes its player and throttling constantly. `yt-dlp` is in a permanent cat-and-mouse game. If downloads break, it's almost always fixable.

### 1. "Unable to extract" / "Video unavailable" / 403 / 429

**Cause:** YouTube changed its signature or your `yt-dlp` is outdated.

**Fix:**
```bash
pip install -U yt-dlp
# or if using binary, rebuild after updating:
pip install -U yt-dlp && bash build.sh
```
Check latest release: https://github.com/yt-dlp/yt-dlp/releases — if your version is >1 week old, update.

Still failing? Try:
```bash
yt-dlp --update
yt-dlp --verbose "https://www.youtube.com/watch?v=BaW_jenozKc"
```
If that fails outside AuraFetch too, it's an upstream yt-dlp issue — wait for a patch (usually <24h).

### 2. "Requested format is not available"

AuraFetch already handles this with fallback formats (`bv*+ba/b`, `bestaudio/best`). If you still see it:

- Switch **Quality** to `Best` (MP4) or `320 kbps` (MP3)
- Update yt-dlp (see above)
- Check if the video is **members-only / private / region-locked** — those can't be downloaded without auth

### 3. "ffmpeg not found" / MP3 is .webm/.m4a instead of .mp3

Install ffmpeg (see Installation) and restart the app. Without ffmpeg, AuraFetch saves the raw best-audio stream as fallback.

### 4. Downloads are slow / throttled (Especially on 1080p+)

YouTube throttles non-browser clients. Fixes:

- Update yt-dlp — it includes `n` and `m` throttling workarounds
- The app already uses `concurrent_fragment_downloads=4` and `http_chunk_size=10M` to help
- Try lower quality (720p is often much faster)
- Some networks/VPNs are throttled harder — try without VPN

### 5. "Sign in to confirm you're not a bot"

Age-restricted / bot-check videos need cookies:

1. Install browser extension **Get cookies.txt LOCALLY**
2. Export cookies for `youtube.com`
3. Save as `cookies.txt` next to `app.py` (or next to `AuraFetch.exe`)
4. AuraFetch will auto-use it if you add to yt-dlp opts — or run manually:
```bash
yt-dlp --cookies cookies.txt "URL"
```

> To enable in the app, add `"cookiefile": "cookies.txt"` to `base_opts` in `app.py`.

### 6. Playlist only downloads first video

Enable the **Entire playlist** switch before fetching. It's `noplaylist=False` under the hood.

### 7. Antivirus flags the .exe

False positive — PyInstaller one-file exes are often flagged (especially with `requests` + `yt-dlp`). Solutions: add an exception, build from source, or use `pipx` run without binary.

### 8. App won't start / blank window (Linux)

```bash
sudo apt install python3-tk tk-dev
pip install --force-reinstall customtkinter
```

### Still broken?

1. Run from source with console to see the real error: `python app.py`
2. Test the URL with yt-dlp directly: `yt-dlp -F "URL"`
3. Open an issue with: OS, Python version, `yt-dlp --version`, full error, and URL (if public)

## 🧰 Tech Stack

- **Python** + **CustomTkinter** (UI), **yt-dlp** (extraction), **Pillow** (thumbnails), **requests**
- No backend, no API keys, no tracking

## 📁 Project Structure

```
.
├── app.py              # Main app — single-file Tk app
├── requirements.txt    # Deps (incl. pyinstaller for building)
├── AuraFetch.spec      # PyInstaller spec (onefile, windowed)
├── build.bat / build.sh# One-click build scripts
├── run.bat / run.sh    # Quick run without building
├── .gitignore
└── README.md
```

## ⚖️ Legal

This tool is for **personal use** only. Only download content you have rights to. Respect YouTube's Terms of Service and creators' copyright. The authors are not responsible for misuse.

## 🤝 Contributing

Vibe-coded or not, contributions are welcome:

```bash
git checkout -b feat/my-feature
# make changes, test on at least one OS
pip install ruff && ruff check app.py
```

Open a PR — please include OS tested + yt-dlp version.

## 📄 License

MIT — do whatever you want, just don't blame us.

---

Made with ♥ and a little AI. If AuraFetch saved you time, give it a ⭐.
