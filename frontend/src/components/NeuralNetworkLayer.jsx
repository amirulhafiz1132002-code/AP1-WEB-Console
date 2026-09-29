import React, { useMemo, useState } from 'react';
import './NeuralNetworkLayer.css';

const DEFAULT_NODES = [
  { id: 'human', label: 'HUMAN', group: 'core', x: 50, y: 50, r: 11 },
  { id: 'orchestrator', label: 'AP1', group: 'core', x: 50, y: 20, r: 9 },
  { id: 'planner', label: 'PLANNER', group: 'agent', x: 24, y: 31, r: 7 },
  { id: 'builder', label: 'BUILDER', group: 'agent', x: 76, y: 31, r: 7 },
  { id: 'brain', label: 'BRAIN', group: 'agent', x: 20, y: 68, r: 7 },
  { id: 'debugger', label: 'DEBUGGER', group: 'agent', x: 80, y: 68, r: 7 },
  { id: 'memory', label: 'MEMORY', group: 'data', x: 33, y: 87, r: 7 },
  { id: 'runtime', label: 'RUNTIME', group: 'runtime', x: 67, y: 87, r: 7 },
];

const DEFAULT_CONNECTIONS = [
  ['human', 'orchestrator'],
  ['orchestrator', 'planner'],
  ['orchestrator', 'builder'],
  ['planner', 'brain'],
  ['planner', 'memory'],
  ['builder', 'debugger'],
  ['builder', 'runtime'],
  ['brain', 'human'],
  ['debugger', 'human'],
  ['memory', 'human'],
  ['runtime', 'human'],
];

export const NeuralNetworkLayer = ({
  nodes = DEFAULT_NODES,
  connections = DEFAULT_CONNECTIONS,
  title = 'NEURAL NETWORK',
  subtitle = 'AP1 SYSTEM VISUAL LAYER',
}) => {
  const [selectedNode, setSelectedNode] = useState(null);

  const nodeMap = useMemo(
    () => Object.fromEntries(nodes.map((node) => [node.id, node])),
    [nodes]
  );

  return (
    <section id="neural-network" className="neural-network-section" aria-labelledby="neural-network-title">
      <div className="neural-network-shell">
        <div className="neural-network-header">
          <div>
            <span className="neural-network-kicker">SYSTEM LAYER · CONCEPT</span>
            <h2 id="neural-network-title">{title}</h2>
            <p>{subtitle}</p>
          </div>
          <div className="neural-network-truth">
            <span className="truth-dot" />
            <span>STATIC SAMPLE</span>
            <small>RUNTIME NOT CONNECTED</small>
          </div>
        </div>

        <div className="neural-network-stage">
          <div className="network-grid" aria-hidden="true" />

          <svg className="network-connections" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
            <defs>
              <filter id="neural-glow">
                <feGaussianBlur stdDeviation="0.45" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            {connections.map(([from, to], index) => {
              const source = nodeMap[from];
              const target = nodeMap[to];
              if (!source || !target) return null;

              return (
                <g key={`${from}-${to}`} className="network-link">
                  <line
                    x1={source.x}
                    y1={source.y}
                    x2={target.x}
                    y2={target.y}
                    pathLength="1"
                  />
                  <circle
                    className="network-particle"
                    r="0.65"
                    filter="url(#neural-glow)"
                    style={{ animationDelay: `${index * -0.45}s` }}
                  >
                    <animateMotion
                      dur={`${3.2 + (index % 3) * 0.7}s`}
                      repeatCount="indefinite"
                      begin={`${index * -0.35}s`}
                      path={`M ${source.x} ${source.y} L ${target.x} ${target.y}`}
                    />
                  </circle>
                </g>
              );
            })}
          </svg>

          <div className="network-nodes">
            {nodes.map((node) => {
              const isSelected = selectedNode === node.id;
              return (
                <button
                  key={node.id}
                  type="button"
                  className={`neural-node neural-node--${node.group} ${isSelected ? 'is-selected' : ''}`}
                  style={{
                    left: `${node.x}%`,
                    top: `${node.y}%`,
                    '--node-size': `${node.r * 2}px`,
                  }}
                  onClick={() => setSelectedNode(isSelected ? null : node.id)}
                  aria-label={`Select ${node.label} neural node`}
                  aria-pressed={isSelected}
                >
                  <span className="neural-node-pulse" />
                  <span className="neural-node-core" />
                  <span className="neural-node-label">{node.label}</span>
                </button>
              );
            })}
          </div>

          <div className="network-center-caption">
            <span>HUMAN ↔ AI</span>
            <strong>OBSERVABLE ARCHITECTURE</strong>
          </div>
        </div>

        <div className="neural-network-footer">
          <div className="network-legend" aria-label="Neural network groups">
            <span><i className="legend-dot legend-dot--core" /> CORE</span>
            <span><i className="legend-dot legend-dot--agent" /> AGENTS</span>
            <span><i className="legend-dot legend-dot--data" /> DATA</span>
            <span><i className="legend-dot legend-dot--runtime" /> RUNTIME</span>
          </div>
          <div className="network-selection" aria-live="polite">
            {selectedNode ? `FOCUS · ${nodeMap[selectedNode]?.label}` : 'SELECT A NODE TO INSPECT'}
          </div>
        </div>
      </div>
    </section>
  );
};

export default NeuralNetworkLayer;
