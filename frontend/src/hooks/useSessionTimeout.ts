/**
 * useSessionTimeout Hook
 * 
 * React hook for managing session timeout with inactivity detection.
 * Provides countdown warnings and automatic logout functionality.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { sessionTimeoutManager, SESSION_CONFIG } from '../services/sessionTimeout';

interface UseSessionTimeoutReturn {
  isSessionActive: boolean;
  remainingTime: number;
  showWarning: boolean;
  warningTimeRemaining: number;
  logout: () => void;
  resetSession: () => void;
  formatTime: (seconds: number) => string;
}

export const useSessionTimeout = (onLogout: () => void): UseSessionTimeoutReturn => {
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [remainingTime, setRemainingTime] = useState(SESSION_CONFIG.TIMEOUT_MS);
  const [showWarning, setShowWarning] = useState(false);
  const [warningTimeRemaining, setWarningTimeRemaining] = useState(SESSION_CONFIG.WARNING_BEFORE_MS);
  
  // Use refs to avoid stale closures in callbacks
  const onLogoutRef = useRef(onLogout);
  onLogoutRef.current = onLogout;
  
  const [countdownInterval, setCountdownInterval] = useState<NodeJS.Timeout | null>(null);

  // Format time as MM:SS
  const formatTime = useCallback((seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);

  // Initialize session timeout
  useEffect(() => {
    const handleTimeout = () => {
      console.log('Session timeout triggered - logging out user');
      setIsSessionActive(false);
      setShowWarning(false);
      if (countdownInterval) {
        clearInterval(countdownInterval);
        setCountdownInterval(null);
      }
      onLogoutRef.current();
    };

    const handleWarning = (remainingMs: number) => {
      console.log('Session timeout warning shown');
      setShowWarning(true);
      setWarningTimeRemaining(remainingMs);
    };

    const handleWarningDismissed = () => {
      console.log('Session timeout warning dismissed (user activity detected)');
      setShowWarning(false);
      setWarningTimeRemaining(SESSION_CONFIG.WARNING_BEFORE_MS);
    };

    sessionTimeoutManager.initialize({
      onTimeout: handleTimeout,
      onWarning: handleWarning,
      onWarningDismissed: handleWarningDismissed
    });

    setIsSessionActive(true);

    // Start countdown timer for warning display
    const interval = setInterval(() => {
      const remaining = sessionTimeoutManager.getRemainingTime();
      if (remaining !== null) {
        setRemainingTime(remaining);
        if (showWarning) {
          setWarningTimeRemaining(Math.max(0, remaining));
        }
      }
    }, 1000);

    setCountdownInterval(interval);

    return () => {
      sessionTimeoutManager.cleanup();
      if (interval) {
        clearInterval(interval);
      }
    };
  }, []);

  // Manual logout function
  const logout = useCallback(() => {
    sessionTimeoutManager.logout();
    setIsSessionActive(false);
    setShowWarning(false);
    if (countdownInterval) {
      clearInterval(countdownInterval);
    }
    onLogoutRef.current();
  }, [countdownInterval]);

  // Reset session (extend timeout)
  const resetSession = useCallback(() => {
    sessionTimeoutManager.resetTimeout();
    setIsSessionActive(true);
    setShowWarning(false);
    setWarningTimeRemaining(SESSION_CONFIG.WARNING_BEFORE_MS);
  }, []);

  return {
    isSessionActive,
    remainingTime,
    showWarning,
    warningTimeRemaining,
    logout,
    resetSession,
    formatTime
  };
};

// Export session configuration for external use
export { SESSION_CONFIG };
