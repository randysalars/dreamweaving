# RAG File Watcher Fixes - 2025-12-15

## Problem Summary

The RAG file watcher (PID 198399) was consuming 989% CPU and had been running for ~7 hours in an infinite retry loop, creating a 30MB log file.

### Root Causes

1. **Qdrant Vector DB Lock Conflict** (Primary)
   - Another Qdrant client had the vector DB locked
   - Error: `Storage folder knowledge/vector_db is already accessed by another instance`
   - Watcher kept retrying indefinitely

2. **Notion API Rate Limiting** (Secondary)
   - Frequent exports triggered Notion API rate limits
   - Error: `You have been rate limited. Please try again in a few minutes.`
   - No backoff mechanism to handle rate limits

3. **No Failure Limits** (Fatal Design Flaw)
   - No maximum retry limit
   - No exponential backoff between retries
   - Continued processing embeddings in a loop for hours
   - CPU spiked to 989% (10 cores)

## Implemented Fixes

### 1. File Watcher (`scripts/ai/rag_file_watcher.py`)

**Added Retry Limits:**
- `MAX_CONSECUTIVE_FAILURES = 3` - Stop after 3 consecutive failures
- Process stops accepting new re-index requests after max failures
- Requires manual restart after fixing underlying issues

**Added Exponential Backoff:**
- `MIN_RETRY_DELAY_SECONDS = 60` - Start with 1 minute delay
- `MAX_RETRY_DELAY_SECONDS = 3600` - Max 1 hour delay
- Doubles delay after each failure: 60s → 120s → 240s → ...
- Resets to minimum on successful re-index

**Enhanced Error Handling:**
- Detects specific error types (DB lock, rate limits)
- Provides actionable error messages
- Re-adds changes to pending queue for retry
- Distinguishes between failures and "skipped" (no changes)

**New State Tracking:**
```python
self.consecutive_failures = 0
self.last_failure_time: Optional[datetime] = None
self.current_backoff_seconds = MIN_RETRY_DELAY_SECONDS
```

### 2. Auto Sync Module (`scripts/ai/rag_auto_sync.py`)

**Added Rate Limiting:**
- `MIN_EXPORT_INTERVAL_SECONDS = 300` - Minimum 5 minutes between Notion exports
- Checks last export time before making API calls
- Saves `last_export` timestamp in sync state
- Provides clear wait time in warning messages

**Enhanced Notion Export:**
- Optional `skip_rate_limit_check` parameter for forced syncs
- Specific error handling for rate limit errors
- Updates state file after successful export
- Guidance to increase interval if rate limits persist

### 3. Log Management

**Rotated Large Log:**
- Moved 30MB `rag_watcher.log` to `rag_watcher.log.old`
- Created fresh log file
- Prevents disk space issues

## How the Fixes Work

### Scenario: DB Lock Error

1. Watcher detects file changes
2. Attempts re-index → DB locked error
3. **NEW:** Increments `consecutive_failures` to 1
4. **NEW:** Waits 60 seconds (backoff)
5. Retries → Still locked
6. **NEW:** Increments to 2, waits 120 seconds
7. Retries → Still locked
8. **NEW:** Increments to 3, waits 240 seconds
9. Retries → Still locked
10. **NEW:** Reaches MAX_FAILURES, stops processing
11. **NEW:** Logs: "Manual intervention required. Restart watcher after fixing issues."

### Scenario: Notion Rate Limit

1. Watcher detects changes, needs Notion export
2. Checks last export: 2 minutes ago
3. **NEW:** Skips export (< 5 min threshold)
4. **NEW:** Logs: "Rate limit: Last export was 120s ago. Minimum interval is 300s. Skipping export (retry in 180s)."
5. Avoids API call, prevents rate limit error

### Scenario: Successful Re-index

1. Re-index completes successfully
2. **NEW:** Resets `consecutive_failures = 0`
3. **NEW:** Resets `last_failure_time = None`
4. **NEW:** Resets `current_backoff_seconds = 60`
5. Ready for next changes without delay

## Testing

Verified that:
- ✅ Python files compile without syntax errors
- ✅ Watcher starts in test mode
- ✅ Watcher responds to shutdown signals
- ✅ Both modules are syntactically valid

## Usage

### Start Watcher with Fixes
```bash
./venv/bin/python3 scripts/ai/rag_file_watcher.py
```

### Test Mode (No Re-indexing)
```bash
./venv/bin/python3 scripts/ai/rag_file_watcher.py --test
```

### Monitor Status
```bash
# Check if watcher is running
ps aux | grep rag_file_watcher

# View live logs
tail -f logs/rag_watcher.log

# Check for failures
grep -E "ERROR|WARNING|Failure" logs/rag_watcher.log | tail -20
```

### After Fixing Issues
If watcher reaches max failures:
1. Fix the underlying issue (DB lock, rate limits, etc.)
2. Restart the watcher process
3. Failure counters reset on restart

## Recommendations for Future

### 1. Use Qdrant Server (High Priority)
Replace file-based Qdrant with server mode to support concurrent access:
```bash
docker run -p 6333:6333 qdrant/qdrant
```
Update embedding pipeline to connect to `http://localhost:6333`

### 2. Increase Rate Limit Interval
If rate limits persist, increase in `rag_auto_sync.py`:
```python
MIN_EXPORT_INTERVAL_SECONDS = 600  # 10 minutes
```

### 3. Add Prometheus Metrics
Track:
- `rag_watcher_failures_total`
- `rag_watcher_reindex_duration_seconds`
- `rag_notion_export_rate_limits_total`

### 4. Log Rotation
Add logrotate config:
```
/home/rsalars/Projects/dreamweaving/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    size 10M
}
```

## Related Files

- `scripts/ai/rag_file_watcher.py` - Main watcher with retry/backoff
- `scripts/ai/rag_auto_sync.py` - Sync manager with rate limiting
- `scripts/ai/rag_polling_monitor.py` - Separate polling service (still running)
- `scripts/scheduling/rag-watcher.service` - Systemd service definition
- `logs/rag_watcher.log` - Active log file
- `logs/rag_watcher.log.old` - 30MB old log from infinite loop

## Lessons Learned

1. **Always add retry limits** - Infinite retries can consume all system resources
2. **Implement exponential backoff** - Prevents thundering herd, gives systems time to recover
3. **Respect API rate limits** - Track last call time, enforce minimum intervals
4. **Provide actionable errors** - Tell users exactly what's wrong and how to fix it
5. **Monitor log sizes** - 30MB of progress bars is a clear sign of runaway process
6. **Test error paths** - Happy path works, but error handling is where bugs hide
