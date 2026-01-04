import { createContext, useContext, useCallback, useState, useEffect, useRef, useMemo } from 'react';

// Types for gamification
export interface Badge {
  id: string;
  name: string;
  description: string;
  iconUrl: string;
  category: 'achievement' | 'skill' | 'milestone' | 'social' | 'special';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  requirement: string;
  xpValue: number;
  unlockedAt?: string;
  progress?: number;
  maxProgress?: number;
}

export interface UserBadge extends Badge {
  unlockedAt: string;
  progress?: number;
}

export interface XPTransaction {
  id: string;
  amount: number;
  source: string;
  description: string;
  timestamp: string;
  type: 'earned' | 'spent' | 'bonus' | 'penalty';
}

export interface Achievement {
  badge: Badge;
  isNew: boolean;
}

export interface UserLevel {
  level: number;
  title: string;
  xpRequired: number;
  xpForNext: number;
  progress: number;
}

export interface StreakData {
  currentStreak: number;
  longestStreak: number;
  lastActiveDate: string;
  streakFrozen: boolean;
  freezeAvailable: boolean;
}

export interface Challenge {
  id: string;
  title: string;
  description: string;
  type: 'daily' | 'weekly' | 'special';
  status: 'active' | 'completed' | 'expired';
  progress: number;
  maxProgress: number;
  reward: {
    xp: number;
    badge?: Badge;
  };
  expiresAt?: string;
}

export interface LeaderboardEntry {
  rank: number;
  userId: string;
  userName: string;
  avatar?: string;
  xp: number;
  level: number;
  streak: number;
  isCurrentUser: boolean;
}

export interface Leaderboard {
  id: string;
  name: string;
  type: 'global' | 'friends' | 'course' | 'weekly' | 'monthly';
  entries: LeaderboardEntry[];
  currentUserRank?: number;
  totalParticipants: number;
  updatedAt: string;
}

export interface GamificationState {
  // User progress
  currentXP: number;
  totalXP: number;
  level: UserLevel;
  streak: StreakData;
  
  // Achievements
  achievements: Achievement[];
  recentAchievements: Achievement[];
  
  // Challenges
  activeChallenges: Challenge[];
  completedChallenges: Challenge[];
  
  // Leaderboards
  leaderboards: Record<string, Leaderboard>;
  currentLeaderboard: Leaderboard | null;
  
  // Notifications
  notifications: GamificationNotification[];
  unreadCount: number;
  
  // XP gains (for animations)
  pendingXPGains: XPGain[];
}

export interface XPGain {
  id: string;
  amount: number;
  source: string;
  timestamp: string;
}

export interface GamificationNotification {
  id: string;
  type: 'level_up' | 'badge_unlocked' | 'challenge_complete' | 'streak_milestone' | 'achievement';
  title: string;
  message: string;
  data?: Record<string, unknown>;
  read: boolean;
  timestamp: string;
}

export interface GamificationContextType {
  // State
  state: GamificationState;
  
  // XP Management
  addXP: (amount: number, source: string) => void;
  spendXP: (amount: number, reason: string) => Promise<boolean>;
  
  // Level Management
  checkLevelUp: () => void;
  
  // Streak Management
  updateStreak: () => void;
  useStreakFreeze: () => Promise<boolean>;
  
  // Badges
  unlockBadge: (badgeId: string) => void;
  getBadgeProgress: (badgeId: string) => number;
  
  // Challenges
  acceptChallenge: (challengeId: string) => Promise<void>;
  updateChallengeProgress: (challengeId: string, progress: number) => void;
  completeChallenge: (challengeId: string) => Promise<void>;
  
  // Leaderboards
  fetchLeaderboard: (type: string) => Promise<void>;
  setCurrentLeaderboard: (type: string) => void;
  
  // Notifications
  markNotificationRead: (notificationId: string) => void;
  markAllNotificationsRead: () => void;
  dismissNotification: (notificationId: string) => void;
  
  // History
  getXPSummary: (days: number) => Promise<Array<{ date: string; xp: number }>>;
  
  // Initialization
  loadUserProgress: () => Promise<void>;
  refreshState: () => Promise<void>;
}

