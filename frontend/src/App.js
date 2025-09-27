import React, { useState } from 'react';
import './styles.css';
import AISummarizer from './AISummarizer';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    const isUrgent = /help|injury|fire|rescue|trapped/i.test(input);
    const newMessage = { text: input.trim(), urgent: isUrgent };
    setMessages((s) => [...s, newMessage]);
    setInput('');
  };

  const handleSOS = () => {
    const sosMessage = { text: 'SOS broadcast activated!', urgent: true };
    setMessages((s) => [...s, sosMessage]);
  };

  

  return (
    <div className="app-shell root">
      <div className="header">
        <div className="brand">
          <div className="logo">TL</div>
          <div>
            <h1>TerraLink X</h1>
            <p>Resilient comms demo</p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={toggleColorblind} className="colorblind-toggle">
            Colorblind Mode
          </button>
          <button onClick={handleSOS} className="sos-button">
            Send SOS
          </button>
        </div>
      </div>

      <div className="panel chat-container">
        <div className="chat-box">
          {messages.map((msg, idx) => (
            <div key={idx} className={msg.urgent ? 'message urgent' : 'message'}>
              {msg.text}
            </div>
          ))}
        </div>

        <div className="input-row">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message"
          />
          <button onClick={handleSend}>Send</button>
        </div>
      </div>

      <div className="panel">
        <AISummarizer />
        <div style={{ height: 12 }} />
        <div className="mesh-container">
          <h3 style={{ marginTop: 0, color: '#9fb0c8' }}>Live Mesh</h3>
          <p style={{ color: '#9fb0c8', fontSize: 13 }}>
            Simple visualization of nearby nodes.
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
