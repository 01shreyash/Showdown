import os
from groq import Groq
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ ERROR: GROQ_API_KEY not found in .env")
else:
    print("✅ Groq API Key detected. Using Llama 3.")

client = Groq(api_key=api_key)

def generate_team_analysis(parsed_team: list, features: dict) -> str:
    """Uses Llama 3 via Groq to provide fast, free strategic analysis."""
    
    team_summary = [f"{mon['species']} @ {mon.get('item', 'None')}" for mon in parsed_team]
    synergy = features.get('team_synergy_score', 0)
    
    prompt = f"""
    You are a professional Pokemon Showdown coach for Gen 9 OU.
    
    Analyze this team (Synergy Score: {synergy}):
    Lineup: {', '.join(team_summary)}.
    
    Provide a 2-paragraph strategic analysis:
    1. Primary win condition and core strengths (e.g., Sun, Rain, Stall, Hyper Offense).
    2. Significant meta threats or structural vulnerabilities.
    
    Keep the tone analytical and strictly competitive. No fluff.
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a data-driven competitive Pokemon analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=512
        )
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"AI Analysis Unavailable: {str(e)}"