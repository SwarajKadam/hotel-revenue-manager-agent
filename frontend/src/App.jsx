import { useState } from "react";
import { askAgent } from "./api";
import "./App.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const exampleQuestions = [
  "What revenue is on the books by month?",
  "Are we too dependent on OTA?",
  "Which room type has the highest ADR?",
  "What changed in the last 7 days?",
  "How much business was cancelled?",
  "Which market segments are driving demand?",
];

function App() {
  const APP_PASSWORD = import.meta.env.VITE_APP_PASSWORD || "demo123";

  const [isAuthenticated, setIsAuthenticated] = useState(
    localStorage.getItem("hotel_agent_auth") === "true"
  );

  const [passwordInput, setPasswordInput] = useState("");
  const [passwordError, setPasswordError] = useState("");

  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [toolsUsed, setToolsUsed] = useState([]);
  const [skillsUsed, setSkillsUsed] = useState([]);
  const [subagentsUsed, setSubagentsUsed] = useState([]);

  function handleLogin() {
    if (passwordInput === APP_PASSWORD) {
      localStorage.setItem("hotel_agent_auth", "true");
      setIsAuthenticated(true);
      setPasswordError("");
    } else {
      setPasswordError("Incorrect password.");
    }
  }

  function handleLogout() {
    localStorage.removeItem("hotel_agent_auth");
    setIsAuthenticated(false);
    setPasswordInput("");
    setPasswordError("");
  }

  async function handleAsk(customQuestion) {
    const finalQuestion = customQuestion || message;

    if (!finalQuestion.trim()) return;

    setLoading(true);
    setAnswer("");
    setQuestion(finalQuestion);
    setToolsUsed([]);
    setSkillsUsed([]);
    setSubagentsUsed([]);

    try {
      const data = await askAgent(finalQuestion);

      setAnswer(data.answer);
      setToolsUsed(data.tools_used || []);
      setSkillsUsed(data.skills_used || []);
      setSubagentsUsed(data.subagents_used || []);
      setMessage("");
    } catch (error) {
      console.error(error);
      setAnswer("Something went wrong while contacting the backend.");
    } finally {
      setLoading(false);
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="page">
        <div className="container">
          <section className="card loginCard">
            <p className="eyebrow">Protected Demo</p>
            <h1>Hotel Revenue Manager Agent</h1>
            <p className="subtitle">
              Enter the demo password to access the revenue manager chat.
            </p>

            <div className="inputRow loginRow">
              <input
                type="password"
                value={passwordInput}
                onChange={(e) => {
                  setPasswordInput(e.target.value);
                  setPasswordError("");
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleLogin();
                }}
                placeholder="Enter password"
              />

              <button onClick={handleLogin}>Enter</button>
            </div>

            {passwordError && <p className="errorText">{passwordError}</p>}
          </section>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <header className="header">
          <div>
            <p className="eyebrow">Hotel Revenue Intelligence</p>
            <h1>AI Revenue Manager Agent</h1>
            <p className="subtitle">
              Ask business questions about revenue, ADR, OTA dependency,
              cancellations, pickup, room types, and market mix.
            </p>
          </div>

          <button className="logoutButton" onClick={handleLogout}>
            Logout
          </button>
        </header>

        <section className="card askCard">
          <div className="cardTop">
            <div>
              <p className="label">Ask the revenue manager</p>
              <h2 className="cardTitle">What would you like to analyse?</h2>
            </div>
          </div>

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
            <div className="questionBlock">
              <p className="answerLabel">Question</p>
              <h2>{question}</h2>
            </div>

            {!loading &&
              (toolsUsed.length > 0 ||
                skillsUsed.length > 0 ||
                subagentsUsed.length > 0) && (
                <div className="activityBox">
                  <div className="activityGrid">
                    {toolsUsed.length > 0 && (
                      <div className="activitySection">
                        <p className="activityTitle">Tools Used</p>
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
                      <div className="activitySection">
                        <p className="activityTitle">Skills Used</p>
                        <div className="pillRow">
                          {skillsUsed.map((skill) => (
                            <span className="pill skillPill" key={skill}>
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {subagentsUsed.length > 0 && (
                      <div className="activitySection">
                        <p className="activityTitle">Subagents Used</p>
                        <div className="pillRow">
                          {subagentsUsed.map((agent) => (
                            <span className="pill subagentPill" key={agent}>
                              {agent}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

            <div className="answerBlock">
              <p className="answerLabel">Answer</p>

              {loading ? (
                <div className="loadingBox">
                  <span className="loadingDot" />
                  <p className="loading">Analyzing hotel revenue data...</p>
                </div>
              ) : (
                <div className="answerText">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {answer}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default App;