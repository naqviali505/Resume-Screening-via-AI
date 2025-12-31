import { useLocation, useNavigate } from "react-router-dom";

function ResultsPage() {
  const { state } = useLocation();
  const navigate = useNavigate();

  const isRateLimited = state?.error === "rate_limit_exceeded";
  const candidates = state?.candidates || [];

  return (
    <div className="container">
      <h1>Shortlisted Candidates</h1>

      {isRateLimited ? (
        <div className="rate-limit-box">
          <p>{state.message}</p>

          <button onClick={() => navigate("/add-api-key")}>
            Add API Key
          </button>

          <button onClick={() => navigate("/")}>
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
    </div>
  );
}

export default ResultsPage;
