<h1 align="center">🎭 HOLY REMIX</h1>
<p align="center"><b>AI-Powered Scripture Reimagined</b></p>
<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue.svg"></a>
  <a href="https://aws.amazon.com/bedrock/"><img src="https://img.shields.io/badge/AWS-Bedrock-orange.svg"></a>
  <a href="https://www.deepseek.com/"><img alt="Homepage" src="https://github.com/deepseek-ai/DeepSeek-V2/blob/main/figures/badge.svg?raw=true"/></a>
</p>

---

> **Transform the Bible into the voices of modern personas with hardcore style transfer.**

---

## 🏗️ Project Structure

**This repository contains the backend stack for HOLY REMIX:**

- **Backend API** - AI-powered translation engine and data processing
- **Infrastructure** - AWS deployment and database management  
- **Documentation** - Complete project documentation and guides

**Frontend Application:**
- A separate codebase will be deployed for the web/mobile interface
- This repo contains all the API documentation and integration details
- The frontend will consume the APIs deployed from this backend stack

---

## 🚀 Features

- 🎭 **Persona Remix:** Translate scripture into the style of Joe Rogan, Samuel L. Jackson, Cardi B, and more!
- 🧠 **Hardcore Style Transfer:** Not just modern lingo—full persona infusion.
- 🔁 **Checkpoint System:** Resume and track progress.
- 💰 **Cost Estimation:** Know your token spend before you translate.
- 📦 **Database-Ready Output:** Strict JSON for DynamoDB.
- 🚀 **Auto-Deployment:** Backend stack deploys automatically via CI/CD.

---

## 📦 Quick Start

```bash
git clone https://github.com/yourusername/holy-remix.git
cd holy-remix
make install
```

---

## 🏗️ Architecture

```
┌───────────────┐    ┌────────────────────┐    ┌───────────────┐
│   Bible Input │───▶│  Hardcore Style AI │───▶│  Output JSON  │
└───────────────┘    └────────────────────┘    └───────────────┘
```

---

## 🎭 Available Personas

| Persona              | Style Description                        |
|----------------------|------------------------------------------|
| Joe Rogan            | Podcast host, "bro science" vibes        |
| Samuel L. Jackson    | Intense, profanity-laced, dramatic       |
| Maya Angelou         | Poetic, soulful, deeply spiritual        |
| Hunter S. Thompson   | Gonzo journalism, wild energy            |
| Cardi B              | Bronx energy, modern slang, attitude     |
| Ram Dass             | Spiritual teacher, psychedelic wisdom    |
| Ernest Hemingway     | Terse, masculine, minimalist prose       |
| Slang Spanish        | Urban Latino street culture              |
| Moody Gen Alpha Teen | Sarcastic, emoji-heavy, TikTok slang     |

---

## 🛠️ Usage

```bash
make preprocess
make list-personas
make estimate-full-bible PERSONA="joe-rogan"
make translate-full-bible PERSONA="joe-rogan"
```

---

## 🧑‍💻 Development

### Setup
```bash
git clone https://github.com/yourusername/holy-remix.git
cd holy-remix
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev]
pre-commit install
```

### Code Quality
- **Formatting:** [Black](https://black.readthedocs.io/)
- **Linting:** [Ruff](https://docs.astral.sh/ruff/)
- **Type Checking:** [mypy](http://mypy-lang.org/)
- **Pre-commit Hooks:** Automatically run on commit

### Running Tests
```bash
pytest
```

---

## 📄 License

MIT

---

## 🙏 Credits

- Built with [DeepSeek](https://www.deepseek.com/) and [AWS Bedrock](https://aws.amazon.com/bedrock/)

---