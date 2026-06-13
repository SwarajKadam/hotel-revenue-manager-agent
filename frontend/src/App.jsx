import { useState } from "react";
import { askAgent } from "./api";
import "./App.css";
import ReactMarkdown from "react-markdown";

const exampleQuestions = [
  "What revenue is on the books by month?",
  "Are we too dependent on OTA?",
  "Which room type has the highest ADR?",
  "What changed in the last 7 days?",
  "How much business was cancelled?",
  "Which market segments are driving demand?",
];

function App() {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [toolsUsed, setToolsUsed] = useState([]);
  const [skillsUsed, setSkillsUsed] = useState([]);

  async function handleAsk(customQuestion) {
    const finalQuestion = customQuestion || message;

    if (!finalQuestion.trim()) return;

    setLoading(true);
    setAnswer("");
    setQuestion(finalQuestion);
    setToolsUsed([]);
    setSkillsUsed([]);

    try {
      const data = await askAgent(finalQuestion);

      setAnswer(data.answer);
      setToolsUsed(data.tools_used || []);
      setSkillsUsed(data.skills_used || []);
      setMessage("");
    } catch (error) {
      console.error(error);
      setAnswer("Something went wrong while contacting the backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="container">
        <header className="header">
          <p className="eyebrow">Hotel Revenue Intelligence</p>
          <h1>AI Revenue Manager Agent</h1>
          <p className="subtitle">
            Ask business questions about revenue, ADR, OTA dependency,
            cancellations, pickup, room types, and market mix.
          </p>
        </header>

        <section className="card">
          <label className="label">Ask the revenue manager</label>

          <div className="inputRow">
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleAsk();
              }}
              placeholder="Example: Are we too dependent on OTA?"
            />

            <button onClick={() => handleAsk()} disabled={loading}>
              {loading ? "Thinking..." : "Ask"}
            </button>
          </div>

          <div className="examples">
            {exampleQuestions.map((item) => (
              <button
                key={item}
                className="exampleButton"
                onClick={() => handleAsk(item)}
                disabled={loading}
              >
                {item}
              </button>
            ))}
          </div>
        </section>

        {(loading || answer) && (
          <section className="answerCard">
            <p className="answerLabel">Question</p>
            <h2>{question}</h2>

            {!loading && (toolsUsed.length > 0 || skillsUsed.length > 0) && (
  <div className="activityBox">
    {toolsUsed.length > 0 && (
      <div>
        <p className="activityTitle">Tools used</p>
        <div className="pillRow">
          {toolsUsed.map((tool) => (
            <span className="pill" key={tool}>
              {tool}
            </span>
          ))}
        </div>
      </div>
    )}

    {skillsUsed.length > 0 && (
      <div>
        <p className="activityTitle">Skills used</p>
            <div className="pillRow">
              {skillsUsed.map((skill) => (
                <span className="pill skillPill" key={skill}>
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    )}

    <p className="answerLabel">Answer</p>
    {loading ? (
      <p className="loading">Analyzing hotel revenue data...</p>
    ) : (
      <div className="answerText">
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>
    )}
          </section>
        )}
      </div>
    </div>
  );
}

export default App;