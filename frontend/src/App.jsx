// src/App.jsx
import { Routes, Route } from "react-router-dom";
import ResumeForm from "./pages/ResumeForm";
import ResultsPage from "./pages/ResultPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<ResumeForm />} />
      <Route path="/results" element={<ResultsPage />} />
    </Routes>
  );
}

export default App;
