# Learning Paths Data Mapping Fixes

## Overview
Fixed critical data mapping mismatches between frontend expectations and actual backend database schema to ensure proper functionality with seeded JAC concepts data.

## Issues Fixed

### 1. Difficulty Level Mapping ❌ → ✅

**Problem**: Frontend expected "difficulty", Database uses "difficulty_level"
```jac
// Before (broken)
{self.get_path_icon(path.get("difficulty", "beginner"))}

// After (fixed)
difficulty = path.get("difficulty_level", path.get("difficulty", "beginner"));
{self.get_path_icon(difficulty)}
```

**Impact**: Icons now display correctly for seeded JAC concepts (beginner, intermediate, advanced, expert)

### 2. Duration Time Units ❌ → ✅

**Problem**: Frontend expected "estimated_duration_hours", Database stores "estimated_duration" in minutes
```jac
// Before (broken)
time_remaining = path.get("estimated_duration_hours", 0) - time_spent;

// After (fixed)
estimated_duration_minutes = path.get("estimated_duration", 0);
estimated_duration_hours = estimated_duration_minutes / 60.0;  // Convert to hours
time_remaining_hours = estimated_duration_hours - time_spent_hours;
```

**Impact**: Time calculations now work correctly with database values

### 3. Progress Field Handling ⚠️

**Issue**: "progress" is not stored in learning_paths table, needs API calculation
```jac
// Current implementation (with note)
progress = path.get("progress", 0.0);  # API should provide calculated progress
```

**Required Backend Fix**: API should calculate progress from UserProgress data:
```python
# Backend recommendation
def calculate_path_progress(path_id: str, user_id: str) -> float:
    """Calculate path progress based on UserProgress for concepts in path"""
    # Join LearningPathConcept with UserProgress
    # Calculate completion percentage
    # Return float between 0.0 and 1.0
```

### 4. Path Metadata Display ❌ → ✅

**Problem**: Duration display showed raw minutes without unit
```jac
// Before (unclear)
<span className="path-duration">{path.get("estimated_duration", "Unknown")}</span>

// After (clear)
<span className="path-duration">{path.get("estimated_duration", "Unknown")} min</span>
```

## Database Schema Reference

### LearningPath Table Fields
- ✅ `name`: String
- ✅ `description`: Text  
- ✅ `difficulty_level`: String (beginner/intermediate/advanced/expert)
- ✅ `estimated_duration`: Integer (minutes)
- ✅ `target_audience`: String
- ✅ `prerequisites`: JSON list
- ❌ `progress`: NOT STORED (needs calculation)

### UserProgress Table Fields
- ✅ `mastery_level`: Float (0.0 - 1.0)
- ✅ `confidence_level`: Float (0.0 - 1.0)
- ✅ `time_spent`: Integer (minutes)
- ✅ `success_rate`: Float (0.0 - 1.0)

## Expected API Response Format

The learning paths API should return data like:
```json
[
    {
        "path_id": "uuid",
        "name": "JAC Programming Fundamentals Journey",
        "description": "...",
        "difficulty_level": "beginner",
        "estimated_duration": 40,  // minutes
        "progress": 0.75,  // CALCULATED from UserProgress
        "time_spent_hours": 12.5,  // CALCULATED from UserProgress.time_spent / 60
        "concepts_count": 11,
        "target_audience": "Beginner programmers new to JAC"
    }
]
```

## Frontend Compatibility Matrix

| Frontend Field | Backend Field | Status | Notes |
|---------------|---------------|--------|-------|
| `difficulty` | `difficulty_level` | ✅ Fixed | Fallback implemented |
| `estimated_duration_hours` | `estimated_duration` (minutes) | ✅ Fixed | Conversion added |
| `progress` | NOT STORED | ⚠️ Needs Backend | Must be calculated |
| `time_spent_hours` | `UserProgress.time_spent` (minutes) | ⚠️ Needs Backend | Must be calculated |

## Testing Scenarios

### ✅ Now Working
1. **Difficulty Icons**: Show correct icons for all seeded paths
2. **Duration Display**: Shows "40 min" instead of "40"
3. **Time Calculations**: Proper hour conversion from minutes

### ⚠️ Still Needs Backend
1. **Progress Bars**: Need API to calculate from UserProgress
2. **Active Path Count**: Requires progress data
3. **Time Spent**: Needs aggregation from UserProgress records

## Backend API Requirements

To make the frontend fully functional, the learning paths endpoint should:

1. **Join Tables**: 
   - LearningPath + LearningPathConcept + UserProgress
   - Calculate progress from completed concepts

2. **Calculate Metrics**:
   - `progress`: (completed_concepts / total_concepts)
   - `time_spent_hours`: SUM(UserProgress.time_spent) / 60
   - `active_count`: COUNT(paths WHERE 0 < progress < 1)

3. **Example SQL**:
```sql
SELECT 
    lp.path_id,
    lp.name,
    lp.difficulty_level,
    lp.estimated_duration,
    -- Calculate progress
    COUNT(CASE WHEN up.mastery_level >= 0.8 THEN 1 END) * 1.0 / COUNT(lpc.concept_id) as progress,
    -- Calculate time spent
    COALESCE(SUM(up.time_spent), 0) / 60.0 as time_spent_hours
FROM learning_paths lp
JOIN learning_path_concepts lpc ON lp.path_id = lpc.path_id
LEFT JOIN user_progress up ON lpc.concept_id = up.concept_id 
WHERE lp.is_public = true
GROUP BY lp.path_id;
```

## Result

✅ **Immediate Fixes Applied**:
- Difficulty icons work with existing data
- Duration display shows proper units
- Time calculations handle minute-to-hour conversion

⚠️ **Backend Integration Needed**:
- Progress calculation and aggregation
- Time spent tracking
- Active path determination

The frontend is now data-compatible with the seeded JAC concepts and ready for full backend integration.