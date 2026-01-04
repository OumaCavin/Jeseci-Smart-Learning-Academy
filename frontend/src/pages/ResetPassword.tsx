/**
 * Reset Password Page
 * Allows users to set a new password after clicking the reset link
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { apiService } from '../services/api';
import './Auth.css';

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [tokenInfo, setTokenInfo] = useState<{ username: string; email: string; expires_at: string } | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  // Get token from URL params on component mount
  useEffect(() => {
    const resetToken = searchParams.get('token');
    if (resetToken) {
      setToken(resetToken);
      validateToken(resetToken);
    } else {
      setValidating(false);
      setMessage({
        type: 'error',
        text: 'Invalid or missing reset token. Please request a new password reset link.'
      });
    }
  }, [searchParams]);

  const validateToken = async (resetToken: string) => {
    setValidating(true);
    try {
      const result = await apiService.validateResetToken(resetToken);
      
      if (result.valid) {
        setTokenValid(true);
        setTokenInfo({
          username: result.username,
          email: result.email,
          expires_at: result.expires_at
        });
      } else {
        setTokenValid(false);
        setMessage({
          type: 'error',
          text: result.error || 'This reset link is invalid or has expired.'
        });
      }
    } catch (error: any) {
      setTokenValid(false);
      setMessage({
        type: 'error',
        text: 'Failed to validate reset token. Please try again or request a new link.'
      });
    } finally {
      setValidating(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    // Validate passwords match
    if (newPassword !== confirmPassword) {
      setMessage({
        type: 'error',
        text: 'Passwords do not match. Please confirm your password.'
      });
      setLoading(false);
      return;
    }

    // Validate password strength
    if (newPassword.length < 8) {
      setMessage({
        type: 'error',
        text: 'Password must be at least 8 characters long.'
      });
      setLoading(false);
      return;
    }

    try {
      const result = await apiService.resetPassword(token, newPassword, confirmPassword);

      if (result.success) {
        setMessage({
          type: 'success',
          text: result.message || 'Your password has been reset successfully!'
        });
        // Clear form
        setNewPassword('');
        setConfirmPassword('');
        
        // Redirect to login after short delay
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        setMessage({
          type: 'error',
          text: result.error || 'Failed to reset password. Please try again.'
        });
      }
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.message || 'An unexpected error occurred. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };

  if (validating) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <div className="auth-card">
            <div className="auth-header">
              <h1>🔐</h1>
              <h2>Validating Link</h2>
              <p>Please wait while we validate your reset link...</p>
            </div>
            <div className="auth-loading">
              <span className="spinner-large"></span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>🔐</h1>
            <h2>Reset Password</h2>
            {tokenInfo && (
              <p className="token-info">
                Resetting password for <strong>{tokenInfo.username}</strong> ({tokenInfo.email})
              </p>
            )}
          </div>

          {message && (
            <div className={`auth-message ${message.type}`}>
              {message.type === 'success' ? '✓ ' : '⚠ '}
              {message.text}
            </div>
          )}

          {tokenValid && (
            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label className="form-label" htmlFor="newPassword">
                  New Password
                </label>
                <div className="password-input-wrapper">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="newPassword"
                    className="form-input"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Enter new password (min 8 characters)"
                    required
                    disabled={loading}
                    minLength={8}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    tabIndex={-1}
                  >
                    {showPassword ? '👁️' : '👁️‍🗨️'}
                  </button>
                </div>
                <div className="password-requirements">
                  <small>Password must be at least 8 characters</small>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="confirmPassword">
                  Confirm New Password
                </label>
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  className="form-input"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your new password"
                  required
                  disabled={loading}
                  minLength={8}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-full"
                disabled={loading || !newPassword || !confirmPassword}
              >
                {loading ? (
                  <span className="btn-loading">
                    <span className="spinner"></span>
                    Resetting...
                  </span>
                ) : (
                  'Reset Password'
                )}
              </button>
            </form>
          )}

          {!tokenValid && !validating && (
            <div className="token-error">
              <div className="error-icon">⚠️</div>
              <p>This password reset link is invalid or has expired.</p>
              <Link to="/forgot-password" className="btn btn-primary btn-full">
                Request New Link
              </Link>
            </div>
          )}

          <div className="auth-footer">
            <p>
              Remember your password?{' '}
              <Link to="/login" className="auth-link">
                Back to Login
              </Link>
            </p>
          </div>

          <div className="auth-back">
            <Link to="/" className="back-link">
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;
