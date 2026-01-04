import React, { createContext, useContext, useState, useCallback, useReducer, ReactNode } from 'react';

// Type definitions for curriculum and content management
export interface Resource {
  id: string;
  type: 'video' | 'article' | 'code_challenge' | 'quiz' | 'document' | 'external_link';
  title: string;
  description: string;
  content: Record<string, unknown>;
  duration?: number; // in minutes
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  prerequisites: string[];
  metadata: {
    createdAt: string;
    updatedAt: string;
    authorId: string;
    version: number;
    status: 'draft' | 'published' | 'archived';
  };
}

export interface CourseModule {
  id: string;
  title: string;
  description: string;
  order: number;
  resources: Resource[];
  prerequisites: string[];
  unlockCondition?: {
    type: 'prerequisite' | 'completion' | 'time' | 'score';
    moduleId?: string;
    score?: number;
    date?: string;
  };
  estimatedDuration: number;
}

export interface Course {
  id: string;
  title: string;
  description: string;
  thumbnail?: string;
  category: string;
  tags: string[];
  modules: CourseModule[];
  settings: {
    isPublic: boolean;
    allowLateSubmission: boolean;
    enableDiscussions: boolean;
    passingScore: number;
  };
  metadata: {
    createdAt: string;
    updatedAt: string;
    authorId: string;
    version: number;
    enrollmentCount: number;
    averageRating: number;
  };
}

export interface LearningPath {
  id: string;
  title: string;
  description: string;
  courses: {
    courseId: string;
    order: number;
    required: boolean;
    unlockCondition?: {
      type: 'prerequisite' | 'time';
      courseId?: string;
      daysAfterEnrollment?: number;
    };
  }[];
  targetAudience: 'beginner' | 'intermediate' | 'advanced' | 'all';
  estimatedDuration: number;
  skills: string[];
  metadata: {
    createdAt: string;
    updatedAt: string;
    authorId: string;
    enrollmentCount: number;
  };
}

export interface CurriculumState {
  courses: Course[];
  learningPaths: LearningPath[];
  draftCourse: Course | null;
  draftPath: LearningPath | null;
  selectedCourse: Course | null;
  selectedModule: CourseModule | null;
  isLoading: boolean;
  error: string | null;
  hasUnsavedChanges: boolean;
}

export type CurriculumAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_COURSES'; payload: Course[] }
  | { type: 'SET_LEARNING_PATHS'; payload: LearningPath[] }
  | { type: 'SELECT_COURSE'; payload: Course | null }
  | { type: 'SELECT_MODULE'; payload: CourseModule | null }
  | { type: 'CREATE_DRAFT_COURSE'; payload: Course }
  | { type: 'UPDATE_DRAFT_COURSE'; payload: Partial<Course> }
  | { type: 'ADD_MODULE_TO_DRAFT'; payload: CourseModule }
  | { type: 'UPDATE_MODULE_IN_DRAFT'; payload: { moduleId: string; updates: Partial<CourseModule> } }
  | { type: 'REMOVE_MODULE_FROM_DRAFT'; payload: string }
  | { type: 'REORDER_MODULES_IN_DRAFT'; payload: { fromIndex: number; toIndex: number } }
  | { type: 'ADD_RESOURCE_TO_MODULE'; payload: { moduleId: string; resource: Resource } }
  | { type: 'UPDATE_RESOURCE_IN_MODULE'; payload: { moduleId: string; resourceId: string; updates: Partial<Resource> } }
  | { type: 'REMOVE_RESOURCE_FROM_MODULE'; payload: { moduleId: string; resourceId: string } }
  | { type: 'CREATE_DRAFT_PATH'; payload: LearningPath }
  | { type: 'UPDATE_DRAFT_PATH'; payload: Partial<LearningPath> }
  | { type: 'ADD_COURSE_TO_PATH'; payload: { courseId: string; order: number } }
  | { type: 'REMOVE_COURSE_FROM_PATH'; payload: string }
  | { type: 'SET_UNSAVED_CHANGES'; payload: boolean }
  | { type: 'CLEAR_DRAFT' }
  | { type: 'PUBLISH_COURSE'; payload: string }
  | { type: 'ARCHIVE_COURSE'; payload: string };

