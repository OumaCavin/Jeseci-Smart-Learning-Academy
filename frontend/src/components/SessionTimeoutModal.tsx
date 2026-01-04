/**
 * Session Timeout Modal Component
 * 
 * Displays a warning dialog when the session is about to expire
 * due to inactivity, allowing the user to stay logged in.
 */

import React from 'react';
import './SessionTimeout.css';

interface SessionTimeoutModalProps {
  show: boolean;
  remainingSeconds: number;
  onStayLoggedIn: () => void;
  formatTime: (seconds: number) => string;
}

const SessionTimeoutModal: React.FC<SessionTimeoutModalProps> = ({
  show,
  remainingSeconds,
  onStayLoggedIn,
  formatTime
}) => {
  if (!show) return null;

  const isCritical = remainingSeconds <= 30;

  return (
    <div className="session-timeout-overlay">
      <div className={`session-timeout-modal ${isCritical ? 'critical' : ''}`}>
        <div className="session-timeout-icon">
          ⏰
        </div>
        
        <h2 className="session-timeout-title">
          {isCritical ? 'Session Expiring Soon!' : 'Session Timeout Warning'}
        </h2>
        
        <p className="session-timeout-message">
          Your session will expire due to inactivity. For security purposes,
          you will be automatically logged out to protect your account.
        </p>
        
        <div className="session-timeout-countdown">
          <span className="countdown-label">Time remaining:</span>
          <span className={`countdown-value ${isCritical ? 'critical' : ''}`}>
            {formatTime(remainingSeconds)}
          </span>
        </div>
        
        <div className="session-timeout-actions">
          <button 
            className="btn btn-primary session-timeout-stay"
            onClick={onStayLoggedIn}
          >
            ✨ Stay Logged In
          </button>
          
          <p className="session-timeout-hint">
            Moving your mouse, typing, or clicking anywhere will also extend your session.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SessionTimeoutModal;
