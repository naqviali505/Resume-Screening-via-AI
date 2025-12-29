// src/pages/ResultsPage.jsx
import { useLocation, useNavigate } from "react-router-dom";

function ResultsPage() {
  const { state } = useLocation();
  const navigate = useNavigate();

  const candidates = state?.candidates || [];

  return (
    <div className="container">
      <h1>Shortlisted Candidates</h1>

      {candidates.length === 0 ? (
        <p>No candidates found.</p>
      ) : (
        <ul>
          {candidates.map((candidate, index) => (
            <li key={index}>{candidate}</li>
          ))}
        </ul>
      )}

      <button onClick={() => navigate("/")}>
        Filter Resumes Again
      </button>
    </div>
  );
}

export default ResultsPage;
