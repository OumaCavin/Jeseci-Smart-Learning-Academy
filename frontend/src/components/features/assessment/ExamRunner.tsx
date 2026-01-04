import React, { useState, useEffect, useCallback } from 'react';
import { useExamSession, ExamQuestion } from '../../hooks/assessment/useExamSession';
import './ExamRunner.css';

export interface ExamRunnerProps {
  assessmentId: string;
  onComplete?: (result: Awaited<ReturnType<typeof useExamSession>['finishExam']>) => void;
  onExit?: () => void;
  showExitButton?: boolean;
}

export function ExamRunner({
  assessmentId,
  onComplete,
  onExit,
  showExitButton = true,
}: ExamRunnerProps) {
  const {
    session,
    questions,
    currentQuestion,
    isLoading,
    isSubmitting,
    timeRemaining,
    tabSwitchCount,
    startSession,
    submitAnswer,
    navigateQuestion,
    goToQuestion,
    finishExam,
    abandonExam,
    toggleFlag,
    getAnsweredCount,
    getFlaggedCount,
    getProgress,
    startTimer,
  } = useExamSession({ assessmentId });

  const [showReview, setShowReview] = useState(false);
  const [confirmSubmit, setConfirmSubmit] = useState(false);

  // Start session and timer on mount
  useEffect(() => {
    if (!session) {
      startSession().then(() => startTimer());
    }
  }, [session, startSession, startTimer]);

  // Handle exam completion
  useEffect(() => {
    if (session?.status === 'submitted' && session.feedback) {
      // Exam submitted, show results
      setShowReview(true);
    }
  }, [session]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimeColor = (seconds: number): string => {
    if (seconds < 60) return '#ef4444';
    if (seconds < 300) return '#f59e0b';
    return '#10b981';
  };

  const handleSubmit = useCallback(async () => {
    const result = await finishExam();
    if (result) {
      onComplete?.(result);
    }
  }, [finishExam, onComplete]);

  const handleExit = useCallback(async () => {
    if (window.confirm('Are you sure you want to exit? Your progress will be lost.')) {
      await abandonExam();
      onExit?.();
    }
  }, [abandonExam, onExit]);

  const handleAnswerChange = (answer: string | string[]) => {
    if (currentQuestion) {
      submitAnswer(currentQuestion.id, answer);
    }
  };

  const renderQuestion = (question: ExamQuestion, index: number) => {
    const answer = session?.answers.find(a => a.questionId === question.id);
    const isAnswered = answer &&
      ((typeof answer.answer === 'string' && answer.answer.trim() !== '') ||
       (Array.isArray(answer.answer) && answer.answer.length > 0));
    const isFlagged = answer?.isFlagged;

    return (
      <div
        key={question.id}
        className={`question-item ${currentQuestion?.id === question.id ? 'current' : ''} ${isAnswered ? 'answered' : ''} ${isFlagged ? 'flagged' : ''}`}
        onClick={() => goToQuestion(index)}
      >
        <span className="question-number">{index + 1}</span>
        {isFlagged && <span className="flag-indicator">🚩</span>}
        {isAnswered && <span className="answered-indicator">✓</span>}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="exam-runner loading">
        <div className="exam-loading">
          <div className="loading-spinner"></div>
          <p>Loading exam...</p>
        </div>
      </div>
    );
  }

  if (!session || questions.length === 0) {
    return (
      <div className="exam-runner error">
        <p>Failed to load exam</p>
        <button onClick={onExit}>Go Back</button>
      </div>
    );
  }

  if (showReview && session.status === 'submitted') {
    return (
      <div className="exam-runner review-mode">
        <div className="review-header">
          <h2>Exam Completed</h2>
          <div className="review-score">
            <span className="score-percentage">
              {session.feedback?.percentage.toFixed(1)}%
            </span>
            <span className={`score-status ${session.feedback?.passed ? 'passed' : 'failed'}`}>
              {session.feedback?.passed ? 'PASSED' : 'FAILED'}
            </span>
          </div>
        </div>
        
        <div className="review-summary">
          <div className="summary-item">
            <span className="summary-label">Total Points</span>
            <span className="summary-value">{session.feedback?.earnedPoints} / {session.feedback?.totalPoints}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Time Taken</span>
            <span className="summary-value">
              {session.startedAt && session.submittedAt
                ? Math.floor((new Date(session.submittedAt).getTime() - new Date(session.startedAt).getTime()) / 60000)
                : 0} minutes
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Questions Answered</span>
            <span className="summary-value">{getAnsweredCount()} / {questions.length}</span>
          </div>
        </div>

        <div className="review-details">
          <h3>Question Review</h3>
          {questions.map((question, index) => {
            const result = session.feedback?.questionResults.find(r => r.questionId === question.id);
            return (
              <div key={question.id} className={`review-question ${result?.isCorrect ? 'correct' : 'incorrect'}`}>
                <div className="question-header">
                  <span className="question-num">Q{index + 1}</span>
                  <span className="question-points">{question.points} points</span>
                  <span className="result-badge">
                    {result?.isCorrect ? '✓ Correct' : `✗ Incorrect (-${question.points - (result?.pointsEarned || 0)} pts)`}
                  </span>
                </div>
                <p className="question-text">{question.text}</p>
                {result && !result.isCorrect && question.explanation && (
                  <p className="question-explanation">{question.explanation}</p>
                )}
              </div>
            );
          })}
        </div>

        <div className="review-actions">
          <button className="btn-primary" onClick={onExit}>
            {session.feedback?.passed ? 'Continue' : 'Try Again'}
          </button>
        </div>
      </div>
    );
  }

  const progress = getProgress();

  return (
    <div className="exam-runner">
      <div className="exam-header">
        <div className="exam-title">
          <h2>Exam in Progress</h2>
          {tabSwitchCount > 0 && (
            <span className="tab-warning">
              ⚠️ Tab switches: {tabSwitchCount}
            </span>
          )}
        </div>
        
        <div className="exam-timer" style={{ color: getTimeColor(timeRemaining) }}>
          <span className="timer-icon">⏱️</span>
          <span className="timer-value">{formatTime(timeRemaining)}</span>
        </div>
        
        {showExitButton && (
          <button className="btn-exit" onClick={handleExit}>
            Exit Exam
          </button>
        )}
      </div>

      <div className="exam-progress">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress.percentage}%` }}
          ></div>
        </div>
        <span className="progress-text">
          {progress.answered} of {progress.total} questions answered
        </span>
      </div>

      <div className="exam-content">
        <div className="question-navigation">
          <h4>Questions</h4>
          <div className="question-grid">
            {questions.map((question, index) => renderQuestion(question, index))}
          </div>
          <div className="nav-legend">
            <span className="legend-item"><span className="legend-dot current"></span> Current</span>
            <span className="legend-item"><span className="legend-dot answered"></span> Answered</span>
            <span className="legend-item"><span className="legend-dot flagged"></span> Flagged</span>
          </div>
        </div>

        <div className="question-panel">
          {currentQuestion ? (
            <>
              <div className="question-header">
                <span className="question-counter">
                  Question {session.currentQuestionIndex + 1} of {questions.length}
                </span>
                <span className="question-points">{currentQuestion.points} points</span>
                <button
                  className={`btn-flag ${session.answers.find(a => a.questionId === currentQuestion.id)?.isFlagged ? 'flagged' : ''}`}
                  onClick={() => toggleFlag(currentQuestion.id)}
                >
                  🚩
                </button>
              </div>

              <div className="question-text">
                <p>{currentQuestion.text}</p>
              </div>

              {currentQuestion.type === 'multiple_choice' && (
                <div className="answer-options">
                  {currentQuestion.options?.map((option) => {
                    const answer = session.answers.find(a => a.questionId === currentQuestion.id);
                    const isSelected = answer?.answer === option.id;
                    
                    return (
                      <label
                        key={option.id}
                        className={`option-item ${isSelected ? 'selected' : ''}`}
                      >
                        <input
                          type="radio"
                          name={`question-${currentQuestion.id}`}
                          value={option.id}
                          checked={isSelected}
                          onChange={() => handleAnswerChange(option.id)}
                        />
                        <span className="option-marker"></span>
                        <span className="option-text">{option.text}</span>
                      </label>
                    );
                  })}
                </div>
              )}

              {currentQuestion.type === 'true_false' && (
                <div className="answer-options tf-options">
                  {['True', 'False'].map((value) => {
                    const answer = session.answers.find(a => a.questionId === currentQuestion.id);
                    const isSelected = answer?.answer === value.toLowerCase();
                    
                    return (
                      <label
                        key={value}
                        className={`option-item ${isSelected ? 'selected' : ''}`}
                      >
                        <input
                          type="radio"
                          name={`question-${currentQuestion.id}`}
                          value={value.toLowerCase()}
                          checked={isSelected}
                          onChange={() => handleAnswerChange(value.toLowerCase())}
                        />
                        <span className="option-marker"></span>
                        <span className="option-text">{value}</span>
                      </label>
                    );
                  })}
                </div>
              )}

              {currentQuestion.type === 'short_answer' && (
                <div className="answer-textarea">
                  <textarea
                    value={(session.answers.find(a => a.questionId === currentQuestion.id)?.answer as string) || ''}
                    onChange={(e) => handleAnswerChange(e.target.value)}
                    placeholder="Type your answer here..."
                    rows={6}
                  />
                </div>
              )}

              <div className="question-actions">
                <button
                  className="btn-nav"
                  onClick={() => navigateQuestion('prev')}
                  disabled={session.currentQuestionIndex === 0}
                >
                  ← Previous
                </button>
                
                {session.currentQuestionIndex === questions.length - 1 ? (
                  <button
                    className="btn-submit"
                    onClick={() => setConfirmSubmit(true)}
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Exam'}
                  </button>
                ) : (
                  <button
                    className="btn-nav"
                    onClick={() => navigateQuestion('next')}
                    disabled={session.currentQuestionIndex === questions.length - 1}
                  >
                    Next →
                  </button>
                )}
              </div>
            </>
          ) : (
            <div className="no-question">
              <p>Select a question from the navigation panel</p>
            </div>
          )}
        </div>
      </div>

      {confirmSubmit && (
        <div className="confirm-modal">
          <div className="modal-content">
            <h3>Submit Exam?</h3>
            <p>
              You have answered {getAnsweredCount()} out of {questions.length} questions.
              {getAnsweredCount() < questions.length && (
                <span className="warning-text">
                  {' '}{questions.length - getAnsweredCount()} questions are unanswered.
                </span>
              )}
            </p>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setConfirmSubmit(false)}>
                Continue Exam
              </button>
              <button className="btn-primary" onClick={handleSubmit} disabled={isSubmitting}>
                {isSubmitting ? 'Submitting...' : 'Confirm Submit'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ExamRunner;
