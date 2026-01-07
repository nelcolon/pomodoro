# Pomodoro CLI Timer

A full-screen terminal countdown timer with ASCII banner display.

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
```

## Features

- Full-screen ASCII time display
- Daily pomodoro count tracking (stored in `~/.pomodoro/`)
- Restart or quit prompt when timer ends
