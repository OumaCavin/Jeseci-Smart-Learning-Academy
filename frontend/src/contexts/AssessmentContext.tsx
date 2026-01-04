import React, { createContext, useContext, useState, useCallback, useEffect, useRef, ReactNode } from 'react';

// Type definitions for assessments
export interface Question {
  id: string;
  type: 'multiple_choice' | 'multiple_select' | 'true_false' | 'short_answer' | 'code' | 'matching';
  text: string;
  options?: {
    id: string;
    text: string;
    isCorrect: boolean;
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
  tags: string[];
  explanation?: string;
  timeLimit?: number; // in seconds, per question
  metadata: {
    createdAt: string;
    updatedAt: string;
    authorId: string;
    usageCount: number;
    successRate: number;
  };
}

export interface Assessment {
  id: string;
  title: string;
  description: string;
  type: 'quiz' | 'exam' | 'practice' | 'challenge';
  questions: Question[];
  settings: {
    timeLimit?: number; // in minutes
    allowBackNavigation: boolean;
    showResults: boolean;
    showCorrectAnswers: boolean;
    shuffleQuestions: boolean;
    shuffleOptions: boolean;
    passingScore: number;
    maxAttempts: number;
    enableProctoring: boolean;
    tabSwitchDetection: boolean;
    cameraRequired: boolean;
  };
  availability: {
    startDate?: string;
    endDate?: string;
    isPublic: boolean;
    courseIds?: string[];
    requiredForCompletion: boolean;
  };
  metadata: {
    createdAt: string;
    updatedAt: string;
    authorId: string;
    totalAttempts: number;
    averageScore: number;
  };
}

export interface AssessmentSession {
  id: string;
  assessmentId: string;
  userId: string;
  status: 'started' | 'in_progress' | 'submitted' | 'timed_out' | 'abandoned';
  answers: {
    questionId: string;
    answer: string | string[];
    isCorrect?: boolean;
    pointsEarned: number;
    timeSpent: number; // in seconds
  }[];
  currentQuestionIndex: number;
  startedAt: string;
  submittedAt?: string;
  timeRemaining?: number; // in seconds
  score?: number;
  feedback?: {
    totalPoints: number;
    earnedPoints: number;
    percentage: number;
    passed: boolean;
    questionFeedback: {
      questionId: string;
      isCorrect: boolean;
      pointsEarned: number;
      feedback?: string;
    }[];
  };
  flags: {
    tabSwitches: number;
    focusLossCount: number;
    suspiciousActivity: boolean;
  };
}

export interface QuestionBankFilter {
  tags?: string[];
  difficulty?: 'easy' | 'medium' | 'hard';
  type?: Question['type'];
  searchText?: string;
  courseId?: string;
}

export interface AssessmentContextType {
  // State
  assessments: Assessment[];
  questionBank: Question[];
  currentSession: AssessmentSession | null;
  currentAssessment: Assessment | null;
  isLoading: boolean;
  error: string | null;
  timeRemaining: number;
  tabSwitchCount: number;
  
  // Assessment operations
  fetchAssessments: (courseId?: string) => Promise<void>;
  fetchAssessmentById: (assessmentId: string) => Promise<Assessment | null>;
  createAssessment: (assessment: Partial<Assessment>) => Assessment;
  updateAssessment: (assessmentId: string, updates: Partial<Assessment>) => void;
  deleteAssessment: (assessmentId: string) => void;
  duplicateAssessment: (assessmentId: string) => Assessment;
  
  // Question bank operations
  fetchQuestionBank: (filter?: QuestionBankFilter) => Promise<void>;
  searchQuestions: (query: string) => Promise<Question[]>;
  createQuestion: (question: Partial<Question>) => Question;
  updateQuestion: (questionId: string, updates: Partial<Question>) => void;
  deleteQuestion: (questionId: string) => void;
  importQuestions: (questions: Partial<Question>[]) => void;
  
  // Session operations
  startSession: (assessmentId: string) => Promise<AssessmentSession>;
  submitAnswer: (questionId: string, answer: string | string[]) => void;
  navigateQuestion: (direction: 'next' | 'prev' | number) => void;
  finishSession: () => Promise<void>;
  abandonSession: () => void;
  getSessionReview: () => AssessmentSession | null;
  
  // Timer operations
  startTimer: () => void;
  pauseTimer: () => void;
  resetTimer: () => void;
  
