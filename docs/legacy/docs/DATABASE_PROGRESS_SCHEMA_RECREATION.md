# Database Progress Schema Recreation

## Visual Schema Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA - PROGRESS FIELDS              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   learning_paths │    │learning_path_   │    │   user_progress │
│                 │    │   concepts      │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ path_id (PK)    │◄───┤ path_id (FK)    │    │ progress_id (PK)│
│ name            │    │ concept_id (FK) │◄───┤ user_id (FK)    │
│ difficulty_level│    │ sequence_order  │    │ concept_id (FK) │
│ estimated_      │    │ required_       │    │ mastery_level   │ ◄─┐
│   duration      │    │   mastery_level │    │ confidence_     │   │
│ is_public       │    └─────────────────┘    │   level         │   │
└─────────────────┘           │              │ time_spent      │   │
                             │              │ success_rate    │   │
┌─────────────────┐          │              │ average_score   │   │
│    concepts     │          │              │ streak_count    │   │
├─────────────────┤          │              │ review_count    │   │
│ concept_id (PK) │◄─────────┘              │ first_attempt   │   │
│ name            │                         │ last_review     │   │
│ difficulty_     │                         └─────────────────┘   │
│   level         │                                         │
│ description     │                                         │
└─────────────────┘                                         │
                                                              │
┌─────────────────┐                                         │
│ learning_session│                                         │
├─────────────────┤                                         │
│ session_id (PK) │                                         │
│ user_id (FK)    │                                         │
│ path_id (FK)    │                                         │
│ progress_       │◄─────────────────────────────────────┘
│   percentage    │
│ concepts_       │
│   completed     │
│ total_duration  │
└─────────────────┘
```

## Progress Calculation Logic

### Learning Path Progress Formula:
```
Path Progress = AVG(concept_mastery_levels)

Where:
- concept_mastery_level = 1.0 if UserProgress.mastery_level >= 0.8 (completed)
- concept_mastery_level = UserProgress.mastery_level if 0 < mastery_level < 0.8 (in progress)
- concept_mastery_level = 0.0 if no UserProgress record (not started)
```

### Active Path Detection:
```
Is Active = (Path Progress > 0) AND (Path Progress < 1)
```

### Time Calculation:
```
Time Spent (hours) = SUM(UserProgress.time_spent) / 60
```

## Sample Data Flow

### User "alice" studies "JAC Programming Fundamentals Journey"

1. **Path**: JAC Programming Fundamentals Journey
   - concepts_count: 11
   - difficulty_level: "beginner"
   - estimated_duration: 40 minutes

2. **User Progress Records**:
   ```
   concept_1: mastery_level = 1.0, time_spent = 15 minutes  (completed)
   concept_2: mastery_level = 0.8, time_spent = 12 minutes  (completed)  
   concept_3: mastery_level = 0.5, time_spent = 8 minutes   (in progress)
   concept_4: mastery_level = 0.0, time_spent = 0 minutes   (not started)
   ... (7 more concepts not started)
   ```

3. **Calculated Results**:
   ```
   progress = (1.0 + 0.8 + 0.5 + 0.0 + ... + 0.0) / 11 = 0.21 (21%)
   is_active = true (0 < 0.21 < 1)
   time_spent_hours = (15 + 12 + 8 + 0 + ...) / 60 = 0.58 hours
   concepts_completed = 2 (concepts with mastery_level >= 0.8)
   ```

4. **API Response**:
   ```json
   {
     "path_id": "path-123",
     "name": "JAC Programming Fundamentals Journey",
     "difficulty_level": "beginner",
     "estimated_duration": 40,
     "progress": 0.21,
     "is_active": true,
     "time_spent_hours": 0.58,
     "concepts_count": 11,
     "concepts_completed": 2
   }
   ```

## Frontend Integration

### Current Frontend Code (Needs Backend):
```jac
# This currently uses fallback logic because API doesn't provide calculated progress
progress = path.get("progress", 0.0);  # Should come from API calculation
```

### Expected API Integration:
```jac
# This should work once backend provides calculated progress
progress = path.get("progress", 0.0);  # Now comes from UserProgress data
if (progress > 0 and progress < 1) { 
    active_count += 1; 
}
```

## Database Schema Creation Script

```sql
-- Create all progress tracking tables
CREATE TABLE learning_paths (
    path_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    difficulty_level VARCHAR(20) NOT NULL,
    estimated_duration INTEGER,
    is_public BOOLEAN DEFAULT false
);

CREATE TABLE user_progress (
    progress_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    concept_id VARCHAR(36) NOT NULL,
    mastery_level FLOAT DEFAULT 0.0,
    time_spent INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE learning_path_concepts (
    path_id VARCHAR(36) REFERENCES learning_paths(path_id),
    concept_id VARCHAR(36),
    sequence_order INTEGER NOT NULL,
    PRIMARY KEY (path_id, concept_id)
);

-- Indexes for performance
CREATE INDEX idx_progress_user_concept ON user_progress(user_id, concept_id);
CREATE INDEX idx_path_concepts_path ON learning_path_concepts(path_id);
```

---

## Summary: Progress IS Available!

The database has **comprehensive progress tracking**. The learning path progress just needs to be calculated by joining the tables, which is a standard SQL operation.

**Status**: ✅ Progress fields exist and are well-designed
**Next Step**: Update API to calculate and return learning path progress