const GamificationContext = createContext<GamificationContextType | null>(null);

// Level configuration
const LEVEL_THRESHOLDS = [
  { level: 1, title: 'Novice', xpRequired: 0 },
  { level: 2, title: 'Beginner', xpRequired: 100 },
  { level: 3, title: 'Learner', xpRequired: 250 },
  { level: 4, title: 'Explorer', xpRequired: 500 },
  { level: 5, title: 'Developer', xpRequired: 1000 },
  { level: 6, title: 'Coder', xpRequired: 1750 },
  { level: 7, title: 'Programmer', xpRequired: 2750 },
  { level: 8, title: 'Engineer', xpRequired: 4000 },
  { level: 9, title: 'Architect', xpRequired: 5500 },
  { level: 10, title: 'Master', xpRequired: 7500 },
  { level: 11, title: 'Guru', xpRequired: 10000 },
  { level: 12, title: 'Legend', xpRequired: 15000 },
  { level: 13, title: 'Mythic', xpRequired: 22500 },
  { level: 14, title: 'Titan', xpRequired: 35000 },
  { level: 15, title: 'Divine', xpRequired: 50000 }
];

// Badge definitions
const BADGE_DEFINITIONS: Record<string, Omit<Badge, 'unlockedAt' | 'progress'>> = {
  'first-code': {
    id: 'first-code',
    name: 'Hello World',
    description: 'Executed your first piece of code',
    iconUrl: '/badges/hello-world.svg',
    category: 'milestone',
    rarity: 'common',
    requirement: 'Complete 1 code execution',
    xpValue: 50
  },
  'code-warrior': {
    id: 'code-warrior',
    name: 'Code Warrior',
    description: 'Completed 100 code executions',
    iconUrl: '/badges/code-warrior.svg',
    category: 'milestone',
    rarity: 'rare',
    requirement: 'Complete 100 code executions',
    xpValue: 200
  },
  'problem-solver': {
    id: 'problem-solver',
    name: 'Problem Solver',
    description: 'Passed 50 tests on the first try',
    iconUrl: '/badges/problem-solver.svg',
    category: 'achievement',
    rarity: 'rare',
    requirement: 'Pass 50 tests on first attempt',
    xpValue: 300
  },
  'streak-week': {
    id: 'streak-week',
    name: 'Week Warrior',
    description: 'Maintained a 7-day streak',
    iconUrl: '/badges/streak-week.svg',
    category: 'milestone',
    rarity: 'rare',
    requirement: '7-day activity streak',
    xpValue: 250
  },
  'streak-month': {
    id: 'streak-month',
    name: 'Consistency King',
    description: 'Maintained a 30-day streak',
    iconUrl: '/badges/streak-month.svg',
    category: 'milestone',
    rarity: 'epic',
    requirement: '30-day activity streak',
    xpValue: 1000
  },
  'collaborator': {
    id: 'collaborator',
    name: 'Team Player',
    description: 'Participated in 10 collaborative sessions',
    iconUrl: '/badges/collaborator.svg',
    category: 'social',
    rarity: 'rare',
    requirement: 'Join 10 collaboration sessions',
    xpValue: 200
  },
  'mentor': {
    id: 'mentor',
    name: 'Helpful Mentor',
    description: 'Helped 5 other students',
    iconUrl: '/badges/mentor.svg',
    category: 'social',
    rarity: 'epic',
    requirement: 'Help 5 other students',
    xpValue: 500
  },
  'perfectionist': {
    id: 'perfectionist',
    name: 'Perfectionist',
    description: 'Achieved 100% on 10 assignments',
    iconUrl: '/badges/perfectionist.svg',
    category: 'achievement',
    rarity: 'epic',
    requirement: 'Score 100% on 10 assignments',
    xpValue: 750
  },
  'polyglot': {
    id: 'polyglot',
    name: 'Polyglot',
    description: 'Used 5 different programming languages',
    iconUrl: '/badges/polyglot.svg',
    category: 'skill',
    rarity: 'epic',
    requirement: 'Use 5 different languages',
    xpValue: 500
  },
  'champion': {
    id: 'champion',
    name: 'Champion',
    description: 'Reached level 10',
    iconUrl: '/badges/champion.svg',
    category: 'milestone',
    rarity: 'legendary',
    requirement: 'Reach level 10',
    xpValue: 2000
  }
};

