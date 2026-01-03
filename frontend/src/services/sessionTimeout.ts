/**
 * Session Timeout Manager for Jeseci Smart Learning Academy
 * 
 * This module handles automatic logout after a period of inactivity.
 * Tracks user interactions (mouse, keyboard, touch) and logs out
 * the user after the configured timeout duration.
 */

// Session timeout configuration
const SESSION_TIMEOUT_MS = 3 * 60 * 1000; // 3 minutes in milliseconds
const WARNING_BEFORE_TIMEOUT_MS = 60 * 1000; // Show warning 1 minute before timeout
const WARNING_CHECK_INTERVAL_MS = 1000; // Check for warnings every second

interface SessionManagerCallbacks {
  onTimeout: () => void;
  onWarning: (remainingMs: number) => void;
  onWarningDismissed: () => void;
}

class SessionTimeoutManager {
  private timeoutId: number | null = null;
  private warningCheckId: number | null = null;
  private warningId: number | null = null;
  private callbacks: SessionManagerCallbacks | null = null;
  private isInitialized: boolean = false;
  private lastActivityTime: number = 0;
  private warningShown: boolean = false;

  /**
   * Initialize the session timeout manager
   * @param callbacks Object containing callback functions for timeout and warning events
   */
  initialize(callbacks: SessionManagerCallbacks): void {
    if (this.isInitialized) {
      this.cleanup();
    }

    this.callbacks = callbacks;
    this.lastActivityTime = Date.now();
    this.isInitialized = true;
    this.warningShown = false;

    // Set up activity event listeners
    this.setupActivityListeners();

    // Start the timeout timer
    this.startTimeoutTimer();

    console.log('Session timeout manager initialized with 3-minute inactivity timeout');
  }

  /**
   * Set up event listeners for user activity detection
   */
  private setupActivityListeners(): void {
    // Use passive listeners for better performance
    const activityEvents = [
      'mousedown',
      'keydown',
      'touchstart',
      'scroll',
      'mousemove'
    ];

    activityEvents.forEach(event => {
      document.addEventListener(event, () => this.handleActivity(), { passive: true });
    });

    // Also listen for visibility changes (tab switching)
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        this.handleActivity();
      }
    });
  }

  /**
   * Handle user activity - reset the timeout timer
   */
  private handleActivity(): void {
    if (!this.isInitialized) return;

    const now = Date.now();
    const timeSinceLastActivity = now - this.lastActivityTime;

    // Only reset if we've been inactive for at least 1 second to avoid excessive resets
    if (timeSinceLastActivity < 1000) return;

    this.lastActivityTime = now;

    // If warning was shown and user became active, dismiss the warning
    if (this.warningShown) {
      this.warningShown = false;
      if (this.callbacks?.onWarningDismissed) {
        this.callbacks.onWarningDismissed();
      }
      if (this.warningId !== null) {
        clearTimeout(this.warningId);
        this.warningId = null;
      }
    }

    // Restart the timeout timer
    this.restartTimeoutTimer();
  }

  /**
   * Start the timeout timer
   */
  private startTimeoutTimer(): void {
    if (this.timeoutId !== null) {
      clearTimeout(this.timeoutId);
    }

    // Set the main timeout
    this.timeoutId = window.setTimeout(() => {
      this.handleTimeout();
    }, SESSION_TIMEOUT_MS);

    // Start checking for warning time
    this.startWarningCheck();
  }

  /**
   * Restart the timeout timer (called on user activity)
   */
  private restartTimeoutTimer(): void {
    this.startTimeoutTimer();
  }

  /**
   * Start checking if we should show a warning
   */
  private startWarningCheck(): void {
    if (this.warningCheckId !== null) {
      clearInterval(this.warningCheckId);
    }

    this.warningCheckId = window.setInterval(() => {
      const elapsed = Date.now() - this.lastActivityTime;
      const remaining = SESSION_TIMEOUT_MS - elapsed;

      // Check if we should show warning (1 minute before timeout)
      if (remaining <= WARNING_BEFORE_TIMEOUT_MS && remaining > WARNING_BEFORE_TIMEOUT_MS - WARNING_CHECK_INTERVAL_MS) {
        if (!this.warningShown && this.callbacks?.onWarning) {
          this.warningShown = true;
          this.callbacks.onWarning(remaining);
        }
      }
    }, WARNING_CHECK_INTERVAL_MS);
  }

  /**
   * Handle session timeout
   */
  private handleTimeout(): void {
    console.log('Session timeout reached - logging out user');

    if (this.callbacks?.onTimeout) {
      this.callbacks.onTimeout();
    }

    this.cleanup();
  }

  /**
   * Clean up all timers and listeners
   */
  cleanup(): void {
    if (this.timeoutId !== null) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }

    if (this.warningCheckId !== null) {
      clearInterval(this.warningCheckId);
      this.warningCheckId = null;
    }

    if (this.warningId !== null) {
      clearTimeout(this.warningId);
      this.warningId = null;
    }

    this.isInitialized = false;
    this.warningShown = false;
  }

  /**
   * Manually trigger a logout (for "Logout" button clicks)
   */
  logout(): void {
    this.cleanup();
  }

  /**
   * Get remaining time until timeout
   * @returns Remaining time in milliseconds, or null if not initialized
   */
  getRemainingTime(): number | null {
    if (!this.isInitialized) return null;
    const elapsed = Date.now() - this.lastActivityTime;
    return Math.max(0, SESSION_TIMEOUT_MS - elapsed);
  }

  /**
   * Check if session timeout manager is active
   * @returns true if active, false otherwise
   */
  isActive(): boolean {
    return this.isInitialized;
  }

  /**
   * Reset the session timeout timer (public method to restart the timer)
   */
  resetTimeout(): void {
    if (this.isInitialized) {
      this.restartTimeoutTimer();
    }
  }
}

// Export singleton instance
export const sessionTimeoutManager = new SessionTimeoutManager();

// Export configuration constants
export const SESSION_CONFIG = {
  TIMEOUT_MS: SESSION_TIMEOUT_MS,
  WARNING_BEFORE_MS: WARNING_BEFORE_TIMEOUT_MS,
  WARNING_CHECK_INTERVAL_MS: WARNING_CHECK_INTERVAL_MS,
  TIMEOUT_SECONDS: SESSION_TIMEOUT_MS / 1000,
  WARNING_SECONDS: WARNING_BEFORE_TIMEOUT_MS / 1000
};

export default sessionTimeoutManager;
