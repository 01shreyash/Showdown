import { useState } from "react";

const API = "http://localhost:8000";

const SAMPLE_PASTE = `Ogerpon-Wellspring @ Wellspring Mask
Ability: Water Absorb
Tera Type: Water
EVs: 252 Atk / 4 SpD / 252 Spe
Jolly Nature
- Ivy Cudgel
- Horn Leech
- Follow Me
- Spiky Shield

Great Tusk @ Booster Energy
Ability: Protosynthesis
Tera Type: Ground
EVs: 252 Atk / 4 SpD / 252 Spe
Jolly Nature
- Headlong Rush
- Ice Spinner
- Rapid Spin
- Knock Off

Gholdengo @ Choice Specs
Ability: Good as Gold
Tera Type: Steel
EVs: 252 SpA / 4 SpD / 252 Spe
Timid Nature
- Make It Rain
- Shadow Ball
- Trick
- Nasty Plot

Kingambit @ Assault Vest
Ability: Supreme Overlord
Tera Type: Dark
EVs: 252 HP / 60 Atk / 196 SpD
Careful Nature
- Kowtow Cleave
- Sucker Punch
- Iron Head
- Swords Dance

Raging Bolt @ Booster Energy
Ability: Protosynthesis
Tera Type: Electric
EVs: 252 SpA / 4 SpD / 252 Spe
Timid Nature
- Thunderclap
- Dragon Pulse
- Calm Mind
- Volt Switch

Zamazenta @ Rusted Shield
Ability: Dauntless Shield
Tera Type: Fairy
EVs: 252 HP / 4 Atk / 252 Def
Impish Nature
- Body Press
- Heavy Slam
- Crunch
- Roar`;

function Spinner() {
  return (
    <span style={{
      display: "inline-block", width: 14, height: 14,
      border: "2px solid rgba(255,255,255,0.35)",
      borderTopColor: "#fff", borderRadius: "50%",
      animation: "spin 0.7s linear infinite", flexShrink: 0,
    }} />
  );
}

function StepBar({ step }) {
  const steps = ["Paste Team", "Review Parse", "Strategy"];
  return (
    <div style={{
      display: "flex", marginBottom: 28,
      borderRadius: 10, overflow: "hidden",
      border: "1px solid #e2e0da",
    }}>
      {steps.map((label, i) => {
        const n = i + 1;
        const active = step === n;
        const done = step > n;
        return (
          <div key={n} style={{
            flex: 1, display: "flex", alignItems: "center",
            justifyContent: "center", gap: 8, padding: "11px 8px",
            background: active ? "#fff" : done ? "#f0fdf8" : "#f7f6f2",
            borderRight: i < 2 ? "1px solid #e2e0da" : "none",
          }}>
            <div style={{
              width: 20, height: 20, borderRadius: "50%",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 11, fontFamily: "monospace", fontWeight: 700,
              background: active ? "#c0392b" : done ? "#00b894" : "#dddbd3",
              color: "#fff", flexShrink: 0,
            }}>
              {done ? "✓" : n}
            </div>
            <span style={{
              fontSize: 12, fontFamily: "monospace",
              color: active ? "#1a1a18" : done ? "#007a5e" : "#999",
              fontWeight: active ? 700 : 400,
            }}>{label}</span>
          </div>
        );
      })}
    </div>
  );
}

function StepPaste({ onSubmit }) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    if (!text.trim()) { setError("Paste a Showdown team export first."); return; }
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paste_text: text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Server error");
      onSubmit(data);
    } catch (e) {
      setError(e.message + " — is the backend running on localhost:8000?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <p style={{ fontSize: 13, color: "#888", fontFamily: "monospace", marginBottom: 12 }}>
        Showdown → Team Builder → Export → paste below.
      </p>
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder={"Ogerpon-Wellspring @ Wellspring Mask\nAbility: Water Absorb\nEVs: 252 Atk / 252 Spe\nJolly Nature\n- Ivy Cudgel\n..."}
        style={{
          width: "100%", minHeight: 230, resize: "vertical",
          fontFamily: "monospace", fontSize: 12, lineHeight: 1.65,
          padding: "14px 16px", boxSizing: "border-box",
          background: "#f7f6f2", border: "1px solid #e2e0da",
          borderRadius: 8, color: "#1a1a18", outline: "none",
        }}
        onFocus={e => e.target.style.borderColor = "#c0392b"}
        onBlur={e => e.target.style.borderColor = "#e2e0da"}
      />
      {error && (
        <div style={{
          marginTop: 10, padding: "10px 14px", borderRadius: 8,
          background: "#fff1f0", border: "1px solid #ffb3b0",
          fontSize: 12, fontFamily: "monospace", color: "#9b1c1c",
        }}>{error}</div>
      )}
      <div style={{ display: "flex", gap: 10, marginTop: 14 }}>
        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            display: "flex", alignItems: "center", gap: 8,
            padding: "10px 22px", borderRadius: 8, border: "none",
            background: loading ? "#e08080" : "#c0392b", color: "#fff",
            fontFamily: "monospace", fontSize: 13, fontWeight: 700,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? <><Spinner /> Analyzing…</> : "Analyze Team →"}
        </button>
        <button
          onClick={() => setText(SAMPLE_PASTE)}
          style={{
            padding: "10px 18px", borderRadius: 8,
            border: "1px solid #e2e0da", background: "#fff",
            fontFamily: "monospace", fontSize: 13, color: "#555",
            cursor: "pointer",
          }}
        >
          Load Sample
        </button>
      </div>
    </div>
  );
}

