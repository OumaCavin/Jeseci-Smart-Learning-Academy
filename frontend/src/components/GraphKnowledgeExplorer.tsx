import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiService } from '../services/api';

interface GraphNode {
  id: string;
  label: string;
  type: string;
  category?: string;
  difficulty?: string;
  x?: number;
  y?: number;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
  strength?: number;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

const GraphKnowledgeExplorer: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'explore' | 'recommendations' | 'search'>('explore');
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  useEffect(() => {
    loadGraphData();
  }, []);

  useEffect(() => {
    if (canvasRef.current) {
      drawGraph();
    }
  }, [graphData, selectedNode, zoom, pan]);

  const loadGraphData = async () => {
    try {
      setLoading(true);
      // Load some sample graph data for demonstration
      const sampleNodes: GraphNode[] = [
        { id: 'osp', label: 'Object-Spatial Programming', type: 'concept', category: 'Paradigm', difficulty: 'intermediate' },
        { id: 'nodes', label: 'Nodes', type: 'concept', category: 'Graph Structures', difficulty: 'beginner' },
        { id: 'edges', label: 'Edges', type: 'concept', category: 'Graph Structures', difficulty: 'beginner' },
        { id: 'walkers', label: 'Walkers', type: 'concept', category: 'Computation', difficulty: 'intermediate' },
        { id: 'jac', label: 'Jac Language', type: 'language', category: 'Programming' },
        { id: 'patterns', label: 'Design Patterns', type: 'concept', category: 'Software Engineering', difficulty: 'advanced' },
        { id: 'algorithms', label: 'Algorithms', type: 'concept', category: 'Computer Science', difficulty: 'intermediate' },
        { id: 'graphs', label: 'Graph Theory', type: 'concept', category: 'Mathematics', difficulty: 'advanced' },
      ];

      const sampleEdges: GraphEdge[] = [
        { source: 'osp', target: 'nodes', type: 'includes' },
        { source: 'osp', target: 'edges', type: 'includes' },
        { source: 'osp', target: 'walkers', type: 'includes' },
        { source: 'jac', target: 'osp', type: 'implements' },
        { source: 'patterns', target: 'osp', type: 'applies' },
        { source: 'algorithms', target: 'walkers', type: 'uses' },
        { source: 'graphs', target: 'osp', type: 'foundation' },
        { source: 'nodes', target: 'graphs', type: 'based_on' },
        { source: 'edges', target: 'graphs', type: 'based_on' },
      ];

      setGraphData({ nodes: sampleNodes, edges: sampleEdges });
    } catch (error) {
      console.error('Error loading graph data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async () => {
    try {
      const response = await apiService.snippetVersion('list', {});
      // Placeholder for recommendations
      setRecommendations([
        { id: 'rec1', title: 'Advanced Walker Patterns', reason: 'Based on your progress' },
        { id: 'rec2', title: 'Graph Algorithms', reason: 'Popular among learners' },
        { id: 'rec3', title: 'Distributed Systems', reason: 'Recommended for your skill level' },
      ]);
    } catch (error) {
      console.error('Error loading recommendations:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      setLoading(true);
      // Filter nodes based on search query
      const filteredNodes = graphData.nodes.filter(node =>
        node.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.category?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      
      setGraphData(prev => ({
        ...prev,
        nodes: searchQuery ? filteredNodes : prev.nodes
      }));
      setViewMode('search');
    } catch (error) {
      console.error('Error searching graph:', error);
    } finally {
      setLoading(false);
    }
  };

  const drawGraph = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, width, height);

    // Apply transformations
    ctx.save();
    ctx.translate(pan.x + width / 2, pan.y + height / 2);
    ctx.scale(zoom, zoom);

    // Draw edges
    graphData.edges.forEach(edge => {
      const sourceNode = graphData.nodes.find(n => n.id === edge.source);
      const targetNode = graphData.nodes.find(n => n.id === edge.target);

      if (sourceNode && targetNode) {
        const x1 = (graphData.nodes.indexOf(sourceNode) % 4) * 150 - 225;
        const y1 = Math.floor(graphData.nodes.indexOf(sourceNode) / 4) * 150 - 75;
        const x2 = (graphData.nodes.indexOf(targetNode) % 4) * 150 - 225;
        const y2 = Math.floor(graphData.nodes.indexOf(targetNode) / 4) * 150 - 75;

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = 'rgba(102, 126, 234, 0.4)';
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    });

    // Draw nodes
    graphData.nodes.forEach((node, index) => {
      const x = (index % 4) * 150 - 225;
      const y = Math.floor(index / 4) * 150 - 75;

      const isSelected = selectedNode?.id === node.id;
      const isHighlighted = selectedNode && (
        graphData.edges.some(e => e.source === node.id || e.target === node.id)
      );

      // Node circle
      ctx.beginPath();
      ctx.arc(x, y, isSelected ? 35 : 30, 0, Math.PI * 2);
      
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, 35);
      if (isSelected) {
        gradient.addColorStop(0, '#667eea');
        gradient.addColorStop(1, '#764ba2');
      } else if (isHighlighted) {
        gradient.addColorStop(0, '#48bb78');
        gradient.addColorStop(1, '#38a169');
      } else {
        gradient.addColorStop(0, '#4a5568');
        gradient.addColorStop(1, '#2d3748');
      }
      ctx.fillStyle = gradient;
      ctx.fill();

      // Node border
      ctx.strokeStyle = isSelected ? '#fff' : 'rgba(255,255,255,0.2)';
      ctx.lineWidth = isSelected ? 3 : 1;
      ctx.stroke();

      // Node label
      ctx.fillStyle = '#fff';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      const labelLines = node.label.split(' ');
      labelLines.forEach((line, i) => {
        ctx.fillText(line, x, y - 8 + i * 14);
      });

      // Store position for interaction
      node.x = x;
      node.y = y;
    });

    ctx.restore();
  }, [graphData, selectedNode, zoom, pan]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Check if clicked on a node
    graphData.nodes.forEach(node => {
      if (node.x !== undefined && node.y !== undefined) {
        const screenX = (node.x * zoom) + pan.x + canvas.width / 2;
        const screenY = (node.y * zoom) + pan.y + canvas.height / 2;
        const distance = Math.sqrt(Math.pow(x - screenX, 2) + Math.pow(y - screenY, 2));

        if (distance < 35 * zoom) {
          setSelectedNode(node);
        }
      }
    });
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.2, 3));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.2, 0.5));
  };

  const handleResetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSelectedNode(null);
  };

  return (
    <div className="graph-explorer">
      <div className="explorer-header">
        <h2>Knowledge Graph Explorer</h2>
        <p>Visualize and navigate the learning knowledge graph</p>
      </div>

      <div className="explorer-toolbar">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search concepts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch}>Search</button>
        </div>

        <div className="view-modes">
          <button
            className={viewMode === 'explore' ? 'active' : ''}
            onClick={() => { setViewMode('explore'); loadGraphData(); }}
          >
            Explore
          </button>
          <button
            className={viewMode === 'recommendations' ? 'active' : ''}
            onClick={() => { setViewMode('recommendations'); loadRecommendations(); }}
          >
            Recommendations
          </button>
        </div>

        <div className="zoom-controls">
          <button onClick={handleZoomOut}>−</button>
          <span>{Math.round(zoom * 100)}%</span>
          <button onClick={handleZoomIn}>+</button>
          <button onClick={handleResetView}>Reset</button>
        </div>
      </div>

      <div className="explorer-content">
        <div className="graph-container">
          {loading ? (
            <div className="loading-state">
              <span className="loading-spinner"></span>
              Loading graph...
            </div>
          ) : (
            <canvas
              ref={canvasRef}
              width={800}
              height={500}
              onClick={handleCanvasClick}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
            />
          )}
        </div>

        <aside className="explorer-sidebar">
          {selectedNode ? (
            <div className="node-details">
              <h3>{selectedNode.label}</h3>
              <div className="detail-badges">
                <span className="badge type">{selectedNode.type}</span>
                {selectedNode.category && (
                  <span className="badge category">{selectedNode.category}</span>
                )}
                {selectedNode.difficulty && (
                  <span className={`badge difficulty ${selectedNode.difficulty}`}>
                    {selectedNode.difficulty}
                  </span>
                )}
              </div>
              
              <div className="related-section">
                <h4>Related Concepts</h4>
                {graphData.edges
                  .filter(e => e.source === selectedNode.id || e.target === selectedNode.id)
                  .map(edge => {
                    const relatedId = edge.source === selectedNode.id ? edge.target : edge.source;
                    const relatedNode = graphData.nodes.find(n => n.id === relatedId);
                    return relatedNode ? (
                      <div
                        key={relatedId}
                        className="related-item"
                        onClick={() => setSelectedNode(relatedNode)}
                      >
                        <span className="relation-type">{edge.type}</span>
                        <span>{relatedNode.label}</span>
                      </div>
                    ) : null;
                  })}
              </div>

              <button className="btn btn-primary">Start Learning</button>
            </div>
          ) : (
            <div className="no-selection">
              <span className="icon">🗺️</span>
              <p>Select a node to view details</p>
            </div>
          )}

          {viewMode === 'recommendations' && recommendations.length > 0 && (
            <div className="recommendations-section">
              <h4>AI Recommendations</h4>
              {recommendations.map(rec => (
                <div key={rec.id} className="recommendation-item">
                  <span className="rec-title">{rec.title}</span>
                  <span className="rec-reason">{rec.reason}</span>
                </div>
              ))}
            </div>
          )}
        </aside>
      </div>

      <div className="explorer-legend">
        <div className="legend-item">
          <span className="legend-dot concept"></span>
          <span>Concept</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot language"></span>
          <span>Language</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot pattern"></span>
          <span>Pattern</span>
        </div>
      </div>
    </div>
  );
};

export default GraphKnowledgeExplorer;
