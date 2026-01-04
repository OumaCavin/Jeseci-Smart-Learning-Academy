import { useState, useCallback, useEffect, useRef } from 'react';

// Type definitions for exam session
export interface ExamQuestion {
  id: string;
  type: 'multiple_choice' | 'multiple_select' | 'true_false' | 'short_answer' | 'code' | 'matching';
  text: string;
  options?: {
    id: string;
    text: string;
  }[];
  correctAnswer?: string | string[];
  codeLanguage?: string;
  starterCode?: string;
  testCases?: {
    input: string;
    expectedOutput: string;
    isHidden: boolean;
  }[];
  points: number;
  difficulty: 'easy' | 'medium' | 'hard';
  timeLimit?: number;
  explanation?: string;
}

export interface ExamSessionData {
  id: string;
  assessmentId: string;
  status: 'not_started' | 'in_progress' | 'submitted' | 'timed_out' | 'abandoned';
  answers: {
    questionId: string;
    answer: string | string[];
    isFlagged: boolean;
    timeSpent: number;
  }[];
  currentQuestionIndex: number;
  startedAt?: string;
  submittedAt?: string;
  timeRemaining?: number;
  flags: {
    tabSwitches: number;
    focusLossCount: number;
    suspiciousActivity: boolean;
  };
}

export interface ExamResult {
  sessionId: string;
  totalPoints: number;
  earnedPoints: number;
  percentage: number;
  passed: boolean;
  questionResults: {
    questionId: string;
    isCorrect: boolean;
    pointsEarned: number;
    feedback?: string;
  }[];
  timeTaken: number;
}

export interface UseExamSessionOptions {
  assessmentId: string;
  onTimeWarning?: (timeRemaining: number) => void;
  onTimeUp?: () => void;
  onTabSwitch?: (count: number) => void;
  enableProctoring?: boolean;
  saveInterval?: number;
}

export interface UseExamSessionReturn {
  // Session state
  session: ExamSessionData | null;
  questions: ExamQuestion[];
  currentQuestion: ExamQuestion | null;
  isLoading: boolean;
  isSubmitting: boolean;
  timeRemaining: number;
  tabSwitchCount: number;
  
  // Session actions
  startSession: () => Promise<void>;
  submitAnswer: (questionId: string, answer: string | string[]) => void;
  navigateQuestion: (direction: 'next' | 'prev' | number) => void;
  goToQuestion: (index: number) => void;
  finishExam: () => Promise<ExamResult | null>;
  abandonExam: () => Promise<void>;
  
  // Question actions
  flagQuestion: (questionId: string) => void;
  unflagQuestion: (questionId: string) => void;
  toggleFlag: (questionId: string) => void;
  getAnsweredCount: () => number;
  getFlaggedCount: () => number;
  getAnsweredQuestionIds: () => string[];
  
  // Timer actions
  startTimer: () => void;
  pauseTimer: () => void;
  resetTimer: () => void;
  
  // Review
  getQuestionResult: (questionId: string) => ExamResult['questionResults'][0] | undefined;
  getProgress: () => { answered: number; total: number; percentage: number };
}

