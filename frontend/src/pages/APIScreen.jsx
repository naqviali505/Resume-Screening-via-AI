import { useState } from "react";
import "./ApiScreen.css";

export default function ApiKeyDialog({ onAdd, onCancel }) {
  const [apiKey, setApiKey] = useState("");

  const handleAdd = () => {
    if (!apiKey.trim()) {
      alert("Please enter a valid API key");
      return;
    }
    onAdd(apiKey);
  };

  return (
    <div className="api-overlay">
      <div className="api-modal">
        <h2 className="api-title">Enter API Key</h2>

        <input
          type="text"
          className="api-input"
          placeholder="Paste your API key here"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
        />

        <div className="api-button-container">
          <button className="api-add-btn" onClick={handleAdd}>
            Add
          </button>
          <button className="api-cancel-btn" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
