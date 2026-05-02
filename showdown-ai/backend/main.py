from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from parser import parse_showdown_export
from features import extract_team_features
from llm_advisor import generate_team_analysis

# ONE app instance only
app = FastAPI(
    title="Showdown AI Rater API",
    description="A data-driven competitive Pokemon analyst combining Smogon stats and LLM reasoning.",
    version="1.1.0"
)

# CORS must be added right after app creation, before any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TeamRequest(BaseModel):
    paste_text: str

@app.get("/")
async def health_check():
    return {"status": "online", "message": "Showdown AI Rater is ready to analyze."}

@app.post("/api/analyze")
async def analyze_team(request: TeamRequest):
    raw_text = request.paste_text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Team text is required.")

    parsed_team = parse_showdown_export(raw_text)
    if not parsed_team:
        raise HTTPException(status_code=400, detail="Failed to parse team. Ensure it follows the standard Showdown export format.")

    features = extract_team_features(parsed_team)
    llm_feedback = generate_team_analysis(parsed_team, features)

    return {
        "status": "success",
        "parsed_team": parsed_team,
        "features": features,
        "llm_analysis": llm_feedback
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)