import React, { useState } from 'react';
import './styles.css';

function AISummarizer() {
  const [text, setText] = useState('');
  const [summary, setSummary] = useState('');

  const handleSummarize = async () => {
    const res = await fetch('/api/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    setSummary(data.summary);
  };

  return (
    <div className="summarizer-container">
      <h2>AI Text Summarizer</h2>
      <textarea
        rows="6"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste long message here..."
      />
      <button onClick={handleSummarize}>Summarize</button>
      {summary && (
        <div className="summary-box">
          <h4>Summary:</h4>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}

export default AISummarizer;