  // Utilities
  calculateScore: () => { percentage: number; passed: boolean };
  getFlaggedQuestions: () => string[];
  toggleFlag: (questionId: string) => void;
}

const AssessmentContext = createContext<AssessmentContextType | undefined>(undefined);

export function AssessmentProvider({ children }: { children: ReactNode }) {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [questionBank, setQuestionBank] = useState<Question[]>([]);
  const [currentSession, setCurrentSession] = useState<AssessmentSession | null>(null);
  const [currentAssessment, setCurrentAssessment] = useState<Assessment | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [tabSwitchCount, setTabSwitchCount] = useState(0);
  const [flaggedQuestions, setFlaggedQuestions] = useState<string[]>([]);
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch assessments
  const fetchAssessments = useCallback(async (courseId?: string) => {
    setIsLoading(true);
    try {
      const response = await new Promise<Assessment[]>((resolve) => {
        setTimeout(() => resolve([]), 500);
      });
      setAssessments(response);
    } catch (err) {
      setError('Failed to fetch assessments');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch assessment by ID
  const fetchAssessmentById = useCallback(async (assessmentId: string): Promise<Assessment | null> => {
    setIsLoading(true);
    try {
      const response = await new Promise<Assessment | null>((resolve) => {
        setTimeout(() => resolve(null), 300);
      });
      if (response) {
        setCurrentAssessment(response);
      }
      return response;
    } catch (err) {
      setError('Failed to fetch assessment');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Create assessment
  const createAssessment = useCallback((assessment: Partial<Assessment>): Assessment => {
    const newAssessment: Assessment = {
      id: `assessment-${Date.now()}`,
      title: assessment.title || 'Untitled Assessment',
      description: assessment.description || '',
      questions: assessment.questions || [],
      settings: {
        allowBackNavigation: true,
        showResults: true,
        showCorrectAnswers: false,
        shuffleQuestions: false,
        shuffleOptions: false,
        passingScore: 70,
        maxAttempts: 3,
        enableProctoring: false,
        tabSwitchDetection: true,
        cameraRequired: false,
        ...assessment.settings,
      },
      availability: {
        isPublic: false,
        ...assessment.availability,
      },
      metadata: {
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        authorId: 'current-user',
        totalAttempts: 0,
        averageScore: 0,
      },
      ...assessment,
    };
    
    setAssessments(prev => [...prev, newAssessment]);
    return newAssessment;
  }, []);

  // Update assessment
  const updateAssessment = useCallback((assessmentId: string, updates: Partial<Assessment>) => {
    setAssessments(prev =>
      prev.map(a => a.id === assessmentId ? { ...a, ...updates } : a)
    );
  }, []);

  // Delete assessment
  const deleteAssessment = useCallback((assessmentId: string) => {
    setAssessments(prev => prev.filter(a => a.id !== assessmentId));
  }, []);

  // Duplicate assessment
  const duplicateAssessment = useCallback((assessmentId: string): Assessment => {
    const original = assessments.find(a => a.id === assessmentId);
    if (!original) {
      throw new Error('Assessment not found');
    }
    return createAssessment({
      ...original,
      title: `${original.title} (Copy)`,
      metadata: {
        ...original.metadata,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    });
  }, [assessments, createAssessment]);

  // Fetch question bank
  const fetchQuestionBank = useCallback(async (filter?: QuestionBankFilter) => {
    setIsLoading(true);
    try {
      const response = await new Promise<Question[]>((resolve) => {
        setTimeout(() => resolve([]), 500);
      });
      setQuestionBank(response);
    } catch (err) {
      setError('Failed to fetch question bank');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Search questions
  const searchQuestions = useCallback(async (query: string): Promise<Question[]> => {
    const response = await new Promise<Question[]>((resolve) => {
      setTimeout(() => resolve([]), 300);
    });
    return response.filter(q => 
      q.text.toLowerCase().includes(query.toLowerCase()) ||
      q.tags.some(t => t.toLowerCase().includes(query.toLowerCase()))
    );
  }, []);

  // Create question
  const createQuestion = useCallback((question: Partial<Question>): Question => {
    const newQuestion: Question = {
      id: `question-${Date.now()}`,
      type: question.type || 'multiple_choice',
      text: question.text || '',
      points: question.points || 1,
      difficulty: question.difficulty || 'medium',
      tags: question.tags || [],
      metadata: {
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        authorId: 'current-user',
        usageCount: 0,
        successRate: 0,
      },
      ...question,
    };
    
    setQuestionBank(prev => [...prev, newQuestion]);
    return newQuestion;
  }, []);

  // Update question
  const updateQuestion = useCallback((questionId: string, updates: Partial<Question>) => {
    setQuestionBank(prev =>
      prev.map(q => q.id === questionId ? { ...q, ...updates } : q)
    );
  }, []);

  // Delete question
  const deleteQuestion = useCallback((questionId: string) => {
    setQuestionBank(prev => prev.filter(q => q.id !== questionId));
  }, []);

  // Import questions
  const importQuestions = useCallback((questions: Partial<Question>[]) => {
    const newQuestions = questions.map(q => createQuestion(q));
    return newQuestions;
  }, [createQuestion]);

  // Start session
  const startSession = useCallback(async (assessmentId: string): Promise<AssessmentSession> => {
    const assessment = assessments.find(a => a.id === assessmentId);
    if (!assessment) {
      throw new Error('Assessment not found');
    }

    const session: AssessmentSession = {
      id: `session-${Date.now()}`,
      assessmentId,
      userId: 'current-user',
      status: 'started',
      answers: [],
      currentQuestionIndex: 0,
      startedAt: new Date().toISOString(),
      flags: {
        tabSwitches: 0,
        focusLossCount: 0,
        suspiciousActivity: false,
      },
    };

    // Shuffle questions if configured
    if (assessment.settings.shuffleQuestions) {
      session.answers = assessment.questions.map(q => ({
        questionId: q.id,
        answer: q.type === 'multiple_select' ? [] : '',
        pointsEarned: 0,
        timeSpent: 0,
      }));
    }

    setCurrentSession(session);
    setCurrentAssessment(assessment);
    setTimeRemaining((assessment.settings.timeLimit || 0) * 60);
    setTabSwitchCount(0);
    setFlaggedQuestions([]);

    // Start heartbeat
    heartbeatRef.current = setInterval(() => {
      // Send heartbeat to server
    }, 30000);

    return session;
  }, [assessments]);

  // Submit answer
  const submitAnswer = useCallback((questionId: string, answer: string | string[]) => {
    if (!currentSession) return;

    setCurrentSession(prev => {
      if (!prev) return prev;
      
      const existingAnswerIndex = prev.answers.findIndex(a => a.questionId === questionId);
      const newAnswers = [...prev.answers];
      
      if (existingAnswerIndex >= 0) {
        newAnswers[existingAnswerIndex] = {
          ...newAnswers[existingAnswerIndex],
          answer,
        };
      } else {
        newAnswers.push({
          questionId,
          answer,
          pointsEarned: 0,
          timeSpent: 0,
        });
      }
      
      return {
        ...prev,
        answers: newAnswers,
      };
    });
  }, [currentSession]);

  // Navigate questions
  const navigateQuestion = useCallback((direction: 'next' | 'prev' | number) => {
    if (!currentSession) return;

    setCurrentSession(prev => {
      if (!prev) return prev;
      
      let newIndex: number;
      
      if (typeof direction === 'number') {
        newIndex = direction;
      } else if (direction === 'next') {
        newIndex = prev.currentQuestionIndex + 1;
      } else {
        newIndex = prev.currentQuestionIndex - 1;
      }
      
      // Bounds check
      if (currentAssessment) {
        newIndex = Math.max(0, Math.min(currentAssessment.questions.length - 1, newIndex));
      }
      
      return {
        ...prev,
        currentQuestionIndex: newIndex,
      };
    });
  }, [currentSession, currentAssessment]);

  // Finish session
  const finishSession = useCallback(async () => {
    if (!currentSession || !currentAssessment) return;

    // Calculate score
    let totalPoints = 0;
    let earnedPoints = 0;
    
    const questionFeedback = currentAssessment.questions.map(question => {
      const answer = currentSession.answers.find(a => a.questionId === question.id);
      totalPoints += question.points;
      
      let isCorrect = false;
      let pointsEarned = 0;
      
      if (answer) {
        // Basic answer validation (expand with actual logic)
        if (question.type === 'multiple_choice' || question.type === 'true_false') {
          const correctOption = question.options?.find(o => o.isCorrect);
          isCorrect = answer.answer === correctOption?.id;
        } else if (question.type === 'multiple_select') {
          const correctOptions = question.options?.filter(o => o.isCorrect).map(o => o.id) || [];
          isCorrect = Array.isArray(answer.answer) && 
            correctOptions.length === answer.answer.length &&
            correctOptions.every(opt => answer.answer.includes(opt));
        }
        
        if (isCorrect) {
          pointsEarned = question.points;
          earnedPoints += pointsEarned;
        }
      }
      
      return {
        questionId: question.id,
        isCorrect,
        pointsEarned,
      };
    });

    const percentage = totalPoints > 0 ? (earnedPoints / totalPoints) * 100 : 0;
    const passed = percentage >= currentAssessment.settings.passingScore;

    const submittedSession: AssessmentSession = {
      ...currentSession,
      status: 'submitted',
      submittedAt: new Date().toISOString(),
      score: earnedPoints,
      feedback: {
        totalPoints,
        earnedPoints,
        percentage,
        passed,
        questionFeedback,
      },
    };

    setCurrentSession(submittedSession);

    // Clear timers
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    if (heartbeatRef.current) {
      clearInterval(heartbeatRef.current);
    }

    return submittedSession;
  }, [currentSession, currentAssessment]);

  // Abandon session
  const abandonSession = useCallback(() => {
    if (!currentSession) return;

    setCurrentSession(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        status: 'abandoned',
        submittedAt: new Date().toISOString(),
      };
    });

    // Clear timers
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    if (heartbeatRef.current) {
      clearInterval(heartbeatRef.current);
    }
  }, [currentSession]);

  // Get session review
  const getSessionReview = useCallback((): AssessmentSession | null => {
    return currentSession;
  }, [currentSession]);

  // Start timer
  const startTimer = useCallback(() => {
    if (timerRef.current) return;
    
    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          // Time's up - auto submit
          finishSession();
          if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
          }
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, [finishSession]);

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
    if (currentAssessment?.settings.timeLimit) {
      setTimeRemaining(currentAssessment.settings.timeLimit * 60);
    }
  }, [pauseTimer, currentAssessment]);

  // Calculate score
  const calculateScore = useCallback((): { percentage: number; passed: boolean } => {
    if (!currentSession || !currentAssessment) {
      return { percentage: 0, passed: false };
    }
    
    let totalPoints = 0;
    let earnedPoints = 0;
    
    currentAssessment.questions.forEach(question => {
      totalPoints += question.points;
      const answer = currentSession.answers.find(a => a.questionId === question.id);
      if (answer && answer.pointsEarned) {
        earnedPoints += answer.pointsEarned;
      }
    });
    
    const percentage = totalPoints > 0 ? (earnedPoints / totalPoints) * 100 : 0;
    const passed = percentage >= currentAssessment.settings.passingScore;
    
    return { percentage, passed };
  }, [currentSession, currentAssessment]);

  // Get flagged questions
  const getFlaggedQuestions = useCallback((): string[] => {
    return flaggedQuestions;
  }, [flaggedQuestions]);

  // Toggle flag
  const toggleFlag = useCallback((questionId: string) => {
    setFlaggedQuestions(prev => {
      if (prev.includes(questionId)) {
        return prev.filter(id => id !== questionId);
      }
      return [...prev, questionId];
    });
  }, []);

  // Tab switch detection
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && currentSession?.status === 'in_progress') {
        setTabSwitchCount(prev => {
          const newCount = prev + 1;
          
          // Update session flags
          setCurrentSession(prevSession => {
            if (!prevSession) return prevSession;
            return {
              ...prevSession,
              flags: {
                ...prevSession.flags,
                tabSwitches: newCount,
                suspiciousActivity: newCount >= 3,
              },
            };
          });
          
          return newCount;
        });
      }
    };

    const handleFocusLoss = () => {
      if (currentSession?.status === 'in_progress') {
        setCurrentSession(prev => {
          if (!prev) return prev;
          return {
            ...prev,
            flags: {
              ...prev.flags,
              focusLossCount: prev.flags.focusLossCount + 1,
            },
          };
        });
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleFocusLoss);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleFocusLoss);
    };
  }, [currentSession]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (heartbeatRef.current) clearInterval(heartbeatRef.current);
    };
  }, []);

  const value: AssessmentContextType = {
    assessments,
    questionBank,
    currentSession,
    currentAssessment,
    isLoading,
    error,
    timeRemaining,
    tabSwitchCount,
    fetchAssessments,
    fetchAssessmentById,
    createAssessment,
    updateAssessment,
    deleteAssessment,
    duplicateAssessment,
    fetchQuestionBank,
    searchQuestions,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    importQuestions,
    startSession,
    submitAnswer,
    navigateQuestion,
    finishSession,
    abandonSession,
    getSessionReview,
    startTimer,
    pauseTimer,
    resetTimer,
    calculateScore,
    getFlaggedQuestions,
    toggleFlag,
  };

  return (
    <AssessmentContext.Provider value={value}>
      {children}
    </AssessmentContext.Provider>
  );
}

export function useAssessment() {
  const context = useContext(AssessmentContext);
  if (context === undefined) {
    throw new Error('useAssessment must be used within an AssessmentProvider');
  }
  return context;
}

export default AssessmentContext;
