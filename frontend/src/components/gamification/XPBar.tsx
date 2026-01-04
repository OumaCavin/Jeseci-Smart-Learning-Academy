import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useGamification, Badge, Challenge, XPGain } from '../../hooks/useGamification';

// Icons
const TrophyIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
  </svg>
);

const FireIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
  </svg>
);

const StarIcon = () => (
  <svg className="w-5 h-5 text-yellow-500 fill-current" viewBox="0 0 20 20">
    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
  </svg>
);

const ChevronUpIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
  </svg>
);

interface XPBarProps {
  currentXP: number;
  totalXP: number;
  level: number;
  levelTitle: string;
  xpForNext: number;
  showAnimation?: boolean;
  compact?: boolean;
  onClick?: () => void;
}

export function XPBar({
  currentXP,
  totalXP,
  level,
  levelTitle,
  xpForNext,
  showAnimation = true,
  compact = false,
  onClick
}: XPBarProps) {
  const xpInLevel = currentXP % xpForNext;
  const progress = (xpInLevel / xpForNext) * 100;
  const prevProgress = useRef(progress);

  // Animate progress bar
  useEffect(() => {
    if (showAnimation && progress > prevProgress.current) {
      // Animation would be handled by CSS transitions
    }
    prevProgress.current = progress;
  }, [progress, showAnimation]);

  if (compact) {
    return (
      <div 
        onClick={onClick}
        className="flex items-center gap-2 cursor-pointer"
      >
        <div className="flex items-center gap-1">
          <StarIcon />
          <span className="font-bold text-gray-900 dark:text-gray-100">{level}</span>
        </div>
        <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="text-xs text-gray-500">{xpInLevel}/{xpForNext} XP</span>
      </div>
    );
  }

  return (
    <div 
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-100 
               dark:border-gray-700 cursor-pointer hover:shadow-md transition-shadow"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl 
                        flex items-center justify-center text-white font-bold text-lg">
            {level}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-gray-900 dark:text-gray-100 text-lg">
                Level {level}
              </span>
              <span className="text-sm text-gray-500">- {levelTitle}</span>
            </div>
            <div className="text-sm text-gray-500">
              {totalXP.toLocaleString()} total XP
            </div>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {xpForNext - xpInLevel}
          </div>
          <div className="text-xs text-gray-500">XP to next level</div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="relative h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 flex">
          {Array.from({ length: 10 }).map((_, i) => (
            <div 
              key={i} 
              className="flex-1 border-r border-gray-300 dark:border-gray-600" 
            />
          ))}
        </div>
        
        {/* Progress */}
        <div 
          className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 
                   rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
        
        {/* Milestone markers */}
        <div 
          className="absolute top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-white dark:bg-gray-800 rounded-full"
          style={{ left: '33%' }}
        />
        <div 
          className="absolute top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-white dark:bg-gray-800 rounded-full"
          style={{ left: '66%' }}
        />
      </div>

      {/* XP details */}
      <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
        <span>{xpInLevel.toLocaleString()} XP</span>
        <span>{xpForNext.toLocaleString()} XP</span>
      </div>
    </div>
  );
}

interface AchievementToastProps {
  badge: Badge;
  onDismiss: () => void;
  onViewAll?: () => void;
}

