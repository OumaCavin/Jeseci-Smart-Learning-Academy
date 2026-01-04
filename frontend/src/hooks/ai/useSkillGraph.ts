import { useState, useCallback, useEffect, useMemo } from 'react';
import { useAI, SkillNode, LearningRecommendation, AILearningPath } from '../../contexts/AILearningContext';

export interface UseSkillGraphOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  showCompletedSkills?: boolean;
  showLockedSkills?: boolean;
}

export interface UseSkillGraphReturn {
  // Graph Data
  nodes: SkillNode[];
  links: { source: string; target: string; }[];
  categories: string[];
  
  // Statistics
  completedCount: number;
  inProgressCount: number;
  availableCount: number;
  lockedCount: number;
  averageProficiency: number;
  
  // Progress
  overallProgress: number;
  totalHoursInvested: number;
  
  // Filtering
  filterByCategory: (category: string | null) => void;
  filterByStatus: (status: SkillNode['status'] | null) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  
  // Selection
  selectedNode: SkillNode | null;
  selectNode: (nodeId: string | null) => void;
  hoveredNode: SkillNode | null;
  setHoveredNode: (node: SkillNode | null) => void;
  
  // Actions
  refreshGraph: () => Promise<void>;
  getPathToSkill: (skillId: string) => SkillNode[];
}

export function useSkillGraph(options: UseSkillGraphOptions = {}): UseSkillGraphReturn {
  const {
    autoRefresh = false,
    refreshInterval = 60000,
    showCompletedSkills = true,
    showLockedSkills = true,
  } = options;

  const {
    skillGraph,
    fetchSkillGraph,
    getSkillById,
    getSkillPath,
  } = useAI();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<SkillNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<SkillNode | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<SkillNode['status'] | null>(null);

  // Filter and process nodes
  const filteredNodes = useMemo(() => {
    return skillGraph.filter(node => {
      // Search filter
      if (searchQuery && !node.label.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      
      // Category filter
      if (categoryFilter && node.category !== categoryFilter) {
        return false;
      }
      
      // Status filter
      if (statusFilter && node.status !== statusFilter) {
        return false;
      }
      
      // Toggle filters
      if (!showCompletedSkills && node.status === 'completed') {
        return false;
      }
      if (!showLockedSkills && node.status === 'locked') {
        return false;
      }
      
      return true;
    });
  }, [skillGraph, searchQuery, categoryFilter, statusFilter, showCompletedSkills, showLockedSkills]);

  // Generate links based on dependencies
  const links = useMemo(() => {
    const linkSet = new Set<string>();
    
    filteredNodes.forEach(node => {
      node.dependencies.forEach(depId => {
        if (skillGraph.find(s => s.id === depId)) {
          const key = `${depId}->${node.id}`;
          const reverseKey = `${node.id}->${depId}`;
          if (!linkSet.has(reverseKey)) {
            linkSet.add(key);
          }
        }
      });
      
      node.relatedSkills.forEach(relatedId => {
        if (skillGraph.find(s => s.id === relatedId)) {
          const key = `${node.id}->${relatedId}`;
          if (!linkSet.has(key)) {
            linkSet.add(key);
          }
        }
      });
    });
    
    return Array.from(linkSet).map(link => {
      const [source, target] = link.split('->');
      return { source, target };
    });
  }, [filteredNodes, skillGraph]);

  // Get unique categories
  const categories = useMemo(() => {
    return [...new Set(skillGraph.map(node => node.category))];
  }, [skillGraph]);

  // Calculate statistics
  const completedCount = useMemo(() => {
    return skillGraph.filter(node => node.status === 'completed').length;
  }, [skillGraph]);

  const inProgressCount = useMemo(() => {
    return skillGraph.filter(node => node.status === 'in_progress').length;
  }, [skillGraph]);

  const availableCount = useMemo(() => {
    return skillGraph.filter(node => node.status === 'available').length;
  }, [skillGraph]);

  const lockedCount = useMemo(() => {
    return skillGraph.filter(node => node.status === 'locked').length;
  }, [skillGraph]);

  const averageProficiency = useMemo(() => {
    if (skillGraph.length === 0) return 0;
    const total = skillGraph.reduce((sum, node) => sum + node.proficiency, 0);
    return Math.round(total / skillGraph.length);
  }, [skillGraph]);

  // Calculate overall progress
  const overallProgress = useMemo(() => {
    if (skillGraph.length === 0) return 0;
    const totalWeight = skillGraph.length;
    const completedWeight = completedCount + (inProgressCount * 0.5);
    return Math.round((completedWeight / totalWeight) * 100);
  }, [skillGraph.length, completedCount, inProgressCount]);

  // Calculate total hours invested
  const totalHoursInvested = useMemo(() => {
    return skillGraph
      .filter(node => node.status === 'completed' || node.status === 'in_progress')
      .reduce((sum, node) => {
        const progress = node.status === 'completed' ? 1 : (node.resourcesCompleted / node.totalResources);
        return sum + (node.estimatedHours * progress);
      }, 0);
  }, [skillGraph]);

  // Filter by category
  const filterByCategory = useCallback((category: string | null) => {
    setCategoryFilter(category);
  }, []);

  // Filter by status
  const filterByStatus = useCallback((status: SkillNode['status'] | null) => {
    setStatusFilter(status);
  }, []);

  // Select node
  const selectNode = useCallback((nodeId: string | null) => {
    if (nodeId === null) {
      setSelectedNode(null);
    } else {
      const node = getSkillById(nodeId);
      setSelectedNode(node || null);
    }
  }, [getSkillById]);

  // Refresh graph
  const refreshGraph = useCallback(async () => {
    await fetchSkillGraph();
  }, [fetchSkillGraph]);

  // Get path to skill
  const getPathToSkill = useCallback((skillId: string): SkillNode[] => {
    return getSkillPath('js-basics', skillId);
  }, [getSkillPath]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      fetchSkillGraph();
    }, refreshInterval);
    
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchSkillGraph]);

  return {
    nodes: filteredNodes,
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
    getPathToSkill,
  };
}

export default useSkillGraph;
