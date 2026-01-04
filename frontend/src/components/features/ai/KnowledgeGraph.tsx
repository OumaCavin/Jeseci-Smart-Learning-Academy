import React, { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { useSkillGraph, SkillNode } from '../../hooks/ai/useSkillGraph';
import './KnowledgeGraph.css';

interface KnowledgeGraphProps {
  onNodeClick?: (node: SkillNode) => void;
  onNodeHover?: (node: SkillNode | null) => void;
  height?: number | string;
  showLegend?: boolean;
  showFilters?: boolean;
  showStats?: boolean;
  layout?: 'force' | 'tree' | 'grid';
}

export function KnowledgeGraph({
  onNodeClick,
  onNodeHover,
  height = 600,
  showLegend = true,
  showFilters = true,
  showStats = true,
  layout = 'force',
}: KnowledgeGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  
  const {
    nodes,
    links,
    categories,
    completedCount,
    inProgressCount,
    availableCount,
    lockedCount,
    averageProficiency,
    overallProgress,
    totalHoursInvested,
    filterByCategory,
    filterByStatus,
    searchQuery,
    setSearchQuery,
    selectedNode,
    selectNode,
    hoveredNode,
    setHoveredNode,
    refreshGraph,
  } = useSkillGraph({ showCompletedSkills: true, showLockedSkills: true });

  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [activeStatus, setActiveStatus] = useState<string | null>(null);

  // Get node color based on status
  const getNodeColor = (node: SkillNode): string => {
    switch (node.status) {
      case 'completed':
        return '#10b981'; // Green
      case 'in_progress':
        return '#3b82f6'; // Blue
      case 'available':
        return '#f59e0b'; // Amber
      case 'locked':
        return '#6b7280'; // Gray
      default:
        return '#6b7280';
    }
  };

  // Get node size based on proficiency
  const getNodeSize = (node: SkillNode): number => {
    return 30 + (node.proficiency / 100) * 40;
  };

  // Handle node click
  const handleNodeClick = useCallback((node: SkillNode) => {
    selectNode(node.id);
    onNodeClick?.(node);
  }, [selectNode, onNodeClick]);

  // Handle node hover
  const handleNodeHover = useCallback((node: SkillNode | null) => {
    setHoveredNode(node);
    onNodeHover?.(node);
  }, [setHoveredNode, onNodeHover]);

  // Handle zoom
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setTransform(prev => ({
      ...prev,
      k: Math.min(Math.max(prev.k * delta, 0.5), 3),
    }));
  }, []);

  // Handle pan
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 0) return;
    
    const startX = e.clientX;
    const startY = e.clientY;
    const startTransform = { ...transform };

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const dx = moveEvent.clientX - startX;
      const dy = moveEvent.clientY - startY;
      setTransform({
        x: startTransform.x + dx,
        y: startTransform.y + dy,
        k: startTransform.k,
      });
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [transform]);

  // Reset view
  const handleResetView = useCallback(() => {
    setTransform({ x: 0, y: 0, k: 1 });
  }, []);

  // Calculate node positions (simple force layout simulation)
  const nodePositions = useMemo(() => {
    const positions: Record<string, { x: number; y: number }> = {};
    const centerX = 400;
    const centerY = 300;
    const radius = 200;

    if (layout === 'grid') {
      const cols = Math.ceil(Math.sqrt(nodes.length));
      nodes.forEach((node, i) => {
        const col = i % cols;
        const row = Math.floor(i / cols);
        positions[node.id] = {
          x: centerX + (col - cols / 2) * 120,
          y: centerY + (row - nodes.length / cols / 2) * 100,
        };
      });
    } else if (layout === 'tree') {
      // Hierarchical layout
      nodes.forEach((node, i) => {
        positions[node.id] = {
          x: centerX + (i - nodes.length / 2) * 100,
          y: centerY - (node.level === 'beginner' ? 100 : node.level === 'expert' ? 100 : 0),
        };
      });
    } else {
      // Radial layout
      nodes.forEach((node, i) => {
        const angle = (i / nodes.length) * 2 * Math.PI;
        positions[node.id] = {
          x: centerX + Math.cos(angle) * radius,
          y: centerY + Math.sin(angle) * radius,
        };
      });
    }

    return positions;
  }, [nodes, layout]);

  return (
    <div className="knowledge-graph" ref={containerRef}>
      {showFilters && (
        <div className="graph-filters">
          <div className="filter-group">
            <input
              type="text"
              placeholder="Search skills..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="filter-group">
            <label>Category:</label>
            <select
              value={activeCategory || ''}
              onChange={(e) => {
                setActiveCategory(e.target.value || null);
                filterByCategory(e.target.value || null);
              }}
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label>Status:</label>
            <select
              value={activeStatus || ''}
              onChange={(e) => {
                setActiveStatus(e.target.value || null);
                filterByStatus(e.target.value || null);
              }}
            >
              <option value="">All Status</option>
              <option value="completed">Completed</option>
              <option value="in_progress">In Progress</option>
              <option value="available">Available</option>
              <option value="locked">Locked</option>
            </select>
          </div>
          
          <button onClick={refreshGraph} className="refresh-btn">
            ↻ Refresh
          </button>
        </div>
      )}

      {showStats && (
        <div className="graph-stats">
          <div className="stat-item">
            <span className="stat-value">{overallProgress}%</span>
            <span className="stat-label">Overall Progress</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{completedCount}</span>
            <span className="stat-label">Completed</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{inProgressCount}</span>
            <span className="stat-label">In Progress</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{averageProficiency}%</span>
            <span className="stat-label">Avg Proficiency</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{totalHoursInvested.toFixed(0)}h</span>
            <span className="stat-label">Hours Invested</span>
          </div>
        </div>
      )}

      <div
        className="graph-container"
        style={{ height }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
      >
        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          viewBox="-400 -300 800 600"
          preserveAspectRatio="xMidYMid meet"
        >
          <g transform={`translate(${transform.x}, ${transform.y}) scale(${transform.k})`}>
            {/* Links */}
            {links.map((link, i) => {
              const sourcePos = nodePositions[link.source];
              const targetPos = nodePositions[link.target];
              
              if (!sourcePos || !targetPos) return null;
              
              return (
                <line
                  key={i}
                  x1={sourcePos.x}
                  y1={sourcePos.y}
                  x2={targetPos.x}
                  y2={targetPos.y}
                  className="graph-link"
                />
              );
            })}

            {/* Nodes */}
            {nodes.map((node) => {
              const pos = nodePositions[node.id];
              if (!pos) return null;
              
              const isSelected = selectedNode?.id === node.id;
              const isHovered = hoveredNode?.id === node.id;
              const size = getNodeSize(node);
              
              return (
                <g
                  key={node.id}
                  className={`graph-node ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`}
                  onClick={() => handleNodeClick(node)}
                  onMouseEnter={() => handleNodeHover(node)}
                  onMouseLeave={() => handleNodeHover(null)}
                  transform={`translate(${pos.x}, ${pos.y})`}
                >
                  {/* Outer ring */}
                  <circle
                    r={size / 2 + 5}
                    fill="none"
                    stroke={getNodeColor(node)}
                    strokeWidth={isSelected ? 3 : 1}
                    opacity={0.3}
                  />
                  
                  {/* Main circle */}
                  <circle
                    r={size / 2}
                    fill={getNodeColor(node)}
                    fillOpacity={0.8}
                    stroke={isSelected ? '#fff' : 'none'}
                    strokeWidth={2}
                  />
                  
                  {/* Proficiency indicator */}
                  <circle
                    r={size / 4}
                    fill="#fff"
                    fillOpacity={0.9}
                  />
                  
                  {/* Label */}
                  <text
                    y={size / 2 + 20}
                    textAnchor="middle"
                    className="node-label"
                    fill="#fff"
                    fontSize="12"
                  >
                    {node.label.length > 15 ? node.label.slice(0, 15) + '...' : node.label}
                  </text>
                  
                  {/* Proficiency text */}
                  <text
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill={getNodeColor(node)}
                    fontSize="10"
                    fontWeight="bold"
                  >
                    {node.proficiency}%
                  </text>
                </g>
              );
            })}
          </g>
        </svg>
        
        {/* Hover tooltip */}
        {hoveredNode && (
          <div
            className="node-tooltip"
            style={{
              position: 'absolute',
              left: '50%',
              top: '20px',
              transform: 'translateX(-50%)',
            }}
          >
            <h4>{hoveredNode.label}</h4>
            <p>Category: {hoveredNode.category}</p>
            <p>Level: {hoveredNode.level}</p>
            <p>Proficiency: {hoveredNode.proficiency}%</p>
            <p>Status: {hoveredNode.status}</p>
          </div>
        )}
        
        {/* Zoom controls */}
        <div className="zoom-controls">
          <button onClick={() => setTransform(prev => ({ ...prev, k: Math.min(prev.k * 1.2, 3) }))}>+</button>
          <button onClick={() => setTransform(prev => ({ ...prev, k: Math.max(prev.k * 0.8, 0.5) }))}>-</button>
          <button onClick={handleResetView}>⟲</button>
        </div>
      </div>

      {showLegend && (
        <div className="graph-legend">
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#10b981' }}></span>
            <span>Completed ({completedCount})</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#3b82f6' }}></span>
            <span>In Progress ({inProgressCount})</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#f59e0b' }}></span>
            <span>Available ({availableCount})</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#6b7280' }}></span>
            <span>Locked ({lockedCount})</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default KnowledgeGraph;
