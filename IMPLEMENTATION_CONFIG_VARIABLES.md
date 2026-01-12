# Configuration Variables Implementation Summary

This document describes the comprehensive implementation of configuration variables throughout the Jeseci Smart Learning Academy application.

## Overview

The following environment variables have been implemented to control application behavior:

| Variable | Description | Default | Values |
|----------|-------------|---------|--------|
| `AI_CONTENT_ENABLED` | Toggle AI content generation | `true` | `true`/`false` |
| `AI_CHAT_ENABLED` | Toggle AI chat functionality | `true` | `true`/`false` |
| `ENABLE_MOCK_DATA` | Use mock data instead of database | `false` | `true`/`false` |
| `LOG_LEVEL` | Application logging verbosity | `info` | `debug`/`info`/`warning`/`error`/`critical` |

## Files Modified

### 1. Configuration Template (`backend/config/.env.template`)

Updated the environment variable documentation to provide clear descriptions for each configuration option.

**Location:** Lines 134-144

### 2. Application Configuration Module (`backend/config/app_config.py`)

Created a new centralized configuration module that:

- Defines dataclasses for each configuration category (`AIConfig`, `LoggingConfig`, `DevelopmentConfig`, `AppConfig`)
- Provides `from_env()` class methods to read values from environment variables
- Implements `get_app_config()` function with `@lru_cache()` for performance
- Provides `setup_logging()` function to configure Python logging
- Includes `is_feature_enabled()` convenience function for checking features
- Returns a configuration summary for debugging purposes

### 3. Main FastAPI Server (`backend/main.py`)

Updated to use the configuration system:

**Changes:**
- Added `logging` import and initialized `setup_logging()`
- Imported and used `get_app_config()` at module level
- Conditionally import and include `ai_content_router` based on `AI_CONTENT_ENABLED`
- Updated `/health` endpoint to report configuration status and AI feature availability
- Updated `/courses` endpoint to return mock or real data based on `ENABLE_MOCK_DATA`
- Updated `/ai/generate` endpoint to check `AI_CONTENT_ENABLED` before processing
- Updated `/ai/chat` endpoint to check `AI_CHAT_ENABLED` before processing
- Added appropriate logging throughout the application

**Key Features:**
- AI routes are only included when `AI_CONTENT_ENABLED=true`
- AI endpoints return 403 errors when disabled with helpful error messages
- Course data is clearly marked as mock when `ENABLE_MOCK_DATA=true`
- Application configuration is logged at startup

### 4. Jaclang Backend (`backend/app.jac`)

Updated multiple walkers to respect configuration:

**Health Check Walker (lines 66-95):**
- Now reads `AI_CONTENT_ENABLED`, `AI_CHAT_ENABLED`, `ENABLE_MOCK_DATA`, and `LOG_LEVEL`
- Returns configuration status in health check response
- Reports "disabled" status when AI features are turned off

**Courses Walker (lines 343-425):**
- Checks `ENABLE_MOCK_DATA` before returning data
- Returns mock data with "(MOCK)" suffix when enabled
- Reports data source (mock/database/fallback) in response
- Respects database-first approach when mock mode is disabled

**AI Content Walker (lines 688-729):**
- Validates `AI_CONTENT_ENABLED` before generating content
- Returns error response when feature is disabled
- Includes helpful message about enabling the feature

**Chat Walker (lines 1581-1602):**
- Validates `AI_CHAT_ENABLED` before processing chat requests
- Returns error response when feature is disabled

**AI Code Chat Walker (lines 751-788):**
- Validates `AI_CHAT_ENABLED` before code chat operations
- Updates health check to report `ai_chat_enabled` status

### 5. Logging Configuration (`backend/logger_config.py`)

Enhanced logging system to respect `LOG_LEVEL`:

**Changes:**
- Added `get_log_level_from_env()` function to parse environment variable
- Modified `setup_logging()` to accept optional log level parameter
- Defaults to environment variable when no explicit level provided
- Supports all standard Python logging levels

### 6. Configuration Package (`backend/config/__init__.py`)

Updated to export new configuration utilities alongside existing database exports.

## Usage Examples

### Enable Mock Data Mode

```bash
# In .env file
ENABLE_MOCK_DATA=true
```

This will cause the application to return mock course data instead of querying the database.

### Disable AI Features

```bash
# Disable AI content generation
AI_CONTENT_ENABLED=false

# Disable AI chat
AI_CHAT_ENABLED=false
```

### Configure Logging

```bash
# Enable debug logging
LOG_LEVEL=debug

# Minimal logging for production
LOG_LEVEL=warning
```

## API Responses

### Health Check Response

```json
{
  "service": "Jeseci Smart Learning Academy API",
  "status": "healthy",
  "version": "7.0.0",
  "ai_status": "disabled",
  "configuration": {
    "ai_content_enabled": "false",
    "ai_chat_enabled": "true",
    "mock_data_enabled": "false",
    "log_level": "info"
  }
}
```

### Course Response (Mock Mode)

```json
{
  "success": true,
  "courses": [
    {
      "course_id": "course_jac_fundamentals",
      "title": "JAC Programming Fundamentals (MOCK)",
      "description": "Mock Data",
      "domain": "Jaclang Programming",
      "difficulty": "beginner",
      "content_type": "interactive"
    }
  ],
  "total": 3,
  "source": "mock"
}
```

### AI Feature Disabled Response

```json
{
  "success": false,
  "error": "AI content generation is disabled",
  "message": "Please set AI_CONTENT_ENABLED=true in your .env file to enable this feature"
}
```

## Programmatic Usage

```python
from config.app_config import get_app_config, is_feature_enabled

# Get full configuration
config = get_app_config()

# Check specific features
if config.is_ai_content_enabled():
    print("AI content generation is enabled")

if config.is_mock_data_enabled():
    print("Using mock data mode")

# Convenience function
if is_feature_enabled('ai_chat'):
    print("AI chat is available")
```

## Migration Guide

### For Existing Deployments

1. Update `.env` file with new configuration variables
2. No breaking changes - defaults maintain existing behavior
3. AI features remain enabled by default
4. Mock data mode remains disabled by default

### For New Deployments

1. Copy `.env.template` to `.env`
2. Configure variables as needed
3. Restart application to apply changes

## Testing Recommendations

1. Test with `AI_CONTENT_ENABLED=false` - verify 403 errors
2. Test with `AI_CHAT_ENABLED=false` - verify 403 errors
3. Test with `ENABLE_MOCK_DATA=true` - verify mock data responses
4. Test with different `LOG_LEVEL` values - verify log output changes
5. Verify health check reflects configuration status