const initialState: CurriculumState = {
  courses: [],
  learningPaths: [],
  draftCourse: null,
  draftPath: null,
  selectedCourse: null,
  selectedModule: null,
  isLoading: false,
  error: null,
  hasUnsavedChanges: false,
};

function curriculumReducer(state: CurriculumState, action: CurriculumAction): CurriculumState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_COURSES':
      return { ...state, courses: action.payload };
    case 'SET_LEARNING_PATHS':
      return { ...state, learningPaths: action.payload };
    case 'SELECT_COURSE':
      return { ...state, selectedCourse: action.payload, selectedModule: null };
    case 'SELECT_MODULE':
      return { ...state, selectedModule: action.payload };
    case 'CREATE_DRAFT_COURSE':
      return { ...state, draftCourse: action.payload, hasUnsavedChanges: true };
    case 'UPDATE_DRAFT_COURSE':
      return state.draftCourse
        ? { ...state, draftCourse: { ...state.draftCourse, ...action.payload }, hasUnsavedChanges: true }
        : state;
    case 'ADD_MODULE_TO_DRAFT':
      return state.draftCourse
        ? {
            ...state,
            draftCourse: {
              ...state.draftCourse,
              modules: [...state.draftCourse.modules, action.payload],
            },
            hasUnsavedChanges: true,
          }
        : state;
    case 'UPDATE_MODULE_IN_DRAFT':
      return state.draftCourse
        ? {
            ...state,
            draftCourse: {
              ...state.draftCourse,
              modules: state.draftCourse.modules.map((m) =>
                m.id === action.payload.moduleId ? { ...m, ...action.payload.updates } : m
              ),
            },
            hasUnsavedChanges: true,
          }
        : state;
    case 'REMOVE_MODULE_FROM_DRAFT':
      return state.draftCourse
        ? {
            ...state,
            draftCourse: {
              ...state.draftCourse,
              modules: state.draftCourse.modules.filter((m) => m.id !== action.payload),
            },
            hasUnsavedChanges: true,
          }
        : state;
    case 'REORDER_MODULES_IN_DRAFT':
      return state.draftCourse
        ? {
            ...state,
            draftCourse: {
              ...state.draftCourse,
              modules: (() => {
                const modules = [...state.draftCourse.modules];
                const [removed] = modules.splice(action.payload.fromIndex, 1);
                modules.splice(action.payload.toIndex, 0, removed);
                return modules.map((m, index) => ({ ...m, order: index }));
              })(),
            },
            hasUnsavedChanges: true,
          }
        : state;
    case 'ADD_RESOURCE_TO_MODULE':
      return state.draftCourse
        ? {
            ...state,
            draftCourse: {
              ...state.draftCourse,
              modules: state.draftCourse.modules.map((m) =>
                m.id === action.payload.moduleId
                  ? { ...m, resources: [...m.resources, action.payload.resource] }
                  : m
              ),
            },
            hasUnsavedChanges: true,
          }
        : state;
    case 'UPDATE_RESOURCE_IN_MODULE':
      return state.draftCourse
        ? {
            ...state,
            draftCourse: {
              ...state.draftCourse,
              modules: state.draftCourse.modules.map((m) =>
                m.id === action.payload.moduleId
                  ? {
                      ...m,
                      resources: m.resources.map((r) =>
                        r.id === action.payload.resourceId
                          ? { ...r, ...action.payload.updates }
                          : r
                      ),
                    }
                  : m
              ),
            },
            hasUnsavedChanges: true,
          }
        : state;
    case 'REMOVE_RESOURCE_FROM_MODULE':
      return state.draftCourse
        ? {
            ...state,
            draftCourse: {
              ...state.draftCourse,
              modules: state.draftCourse.modules.map((m) =>
                m.id === action.payload.moduleId
                  ? { ...m, resources: m.resources.filter((r) => r.id !== action.payload.resourceId) }
                  : m
              ),
            },
            hasUnsavedChanges: true,
          }
        : state;
    case 'CREATE_DRAFT_PATH':
      return { ...state, draftPath: action.payload, hasUnsavedChanges: true };
    case 'UPDATE_DRAFT_PATH':
      return state.draftPath
        ? { ...state, draftPath: { ...state.draftPath, ...action.payload }, hasUnsavedChanges: true }
        : state;
    case 'ADD_COURSE_TO_PATH':
      return state.draftPath
        ? {
            ...state,
            draftPath: {
              ...state.draftPath,
              courses: [
                ...state.draftPath.courses,
                { courseId: action.payload.courseId, order: action.payload.order, required: true },
              ],
            },
            hasUnsavedChanges: true,
          }
        : state;
    case 'REMOVE_COURSE_FROM_PATH':
      return state.draftPath
        ? {
            ...state,
            draftPath: {
              ...state.draftPath,
              courses: state.draftPath.courses.filter((c) => c.courseId !== action.payload),
            },
            hasUnsavedChanges: true,
          }
        : state;
    case 'SET_UNSAVED_CHANGES':
      return { ...state, hasUnsavedChanges: action.payload };
    case 'CLEAR_DRAFT':
      return { ...state, draftCourse: null, draftPath: null, hasUnsavedChanges: false };
    case 'PUBLISH_COURSE':
      return {
        ...state,
        courses: state.courses.map((c) =>
          c.id === action.payload ? { ...c, metadata: { ...c.metadata, status: 'published' } } : c
        ),
      };
    case 'ARCHIVE_COURSE':
      return {
        ...state,
        courses: state.courses.map((c) =>
          c.id === action.payload ? { ...c, metadata: { ...c.metadata, status: 'archived' } } : c
        ),
      };
    default:
      return state;
  }
}

