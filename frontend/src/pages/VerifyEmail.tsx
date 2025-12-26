/**
 * Email Verification Page
 * Handles email verification flow for new users
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import './Auth.css';

const VerifyEmail: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'resend'>('loading');
  const [message, setMessage] = useState('Verifying your email...');
  const [resendCooldown, setResendCooldown] = useState(0);
  const [email, setEmail] = useState(searchParams.get('email') || '');
  const [resendStatus, setResendStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
  const [resendMessage, setResendMessage] = useState('');

  const token = searchParams.get('token');

  useEffect(() => {
    if (token) {
      verifyEmail(token);
    } else {
      setStatus('resend');
      if (email) {
        setMessage(`No verification token found. Please request a new verification email for ${email}.`);
      } else {
        setMessage('No verification token found. Please check your email for the verification link.');
      }
    }
  }, [token, email]);

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  const verifyEmail = async (verificationToken: string) => {
    try {
      const response = await apiService.verifyEmail(verificationToken);
      
      if (response.success) {
        setStatus('success');
        setMessage(response.message || 'Your email has been verified successfully!');
      } else {
        setStatus('error');
        setMessage(response.error || 'Verification failed. The token may be invalid or expired.');
      }
    } catch (error: any) {
      setStatus('error');
      setMessage(error.message || 'An error occurred during verification.');
    }
  };

  const handleResendEmail = async () => {
    if (!email) {
      setResendMessage('Please enter your email address');
      setResendStatus('error');
      return;
    }

    setResendStatus('sending');
    try {
      const response = await apiService.resendVerificationEmail(email);
      
      if (response.success) {
        setResendStatus('sent');
        setResendMessage('Verification email sent successfully! Check your inbox.');
        setResendCooldown(60);
      } else {
        setResendStatus('error');
        setResendMessage(response.error || 'Failed to send verification email');
      }
    } catch (error: any) {
      setResendStatus('error');
      setResendMessage('An error occurred. Please try again.');
    }
  };

  const handleGoToLogin = () => {
    navigate('/login');
  };

  const handleGoHome = () => {
    navigate('/');
  };

  if (status === 'loading') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-logo">🎓</div>
            <h1>Jeseci Smart Learning</h1>
          </div>
          <div className="auth-body">
            <div className="loading-spinner-container">
              <div className="spinner"></div>
              <p>{message}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-logo">🎓</div>
            <h1>Jeseci Smart Learning</h1>
          </div>
          <div className="auth-body">
            <div className="verification-success">
              <div className="success-icon">✅</div>
              <h2>Email Verified!</h2>
              <p>{message}</p>
              <p className="verification-info">
                You can now log in to your account and access all features.
              </p>
              <button className="btn btn-primary" onClick={handleGoToLogin}>
                Go to Login
              </button>
              <button className="btn btn-secondary" onClick={handleGoHome}>
                Go to Home
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">🎓</div>
          <h1>Jeseci Smart Learning</h1>
        </div>
        <div className="auth-body">
          <div className="verification-error">
            <div className="error-icon">⚠️</div>
            <h2>Verification Failed</h2>
            <p>{message}</p>
            
            <div className="resend-section">
              <h3>Resend Verification Email</h3>
              <p>Enter your email address and we'll send you a new verification link.</p>
              
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input
                  type="email"
                  className="form-input"
                  placeholder="Enter your registered email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              
              <button
                className="btn btn-primary"
                onClick={handleResendEmail}
                disabled={resendStatus === 'sending' || resendCooldown > 0}
              >
                {resendStatus === 'sending' ? 'Sending...' : resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend Verification Email'}
              </button>
              
              {resendMessage && (
                <p className={`resend-message ${resendStatus === 'error' ? 'error' : 'success'}`}>
                  {resendMessage}
                </p>
              )}
            </div>
            
            <div className="auth-links">
              <a href="/login" className="auth-link">Back to Login</a>
              <span className="auth-separator">|</span>
              <a href="/" className="auth-link">Back to Home</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmail;
