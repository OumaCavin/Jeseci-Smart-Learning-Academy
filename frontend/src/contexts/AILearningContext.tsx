import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';

// Type definitions for AI learning recommendations
export interface SkillNode {
  id: string;
  label: string;
  category: string;
  proficiency: number; // 0-100
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  dependencies: string[];
  relatedSkills: string[];
  status: 'locked' | 'available' | 'in_progress' | 'completed';
  estimatedHours: number;
  resourcesCompleted: number;
  totalResources: number;
  lastAccessedAt?: string;
  completedAt?: string;
}

export interface LearningRecommendation {
  id: string;
  moduleId: string;
  moduleTitle: string;
  confidence: number; // 0-1
  reason: 'gap_fill' | 'advancement' | 'reinforcement' | 'project_based' | 'prerequisite';
  reasoning: string;
  priority: number;
  estimatedDuration: number;
  skillsGained: string[];
  prerequisitesMet: boolean;
  projectedOutcome: string;
  metadata?: {
    difficulty: number;
    engagementScore: number;
    completionRate: number;
  };
}

export interface AILearningPath {
  id: string;
  title: string;
  description: string;
  targetRole: string;
  totalDuration: number;
  totalModules: number;
  skills: string[];
  modules: {
    moduleId: string;
    order: number;
    isRecommended: boolean;
    alternativeModules?: string[];
  }[];
  progress: number;
  estimatedCompletionDate?: string;
}

export interface UserLearningProfile {
  userId: string;
  currentSkillGraph: SkillNode[];
  activePath: AILearningPath | null;
  recommendations: LearningRecommendation[];
  learningVelocity: number; // hours per week
  preferredLearningStyle: 'visual' | 'practical' | 'theoretical' | 'mixed';
  goals: string[];
  weakAreas: string[];
  strongAreas: string[];
  recentActivity: {
    skillId: string;
    action: string;
    timestamp: string;
  }[];
}

export interface AIRecommendationConfig {
  maxRecommendations: number;
  includeAlternatives: boolean;
  prioritizeWeakAreas: boolean;
  respectLearningPath: boolean;
  adaptToVelocity: boolean;
}

export interface AIContextType {
  // State
  skillGraph: SkillNode[];
  recommendations: LearningRecommendation[];
  activePath: AILearningPath | null;
  userProfile: UserLearningProfile | null;
  isLoading: boolean;
  error: string | null;
  config: AIRecommendationConfig;
  
  // Skill Graph Operations
  fetchSkillGraph: () => Promise<void>;
  updateSkillProficiency: (skillId: string, proficiency: number) => void;
  getSkillById: (skillId: string) => SkillNode | undefined;
  getSkillPath: (fromSkillId: string, toSkillId: string) => SkillNode[];
  
  // Recommendation Operations
  fetchRecommendations: () => Promise<void>;
  dismissRecommendation: (recommendationId: string) => void;
  acceptRecommendation: (recommendationId: string) => Promise<void>;
  reorderRecommendations: (fromIndex: number, toIndex: number) => void;
  
  // Path Operations
  fetchLearningPaths: () => Promise<AILearningPath[]>;
  setActivePath: (pathId: string) => Promise<void>;
  updatePathProgress: (pathId: string, moduleId: string, completed: boolean) => Promise<void>;
  getNextRecommendedModule: () => LearningRecommendation | null;
  
  // Profile Operations
  fetchUserProfile: () => Promise<void>;
  updateLearningPreferences: (preferences: Partial<UserLearningProfile>) => Promise<void>;
  addGoal: (goal: string) => Promise<void>;
  removeGoal: (goal: string) => Promise<void>;
  
  // Configuration
  updateConfig: (config: Partial<AIRecommendationConfig>) => void;
  resetConfig: () => void;
}

const AIContext = createContext<AIContextType | undefined>(undefined);

