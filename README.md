# Pomodoro CLI Timer

A full-screen terminal countdown timer with ASCII banner display.

<img width="1364" height="486" alt="image" src="https://github.com/user-attachments/assets/417094ca-1e82-4de3-bb9b-61120d2805cf" />

## Usage

```bash
# Start a 25-minute timer (default)
python3 pomodoro.py

# Custom durations
python3 pomodoro.py 45        # 45 minutes
python3 pomodoro.py 1h30m     # 1 hour 30 minutes

# Check/reset today's count
python3 pomodoro.py --status
python3 pomodoro.py --reset

# View statistics
python3 pomodoro.py --stats              # All-time stats
python3 pomodoro.py --stats today        # Today's stats
python3 pomodoro.py --stats week         # Last 7 days
python3 pomodoro.py --stats month        # Last 30 days
python3 pomodoro.py --stats 2025-01-01:2025-01-31   # Custom date range
```

## Features

- Full-screen ASCII time display
- Daily pomodoro count tracking (stored in `~/.pomodoro/`)
- Restart or quit prompt when timer ends
- Statistics with total pomodoros, time spent, days active, and daily average
