# JavaScript Syntax Error Fix - Start Path Button

## Bug Description
The "Start Path" button on learning paths was not opening the AI-Generated Lesson modal when clicked. The issue was a JavaScript syntax error in the HTML generation.

## Root Cause
UUID strings (like `01b94ca2-...`) were being passed as unquoted parameters in onclick attributes, causing JavaScript to interpret them as invalid variable names or numbers.

## The Problem
**Before Fix (Line 1015 in index.html):**
```html
<button onclick="startLearningPath(${path.id}, '${path.title}')">
```

**Generated HTML (BROKEN):**
```html
<button onclick="startLearningPath(01b94ca2-..., 'JAC Programming Fundamentals Journey')">
```

**JavaScript Error:**
```
Uncaught ReferenceError: 01b94ca2 is not defined
```

## The Solution
**After Fix:**
```html
<button onclick="startLearningPath('${path.id}', '${path.title}')">
```

**Generated HTML (FIXED):**
```html
<button onclick="startLearningPath('01b94ca2-...', 'JAC Programming Fundamentals Journey')">
```

## Technical Details

### Why This Error Occurred
1. **UUID Format**: Learning path IDs are UUID strings (e.g., `01b94ca2-8f4a-4c4d-9c5e-123456789abc`)
2. **JavaScript Rules**: In onclick attributes, unquoted strings starting with numbers are treated as numeric literals or variable names
3. **Browser Behavior**: The browser throws a syntax error before the function can even be called

### Why Other onclick Handlers Worked
- `startLearningConcept('${concept.concept_id}', '${concept.display_name}')` - Already had quotes
- No other onclick handlers had this issue

## Impact
- **Before**: "Start Path" button completely non-functional
- **After**: "Start Path" button properly opens AI lesson modal
- **User Experience**: Users can now start learning paths and begin AI-generated lessons

## Testing the Fix
1. Navigate to learning paths page
2. Click "Start Path" on any learning path (like "JAC Programming Fundamentals Journey")
3. **Expected Result**: AI-Generated Lesson modal should pop up with appropriate content
4. **Verification**: No JavaScript errors in browser console

## Prevention
This type of error can be prevented by:
1. Always quoting string parameters in onclick attributes
2. Using template literals consistently (`${variable}`)
3. Testing all onclick handlers with different data types
4. Using UUID validation in development

## Files Modified
- `frontend-jac/index.html`: Fixed line 1015 onclick attribute quoting

## Status
✅ **RESOLVED** - Start Path functionality now works correctly