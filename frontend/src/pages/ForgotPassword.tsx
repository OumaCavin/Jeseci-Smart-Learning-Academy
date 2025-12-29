/**
 * Forgot Password Page
 * Allows users to request a password reset link
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import './Auth.css';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const result = await apiService.forgotPassword(email);

      if (result.success) {
        setMessage({
          type: 'success',
          text: result.message || 'If an account with that email exists, a password reset link has been sent to your email.'
        });
        // Clear form after success
        setEmail('');
      } else {
        setMessage({
          type: 'error',
          text: result.error || 'Failed to process request. Please try again.'
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

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>🔐</h1>
            <h2>Forgot Password?</h2>
            <p>No worries! Enter your email address and we'll send you a link to reset your password.</p>
          </div>

          {message && (
            <div className={`auth-message ${message.type}`}>
              {message.type === 'success' ? '✓ ' : '⚠ '}
              {message.text}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label className="form-label" htmlFor="email">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                className="form-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your registered email"
                required
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={loading || !email}
            >
              {loading ? (
                <span className="btn-loading">
                  <span className="spinner"></span>
                  Sending...
                </span>
              ) : (
                'Send Reset Link'
              )}
            </button>
          </form>

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

export default ForgotPassword;