export function AIProvider({ children }: { children: ReactNode }) {
  const [skillGraph, setSkillGraph] = useState<SkillNode[]>([]);
  const [recommendations, setRecommendations] = useState<LearningRecommendation[]>([]);
  const [activePath, setActivePath] = useState<AILearningPath | null>(null);
  const [userProfile, setUserProfile] = useState<UserLearningProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [config, setConfig] = useState<AIRecommendationConfig>({
    maxRecommendations: 5,
    includeAlternatives: true,
    prioritizeWeakAreas: true,
    respectLearningPath: true,
    adaptToVelocity: true,
  });

  // Fetch skill graph
  const fetchSkillGraph = useCallback(async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      const response = await new Promise<SkillNode[]>((resolve) => {
        setTimeout(() => {
          const skills: SkillNode[] = [
            {
              id: 'js-basics',
              label: 'JavaScript Fundamentals',
              category: 'Programming',
              proficiency: 75,
              level: 'intermediate',
              dependencies: [],
              relatedSkills: ['html', 'css'],
              status: 'completed',
              estimatedHours: 20,
              resourcesCompleted: 8,
              totalResources: 10,
              completedAt: '2025-12-01T10:00:00Z',
            },
            {
              id: 'react-basics',
              label: 'React Fundamentals',
              category: 'Frontend',
              proficiency: 45,
              level: 'intermediate',
              dependencies: ['js-basics'],
              relatedSkills: ['state-management', 'hooks'],
              status: 'in_progress',
              estimatedHours: 30,
              resourcesCompleted: 5,
              totalResources: 15,
              lastAccessedAt: '2025-12-15T14:30:00Z',
            },
            {
              id: 'typescript',
              label: 'TypeScript',
              category: 'Programming',
              proficiency: 0,
              level: 'intermediate',
              dependencies: ['js-basics'],
              relatedSkills: ['react', 'nodejs'],
              status: 'available',
              estimatedHours: 25,
              resourcesCompleted: 0,
              totalResources: 12,
            },
            {
              id: 'nodejs',
              label: 'Node.js Backend',
              category: 'Backend',
              proficiency: 20,
              level: 'intermediate',
              dependencies: ['js-basics'],
              relatedSkills: ['express', 'databases'],
              status: 'in_progress',
              estimatedHours: 40,
              resourcesCompleted: 4,
              totalResources: 20,
              lastAccessedAt: '2025-12-10T09:00:00Z',
            },
          ];
          resolve(skills);
        }, 500);
      });
      setSkillGraph(response);
    } catch (err) {
      setError('Failed to fetch skill graph');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Update skill proficiency
  const updateSkillProficiency = useCallback((skillId: string, proficiency: number) => {
    setSkillGraph(prev =>
      prev.map(skill =>
        skill.id === skillId
          ? { ...skill, proficiency: Math.min(100, Math.max(0, proficiency)) }
          : skill
      )
    );
  }, []);

  // Get skill by ID
  const getSkillById = useCallback((skillId: string) => {
    return skillGraph.find(skill => skill.id === skillId);
  }, [skillGraph]);

  // Get path between two skills
  const getSkillPath = useCallback((fromSkillId: string, toSkillId: string): SkillNode[] => {
    const fromSkill = getSkillById(fromSkillId);
    const toSkill = getSkillById(toSkillId);
    
    if (!fromSkill || !toSkill) return [];
    
    // Simple path finding - in production, use proper graph algorithm
    const path: SkillNode[] = [fromSkill];
    if (fromSkill.relatedSkills.includes(toSkillId)) {
      path.push(toSkill);
    }
    return path;
  }, [getSkillById]);

  // Fetch recommendations
  const fetchRecommendations = useCallback(async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      const response = await new Promise<LearningRecommendation[]>((resolve) => {
        setTimeout(() => {
          const recs: LearningRecommendation[] = [
            {
              id: 'rec-1',
              moduleId: 'typescript',
              moduleTitle: 'TypeScript Essentials',
              confidence: 0.92,
              reason: 'gap_fill',
              reasoning: 'TypeScript fills the gap between your JavaScript knowledge and enterprise-level development requirements.',
              priority: 1,
              estimatedDuration: 25,
              skillsGained: ['types', 'interfaces', 'generics'],
              prerequisitesMet: true,
              projectedOutcome: 'Ability to write type-safe JavaScript applications',
              metadata: { difficulty: 3, engagementScore: 85, completionRate: 78 },
            },
            {
              id: 'rec-2',
              moduleId: 'react-hooks',
              moduleTitle: 'Advanced React Hooks',
              confidence: 0.88,
              reason: 'advancement',
              reasoning: 'Building on your React progress, mastering hooks will significantly boost your development efficiency.',
              priority: 2,
              estimatedDuration: 15,
              skillsGained: ['custom-hooks', 'useReducer', 'useMemo'],
              prerequisitesMet: true,
              projectedOutcome: 'Expertise in React hooks patterns and custom hook creation',
              metadata: { difficulty: 4, engagementScore: 90, completionRate: 72 },
            },
            {
              id: 'rec-3',
              moduleId: 'express-basics',
              moduleTitle: 'Express.js Fundamentals',
              confidence: 0.75,
              reason: 'project_based',
              reasoning: 'Complements your Node.js progress with practical backend framework skills.',
              priority: 3,
              estimatedDuration: 20,
              skillsGained: ['routing', 'middleware', 'rest-apis'],
              prerequisitesMet: true,
              projectedOutcome: 'Ability to create RESTful APIs with Express.js',
              metadata: { difficulty: 3, engagementScore: 82, completionRate: 85 },
            },
          ];
          resolve(recs);
        }, 600);
      });
      setRecommendations(response);
    } catch (err) {
      setError('Failed to fetch recommendations');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Dismiss recommendation
  const dismissRecommendation = useCallback((recommendationId: string) => {
    setRecommendations(prev => prev.filter(r => r.id !== recommendationId));
  }, []);

  // Accept recommendation
  const acceptRecommendation = useCallback(async (recommendationId: string) => {
    const recommendation = recommendations.find(r => r.id === recommendationId);
    if (!recommendation) return;
    
    // In production, this would trigger navigation or enrollment
    console.log('Accepted recommendation:', recommendation.moduleTitle);
    setRecommendations(prev => prev.filter(r => r.id !== recommendationId));
  }, [recommendations]);

  // Reorder recommendations
  const reorderRecommendations = useCallback((fromIndex: number, toIndex: number) => {
    setRecommendations(prev => {
      const updated = [...prev];
      const [removed] = updated.splice(fromIndex, 1);
      updated.splice(toIndex, 0, removed);
      return updated;
    });
  }, []);

  // Fetch learning paths
  const fetchLearningPaths = useCallback(async (): Promise<AILearningPath[]> => {
    return [
      {
        id: 'path-fullstack',
        title: 'Full Stack Developer',
        description: 'Master both frontend and backend development',
        targetRole: 'Full Stack Developer',
        totalDuration: 200,
        totalModules: 12,
        skills: ['JavaScript', 'React', 'Node.js', 'TypeScript', 'Databases'],
        modules: [
          { moduleId: 'js-basics', order: 1, isRecommended: true },
          { moduleId: 'react-basics', order: 2, isRecommended: true },
          { moduleId: 'typescript', order: 3, isRecommended: true },
          { moduleId: 'nodejs', order: 4, isRecommended: true },
        ],
        progress: 35,
        estimatedCompletionDate: '2026-06-01',
      },
    ];
  }, []);

  // Set active learning path
  const setActivePath = useCallback(async (pathId: string) => {
    const paths = await fetchLearningPaths();
    const path = paths.find(p => p.id === pathId);
    if (path) {
      setActivePath(path);
    }
  }, [fetchLearningPaths]);

  // Update path progress
  const updatePathProgress = useCallback(async (pathId: string, moduleId: string, completed: boolean) => {
    console.log(`Path ${pathId}: Module ${moduleId} marked as ${completed ? 'completed' : 'incomplete'}`);
  }, []);

  // Get next recommended module
  const getNextRecommendedModule = useCallback(() => {
    return recommendations.length > 0 ? recommendations[0] : null;
  }, [recommendations]);

  // Fetch user profile
  const fetchUserProfile = useCallback(async () => {
    setIsLoading(true);
    try {
      const profile: UserLearningProfile = {
        userId: 'user-123',
        currentSkillGraph: [],
        activePath: null,
        recommendations: [],
        learningVelocity: 8.5,
        preferredLearningStyle: 'practical',
        goals: ['Become a Full Stack Developer', 'Master TypeScript'],
        weakAreas: ['Backend Architecture', 'Testing'],
        strongAreas: ['JavaScript', 'React Components'],
        recentActivity: [
          { skillId: 'react-basics', action: 'completed_lesson', timestamp: '2025-12-15T14:30:00Z' },
          { skillId: 'nodejs', action: 'started_module', timestamp: '2025-12-10T09:00:00Z' },
        ],
      };
      setUserProfile(profile);
    } catch (err) {
      setError('Failed to fetch user profile');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Update learning preferences
  const updateLearningPreferences = useCallback(async (preferences: Partial<UserLearningProfile>) => {
    setUserProfile(prev => prev ? { ...prev, ...preferences } : null);
  }, []);

  // Add goal
  const addGoal = useCallback(async (goal: string) => {
    setUserProfile(prev => prev ? { ...prev, goals: [...prev.goals, goal] } : null);
  }, []);

  // Remove goal
  const removeGoal = useCallback(async (goal: string) => {
    setUserProfile(prev => prev ? { ...prev, goals: prev.goals.filter(g => g !== goal) } : null);
  }, []);

  // Update config
  const updateConfig = useCallback((newConfig: Partial<AIRecommendationConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }));
  }, []);

  // Reset config
  const resetConfig = useCallback(() => {
    setConfig({
      maxRecommendations: 5,
      includeAlternatives: true,
      prioritizeWeakAreas: true,
      respectLearningPath: true,
      adaptToVelocity: true,
    });
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchSkillGraph();
    fetchRecommendations();
    fetchUserProfile();
  }, [fetchSkillGraph, fetchRecommendations, fetchUserProfile]);

  const value: AIContextType = {
    skillGraph,
    recommendations,
    activePath,
    userProfile,
    isLoading,
    error,
    config,
    fetchSkillGraph,
    updateSkillProficiency,
    getSkillById,
    getSkillPath,
    fetchRecommendations,
    dismissRecommendation,
    acceptRecommendation,
    reorderRecommendations,
    fetchLearningPaths,
    setActivePath,
    updatePathProgress,
    getNextRecommendedModule,
    fetchUserProfile,
    updateLearningPreferences,
    addGoal,
    removeGoal,
    updateConfig,
    resetConfig,
  };

  return (
    <AIContext.Provider value={value}>
      {children}
    </AIContext.Provider>
  );
}

export function useAI() {
  const context = useContext(AIContext);
  if (context === undefined) {
    throw new Error('useAI must be used within an AIProvider');
  }
  return context;
}

export default AIContext;
