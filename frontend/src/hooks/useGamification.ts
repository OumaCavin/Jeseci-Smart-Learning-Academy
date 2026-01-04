import { useCallback, useState, useEffect } from 'react';
import { useGamification as useGamificationContext, Badge, Challenge, Leaderboard, XPGain } from '../contexts/GamificationContext';

export interface UseGamificationOptions {
  autoLoad?: boolean;
  onLevelUp?: (newLevel: number, title: string) => void;
  onBadgeUnlock?: (badge: Badge) => void;
  onXPGain?: (amount: number, source: string) => void;
}

export interface UseGamificationReturn {
  // User progress
  currentXP: number;
  totalXP: number;
  level: number;
  levelTitle: string;
  levelProgress: number;
  xpForNextLevel: number;
  
  // Streak
  currentStreak: number;
  longestStreak: number;
  streakFrozen: boolean;
  freezeAvailable: boolean;
  
  // Achievements
  achievements: Badge[];
  recentAchievements: Badge[];
  unlockedBadges: Badge[];
  lockedBadges: Badge[];
  
  // Challenges
  activeChallenges: Challenge[];
  completedChallenges: Challenge[];
  
  // XP Animation
  pendingXPGains: XPGain[];
  
  // Actions
  addXP: (amount: number, source: string) => void;
  updateStreak: () => void;
  useStreakFreeze: () => Promise<boolean>;
  acceptChallenge: (challengeId: string) => Promise<void>;
  completeChallenge: (challengeId: string) => Promise<void>;
  checkBadgeProgress: (badgeId: string) => Promise<number>;
  
  // Level up effects
  triggerLevelUpEffect: () => void;
  dismissLevelUpEffect: () => void;
  showLevelUpModal: boolean;
}

export function useGamification(options: UseGamificationOptions = {}): UseGamificationReturn {
  const {
    autoLoad = true,
    onLevelUp,
    onBadgeUnlock,
    onXPGain
  } = options;

  const [showLevelUpModal, setShowLevelUpModal] = useState(false);
  const [pendingLevelUp, setPendingLevelUp] = useState<{ level: number; title: string } | null>(null);

  const {
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
    loadUserProgress
  } = useGamificationContext();

  // Auto-load progress
  useEffect(() => {
    if (autoLoad) {
      loadUserProgress();
    }
  }, [autoLoad, loadUserProgress]);

  // Listen for level up
  useEffect(() => {
    if (state.notifications.length > 0) {
      const latestNotification = state.notifications[0];
      
      if (latestNotification.type === 'level_up' && !latestNotification.read) {
        const newLevel = latestNotification.data?.newLevel as number;
        const levelData = LEVEL_THRESHOLDS.find(l => l.level === newLevel);
        
        setPendingLevelUp({
          level: newLevel,
          title: levelData?.title || 'Unknown'
        });
        setShowLevelUpModal(true);
        onLevelUp?.(newLevel, levelData?.title || 'Unknown');
      }
    }
  }, [state.notifications, onLevelUp]);

  // Listen for badge unlocks
  useEffect(() => {
    if (state.recentAchievements.length > 0) {
      const latest = state.recentAchievements[0];
      if (latest.isNew && onBadgeUnlock) {
        onBadgeUnlock(latest.badge);
      }
    }
  }, [state.recentAchievements, onBadgeUnlock]);

  // Listen for XP gains
  useEffect(() => {
    if (state.pendingXPGains.length > 0) {
      const latestGain = state.pendingXPGains[state.pendingXPGains.length - 1];
      if (latestGain && onXPGain) {
        onXPGain(latestGain.amount, latestGain.source);
      }
    }
  }, [state.pendingXPGains, onXPGain]);

  // Trigger level up effect
  const triggerLevelUpEffect = useCallback(() => {
    checkLevelUp();
  }, [checkLevelUp]);

  // Dismiss level up modal
  const dismissLevelUpEffect = useCallback(() => {
    setShowLevelUpModal(false);
    setPendingLevelUp(null);
  }, []);

  // Check badge progress
  const checkBadgeProgress = useCallback(async (badgeId: string): Promise<number> => {
    // This would connect to actual progress tracking
    return getBadgeProgress(badgeId);
  }, [getBadgeProgress]);

  return {
    currentXP: state.currentXP,
    totalXP: state.totalXP,
    level: state.level.level,
    levelTitle: state.level.title,
    levelProgress: state.level.progress,
    xpForNextLevel: state.level.xpForNext,
    currentStreak: state.streak.currentStreak,
    longestStreak: state.streak.longestStreak,
    streakFrozen: state.streak.streakFrozen,
    freezeAvailable: state.streak.freezeAvailable,
    achievements: state.achievements.map(a => a.badge),
    recentAchievements: state.recentAchievements.map(a => a.badge),
    unlockedBadges: state.achievements.filter(a => a.badge.unlockedAt).map(a => a.badge),
    lockedBadges: state.achievements.filter(a => !a.badge.unlockedAt).map(a => a.badge),
    activeChallenges: state.activeChallenges,
    completedChallenges: state.completedChallenges,
    pendingXPGains: state.pendingXPGains,
    addXP,
    updateStreak,
    useStreakFreeze,
    acceptChallenge,
    completeChallenge,
    checkBadgeProgress,
    triggerLevelUpEffect,
    dismissLevelUpEffect,
    showLevelUpModal
  };
}

// Level thresholds (should match GamificationContext)
const LEVEL_THRESHOLDS = [
  { level: 1, title: 'Novice' },
  { level: 2, title: 'Beginner' },
  { level: 3, title: 'Learner' },
  { level: 4, title: 'Explorer' },
  { level: 5, title: 'Developer' },
  { level: 6, title: 'Coder' },
  { level: 7, title: 'Programmer' },
  { level: 8, title: 'Engineer' },
  { level: 9, title: 'Architect' },
  { level: 10, title: 'Master' },
  { level: 11, title: 'Guru' },
  { level: 12, title: 'Legend' },
  { level: 13, title: 'Mythic' },
  { level: 14, title: 'Titan' },
  { level: 15, title: 'Divine' }
];

// Re-export types from context for external use
export type { Badge, Challenge, XPGain };