function MonCard({ mon, index }) {
  const accents = ["#c0392b", "#0984e3", "#00b894", "#e17055", "#6c5ce7", "#fd79a8"];
  const accent = accents[index % accents.length];
  return (
    <div style={{
      background: "#fff", borderRadius: 10,
      border: "1px solid #e2e0da", overflow: "hidden",
      animation: `slideUp 0.3s ease ${index * 0.05}s both`,
    }}>
      <div style={{ height: 4, background: accent }} />
      <div style={{ padding: "12px 14px" }}>
        <div style={{
          fontSize: 13, fontWeight: 700, fontFamily: "monospace",
          color: "#1a1a18", marginBottom: 2,
          whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
        }}>
          {mon.species}
        </div>
        {mon.item && (
          <div style={{ fontSize: 11, color: "#999", fontFamily: "monospace", marginBottom: 6 }}>
            @ {mon.item}
          </div>
        )}
        {mon.ability && (
          <div style={{ fontSize: 11, color: "#bbb", marginBottom: 8 }}>{mon.ability}</div>
        )}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
          {(mon.moves || []).map((m, j) => (
            <span key={j} style={{
              fontSize: 10, fontFamily: "monospace",
              padding: "2px 7px", borderRadius: 4,
              background: "#f0eef8", color: "#5a48b8",
              border: "1px solid #d8d0f0",
            }}>{m}</span>
          ))}
        </div>
        {mon.nature && (
          <div style={{ fontSize: 10, color: "#ccc", fontFamily: "monospace", marginTop: 6 }}>
            {mon.nature} Nature
          </div>
        )}
      </div>
    </div>
  );
}

function StepReview({ data, onBack, onNext }) {
  return (
    <div>
      <p style={{ fontSize: 13, color: "#888", fontFamily: "monospace", marginBottom: 16 }}>
        {data.parsed_team.length} Pokémon parsed — verify before getting the report.
      </p>
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(175px, 1fr))",
        gap: 10,
      }}>
        {data.parsed_team.map((mon, i) => <MonCard key={i} mon={mon} index={i} />)}
      </div>
      <div style={{ display: "flex", gap: 10, marginTop: 20 }}>
        <button
          onClick={onNext}
          style={{
            padding: "10px 22px", borderRadius: 8, border: "none",
            background: "#c0392b", color: "#fff",
            fontFamily: "monospace", fontSize: 13, fontWeight: 700,
            cursor: "pointer",
          }}
        >
          Get AI Strategy →
        </button>
        <button
          onClick={onBack}
          style={{
            padding: "10px 18px", borderRadius: 8,
            border: "1px solid #e2e0da", background: "#fff",
            fontFamily: "monospace", fontSize: 13, color: "#555",
            cursor: "pointer",
          }}
        >
          ← Edit Paste
        </button>
      </div>
    </div>
  );
}

function Badge({ label, color, bg }) {
  return (
    <span style={{
      display: "inline-block", fontSize: 10, fontFamily: "monospace",
      padding: "3px 9px", borderRadius: 4,
      background: bg, color, border: `1px solid ${color}40`,
    }}>{label}</span>
  );
}