export function useExamSession(options: UseExamSessionOptions): UseExamSessionReturn {
  const {
    assessmentId,
    onTimeWarning,
    onTimeUp,
    onTabSwitch,
    enableProctoring = true,
    saveInterval = 30000,
  } = options;

  const [session, setSession] = useState<ExamSessionData | null>(null);
  const [questions, setQuestions] = useState<ExamQuestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [tabSwitchCount, setTabSwitchCount] = useState(0);
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const saveTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Get current question
  const currentQuestion = session !== null && questions.length > 0
    ? questions[session.currentQuestionIndex]
    : null;

  // Start session
  const startSession = useCallback(async () => {
    setIsLoading(true);
    try {
      // Simulate API call to start exam
      const response = await new Promise<{ questions: ExamQuestion[]; timeLimit: number }>((resolve) => {
        setTimeout(() => {
          resolve({
            questions: [
              {
                id: 'q1',
                type: 'multiple_choice',
                text: 'What is the correct way to declare a constant in JavaScript?',
                options: [
                  { id: 'a', text: 'var x = 5' },
                  { id: 'b', text: 'let x = 5' },
                  { id: 'c', text: 'const x = 5' },
                  { id: 'd', text: 'constant x = 5' },
                ],
                correctAnswer: 'c',
                points: 10,
                difficulty: 'easy',
              },
              {
                id: 'q2',
                type: 'true_false',
                text: 'JavaScript is a statically typed language.',
                correctAnswer: 'false',
                points: 10,
                difficulty: 'easy',
              },
            ],
            timeLimit: 30, // 30 minutes
          });
        }, 500);
      });

      const newSession: ExamSessionData = {
        id: `session-${Date.now()}`,
        assessmentId,
        status: 'in_progress',
        answers: response.questions.map(q => ({
          questionId: q.id,
          answer: q.type === 'multiple_select' ? [] : '',
          isFlagged: false,
          timeSpent: 0,
        })),
        currentQuestionIndex: 0,
        startedAt: new Date().toISOString(),
        flags: {
          tabSwitches: 0,
          focusLossCount: 0,
          suspiciousActivity: false,
        },
      };

      setQuestions(response.questions);
      setSession(newSession);
      setTimeRemaining(response.timeLimit * 60);
      setTabSwitchCount(0);
    } catch (error) {
      console.error('Failed to start exam session:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [assessmentId]);

  // Submit answer
  const submitAnswer = useCallback((questionId: string, answer: string | string[]) => {
    setSession(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        answers: prev.answers.map(a =>
          a.questionId === questionId
            ? { ...a, answer }
            : a
        ),
      };
    });
  }, []);

  // Navigate questions
  const navigateQuestion = useCallback((direction: 'next' | 'prev' | number) => {
    setSession(prev => {
      if (!prev) return prev;
      
      let newIndex: number;
      
      if (typeof direction === 'number') {
        newIndex = direction;
      } else if (direction === 'next') {
        newIndex = Math.min(questions.length - 1, prev.currentQuestionIndex + 1);
      } else {
        newIndex = Math.max(0, prev.currentQuestionIndex - 1);
      }
      
      return {
        ...prev,
        currentQuestionIndex: newIndex,
      };
    });
  }, [questions.length]);

  // Go to specific question
  const goToQuestion = useCallback((index: number) => {
    if (index < 0 || index >= questions.length) return;
    
    setSession(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        currentQuestionIndex: index,
      };
    });
  }, [questions.length]);

  // Flag question
  const flagQuestion = useCallback((questionId: string) => {
    setSession(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        answers: prev.answers.map(a =>
          a.questionId === questionId
            ? { ...a, isFlagged: true }
            : a
        ),
      };
    });
  }, []);

  // Unflag question
  const unflagQuestion = useCallback((questionId: string) => {
    setSession(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        answers: prev.answers.map(a =>
          a.questionId === questionId
            ? { ...a, isFlagged: false }
            : a
        ),
      };
    });
  }, []);

  // Toggle flag
  const toggleFlag = useCallback((questionId: string) => {
    setSession(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        answers: prev.answers.map(a =>
          a.questionId === questionId
            ? { ...a, isFlagged: !a.isFlagged }
            : a
        ),
      };
    });
  }, []);

  // Get answered count
  const getAnsweredCount = useCallback(() => {
    if (!session) return 0;
    return session.answers.filter(a =>
      (typeof a.answer === 'string' && a.answer.trim() !== '') ||
      (Array.isArray(a.answer) && a.answer.length > 0)
    ).length;
  }, [session]);

  // Get flagged count
  const getFlaggedCount = useCallback(() => {
    if (!session) return 0;
    return session.answers.filter(a => a.isFlagged).length;
  }, [session]);

  // Get answered question IDs
  const getAnsweredQuestionIds = useCallback(() => {
    if (!session) return [];
    return session.answers
      .filter(a =>
        (typeof a.answer === 'string' && a.answer.trim() !== '') ||
        (Array.isArray(a.answer) && a.answer.length > 0)
      )
      .map(a => a.questionId);
  }, [session]);

  // Start timer
  const startTimer = useCallback(() => {
    if (timerRef.current) return;
    
    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 60 && prev % 30 === 0) {
          onTimeWarning?.(prev);
        }
        
        if (prev <= 1) {
          if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
          }
          onTimeUp?.();
          finishExam();
          return 0;
        }
        
        return prev - 1;
      });
    }, 1000);
  }, [onTimeWarning, onTimeUp]);

  // Pause timer
  const pauseTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  // Reset timer
  const resetTimer = useCallback(() => {
    pauseTimer();
    // Reset to original time limit
    setTimeRemaining(questions.length * 60); // Default 1 min per question
  }, [pauseTimer, questions.length]);

  // Finish exam
  const finishExam = useCallback(async (): Promise<ExamResult | null> => {
    if (!session) return null;
    
    setIsSubmitting(true);
    
    try {
      // Calculate results
      const questionResults = questions.map(question => {
        const answer = session.answers.find(a => a.questionId === question.id);
        let isCorrect = false;
        let pointsEarned = 0;
        
        if (answer && question.correctAnswer) {
          if (question.type === 'multiple_choice' || question.type === 'true_false') {
            isCorrect = answer.answer === question.correctAnswer;
          } else if (question.type === 'multiple_select') {
            const correctAnswers = Array.isArray(question.correctAnswer)
              ? question.correctAnswer
              : [question.correctAnswer];
            isCorrect = Array.isArray(answer.answer) &&
              correctAnswers.length === answer.answer.length &&
              correctAnswers.every(a => answer.answer.includes(a));
          }
          
          if (isCorrect) {
            pointsEarned = question.points;
          }
        }
        
        return {
          questionId: question.id,
          isCorrect,
          pointsEarned,
        };
      });
      
      const totalPoints = questions.reduce((sum, q) => sum + q.points, 0);
      const earnedPoints = questionResults.reduce((sum, r) => sum + r.pointsEarned, 0);
      const percentage = totalPoints > 0 ? (earnedPoints / totalPoints) * 100 : 0;
      
      const result: ExamResult = {
        sessionId: session.id,
        totalPoints,
        earnedPoints,
        percentage,
        passed: percentage >= 70, // Assuming 70% passing score
        questionResults,
        timeTaken: session.startedAt
          ? Math.floor((Date.now() - new Date(session.startedAt).getTime()) / 1000)
          : 0,
      };
      
      // Update session status
      setSession(prev => prev
        ? {
            ...prev,
            status: 'submitted',
            submittedAt: new Date().toISOString(),
          }
        : prev
      );
      
      // Clear timers
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      if (saveTimerRef.current) {
        clearInterval(saveTimerRef.current);
        saveTimerRef.current = null;
      }
      
      return result;
    } catch (error) {
      console.error('Failed to submit exam:', error);
      return null;
    } finally {
      setIsSubmitting(false);
    }
  }, [session, questions]);

  // Abandon exam
  const abandonExam = useCallback(async () => {
    setSession(prev => prev
      ? {
          ...prev,
          status: 'abandoned',
          submittedAt: new Date().toISOString(),
        }
      : prev
    );
    
    // Clear timers
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (saveTimerRef.current) {
      clearInterval(saveTimerRef.current);
      saveTimerRef.current = null;
    }
  }, []);

  // Get question result
  const getQuestionResult = useCallback((questionId: string) => {
    // This would be populated after submission
    return undefined;
  }, []);

  // Get progress
  const getProgress = useCallback(() => {
    const answered = getAnsweredCount();
    const total = questions.length;
    return {
      answered,
      total,
      percentage: total > 0 ? (answered / total) * 100 : 0,
    };
  }, [questions.length, getAnsweredCount]);

  // Tab switch detection
  useEffect(() => {
    if (!enableProctoring || !session) return;
    
    const handleVisibilityChange = () => {
      if (document.hidden) {
        setTabSwitchCount(prev => {
          const newCount = prev + 1;
          onTabSwitch?.(newCount);
          
          setSession(s => s
            ? {
                ...s,
                flags: {
                  ...s.flags,
                  tabSwitches: newCount,
                  suspiciousActivity: newCount >= 3,
                },
              }
            : s
          );
          
          return newCount;
        });
      }
    };
    
    const handleFocusLoss = () => {
      setSession(s => s
        ? {
            ...s,
            flags: {
              ...s.flags,
              focusLossCount: s.flags.focusLossCount + 1,
            },
          }
        : s
      );
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleFocusLoss);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleFocusLoss);
    };
  }, [enableProctoring, session, onTabSwitch]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (saveTimerRef.current) clearInterval(saveTimerRef.current);
    };
  }, []);

  return {
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
    flagQuestion,
    unflagQuestion,
    toggleFlag,
    getAnsweredCount,
    getFlaggedCount,
    getAnsweredQuestionIds,
    startTimer,
    pauseTimer,
    resetTimer,
    getQuestionResult,
    getProgress,
  };
}

export default useExamSession;
