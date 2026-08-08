<h1 align="center">
  <b>˹ 𝞚𝙡𝞸𝞰𝞮 ✗ 𝙈𝙪𝙨𝙞𝙘 ♪ ˼</b>
</h1>

<p align="center">
  <img src="https://files.catbox.moe/pd8fv9.jpg" alt="AloneX Music Bot Logo" width="350">
</p>

<p align="center">
  <b>A powerful, high-performance Telegram Music & Video Streaming Bot powered by Pyrogram v2 and Py-Tgcalls.</b>
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python" alt="Python"></a>
  <a href="https://github.com/pyrogram/pyrogram"><img src="https://img.shields.io/badge/Pyrogram-v2-orange?style=for-the-badge&logo=telegram" alt="Pyrogram"></a>
  <a href="https://render.com"><img src="https://img.shields.io/badge/Render-Ready-brightgreen?style=for-the-badge&logo=render" alt="Render"></a>
  <a href="https://railway.app"><img src="https://img.shields.io/badge/Railway-Ready-purple?style=for-the-badge&logo=railway" alt="Railway"></a>
</p>

---

## 🚀 Quick One-Click Deployments

Deploy AloneX Music Bot effortlessly on cloud hosting providers:

<p align="center">
  <a href="https://render.com/deploy"><img src="https://render.com/images/deploy-to-render.svg" alt="Deploy to Render" height="38"></a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://railway.app/new"><img src="https://railway.app/button.svg" alt="Deploy on Railway" height="38"></a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://heroku.com/deploy"><img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku" height="38"></a>
</p>

---

## ✨ Features

- 🎵 **High-Quality Audio & Video**: Crystal clear voice chat streaming with HD 720p video support.
- 🌐 **Render & Railway Compatible**: Built-in HTTP web server listening on dynamic `PORT` for automatic health checks.
- ⚡ **Super Fast & Lightweight**: Powered by Pyrogram v2 and `ntgcalls`.
- 🎛️ **Interactive Controls**: Inline buttons for Play, Pause, Resume, Skip, Stop, and Loop.
- 🛠️ **Multi-Assistant Support**: Connect up to 3 userbot assistant accounts for load balancing.
- 🔍 **YouTube & Search Integration**: Instant YouTube video/audio download and streaming.
- 🌐 **Multi-Language Support**: Multilingual interface for worldwide communities.

---

## 🛠️ Required Environment Variables

Configure the following variables in your hosting environment (`.env` file or cloud dashboard):

| Variable | Description | Example / Default | Required |
| :--- | :--- | :--- | :---: |
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) | `12345678` | **Yes** |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org) | `abcdef12345...` | **Yes** |
| `BOT_TOKEN` | Bot Token from Telegram [@BotFather](https://t.me/BotFather) | `123456:ABC...` | **Yes** |
| `MONGO_URL` | MongoDB Connection URI from [MongoDB Atlas](https://cloud.mongodb.com) | `mongodb+srv://...` | **Yes** |
| `LOGGER_ID` | Telegram Log Group ID (bot must be admin) | `-1001234567890` | **Yes** |
| `OWNER_ID` | Telegram User ID of Bot Owner | `1234567890` | **Yes** |
| `SESSION` | Pyrogram v2 String Session for Assistant account | `1B...` | **Yes** |
| `PORT` | Dynamic HTTP port for health check server | `8080` | Optional |
| `AUTO_END` | Automatically end stream when queue finishes | `False` | Optional |
| `AUTO_LEAVE` | Automatically leave Voice Chat when idle | `False` | Optional |
| `VIDEO_PLAY` | Enable video playback capability | `True` | Optional |

---

## 📖 Deployment Guides

### 1. Deploying on Render (Recommended)

1. Fork this repository to your GitHub account.
2. Sign in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** -> Select **Web Service**.
4. Connect your GitHub repository.
5. Set the settings:
   - **Environment**: `Python 3` (or `Docker`)
   - **Build Command**: `pip install -U pip && pip install -r requirements.txt`
   - **Start Command**: `python3 -m AloneX`
6. Add all required **Environment Variables** under the Environment tab.
7. Click **Create Web Service**. Render will automatically verify port `8080` (or `$PORT`) via `/healthz`.

### 2. Deploying on Railway

1. Sign in to [Railway.app](https://railway.app).
2. Click **New Project** -> Select **Deploy from GitHub Repo**.
3. Choose your forked repository.
4. Go to **Variables** and add all required environment variables (`API_ID`, `BOT_TOKEN`, `MONGO_URL`, `SESSION`, etc.).
5. Railway will automatically detect `railway.json` and start the bot with dynamic health check monitoring on `/healthz`.

---

## 💻 Local Machine Setup & Installation

### Prerequisites

- **Python 3.11+**
- **FFmpeg** installed and added to system `PATH`
- **Git**

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/SayaTeam/AloneX.git
   cd AloneX
   ```

2. **Install Dependencies**:
   ```bash
   pip3 install -U pip
   pip3 install -U -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `sample.env` to `.env` and fill in your details:
   ```bash
   cp sample.env .env
   ```

4. **Run the Bot**:
   ```bash
   python3 -m AloneX
   ```

---

## 🐳 Docker Deployment

1. **Build Docker Image**:
   ```bash
   docker build -t alonex-music .
   ```

2. **Run Container**:
   ```bash
   docker run -d --name alonex --env-file .env -p 8080:8080 alonex-music
   ```

---

## 📌 Bot Commands

| Command | Description |
| :--- | :--- |
| `/play <song name / link>` | Stream audio in group voice chat |
| `/vplay <video name / link>` | Stream video in group voice chat |
| `/pause` | Pause current playing stream |
| `/resume` | Resume paused stream |
| `/skip` | Skip current track to next track in queue |
| `/stop` or `/end` | Stop stream and clear queue |
| `/ping` or `/alive` | Check bot uptime & system latency |
| `/queue` | View current music queue |
| `/settings` | Open interactive bot configuration menu |

---

## 📄 License & Credits

- Distributed under the **MIT License**.
- Built with ❤️ by [Alone Coder](https://t.me/ErrorQuote).
