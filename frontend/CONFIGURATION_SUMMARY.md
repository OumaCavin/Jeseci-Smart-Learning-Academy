# Jeseci Smart Learning Academy - Configuration Summary

## Overview
This document provides a comprehensive overview of all environment configurations for the Jeseci Smart Learning Academy platform, ensuring consistency between frontend and backend services.

## Environment Files Structure

### Frontend Configuration
- **`.env`**: Active development configuration
- **`.env.example`**: Template with all available options

### Backend Configuration
- **`backend/config/.env`**: Active backend configuration
- **`backend/config/.env.template`**: Backend template

## Key Configuration Values

### Email Configuration
```env
ADMIN_EMAIL=cavin.otieno012@gmail.com
FROM_EMAIL=noreply@jeseci.com
EMAIL_PASSWORD=oakjazoekos
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Database Configuration (PostgreSQL)
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jeseci_learning_academy
POSTGRES_USER=jeseci_academy_user
POSTGRES_PASSWORD=jeseci_secure_password_2024
DB_SCHEMA=jeseci_academy
```

### Graph Database (Neo4j)
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_secure_password_2024
NEO4J_DATABASE=neo4j
```

### AI Configuration
```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-LXc5F7IW85GHT3HZNyHSGZRYNTr1QYt8vYYBdb7Zs9rrktkh4-7MO6NtEJooM-zthkBK@e@dUh7T3B1bkFIECKZ19FrILZ1pAl111£q9x__v9gx1jDxcHDMmZbmtJ4280zWIMd93psyket@zTRUT2FeNHSgUA

# Gemini API Key
GEMINI_API_KEY=ATzaSyBLv9eN8zNSUkSEm7xnAmG1abUotDX3420

# Google API Key
GOOGLE_API_KEY=AIzaSyB3OhghL8KcNaixdZkM4Wfd07_dAoQvrI0

# LLM Provider Selection
LLM_PROVIDER=openai
```

### Contact Form Configuration
```env
VITE_CONTACT_FALLBACK_MODE=true
VITE_DEBUG_MODE=true
VITE_API_BASE_URL=http://localhost:8000
```

### Security Configuration
```env
JWT_SECRET_KEY=jeseci_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_KEY=jeseci_admin_key_2024
```

### CORS Configuration
```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOWED_HEADERS=Content-Type,Authorization,X-Requested-With
```

## Configuration Consistency

### Database Schema Alignment
Both frontend and backend use the same PostgreSQL configuration:
- **Database Name**: `jeseci_learning_academy`
- **User**: `jeseci_academy_user`
- **Schema**: `jeseci_academy`
- **Password**: `jeseci_secure_password_2024`

### API Endpoints
- **Frontend API Base**: `http://localhost:8000`
- **Backend Host**: `0.0.0.0`
- **Backend Port**: `8000`

### Environment Settings
- **Environment**: `development`
- **Debug Mode**: `true`
- **Node Environment**: `production` (for frontend build optimization)

## Service Integration

### OpenAI Service
- Uses `import.meta.env.OPENAI_API_KEY` for configuration
- Falls back gracefully if API key is not available
- Supports environment-based API key rotation

### Contact Service
- Uses `import.meta.env.VITE_API_BASE_URL` for backend communication
- Supports fallback mode for offline/demo functionality
- Debug logging controlled by `VITE_DEBUG_MODE`

### Database Integration
- PostgreSQL for primary data storage
- Neo4j for graph-based learning paths and recommendations
- Connection pooling configured for optimal performance

## Security Considerations

### API Keys
- OpenAI API key configured for production use
- Gemini and Google API keys available for multi-provider support
- Admin credentials properly configured for email notifications

### Database Security
- Strong password policies implemented
- Connection pooling with timeout settings
- Schema-based access control

### JWT Configuration
- Secure secret key configured
- 30-minute token expiration
- HS256 algorithm for signing

## Deployment Notes

### Frontend Build
- Environment variables prefixed with `VITE_` are accessible in the browser build
- API keys are embedded in the build (consider server-side implementation for sensitive data)
- Debug mode should be disabled in production

### Backend Deployment
- All configuration must be available as environment variables
- Database connections should be tested before deployment
- Email service requires proper SMTP configuration

## Troubleshooting

### Common Issues
1. **Database Connection**: Verify PostgreSQL and Neo4j services are running
2. **Email Delivery**: Check SMTP credentials and server accessibility
3. **API Keys**: Ensure all required API keys are properly configured
4. **CORS**: Verify allowed origins include your frontend domain

### Environment Variable Validation
All services include startup validation for required environment variables and will log warnings if critical variables are missing.

## Configuration Management

### Development
1. Copy `.env.example` to `.env` in both frontend and backend directories
2. Update values according to your local environment
3. Ensure database services are running
4. Test email configuration with a test submission

### Production
1. Use environment variables (not .env files) in production
2. Disable debug modes
3. Use strong, unique passwords and keys
4. Implement proper SSL/TLS for database connections
5. Set up monitoring for API key usage and email delivery

## Next Steps

1. **Database Setup**: Initialize PostgreSQL and Neo4j databases with provided schema
2. **Email Testing**: Verify SMTP configuration with test emails
3. **API Testing**: Test all endpoints with Postman or similar tools
4. **Integration Testing**: Verify frontend-backend communication
5. **Security Review**: Conduct security audit before production deployment