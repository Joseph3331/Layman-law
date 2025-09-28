import React from "react";
import "./SimplifiedOutput.css";

function SimplifiedOutput({ summary, highlights }) {
  return (
    <div className="card simplified-output fade-in">

      {highlights && highlights.length > 0 && (
        <div className="highlights">
          <h4>⚠️ Risk Highlights</h4>
          <ul>
            {highlights.map((h, idx) => (
              <li key={idx} className={`highlight ${h.level}`}>
                {h.text}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default SimplifiedOutput;
