# ⚔️ Showdown AI Rater

A full-stack competitive Pokémon team analysis tool that combines **Smogon usage statistics** with **Llama 3 AI strategy** to give you data-driven team ratings and coaching for Gen 9 OU.

[Python]
[FastAPI]
[React]
[Vite]
[Groq]

---

## 📸 What It Does

Paste any Pokémon Showdown team export and get back:

- ✅ **Parsed team** — species, item, ability, moves, nature per Pokémon
- 📊 **Average Meta Usage** — how often each Pokémon appears in Gen 9 OU (from Smogon Chaos data)
- 🔗 **Team Synergy Score** — cross-referenced teammate correlation weights from the Smogon dataset
- 🤖 **AI Strategic Report** — 2-paragraph competitive analysis via Llama 3.3 70B (Groq)

---

## 🗂️ Project Structure

```
showdown-rater/
│
├── backend/                    # FastAPI Python backend
│   ├── data/
│   │   └── gen9ou-1695.json    # Smogon Chaos dataset (Gen 9 OU)
│   ├── main.py                 # FastAPI app + CORS + routes
│   ├── parser.py               # Showdown export text parser
│   ├── features.py             # Usage & synergy score calculator
│   ├── llm_advisor.py          # Groq / Llama 3 integration
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # GROQ_API_KEY (not committed)
│
└── showdown-rater/             # React + Vite frontend
    ├── src/
    │   ├── App.jsx             # Entire frontend (single file)
    │   └── main.jsx            # Vite entry point
    ├── index.html
    ├── vite.config.js
    └── package.json
```

---

## ⚙️ How It Works

```
User pastes Showdown export
        │
        ▼
  parser.py — splits export into blocks, extracts species / item / ability / EVs / moves
        │
        ▼
  features.py — looks up each Pokémon in gen9ou-1695.json
              — calculates average usage % across the team
              — sums teammate correlation weights for synergy score
        │
        ▼
  llm_advisor.py — sends team + scores to Llama 3.3 70B via Groq API
                 — returns 2-paragraph strategic analysis
        │
        ▼
  React frontend — renders parsed cards, stat badges, AI report
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

---

### 1. Clone the repo

```bash
git clone https://github.com/your-username/showdown-rater.git
cd showdown-rater
```

---

### 2. Backend setup

```bash
cd backend

# Install dependencies
pip install fastapi uvicorn groq python-dotenv

# Create your .env file
echo "GROQ_API_KEY=your_key_here" > .env

# Start the server
uvicorn main:app --reload --port 8000
```

You should see:
```
✅ SUCCESS: Loaded 315 Pokemon from Smogon dataset.
✅ Groq API Key detected. Using Llama 3.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

### 3. Frontend setup

Open a **second terminal**:

```bash
# From the project root
cd showdown-rater

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

### 4. Get your Groq API key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free
3. Create an API key
4. Paste it into `backend/.env` as `GROQ_API_KEY=your_key_here`

Groq's free tier is generous — Llama 3.3 70B runs fast with no cost for personal use.

---

## 🔌 API Reference

### `GET /`
Health check.

**Response:**
```json
{
  "status": "online",
  "message": "Showdown AI Rater is ready to analyze."
}
```

---

### `POST /api/analyze`
Analyzes a full team export.

**Request body:**
```json
{
  "paste_text": "Ogerpon-Wellspring @ Wellspring Mask\nAbility: Water Absorb\n..."
}
```

**Response:**
```json
{
  "status": "success",
  "parsed_team": [
    {
      "species": "Ogerpon-Wellspring",
      "item": "Wellspring Mask",
      "ability": "Water Absorb",
      "evs": { "atk": 252, "spd": 4, "spe": 252 },
      "nature": "Jolly",
      "moves": ["Ivy Cudgel", "Horn Leech", "Follow Me", "Spiky Shield"]
    }
  ],
  "features": {
    "average_meta_usage": 0.2517,
    "team_synergy_score": 148364.67
  },
  "llm_analysis": "This team's primary win condition..."
}
```

---

## 🧠 Feature Details

### Average Meta Usage
Each Pokémon's `usage` value is pulled from the Smogon Chaos JSON (`gen9ou-1695.json`). This is the proportion of teams in the dataset that included that Pokémon. The team average is calculated and displayed as a percentage.

| Range | Rating |
|-------|--------|
| ≥ 20% | 🟢 High meta presence |
| 10–20% | 🟡 Moderate presence |
| < 10% | 🔴 Low meta presence |

### Team Synergy Score
For every pair of Pokémon on the team, the tool checks the `Teammates` correlation weight in the Chaos data — how frequently those two appear together. All pairwise weights are summed into a single synergy score.

| Range | Rating |
|-------|--------|
| ≥ 50,000 | 🟢 Strong synergy |
| 15,000–50,000 | 🟡 Decent synergy |
| < 15,000 | 🔴 Low synergy |

### AI Analysis (Llama 3.3 70B via Groq)
The parsed team and scores are sent to Groq's inference API using the `llama-3.3-70b-versatile` model. The prompt instructs it to act as a competitive Gen 9 OU coach and return:
1. Primary win condition and core strengths
2. Meta threats and structural vulnerabilities

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend framework | FastAPI |
| ASGI server | Uvicorn |
| Data validation | Pydantic |
| AI model | Llama 3.3 70B (Groq) |
| Smogon data | Chaos JSON (Gen 9 OU, 1695 rating) |
| Frontend framework | React 18 |
| Frontend build tool | Vite |
| Styling | Inline styles (no external CSS lib) |

---

## 🔒 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Your Groq API key from console.groq.com |

Create a `.env` file in the `backend/` folder:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

> ⚠️ Never commit your `.env` file. It is listed in `.gitignore`.

---

## 📦 Dependencies

### Backend (`backend/requirements.txt`)
```
fastapi
uvicorn
groq
python-dotenv
pydantic
```

### Frontend
```
react
react-dom
vite
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [Smogon University](https://www.smogon.com/) for the Chaos usage statistics dataset
- [Groq](https://groq.com/) for fast, free Llama 3 inference
- [Pokémon Showdown](https://pokemonshowdown.com/) for the team export format