function StepResults({ data, onReset }) {
  const { features, llm_analysis } = data;
  const usage = features?.average_meta_usage ?? 0;
  const synergy = features?.team_synergy_score ?? 0;
  const usagePct = Math.min(usage * 100, 100);

  const usageBadge =
    usagePct >= 20 ? ["High meta presence", "#007a5e", "#e0faf4"] :
    usagePct >= 10 ? ["Moderate presence",  "#b45309", "#fff3ee"] :
                     ["Low meta presence",  "#9b1c1c", "#fff1f0"];

  const synergyBadge =
    synergy >= 50000 ? ["Strong synergy", "#007a5e", "#e0faf4"] :
    synergy >= 15000 ? ["Decent synergy", "#b45309", "#fff3ee"] :
                       ["Low synergy",    "#9b1c1c", "#fff1f0"];

  const paragraphs = (llm_analysis || "").trim().split(/\n\n+/).filter(Boolean);

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 22 }}>
        <div style={{ background: "#f7f6f2", borderRadius: 10, padding: "14px 16px" }}>
          <div style={{ fontSize: 11, fontFamily: "monospace", color: "#aaa", marginBottom: 8 }}>
            Avg meta usage
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, fontFamily: "monospace", color: "#1a1a18", marginBottom: 6 }}>
            {usagePct.toFixed(1)}%
          </div>
          <div style={{ height: 5, background: "#e2e0da", borderRadius: 3, marginBottom: 8 }}>
            <div style={{
              height: "100%", width: `${usagePct}%`,
              background: "#c0392b", borderRadius: 3,
              transition: "width 0.8s ease",
            }} />
          </div>
          <Badge label={usageBadge[0]} color={usageBadge[1]} bg={usageBadge[2]} />
        </div>

        <div style={{ background: "#f7f6f2", borderRadius: 10, padding: "14px 16px" }}>
          <div style={{ fontSize: 11, fontFamily: "monospace", color: "#aaa", marginBottom: 8 }}>
            Team synergy score
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, fontFamily: "monospace", color: "#1a1a18", marginBottom: 6 }}>
            {synergy.toLocaleString()}
          </div>
          <div style={{ fontSize: 11, color: "#ccc", fontFamily: "monospace", marginBottom: 8 }}>
            teammate correlation sum
          </div>
          <Badge label={synergyBadge[0]} color={synergyBadge[1]} bg={synergyBadge[2]} />
        </div>
      </div>

      <div style={{
        display: "flex", alignItems: "center", gap: 8, marginBottom: 10,
        fontSize: 11, fontFamily: "monospace", color: "#aaa",
        letterSpacing: "0.06em", textTransform: "uppercase",
      }}>
        AI Strategic Report
        <div style={{ flex: 1, height: 1, background: "#e2e0da" }} />
        <span style={{
          background: "#fff1f0", color: "#c0392b",
          padding: "2px 8px", borderRadius: 4, fontSize: 10,
        }}>Llama 3 via Groq</span>
      </div>

      {paragraphs.map((p, i) => (
        <div key={i} style={{
          marginBottom: 10, padding: "14px 18px",
          background: "#f7f6f2",
          borderLeft: "3px solid #c0392b",
          borderRadius: "0 8px 8px 0",
          fontSize: 13, lineHeight: 1.75, color: "#2a2a25",
          animation: `slideUp 0.35s ease ${i * 0.1}s both`,
        }}>{p}</div>
      ))}

      <button
        onClick={onReset}
        style={{
          marginTop: 18, padding: 0, border: "none", background: "none",
          fontFamily: "monospace", fontSize: 12, color: "#bbb",
          cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
        }}
      >
        ↺ Analyze another team
      </button>
    </div>
  );
}

export default function App() {
  const [step, setStep] = useState(1);
  const [result, setResult] = useState(null);

  function handleAnalyzed(data) {
    setResult(data);
    setStep(2);
  }

  return (
    <>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #eeece6; font-family: sans-serif; }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>

      <div style={{
        minHeight: "100vh", padding: "32px 16px",
        display: "flex", flexDirection: "column", alignItems: "center",
      }}>
        <div style={{
          width: "100%", maxWidth: 660,
          display: "flex", alignItems: "center", gap: 14,
          marginBottom: 24,
          animation: "slideUp 0.4s ease both",
        }}>
          <div style={{
            width: 44, height: 44, borderRadius: 12,
            background: "#c0392b",
            display: "flex", alignItems: "center", justifyContent: "center",
            flexShrink: 0,
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
              stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </div>
          <div>
            <div style={{ fontSize: 20, fontWeight: 700, color: "#1a1a18", lineHeight: 1 }}>
              Showdown AI Rater
            </div>
            <div style={{ fontSize: 11, fontFamily: "monospace", color: "#aaa", marginTop: 4 }}>
              Gen 9 OU · Smogon Chaos + Llama 3 Strategy
            </div>
          </div>
        </div>

        <div style={{
          width: "100%", maxWidth: 660,
          background: "#fff", borderRadius: 16,
          border: "1px solid #e2e0da",
          padding: "24px",
          animation: "slideUp 0.45s ease 0.05s both",
        }}>
          <StepBar step={step} />

          {step === 1 && <StepPaste onSubmit={handleAnalyzed} />}
          {step === 2 && result && (
            <StepReview
              data={result}
              onBack={() => setStep(1)}
              onNext={() => setStep(3)}
            />
          )}
          {step === 3 && result && (
            <StepResults
              data={result}
              onReset={() => { setResult(null); setStep(1); }}
            />
          )}
        </div>

        <div style={{ marginTop: 20, fontSize: 11, fontFamily: "monospace", color: "#ccc" }}>
          backend · localhost:8000
        </div>
      </div>
    </>
  );
}