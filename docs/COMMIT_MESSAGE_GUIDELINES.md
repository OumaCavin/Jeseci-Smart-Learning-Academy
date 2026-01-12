# Git Commit Message Guidelines

## Format

```
<type>(<scope>): <subject>

- Detailed changes
- More details if needed
```

## Types

- **feat** - A new feature
- **fix** - A bug fix
- **docs** - Documentation only changes
- **style** - Changes that do not affect the meaning of the code (white-space, formatting, etc)
- **refactor** - A code change that neither fixes a bug nor adds a feature
- **perf** - A code change that improves performance
- **test** - Adding missing tests or correcting existing tests
- **chore** - Changes to the build process or auxiliary tools

## Scope

Common scopes:
- **frontend** - Frontend React/TypeScript code
- **backend** - Backend Python/JAC code
- **admin** - Admin panel functionality
- **auth** - Authentication and authorization
- **database** - Database operations
- **api** - API endpoints
- **ui** - User interface components
- **docs** - Documentation
- **jac** - Jaclang walker/node definitions

## Examples

### Good Commit Messages
```
feat(admin): add user management dashboard

- Add user list view with pagination
- Implement user search functionality
- Add role-based access control

fix(auth): resolve token expiration issue

- Extend token validity period
- Add refresh token mechanism

docs(api): update endpoint documentation

- Add missing API endpoint descriptions
- Update request/response examples
```

### Bad Commit Messages
```
Message 355017033945196 - 1768227572  ❌
Fixed bug                                     ❌
Update code                                   ❌
```

## Template

Save this as `.gitmessage` in your repository root:

```
<type>(<scope>): <subject>

- Detailed changes
- More details if needed
```

## Using the Template

```bash
# Set as default commit message template
git config commit.template .gitmessage

# Or use when committing
git commit -t .gitmessage
```

## Best Practices

1. Use imperative mood ("add feature" not "added feature")
2. First line should be 50 characters or less
3. Separate subject from body with a blank line
4. Body should explain what and why, not how
5. Reference issues when relevant (e.g., "Fixes #123")