export function AchievementToast({ badge, onDismiss, onViewAll }: AchievementToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onDismiss, 300);
    }, 5000);

    return () => clearTimeout(timer);
  }, [onDismiss]);

  // Rarity colors
  const rarityColors = {
    common: 'from-gray-400 to-gray-500',
    rare: 'from-blue-400 to-blue-600',
    epic: 'from-purple-400 to-purple-600',
    legendary: 'from-yellow-400 via-orange-500 to-red-500'
  };

  const rarityGlow = {
    common: 'shadow-gray-400/50',
    rare: 'shadow-blue-400/50',
    epic: 'shadow-purple-400/50',
    legendary: 'shadow-yellow-400/50'
  };

  return (
    <div 
      className={`fixed bottom-4 right-4 z-50 transform transition-all duration-300 ${
        isVisible ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
      }`}
    >
      <div className={`bg-gradient-to-br ${rarityColors[badge.rarity]} rounded-xl p-4 shadow-lg 
                     ${rarityGlow[badge.rarity]} max-w-sm`}>
        <div className="flex items-start gap-4">
          {/* Badge icon */}
          <div className="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center 
                        backdrop-blur-sm flex-shrink-0">
            <img src={badge.iconUrl} alt={badge.name} className="w-12 h-12" />
          </div>

          {/* Content */}
          <div className="flex-1 text-white">
            <div className="flex items-center gap-2 mb-1">
              <TrophyIcon />
              <span className="text-xs font-medium uppercase tracking-wider opacity-90">
                Badge Unlocked!
              </span>
            </div>
            <h3 className="font-bold text-lg">{badge.name}</h3>
            <p className="text-sm opacity-90 mt-1">{badge.description}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full capitalize">
                {badge.rarity}
              </span>
              <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">
                +{badge.xpValue} XP
              </span>
            </div>
          </div>

          {/* Close button */}
          <button
            onClick={() => {
              setIsVisible(false);
              setTimeout(onDismiss, 300);
            }}
            className="text-white/60 hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* View all button */}
        {onViewAll && (
          <button
            onClick={onViewAll}
            className="w-full mt-3 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium 
                     transition-colors flex items-center justify-center gap-1"
          >
            View All Badges
            <ChevronUpIcon />
          </button>
        )}
      </div>
    </div>
  );
}

interface StreakCounterProps {
  currentStreak: number;
  longestStreak: number;
  streakFrozen: boolean;
  freezeAvailable: boolean;
  onUseFreeze?: () => void;
  compact?: boolean;
}

export function StreakCounter({
  currentStreak,
  longestStreak,
  streakFrozen,
  freezeAvailable,
  onUseFreeze,
  compact = false
}: StreakCounterProps) {
  const isAtRisk = currentStreak > 0 && currentStreak < 3;
  const isHealthy = currentStreak >= 3;

  if (compact) {
    return (
      <div className={`flex items-center gap-1.5 ${isAtRisk ? 'text-orange-500' : isHealthy ? 'text-orange-500' : 'text-gray-400'}`}>
        <FireIcon />
        <span className="font-bold">{currentStreak}</span>
        {streakFrozen && (
          <span className="text-xs bg-blue-100 text-blue-600 px-1 rounded">Frozen</span>
        )}
      </div>
    );
  }

  return (
    <div className={`bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 
                   rounded-xl p-4 border border-orange-100 dark:border-orange-800/30`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
            isHealthy 
              ? 'bg-gradient-to-br from-orange-400 to-red-500 text-white' 
              : isAtRisk
                ? 'bg-orange-200 text-orange-600'
                : 'bg-gray-200 text-gray-400'
          }`}>
            <FireIcon />
          </div>
          
          <div>
            <div className="flex items-center gap-2">
              <span className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                {currentStreak}
              </span>
              <span className="text-gray-600 dark:text-gray-400">days</span>
              {streakFrozen && (
                <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full font-medium">
                  🔒 Frozen
                </span>
              )}
            </div>
            <div className="text-sm text-gray-500">
              Current streak
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="text-lg font-semibold text-gray-700 dark:text-gray-300">
            {longestStreak} days
          </div>
          <div className="text-xs text-gray-500">Longest streak</div>
        </div>
      </div>

      {/* At risk warning */}
      {isAtRisk && (
        <div className="mt-3 p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center gap-2">
          <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span className="text-sm text-orange-700 dark:text-orange-300">
            Complete an activity today to keep your streak!
          </span>
        </div>
      )}

      {/* Streak freeze */}
      {freezeAvailable && !streakFrozen && onUseFreeze && (
        <button
          onClick={onUseFreeze}
          className="mt-3 w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg 
                   text-sm font-medium transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Use Streak Freeze
        </button>
      )}
    </div>
  );
}

import React, { useState, useCallback, useRef, useEffect } from 'react';
