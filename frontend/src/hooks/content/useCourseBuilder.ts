import { useState, useCallback, useEffect } from 'react';

// Type definitions for course builder
export interface CourseModuleData {
  id: string;
  title: string;
  description: string;
  order: number;
  resources: ResourceData[];
  unlockCondition?: {
    type: 'prerequisite' | 'completion' | 'time' | 'score';
    moduleId?: string;
    score?: number;
    date?: string;
  };
  estimatedDuration: number;
}

export interface ResourceData {
  id: string;
  type: 'video' | 'article' | 'code_challenge' | 'quiz' | 'document' | 'external_link';
  title: string;
  description: string;
  content: Record<string, unknown>;
  duration?: number;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  prerequisites: string[];
}

export interface CourseData {
  id: string;
  title: string;
  description: string;
  thumbnail?: string;
  category: string;
  tags: string[];
  modules: CourseModuleData[];
  settings: {
    isPublic: boolean;
    allowLateSubmission: boolean;
    enableDiscussions: boolean;
    passingScore: number;
  };
}

export interface UseCourseBuilderOptions {
  courseId?: string;
  onAutoSave?: (draft: CourseData) => void;
  autoSaveInterval?: number;
  enableValidation?: boolean;
}

export interface UseCourseBuilderReturn {
  // State
  course: CourseData | null;
  isLoading: boolean;
  isSaving: boolean;
  hasUnsavedChanges: boolean;
  lastSavedAt: Date | null;
  validationErrors: string[];
  selectedModuleId: string | null;
  selectedResourceId: string | null;
  
  // Course operations
  loadCourse: (id: string) => Promise<void>;
  createCourse: (data: Partial<CourseData>) => void;
  updateCourse: (updates: Partial<CourseData>) => void;
  saveCourse: () => Promise<void>;
  publishCourse: () => Promise<void>;
  deleteCourse: () => Promise<void>;
  
  // Module operations
  addModule: (module: Partial<CourseModuleData>) => void;
  updateModule: (moduleId: string, updates: Partial<CourseModuleData>) => void;
  removeModule: (moduleId: string) => void;
  duplicateModule: (moduleId: string) => void;
  reorderModules: (fromIndex: number, toIndex: number) => void;
  selectModule: (moduleId: string | null) => void;
  
  // Resource operations
  addResource: (moduleId: string, resource: Partial<ResourceData>) => void;
  updateResource: (moduleId: string, resourceId: string, updates: Partial<ResourceData>) => void;
  removeResource: (moduleId: string, resourceId: string) => void;
  duplicateResource: (moduleId: string, resourceId: string) => void;
  reorderResources: (moduleId: string, fromIndex: number, toIndex: number) => void;
  selectResource: (resourceId: string | null) => void;
  
  // Validation
  validateCourse: () => { isValid: boolean; errors: string[] };
  validateModule: (moduleId: string) => { isValid: boolean; errors: string[] };
  
  // Utilities
  discardChanges: () => void;
  getModuleById: (moduleId: string) => CourseModuleData | undefined;
  getResourceById: (moduleId: string, resourceId: string) => ResourceData | undefined;
}

