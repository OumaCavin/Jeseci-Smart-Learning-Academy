# How to Access Backend Terminal Logs

## Method 1: Direct Terminal Output (Recommended for Development)

### Run Backend Server:
```bash
cd /workspace
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Output will appear directly in your terminal:**
```
INFO: Started server process [12345]
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

🔄 Updating progress for concept: 01b94ca2-...
📊 Update data received: time_spent_minutes=15, progress_percent=100, status='completed'
✅ Progress updated successfully: completed, time_spent_minutes: 15

📊 Found 1 progress records for user: user_123
```

## Method 2: Save Logs to File

### Run with Log Redirection:
```bash
cd /workspace
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend_logs.txt 2>&1 &
```

**View logs in real-time:**
```bash
tail -f backend_logs.txt
```

**Or view all logs:**
```bash
cat backend_logs.txt
```

## Method 3: Background Process with Output Capture

### Start Backend in Background:
```bash
cd /workspace
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend_logs.txt 2>&1 &
```

### View Logs:
```bash
# Real-time following
tail -f backend_logs.txt

# Last 50 lines
tail -50 backend_logs.txt

# Search for specific debug messages
grep "📊" backend_logs.txt
```

## Method 4: Using tmux/screen for Session Management

### Using tmux:
```bash
# Create named session
tmux new -s backend_logs

# Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Detach from session: Ctrl+B then D
# Reattach: tmux attach -t backend_logs
```

### Using screen:
```bash
# Create named screen session
screen -S backend_logs

# Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Detach: Ctrl+A then D
# Reattach: screen -r backend_logs
```

## Debug Messages to Look For

### Progress Update Logs:
```
🔄 Updating progress for concept: [concept_id]
📊 Update data received: time_spent_minutes=15, progress_percent=100, status='completed'
✅ Progress updated successfully: completed, time_spent_minutes: 15
```

### Dashboard Load Logs:
```
📊 Found 1 progress records for user: [user_id]
```

### Error Messages:
```
❌ Concept not found
❌ Failed to generate lesson for [concept_name]: [error]
```

## Quick Testing Commands

### 1. Start Backend with File Logging:
```bash
cd /workspace
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > logs.txt 2>&1 &
echo "Backend started with logging to logs.txt"
```

### 2. Test Progress Update:
1. Open frontend in browser
2. Complete an AI lesson
3. Check logs: `tail -20 logs.txt`

### 3. Test Dashboard:
1. Refresh dashboard page
2. Check logs: `tail -10 logs.txt`

## Troubleshooting

### If No Logs Appear:
1. **Check if backend is running**: `ps aux | grep uvicorn`
2. **Check port availability**: `netstat -tulpn | grep 8000`
3. **Check for syntax errors**: `python -m py_compile main.py`

### If Logs Show "Found 0 progress records":
- User hasn't completed any lessons yet
- Database connection issue
- Progress update failed (check earlier logs)

### If No Debug Messages:
- Backend might not be reloading properly
- Check for import errors in progress.py
- Restart backend completely

## Log File Locations

### Default:
- **Terminal**: Direct output in terminal window
- **File**: `backend_logs.txt`, `logs.txt`, or whatever filename you specify

### System Logs (if running as service):
- **Linux**: `/var/log/syslog` or `/var/log/messages`
- **macOS**: Console.app or `log show`

## Best Practices for Log Management

1. **Development**: Use direct terminal output for immediate feedback
2. **Testing**: Save to file for post-analysis
3. **Production**: Use structured logging to files with rotation
4. **Debugging**: Use grep to filter specific messages
5. **Monitoring**: Set up log alerts for error messages

## Quick Commands Summary

```bash
# Start with file logging
uvicorn main:app --reload > logs.txt 2>&1 &

# View real-time logs
tail -f logs.txt

# Search for progress messages
grep "📊" logs.txt

# View last 50 lines
tail -50 logs.txt

# Clear log file
> logs.txt

# Stop backend process
pkill -f uvicorn
```