export interface CurriculumContextType extends CurriculumState {
  // Course operations
  fetchCourses: () => Promise<void>;
  fetchCourseById: (courseId: string) => Promise<Course | null>;
  createCourse: (course: Partial<Course>) => Course;
  updateCourse: (courseId: string, updates: Partial<Course>) => void;
  deleteCourse: (courseId: string) => void;
  publishCourse: (courseId: string) => void;
  archiveCourse: (courseId: string) => void;
  
  // Module operations
  addModule: (module: CourseModule) => void;
  updateModule: (moduleId: string, updates: Partial<CourseModule>) => void;
  removeModule: (moduleId: string) => void;
  reorderModules: (fromIndex: number, toIndex: number) => void;
  
  // Resource operations
  addResource: (moduleId: string, resource: Resource) => void;
  updateResource: (moduleId: string, resourceId: string, updates: Partial<Resource>) => void;
  removeResource: (moduleId: string, resourceId: string) => void;
  
  // Learning path operations
  fetchLearningPaths: () => Promise<void>;
  createLearningPath: (path: Partial<LearningPath>) => LearningPath;
  updateLearningPath: (pathId: string, updates: Partial<LearningPath>) => void;
  deleteLearningPath: (pathId: string) => void;
  addCourseToPath: (pathId: string, courseId: string, order: number) => void;
  removeCourseFromPath: (pathId: string, courseId: string) => void;
  
  // Draft operations
  startDraft: (type: 'course' | 'path', templateId?: string) => void;
  saveDraft: () => Promise<void>;
  discardDraft: () => void;
  
  // Selection operations
  selectCourse: (course: Course | null) => void;
  selectModule: (module: CourseModule | null) => void;
  
  // Validation
  validateCourse: () => { isValid: boolean; errors: string[] };
  validatePath: () => { isValid: boolean; errors: string[] };
}

const CurriculumContext = createContext<CurriculumContextType | undefined>(undefined);