export function useCourseBuilder(options: UseCourseBuilderOptions = {}): UseCourseBuilderReturn {
  const {
    courseId,
    onAutoSave,
    autoSaveInterval = 30000,
    enableValidation = true,
  } = options;

  const [course, setCourse] = useState<CourseData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [selectedModuleId, setSelectedModuleId] = useState<string | null>(null);
  const [selectedResourceId, setSelectedResourceId] = useState<string | null>(null);

  // Load existing course
  const loadCourse = useCallback(async (id: string) => {
    setIsLoading(true);
    try {
      // Simulate API call
      const response = await new Promise<CourseData | null>((resolve) => {
        setTimeout(() => resolve(null), 500);
      });
      
      if (response) {
        setCourse(response);
      }
    } catch (error) {
      console.error('Failed to load course:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Validate course - moved before publishCourse
  const validateCourse = useCallback((): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    
    if (!course) {
      errors.push('No course data available');
      return { isValid: false, errors };
    }
    
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
    
    return { isValid: errors.length === 0, errors };
  }, [course]);

  // Create new course
  const createCourse = useCallback((data: Partial<CourseData>) => {
    const newCourse: CourseData = {
      id: `course-${Date.now()}`,
      title: data.title || 'Untitled Course',
      description: data.description || '',
      modules: [],
      settings: {
        isPublic: false,
        allowLateSubmission: true,
        enableDiscussions: true,
        passingScore: 70,
        ...data.settings,
      },
      tags: data.tags || [],
      category: data.category || '',
      ...data,
    };
    
    setCourse(newCourse);
    setHasUnsavedChanges(true);
  }, []);

  // Update course
  const updateCourse = useCallback((updates: Partial<CourseData>) => {
    setCourse(prev => {
      if (!prev) return prev;
      return { ...prev, ...updates };
    });
    setHasUnsavedChanges(true);
  }, []);

  // Save course
  const saveCourse = useCallback(async () => {
    if (!course) return;
    
    setIsSaving(true);
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      setHasUnsavedChanges(false);
      setLastSavedAt(new Date());
      onAutoSave?.(course);
    } catch (error) {
      console.error('Failed to save course:', error);
      throw error;
    } finally {
      setIsSaving(false);
    }
  }, [course, onAutoSave]);

  // Publish course
  const publishCourse = useCallback(async () => {
    if (!course) return;
    
    const validation = validateCourse();
    if (!validation.isValid) {
      setValidationErrors(validation.errors);
      throw new Error('Please fix validation errors before publishing');
    }
    
    await saveCourse();
    console.log('Publishing course:', course.id);
  }, [course, saveCourse, validateCourse]);

  // Delete course
  const deleteCourse = useCallback(async () => {
    if (!course) return;
    
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));
    setCourse(null);
  }, [course]);

  // Add module
  const addModule = useCallback((module: Partial<CourseModuleData>) => {
    if (!course) return;
    
    const newModule: CourseModuleData = {
      id: `module-${Date.now()}`,
      title: module.title || 'New Module',
      description: module.description || '',
      order: course.modules.length,
      resources: [],
      estimatedDuration: 0,
      ...module,
    };
    
    setCourse(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        modules: [...prev.modules, newModule],
      };
    });
    setSelectedModuleId(newModule.id);
    setHasUnsavedChanges(true);
  }, [course]);

  // Update module
  const updateModule = useCallback((moduleId: string, updates: Partial<CourseModuleData>) => {
    setCourse(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        modules: prev.modules.map(m =>
          m.id === moduleId ? { ...m, ...updates } : m
        ),
      };
    });
    setHasUnsavedChanges(true);
  }, []);

  // Remove module
  const removeModule = useCallback((moduleId: string) => {
    setCourse(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        modules: prev.modules.filter(m => m.id !== moduleId),
      };
    });
    
    if (selectedModuleId === moduleId) {
      setSelectedModuleId(null);
    }
    setHasUnsavedChanges(true);
  }, [selectedModuleId]);

  // Duplicate module
  const duplicateModule = useCallback((moduleId: string) => {
    if (!course) return;
    
    const module = course.modules.find(m => m.id === moduleId);
    if (!module) return;
    
    const duplicatedModule: CourseModuleData = {
      ...module,
      id: `module-${Date.now()}`,
      title: `${module.title} (Copy)`,
      order: course.modules.length,
      resources: module.resources.map(r => ({
        ...r,
        id: `resource-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      })),
    };
    
    setCourse(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        modules: [...prev.modules, duplicatedModule],
      };
    });
    setHasUnsavedChanges(true);
  }, [course]);

  // Reorder modules
  const reorderModules = useCallback((fromIndex: number, toIndex: number) => {
    setCourse(prev => {
      if (!prev) return prev;
      
      const modules = [...prev.modules];
      const [removed] = modules.splice(fromIndex, 1);
      modules.splice(toIndex, 0, removed);
      
      return {
        ...prev,
        modules: modules.map((m, index) => ({ ...m, order: index })),
      };
    });
    setHasUnsavedChanges(true);
  }, []);

  // Select module
  const selectModule = useCallback((moduleId: string | null) => {
    setSelectedModuleId(moduleId);
    setSelectedResourceId(null);
  }, []);

  // Add resource
  const addResource = useCallback((moduleId: string, resource: Partial<ResourceData>) => {
    if (!course) return;
    
    const newResource: ResourceData = {
      id: `resource-${Date.now()}`,
      type: resource.type || 'article',
      title: resource.title || 'New Resource',
      description: resource.description || '',
      content: resource.content || {},
      tags: resource.tags || [],
      prerequisites: resource.prerequisites || [],
      ...resource,
    };
    
    setCourse(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        modules: prev.modules.map(m =>
          m.id === moduleId
            ? { ...m, resources: [...m.resources, newResource] }
            : m
        ),
      };
    });
    setSelectedResourceId(newResource.id);
    setHasUnsavedChanges(true);
  }, [course]);

  // Update resource
  const updateResource = useCallback((
    moduleId: string,
    resourceId: string,
    updates: Partial<ResourceData>
  ) => {
    setCourse(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        modules: prev.modules.map(m =>
          m.id === moduleId
            ? {
                ...m,
                resources: m.resources.map(r =>
                  r.id === resourceId ? { ...r, ...updates } : r
                ),
              }
            : m
        ),
      };
    });
    setHasUnsavedChanges(true);
  }, []);

  // Remove resource
  const removeResource = useCallback((moduleId: string, resourceId: string) => {
    setCourse(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        modules: prev.modules.map(m =>
          m.id === moduleId
            ? { ...m, resources: m.resources.filter(r => r.id !== resourceId) }
            : m
        ),
      };
    });
    
    if (selectedResourceId === resourceId) {
      setSelectedResourceId(null);
    }
    setHasUnsavedChanges(true);
  }, [selectedResourceId]);

  // Duplicate resource
  const duplicateResource = useCallback((moduleId: string, resourceId: string) => {
    if (!course) return;
    
    const module = course.modules.find(m => m.id === moduleId);
    const resource = module?.resources.find(r => r.id === resourceId);
    if (!resource) return;
    
    const duplicatedResource: ResourceData = {
      ...resource,
      id: `resource-${Date.now()}`,
      title: `${resource.title} (Copy)`,
    };
    
    setCourse(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        modules: prev.modules.map(m =>
          m.id === moduleId
            ? { ...m, resources: [...m.resources, duplicatedResource] }
            : m
        ),
      };
    });
    setHasUnsavedChanges(true);
  }, [course]);

  // Reorder resources
  const reorderResources = useCallback((moduleId: string, fromIndex: number, toIndex: number) => {
    setCourse(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        modules: prev.modules.map(m =>
          m.id === moduleId
            ? {
                ...m,
                resources: (() => {
                  const resources = [...m.resources];
                  const [removed] = resources.splice(fromIndex, 1);
                  resources.splice(toIndex, 0, removed);
                  return resources;
                })(),
              }
            : m
        ),
      };
    });
    setHasUnsavedChanges(true);
  }, []);

  // Select resource
  const selectResource = useCallback((resourceId: string | null) => {
    setSelectedResourceId(resourceId);
  }, []);

  // Validate specific module
  const validateModule = useCallback((moduleId: string): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    const module = course?.modules.find(m => m.id === moduleId);
    
    if (!module) {
      errors.push('Module not found');
      return { isValid: false, errors };
    }
    
    if (!module.title.trim()) {
      errors.push('Module title is required');
    }
    
    return { isValid: errors.length === 0, errors };
  }, [course]);

  // Discard changes
  const discardChanges = useCallback(() => {
    if (courseId) {
      loadCourse(courseId);
    } else {
      setCourse(null);
    }
    setHasUnsavedChanges(false);
    setValidationErrors([]);
  }, [courseId, loadCourse]);

  // Get module by ID
  const getModuleById = useCallback((moduleId: string): CourseModuleData | undefined => {
    return course?.modules.find(m => m.id === moduleId);
  }, [course]);

  // Get resource by ID
  const getResourceById = useCallback((
    moduleId: string,
    resourceId: string
  ): ResourceData | undefined => {
    const module = course?.modules.find(m => m.id === moduleId);
    return module?.resources.find(r => r.id === resourceId);
  }, [course]);

  // Auto-save effect
  useEffect(() => {
    if (!hasUnsavedChanges || !onAutoSave || !course) return;
    
    const timer = setInterval(() => {
      onAutoSave(course);
    }, autoSaveInterval);
    
    return () => clearInterval(timer);
  }, [hasUnsavedChanges, course, onAutoSave, autoSaveInterval]);

  // Load course on mount if ID provided
  useEffect(() => {
    if (courseId) {
      loadCourse(courseId);
    }
  }, [courseId, loadCourse]);

  return {
    course,
    isLoading,
    isSaving,
    hasUnsavedChanges,
    lastSavedAt,
    validationErrors,
    selectedModuleId,
    selectedResourceId,
    loadCourse,
    createCourse,
    updateCourse,
    saveCourse,
    publishCourse,
    deleteCourse,
    addModule,
    updateModule,
    removeModule,
    duplicateModule,
    reorderModules,
    selectModule,
    addResource,
    updateResource,
    removeResource,
    duplicateResource,
    reorderResources,
    selectResource,
    validateCourse: enableValidation ? validateCourse : () => ({ isValid: true, errors: [] }),
    validateModule: enableValidation ? validateModule : () => ({ isValid: true, errors: [] }),
    discardChanges,
    getModuleById,
    getResourceById,
  };
}

export default useCourseBuilder;
