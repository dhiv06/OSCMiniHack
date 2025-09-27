import React, { useState } from 'react';
import './styles.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    const isUrgent = /help|injury|fire|rescue|trapped/i.test(input);
    const newMessage = { text: input, urgent: isUrgent };
    setMessages([...messages, newMessage]);
    setInput('');
  };

  const handleSOS = () => {
    const sosMessage = { text: 'SOS broadcast activated!', urgent: true };
    setMessages([...messages, sosMessage]);
  };

  return (
    <div className="chat-container">
      <h2>TerraLink X Chat</h2>
      <div className="chat-box">
        {messages.map((msg, idx) => (
          <div key={idx} className={msg.urgent ? 'message urgent' : 'message'}>
            {msg.text}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message"
      />
      <button onClick={handleSend}>Send</button>
      <button className="sos-button" onClick={handleSOS}>Send SOS</button>
    </div>
  );
}

export default App;