export function CurriculumProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(curriculumReducer, initialState);

  // Fetch all courses
  const fetchCourses = useCallback(async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      // Simulate API call
      const response = await new Promise<Course[]>((resolve) => {
        setTimeout(() => resolve([]), 500);
      });
      dispatch({ type: 'SET_COURSES', payload: response });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to fetch courses' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  // Fetch single course
  const fetchCourseById = useCallback(async (courseId: string): Promise<Course | null> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const response = await new Promise<Course | null>((resolve) => {
        setTimeout(() => resolve(null), 300);
      });
      if (response) {
        dispatch({ type: 'SELECT_COURSE', payload: response });
      }
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to fetch course' });
      return null;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  // Create new course
  const createCourse = useCallback((course: Partial<Course>): Course => {
    const newCourse: Course = {
      id: `course-${Date.now()}`,
      title: course.title || 'Untitled Course',
      description: course.description || '',
      category: course.category || 'General',
      modules: course.modules || [],
      settings: {
        isPublic: false,
        allowLateSubmission: true,
        enableDiscussions: true,
        passingScore: 70,
        ...course.settings,
      },
      tags: course.tags || [],
      metadata: {
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        authorId: 'current-user',
        version: 1,
        enrollmentCount: 0,
        averageRating: 0,
        ...course.metadata,
      },
      thumbnail: course.thumbnail,
    };
    
    dispatch({ type: 'CREATE_DRAFT_COURSE', payload: newCourse });
    return newCourse;
  }, []);

  // Update course
  const updateCourse = useCallback((courseId: string, updates: Partial<Course>) => {
    dispatch({ type: 'UPDATE_DRAFT_COURSE', payload: updates });
  }, []);

  // Delete course
  const deleteCourse = useCallback((courseId: string) => {
    // API call would go here
    console.log('Deleting course:', courseId);
  }, []);

  // Publish course
  const publishCourse = useCallback((courseId: string) => {
    dispatch({ type: 'PUBLISH_COURSE', payload: courseId });
  }, []);

  // Archive course
  const archiveCourse = useCallback((courseId: string) => {
    dispatch({ type: 'ARCHIVE_COURSE', payload: courseId });
  }, []);

  // Add module
  const addModule = useCallback((module: CourseModule) => {
    dispatch({ type: 'ADD_MODULE_TO_DRAFT', payload: module });
  }, []);

  // Update module
  const updateModule = useCallback((moduleId: string, updates: Partial<CourseModule>) => {
    dispatch({ type: 'UPDATE_MODULE_IN_DRAFT', payload: { moduleId, updates } });
  }, []);

  // Remove module
  const removeModule = useCallback((moduleId: string) => {
    dispatch({ type: 'REMOVE_MODULE_FROM_DRAFT', payload: moduleId });
  }, []);

  // Reorder modules
  const reorderModules = useCallback((fromIndex: number, toIndex: number) => {
    dispatch({ type: 'REORDER_MODULES_IN_DRAFT', payload: { fromIndex, toIndex } });
  }, []);

  // Add resource
  const addResource = useCallback((moduleId: string, resource: Resource) => {
    dispatch({ type: 'ADD_RESOURCE_TO_MODULE', payload: { moduleId, resource } });
  }, []);

  // Update resource
  const updateResource = useCallback((moduleId: string, resourceId: string, updates: Partial<Resource>) => {
    dispatch({ type: 'UPDATE_RESOURCE_IN_MODULE', payload: { moduleId, resourceId, updates } });
  }, []);

  // Remove resource
  const removeResource = useCallback((moduleId: string, resourceId: string) => {
    dispatch({ type: 'REMOVE_RESOURCE_FROM_MODULE', payload: { moduleId, resourceId } });
  }, []);

  // Fetch learning paths
  const fetchLearningPaths = useCallback(async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const response = await new Promise<LearningPath[]>((resolve) => {
        setTimeout(() => resolve([]), 500);
      });
      dispatch({ type: 'SET_LEARNING_PATHS', payload: response });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to fetch learning paths' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  // Create learning path
  const createLearningPath = useCallback((path: Partial<LearningPath>): LearningPath => {
    const newPath: LearningPath = {
      id: `path-${Date.now()}`,
      title: path.title || 'Untitled Learning Path',
      description: path.description || '',
      courses: path.courses || [],
      targetAudience: path.targetAudience || 'all',
      estimatedDuration: path.estimatedDuration || 0,
      skills: path.skills || [],
      metadata: {
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        authorId: 'current-user',
        enrollmentCount: 0,
        ...path.metadata,
      },
    };
    
    dispatch({ type: 'CREATE_DRAFT_PATH', payload: newPath });
    return newPath;
  }, []);

  // Update learning path
  const updateLearningPath = useCallback((pathId: string, updates: Partial<LearningPath>) => {
    dispatch({ type: 'UPDATE_DRAFT_PATH', payload: updates });
  }, []);

  // Delete learning path
  const deleteLearningPath = useCallback((pathId: string) => {
    console.log('Deleting learning path:', pathId);
  }, []);

  // Add course to path
  const addCourseToPath = useCallback((pathId: string, courseId: string, order: number) => {
    dispatch({ type: 'ADD_COURSE_TO_PATH', payload: { courseId, order } });
  }, []);

  // Remove course from path
  const removeCourseFromPath = useCallback((pathId: string, courseId: string) => {
    dispatch({ type: 'REMOVE_COURSE_FROM_PATH', payload: courseId });
  }, []);

  // Start draft
  const startDraft = useCallback((type: 'course' | 'path', templateId?: string) => {
    if (type === 'course') {
      createCourse({});
    } else {
      createLearningPath({});
    }
  }, [createCourse, createLearningPath]);

  // Save draft
  const saveDraft = useCallback(async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      // API call would go here
      await new Promise((resolve) => setTimeout(resolve, 1000));
      dispatch({ type: 'SET_UNSAVED_CHANGES', payload: false });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to save draft' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  // Discard draft
  const discardDraft = useCallback(() => {
    dispatch({ type: 'CLEAR_DRAFT' });
  }, []);

  // Select course
  const selectCourse = useCallback((course: Course | null) => {
    dispatch({ type: 'SELECT_COURSE', payload: course });
  }, []);

  // Select module
  const selectModule = useCallback((module: CourseModule | null) => {
    dispatch({ type: 'SELECT_MODULE', payload: module });
  }, []);

  // Validate course
  const validateCourse = useCallback((): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    const course = state.draftCourse;

    if (!course) {
      errors.push('No course draft available');
    } else {
      if (!course.title.trim()) {
        errors.push('Course title is required');
      }
      if (course.modules.length === 0) {
        errors.push('Course must have at least one module');
      }
      course.modules.forEach((module, index) => {
        if (!module.title.trim()) {
          errors.push(`Module ${index + 1} needs a title`);
        }
        if (module.resources.length === 0) {
          errors.push(`Module "${module.title}" needs at least one resource`);
        }
      });

      // Check for circular dependencies
      const moduleIds = course.modules.map((m) => m.id);
      course.modules.forEach((module) => {
        module.prerequisites.forEach((prereq) => {
          if (!moduleIds.includes(prereq)) {
            errors.push(`Module "${module.title}" has invalid prerequisite: ${prereq}`);
          }
        });
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }, [state.draftCourse]);

  // Validate path
  const validatePath = useCallback((): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    const path = state.draftPath;

    if (!path) {
      errors.push('No learning path draft available');
    } else {
      if (!path.title.trim()) {
        errors.push('Learning path title is required');
      }
      if (path.courses.length === 0) {
        errors.push('Learning path must include at least one course');
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }, [state.draftPath]);

  const value: CurriculumContextType = {
    ...state,
    fetchCourses,
    fetchCourseById,
    createCourse,
    updateCourse,
    deleteCourse,
    publishCourse,
    archiveCourse,
    addModule,
    updateModule,
    removeModule,
    reorderModules,
    addResource,
    updateResource,
    removeResource,
    fetchLearningPaths,
    createLearningPath,
    updateLearningPath,
    deleteLearningPath,
    addCourseToPath,
    removeCourseFromPath,
    startDraft,
    saveDraft,
    discardDraft,
    selectCourse,
    selectModule,
    validateCourse,
    validatePath,
  };

  return (
    <CurriculumContext.Provider value={value}>
      {children}
    </CurriculumContext.Provider>
  );
}

export function useCurriculum() {
  const context = useContext(CurriculumContext);
  if (context === undefined) {
    throw new Error('useCurriculum must be used within a CurriculumProvider');
  }
  return context;
}

export default CurriculumContext;
