import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import ApiKeyDialog from "./APIScreen";

function ResultsPage() {
  const { state } = useLocation();
  const navigate = useNavigate();

  const isRateLimited = state?.error === "rate_limit_exceeded";
  const candidates = state?.candidates || [];

  const [showApiDialog, setShowApiDialog] = useState(false);

  const handleAddApiKey = async (key) => {
  try {
    const response = await fetch("http://localhost:8000/set-api-key", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ api_key: key }),
    });

    if (!response.ok) {
      throw new Error("Failed to set API key on backend");
    }

    alert("API Key added successfully!");
    setShowApiDialog(false);

  } catch (err) {
    console.error(err);
    alert("Error sending API key to backend");
  }
};

  return (
    <div className="container">
      <h1>Shortlisted Candidates</h1>

      {isRateLimited ? (
        <div className="rate-limit-box">
          <p>{state.message}</p>

          <button onClick={() => setShowApiDialog(true)}>Add API Key</button>

          <button
            style={{ marginLeft: "10px" }}
            onClick={() => navigate("/")}
          >
            Go Back
          </button>
        </div>
      ) : candidates.length === 0 ? (
        <p>No candidates found.</p>
      ) : (
        <ul>
          {candidates.map((candidate, index) => (
            <li key={index}>
              <h3>{candidate.candidate_id}</h3>
              <p>
                <strong>Experience:</strong> {candidate.years_experience} years
              </p>
              <p>
                <strong>Matched Skills:</strong>{" "}
                {candidate.matched_skills.join(", ")}
              </p>
              <p>{candidate.reason}</p>
            </li>
          ))}
        </ul>
      )}

      {!isRateLimited && (
        <button onClick={() => navigate("/")}>
          Filter Resumes Again
        </button>
      )}

      {showApiDialog && (
        <ApiKeyDialog
          onAdd={handleAddApiKey}
          onCancel={() => setShowApiDialog(false)}
        />
      )}
    </div>
  );
}

export default ResultsPage;
