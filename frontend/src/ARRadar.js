import React, { useEffect, useState } from 'react';
import './styles.css';

function ARRadar() {
  const [nodes, setNodes] = useState([
    { id: 'Node1', distance: 5 },
    { id: 'Node2', distance: 12 },
    { id: 'Node3', distance: 20 }
  ]);

  useEffect(() => {
    // Simulate GPS + compass updates
    const interval = setInterval(() => {
      setNodes(nodes.map(n => ({
        ...n,
        distance: Math.max(1, n.distance + (Math.random() * 2 - 1))
      })));
    }, 1000);
    return () => clearInterval(interval);
  }, [nodes]);

  return (
    <div className="ar-container">
      <h2>AR Connection Radar</h2>
      <div className="radar">
        {nodes.map((node, idx) => (
          <div key={idx} className="orb" style={{ left: `${node.distance * 10}px` }}>
            {node.id}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ARRadar;