import React, { useState } from "react";
import "./FileUpload.css";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const [result, setResult] = useState("");
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [endpoint, setEndpoint] = useState("simplify");

  // Track real File object
  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;
    setFile(selected);
    setFileName(selected.name);
  };

  const handleSubmit = async () => {
    if (!file) {
      alert("Please select a file first!");
      return;
    }
    setLoading(true);
    setResult("");
    setRisks([]);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`https://layman-law.onrender.com/${endpoint}`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Something went wrong");

      if (endpoint === "risks") {
        if (Array.isArray(data.risks)) {
          setRisks(data.risks);
        } else {
          setResult("⚠️ Risk data not in expected format.");
        }
      } else {
        let output = "";
        switch (endpoint) {
          case "simplify":
            output = data.simplified;
            break;
          case "extract":
            output = typeof data.clauses === "object"
              ? JSON.stringify(data.clauses, null, 2)
              : data.clauses;
            break;
          case "compare":
            output = data.differences;
            break;
          case "qa":
            output = data.answer;
            break;
          default:
            output = JSON.stringify(data, null, 2);
        }
        setResult(output);
      }
    } catch (err) {
      setResult(`⚠️ Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getRiskClass = (severity) => {
    switch (severity.toLowerCase()) {
      case "red":
        return "risk-high";
      case "yellow":
        return "risk-medium";
      case "green":
        return "risk-low";
      default:
        return "";
    }
  };

  return (
    <div className="file-upload-card fade-in">
      <h2 className="title">📂 Upload Your Legal Document</h2>
      <p className="subtitle">Supported formats: PDF, DOCX, TXT</p>

      <input
        id="fileInput"
        type="file"
        accept=".txt,.doc,.docx,.pdf"
        onChange={handleFileChange}
        className="file-input"
      />

      {fileName && <p className="file-name">✅ {fileName} selected</p>}

      <div className="endpoint-selector">
        <label>
          <input
            type="radio"
            name="endpoint"
            value="simplify"
            checked={endpoint === "simplify"}
            onChange={() => setEndpoint("simplify")}
          />
          Simplify
        </label>
        <label>
          <input
            type="radio"
            name="endpoint"
            value="extract"
            checked={endpoint === "extract"}
            onChange={() => setEndpoint("extract")}
          />
          Extract Clauses
        </label>
        <label>
          <input
            type="radio"
            name="endpoint"
            value="risks"
            checked={endpoint === "risks"}
            onChange={() => setEndpoint("risks")}
          />
          Risk Analysis
        </label>
      </div>

      <button className="btn-submit" onClick={handleSubmit} disabled={loading}>
        {loading ? "Processing..." : "Submit for Processing"}
      </button>

      {(result || risks.length > 0) && (
        <div className="result-card full-screen-result">
          <h4>Result:</h4>
          {endpoint === "risks" && risks.length > 0 ? (
            <table className="risk-table">
              <thead>
                <tr>
                  <th>Clause</th>
                  <th>Severity</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {risks.map((risk, idx) => (
                  <tr key={idx} className={getRiskClass(risk.severity)}>
                    <td>{risk.clause}</td>
                    <td>{risk.severity}</td>
                    <td>{risk.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <textarea value={result} readOnly className="result-textarea" />
          )}
        </div>
      )}
    </div>
  );
}

export default FileUpload;