export function GamificationProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<GamificationState>({
    currentXP: 0,
    totalXP: 0,
    level: { level: 1, title: 'Novice', xpRequired: 0, xpForNext: 100, progress: 0 },
    streak: {
      currentStreak: 0,
      longestStreak: 0,
      lastActiveDate: '',
      streakFrozen: false,
      freezeAvailable: true
    },
    achievements: [],
    recentAchievements: [],
    activeChallenges: [],
    completedChallenges: [],
    leaderboards: {},
    currentLeaderboard: null,
    notifications: [],
    unreadCount: 0,
    pendingXPGains: []
  });

  const isInitialized = useRef(false);

  // Calculate level from XP
  const calculateLevel = useCallback((xp: number): UserLevel => {
    let currentThreshold = 0;
    let nextThreshold = LEVEL_THRESHOLDS[1]?.xpRequired || 100;

    for (let i = LEVEL_THRESHOLDS.length - 1; i >= 0; i--) {
      if (xp >= LEVEL_THRESHOLDS[i].xpRequired) {
        currentThreshold = LEVEL_THRESHOLDS[i].xpRequired;
        nextThreshold = LEVEL_THRESHOLDS[i + 1]?.xpRequired || LEVEL_THRESHOLDS[i].xpRequired + 1000;
        const prevThreshold = i > 0 ? LEVEL_THRESHOLDS[i - 1].xpRequired : 0;
        
        return {
          level: LEVEL_THRESHOLDS[i].level,
          title: LEVEL_THRESHOLDS[i].title,
          xpRequired: prevThreshold,
          xpForNext: nextThreshold,
          progress: ((xp - prevThreshold) / (nextThreshold - prevThreshold)) * 100
        };
      }
    }

    return {
      level: 1,
      title: 'Novice',
      xpRequired: 0,
      xpForNext: nextThreshold,
      progress: (xp / nextThreshold) * 100
    };
  }, []);

  // Add XP
  const addXP = useCallback((amount: number, source: string) => {
    const xpGain: XPGain = {
      id: `xpgain_${Date.now()}`,
      amount,
      source,
      timestamp: new Date().toISOString()
    };

    setState(prev => ({
      ...prev,
      currentXP: prev.currentXP + amount,
      totalXP: prev.totalXP + amount,
      pendingXPGains: [...prev.pendingXPGains, xpGain],
      level: calculateLevel(prev.currentXP + amount)
    }));

    // Clear XP gain after animation
    setTimeout(() => {
      setState(prev => ({
        ...prev,
        pendingXPGains: prev.pendingXPGains.filter(g => g.id !== xpGain.id)
      }));
    }, 3000);
  }, [calculateLevel]);

  // Spend XP
  const spendXP = useCallback(async (amount: number, reason: string): Promise<boolean> => {
    const response = await fetch('/api/gamification/spend-xp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, reason })
    });

    if (response.ok) {
      setState(prev => ({
        ...prev,
        currentXP: prev.currentXP - amount
      }));
      return true;
    }
    return false;
  }, []);

  // Check for level up
  const checkLevelUp = useCallback(() => {
    setState(prev => {
      const newLevel = calculateLevel(prev.currentXP);
      
      if (newLevel.level > prev.level.level) {
        // Level up!
        const notification: GamificationNotification = {
          id: `notif_levelup_${Date.now()}`,
          type: 'level_up',
          title: 'Level Up!',
          message: `Congratulations! You've reached level ${newLevel.level} - ${newLevel.title}`,
          data: { newLevel: newLevel.level },
          read: false,
          timestamp: new Date().toISOString()
        };

        return {
          ...prev,
          level: newLevel,
          notifications: [notification, ...prev.notifications],
          unreadCount: prev.unreadCount + 1
        };
      }

      return prev;
    });
  }, [calculateLevel]);

  // Update streak
  const updateStreak = useCallback(() => {
    const today = new Date().toISOString().split('T')[0];
    
    setState(prev => {
      const lastActive = prev.streak.lastActiveDate;
      let newStreak = prev.streak.currentStreak;

      if (!lastActive) {
        // First activity
        newStreak = 1;
      } else {
        const lastDate = new Date(lastActive);
        const todayDate = new Date(today);
        const diffDays = Math.floor((todayDate.getTime() - lastDate.getTime()) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) {
          // Same day, no change
          return prev;
        } else if (diffDays === 1) {
          // Consecutive day
          newStreak = prev.streak.currentStreak + 1;
        } else {
          // Streak broken
          newStreak = prev.streak.streakFrozen ? prev.streak.currentStreak : 1;
        }
      }

      return {
        ...prev,
        streak: {
          ...prev.streak,
          currentStreak: newStreak,
          longestStreak: Math.max(prev.streak.longestStreak, newStreak),
          lastActiveDate: today,
          streakFrozen: false
        }
      };
    });
  }, []);

  // Use streak freeze
  const useStreakFreeze = useCallback(async (): Promise<boolean> => {
    const response = await fetch('/api/gamification/use-streak-freeze', {
      method: 'POST'
    });

    if (response.ok) {
      setState(prev => ({
        ...prev,
        streak: { ...prev.streak, streakFrozen: true, freezeAvailable: false }
      }));
      return true;
    }
    return false;
  }, []);

  // Unlock badge
  const unlockBadge = useCallback((badgeId: string) => {
    const badgeDef = BADGE_DEFINITIONS[badgeId];
    if (!badgeDef) return;

    setState(prev => {
      // Check if already unlocked
      if (prev.achievements.some(a => a.badge.id === badgeId)) {
        return prev;
      }

      const badge: Badge = {
        ...badgeDef,
        unlockedAt: new Date().toISOString(),
        progress: badgeDef.requirement ? 100 : 0
      };

      const achievement: Achievement = { badge, isNew: true };

      const notification: GamificationNotification = {
        id: `notif_badge_${Date.now()}`,
        type: 'badge_unlocked',
        title: 'Badge Unlocked!',
        message: `You've earned the "${badge.name}" badge!`,
        data: { badge },
        read: false,
        timestamp: new Date().toISOString()
      };

      // Add XP for badge
      const newXP = prev.currentXP + badge.xpValue;

      return {
        ...prev,
        achievements: [...prev.achievements, achievement],
        recentAchievements: [achievement, ...prev.recentAchievements.slice(0, 4)],
        notifications: [notification, ...prev.notifications],
        unreadCount: prev.unreadCount + 1,
        currentXP: newXP,
        totalXP: prev.totalXP + badge.xpValue,
        level: calculateLevel(newXP)
      };
    });
  }, [calculateLevel]);

  // Get badge progress
  const getBadgeProgress = useCallback((badgeId: string): number => {
    // Implementation would connect to actual progress tracking
    return 0;
  }, []);

  // Challenge management
  const acceptChallenge = useCallback(async (challengeId: string) => {
    const response = await fetch(`/api/gamification/challenges/${challengeId}/accept`, {
      method: 'POST'
    });

    if (response.ok) {
      const challenge = await response.json();
      setState(prev => ({
        ...prev,
        activeChallenges: [...prev.activeChallenges, challenge]
      }));
    }
  }, []);

  const updateChallengeProgress = useCallback((challengeId: string, progress: number) => {
    setState(prev => ({
      ...prev,
      activeChallenges: prev.activeChallenges.map(c =>
        c.id === challengeId ? { ...c, progress } : c
      )
    }));
  }, []);

  const completeChallenge = useCallback(async (challengeId: string) => {
    const challenge = state.activeChallenges.find(c => c.id === challengeId);
    if (!challenge) return;

    const response = await fetch(`/api/gamification/challenges/${challengeId}/complete`, {
      method: 'POST'
    });

    if (response.ok) {
      const result = await response.json();

      setState(prev => ({
        ...prev,
        activeChallenges: prev.activeChallenges.filter(c => c.id !== challengeId),
        completedChallenges: [...prev.completedChallenges, { ...challenge, status: 'completed' }],
        currentXP: prev.currentXP + result.reward.xp,
        totalXP: prev.totalXP + result.reward.xp,
        level: calculateLevel(prev.currentXP + result.reward.xp)
      }));
    }
  }, [state.activeChallenges, calculateLevel]);

  // Leaderboards
  const fetchLeaderboard = useCallback(async (type: string) => {
    const response = await fetch(`/api/gamification/leaderboards/${type}`);

    if (response.ok) {
      const leaderboard = await response.json();
      setState(prev => ({
        ...prev,
        leaderboards: { ...prev.leaderboards, [type]: leaderboard }
      }));
    }
  }, []);

  const setCurrentLeaderboard = useCallback((type: string) => {
    setState(prev => ({
      ...prev,
      currentLeaderboard: prev.leaderboards[type] || null
    }));
  }, []);

  // Notifications
  const markNotificationRead = useCallback((notificationId: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.map(n =>
        n.id === notificationId ? { ...n, read: true } : n
      ),
      unreadCount: Math.max(0, prev.unreadCount - 1)
    }));
  }, []);

  const markAllNotificationsRead = useCallback(() => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.map(n => ({ ...n, read: true })),
      unreadCount: 0
    }));
  }, []);

  const dismissNotification = useCallback((notificationId: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.filter(n => n.id !== notificationId),
      unreadCount: Math.max(0, prev.unreadCount - 1)
    }));
  }, []);

  // XP Summary
  const getXPSummary = useCallback(async (days: number) => {
    const response = await fetch(`/api/gamification/xp/summary?days=${days}`);
    if (response.ok) {
      return response.json();
    }
    return [];
  }, []);

  // Load user progress
  const loadUserProgress = useCallback(async () => {
    if (isInitialized.current) return;

    try {
      const response = await fetch('/api/gamification/progress');
      if (response.ok) {
        const data = await response.json();
        
        setState(prev => ({
          ...prev,
          currentXP: data.currentXP || 0,
          totalXP: data.totalXP || 0,
          level: calculateLevel(data.totalXP || 0),
          streak: data.streak || prev.streak,
          achievements: data.achievements?.map((a: Badge) => ({
            badge: a,
            isNew: false
          })) || [],
          activeChallenges: data.activeChallenges || []
        }));

        isInitialized.current = true;
      }
    } catch (error) {
      console.error('Failed to load gamification progress:', error);
    }
  }, [calculateLevel]);

  // Refresh state
  const refreshState = useCallback(async () => {
    await loadUserProgress();
  }, [loadUserProgress]);

  // Effect to check level up when XP changes
  useEffect(() => {
    if (isInitialized.current) {
      checkLevelUp();
    }
  }, [state.currentXP, checkLevelUp]);

  // Effect to load progress on mount
  useEffect(() => {
    loadUserProgress();
  }, [loadUserProgress]);

  const value = useMemo<GamificationContextType>(() => ({
    state,
    addXP,
    spendXP,
    checkLevelUp,
    updateStreak,
    useStreakFreeze,
    unlockBadge,
    getBadgeProgress,
    acceptChallenge,
    updateChallengeProgress,
    completeChallenge,
    fetchLeaderboard,
    setCurrentLeaderboard,
    markNotificationRead,
    markAllNotificationsRead,
    dismissNotification,
    getXPSummary,
    loadUserProgress,
    refreshState
  }), [state, addXP, spendXP, checkLevelUp, updateStreak, useStreakFreeze, unlockBadge,
      getBadgeProgress, acceptChallenge, updateChallengeProgress, completeChallenge,
      fetchLeaderboard, setCurrentLeaderboard, markNotificationRead, markAllNotificationsRead,
      dismissNotification, getXPSummary, loadUserProgress, refreshState]);

  return (
    <GamificationContext.Provider value={value}>
      {children}
    </GamificationContext.Provider>
  );
}

export function useGamification() {
  const context = useContext(GamificationContext);
  if (!context) {
    throw new Error('useGamification must be used within a GamificationProvider');
  }
  return context;
}
