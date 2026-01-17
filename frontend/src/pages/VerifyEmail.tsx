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
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'resend' | 'pending_verification'>('loading');
  const [message, setMessage] = useState('Verifying your email...');
  const [resendCooldown, setResendCooldown] = useState(0);
  const [email, setEmail] = useState(searchParams.get('email') || '');
  const [resendStatus, setResendStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
  const [resendMessage, setResendMessage] = useState('');
  const [autoRedirectSeconds, setAutoRedirectSeconds] = useState(3);

  const token = searchParams.get('token');

  useEffect(() => {
    if (token) {
      verifyEmail(token);
    } else {
      // No token in URL - this is expected after registration
      // User needs to check their email for the verification link
      setStatus('pending_verification');
      if (email) {
        setMessage(`A verification email has been sent to ${email}. Please check your inbox and click the verification link.`);
      } else {
        setMessage('A verification email has been sent. Please check your inbox for the verification link.');
      }
    }
  }, [token, email]);

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  // Auto-redirect countdown for successful verification
  useEffect(() => {
    if (status === 'success' && autoRedirectSeconds > 0) {
      const timer = setTimeout(() => {
        setAutoRedirectSeconds(autoRedirectSeconds - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (status === 'success' && autoRedirectSeconds === 0) {
      // Automatically redirect to login page when countdown reaches 0
      navigate('/login');
    }
  }, [status, autoRedirectSeconds, navigate]);

  const verifyEmail = async (verificationToken: string) => {
    try {
      console.log('Verifying email with token:', verificationToken);
      const response = await apiService.verifyEmail(verificationToken);
      console.log('Verification response:', response);
      
      if (response.success) {
        setStatus('success');
        setMessage(response.message || 'Your email has been verified successfully!');
      } else {
        setStatus('error');
        setMessage(response.error || response.message || 'Verification failed. The token may be invalid or expired.');
        console.error('Verification failed:', response);
      }
    } catch (error: any) {
      setStatus('error');
      console.error('Verification error:', error);
      // Check if it's a network error or API error
      if (error.message) {
        setMessage(error.message);
      } else {
        setMessage('An error occurred during verification. Please try again.');
      }
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

  // New status: Pending verification - email sent, waiting for user to click link
  if (status === 'pending_verification') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-logo">🎓</div>
            <h1>Jeseci Smart Learning</h1>
          </div>
          <div className="auth-body">
            <div className="verification-pending">
              <div className="pending-icon">📧</div>
              <h2>Check Your Email</h2>
              <p className="pending-message">{message}</p>
              <p className="pending-instructions">
                Click the verification link in the email to verify your account. 
                The link will expire in 24 hours.
              </p>
              
              <div className="resend-section">
                <h3>Didn't receive the email?</h3>
                <p>Check your spam folder or request a new verification email.</p>
                
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
              <div className="auto-redirect-notice">
                <p>Redirecting to login page in <strong>{autoRedirectSeconds}</strong> seconds...</p>
              </div>
              <div className="verification-actions">
                <button className="btn btn-primary" onClick={handleGoToLogin}>
                  Go to Login Now
                </button>
                <button className="btn btn-secondary" onClick={handleGoHome}>
                  Go to Home
                </button>
              </div>
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
