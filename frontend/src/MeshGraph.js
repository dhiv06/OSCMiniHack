import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import './styles.css';

function MeshGraph() {
  const ref = useRef();

  useEffect(() => {
    const svg = d3.select(ref.current)
      .attr('width', 400)
      .attr('height', 300);

    const nodes = [
      { id: 'A' }, { id: 'B' }, { id: 'C' }, { id: 'D' }
    ];
    const links = [
      { source: 'A', target: 'B' },
      { source: 'B', target: 'C' },
      { source: 'C', target: 'D' }
    ];

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(200, 150));

    const link = svg.selectAll('.link')
      .data(links)
      .enter().append('line')
      .attr('class', 'link');

    const node = svg.selectAll('.node')
      .data(nodes)
      .enter().append('circle')
      .attr('class', 'node')
      .attr('r', 10);

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
    });
  }, []);

  return (
    <div className="mesh-container">
      <h2>Live Mesh Graph</h2>
      <svg ref={ref}></svg>
    </div>
  );
}

export default MeshGraph;