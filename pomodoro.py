#!/usr/bin/env python3
"""
Pomodoro CLI Timer - A full-screen terminal countdown timer with ASCII banner display.
"""

import argparse
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

# ASCII art digits (5 lines tall, variable width)
DIGITS = {
    '0': [
        " ███ ",
        "█   █",
        "█   █",
        "█   █",
        " ███ ",
    ],
    '1': [
        "  █  ",
        " ██  ",
        "  █  ",
        "  █  ",
        " ███ ",
    ],
    '2': [
        " ███ ",
        "█   █",
        "  ██ ",
        " █   ",
        "█████",
    ],
    '3': [
        " ███ ",
        "█   █",
        "  ██ ",
        "█   █",
        " ███ ",
    ],
    '4': [
        "█   █",
        "█   █",
        "█████",
        "    █",
        "    █",
    ],
    '5': [
        "█████",
        "█    ",
        "████ ",
        "    █",
        "████ ",
    ],
    '6': [
        " ███ ",
        "█    ",
        "████ ",
        "█   █",
        " ███ ",
    ],
    '7': [
        "█████",
        "    █",
        "   █ ",
        "  █  ",
        "  █  ",
    ],
    '8': [
        " ███ ",
        "█   █",
        " ███ ",
        "█   █",
        " ███ ",
    ],
    '9': [
        " ███ ",
        "█   █",
        " ████",
        "    █",
        " ███ ",
    ],
    ':': [
        "     ",
        "  █  ",
        "     ",
        "  █  ",
        "     ",
    ],
}

DIGIT_HEIGHT = 5
DIGIT_WIDTH = 5
COLON_WIDTH = 5


def get_terminal_size():
    """Get the current terminal size."""
    try:
        columns, lines = os.get_terminal_size()
    except OSError:
        columns, lines = 80, 24
    return columns, lines


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_time(seconds):
    """Convert seconds to MM:SS format."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def build_banner(time_str):
    """Build the ASCII banner for the given time string."""
    lines = [[] for _ in range(DIGIT_HEIGHT)]

    for char in time_str:
        digit_art = DIGITS.get(char, DIGITS['0'])
        for i, line in enumerate(digit_art):
            lines[i].append(line)

    # Join each line with a space between digits
    return [" ".join(line_parts) for line_parts in lines]


def center_banner(banner_lines, term_width, term_height):
    """Center the banner in the terminal."""
    banner_width = len(banner_lines[0]) if banner_lines else 0
    banner_height = len(banner_lines)

    # Calculate padding
    left_pad = max(0, (term_width - banner_width) // 2)
    top_pad = max(0, (term_height - banner_height) // 2)

    # Build centered output
    output = []

    # Top padding
    for _ in range(top_pad):
        output.append("")

    # Banner lines with horizontal centering
    for line in banner_lines:
        output.append(" " * left_pad + line)

    return "\n".join(output)


def display_timer(seconds_remaining, pomodoro_count):
    """Display the timer banner."""
    clear_screen()

    term_width, term_height = get_terminal_size()
    time_str = format_time(seconds_remaining)
    banner_lines = build_banner(time_str)

    # Add pomodoro count below the timer
    count_text = f"🍅 Pomodoros today: {pomodoro_count}"

    # Calculate banner width for centering the count text
    banner_width = len(banner_lines[0]) if banner_lines else 0
    left_pad = max(0, (term_width - banner_width) // 2)
    count_left_pad = max(0, (term_width - len(count_text)) // 2)

    # Adjust for count text
    banner_lines.append("")  # Empty line
    banner_lines.append(" " * (count_left_pad - left_pad) + count_text if count_left_pad > left_pad else count_text)

    centered_banner = center_banner(banner_lines[:-2], term_width, term_height - 2)

    # Print banner
    print(centered_banner)

    # Print the count at a fixed position
    remaining_lines = term_height - centered_banner.count('\n') - DIGIT_HEIGHT - 3
    if remaining_lines > 0:
        print("\n" * min(2, remaining_lines), end="")
    print(" " * count_left_pad + count_text)


def get_session_file():
    """Get the path to today's session file."""
    data_dir = Path.home() / ".pomodoro"
    data_dir.mkdir(exist_ok=True)
    return data_dir / f"sessions_{date.today().isoformat()}.txt"


def load_pomodoro_count():
    """Load today's pomodoro count from file."""
    session_file = get_session_file()
    if session_file.exists():
        try:
            return int(session_file.read_text().strip())
        except (ValueError, IOError):
            return 0
    return 0


def save_pomodoro_count(count):
    """Save today's pomodoro count to file."""
    session_file = get_session_file()
    session_file.write_text(str(count))


def get_data_dir():
    """Get the pomodoro data directory."""
    return Path.home() / ".pomodoro"


def load_all_sessions():
    """Load all session files and return a dict of date -> count."""
    data_dir = get_data_dir()
    sessions = {}

    if not data_dir.exists():
        return sessions

    for session_file in data_dir.glob("sessions_*.txt"):
        try:
            # Extract date from filename: sessions_YYYY-MM-DD.txt
            date_str = session_file.stem.replace("sessions_", "")
            session_date = date.fromisoformat(date_str)
            count = int(session_file.read_text().strip())
            sessions[session_date] = count
        except (ValueError, IOError):
            continue

    return sessions


def calculate_stats(start_date=None, end_date=None):
    """
    Calculate pomodoro statistics for a date range.

    Args:
        start_date: Start date (inclusive). None means from the beginning.
        end_date: End date (inclusive). None means until today.

    Returns:
        dict with total_pomodoros, total_minutes, days_active, daily_average
    """
    sessions = load_all_sessions()

    if not sessions:
        return {
            "total_pomodoros": 0,
            "total_minutes": 0,
            "days_active": 0,
            "daily_average": 0.0,
            "start_date": start_date,
            "end_date": end_date,
        }

    # Filter by date range
    if end_date is None:
        end_date = date.today()

    filtered_sessions = {
        d: count for d, count in sessions.items()
        if (start_date is None or d >= start_date) and d <= end_date
    }

    total_pomodoros = sum(filtered_sessions.values())
    days_active = len(filtered_sessions)
    daily_average = total_pomodoros / days_active if days_active > 0 else 0.0

    # Assume default 25 minutes per pomodoro
    total_minutes = total_pomodoros * 25

    return {
        "total_pomodoros": total_pomodoros,
        "total_minutes": total_minutes,
        "days_active": days_active,
        "daily_average": daily_average,
        "start_date": start_date,
        "end_date": end_date,
    }


def format_duration(minutes):
    """Format minutes as hours and minutes string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def display_stats(period="all"):
    """Display pomodoro statistics for the given period."""
    today = date.today()

    if period == "today":
        start_date = today
        period_name = "Today"
    elif period == "week":
        start_date = today - timedelta(days=6)
        period_name = "Last 7 days"
    elif period == "month":
        start_date = today - timedelta(days=29)
        period_name = "Last 30 days"
    elif period == "all":
        start_date = None
        period_name = "All time"
    else:
        # Assume it's a custom date range in format "YYYY-MM-DD:YYYY-MM-DD"
        try:
            parts = period.split(":")
            if len(parts) == 2:
                start_date = date.fromisoformat(parts[0])
                end_date = date.fromisoformat(parts[1])
                period_name = f"{parts[0]} to {parts[1]}"
                stats = calculate_stats(start_date, end_date)
            else:
                print(f"Invalid date range format: {period}")
                print("Use format: YYYY-MM-DD:YYYY-MM-DD")
                return
        except ValueError as e:
            print(f"Invalid date format: {e}")
            print("Use format: YYYY-MM-DD:YYYY-MM-DD")
            return

    if period != "all" and ":" not in period:
        stats = calculate_stats(start_date, today)
    elif period == "all":
        stats = calculate_stats(None, today)

    # Display statistics
    print(f"\n🍅 Pomodoro Statistics - {period_name}")
    print("=" * 40)
    print(f"  Total pomodoros:  {stats['total_pomodoros']}")
    print(f"  Total time:       {format_duration(stats['total_minutes'])}")
    print(f"  Days active:      {stats['days_active']}")
    print(f"  Daily average:    {stats['daily_average']:.1f} pomodoros")
    print("=" * 40)
    print()


def run_timer(duration_minutes):
    """Run the pomodoro timer."""
    pomodoro_count = load_pomodoro_count()
    seconds_remaining = duration_minutes * 60

    try:
        while seconds_remaining >= 0:
            display_timer(seconds_remaining, pomodoro_count)

            if seconds_remaining == 0:
                break

            time.sleep(1)
            seconds_remaining -= 1

        # Timer completed
        pomodoro_count += 1
        save_pomodoro_count(pomodoro_count)

        # Show completion message
        clear_screen()
        term_width, term_height = get_terminal_size()

        completion_msg = [
            "⏰ TIME'S UP! ⏰",
            "",
            f"🍅 Pomodoros completed today: {pomodoro_count}",
            "",
            "What would you like to do?",
            "",
            "[r] Start another pomodoro",
            "[q] Quit",
        ]

        # Center the completion message
        top_pad = max(0, (term_height - len(completion_msg)) // 2)
        print("\n" * top_pad)

        for line in completion_msg:
            left_pad = max(0, (term_width - len(line)) // 2)
            print(" " * left_pad + line)

        # Wait for user input
        while True:
            try:
                choice = input("\n" + " " * ((term_width - 20) // 2) + "Your choice: ").strip().lower()
                if choice == 'r':
                    run_timer(duration_minutes)
                    break
                elif choice == 'q':
                    clear_screen()
                    print(f"\n🍅 Great work! You completed {pomodoro_count} pomodoro(s) today.\n")
                    break
                else:
                    print(" " * ((term_width - 30) // 2) + "Please enter 'r' or 'q'")
            except EOFError:
                break

    except KeyboardInterrupt:
        clear_screen()
        print(f"\n🍅 Session interrupted. Pomodoros completed today: {pomodoro_count}\n")
        sys.exit(0)


def parse_duration(duration_str):
    """Parse duration string (e.g., '25', '25m', '1h30m', '90s')."""
    duration_str = duration_str.strip().lower()

    # Check for simple number (assume minutes)
    if duration_str.isdigit():
        return int(duration_str)

    total_minutes = 0
    current_num = ""

    for char in duration_str:
        if char.isdigit():
            current_num += char
        elif char == 'h' and current_num:
            total_minutes += int(current_num) * 60
            current_num = ""
        elif char == 'm' and current_num:
            total_minutes += int(current_num)
            current_num = ""
        elif char == 's' and current_num:
            total_minutes += int(current_num) / 60
            current_num = ""

    # Handle remaining number (assume minutes if no suffix)
    if current_num:
        total_minutes += int(current_num)

    return max(1, int(total_minutes))


def main():
    parser = argparse.ArgumentParser(
        description="🍅 Pomodoro CLI Timer - A full-screen countdown timer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pomodoro 25        Start a 25-minute timer
  pomodoro 25m       Start a 25-minute timer
  pomodoro 1h        Start a 1-hour timer
  pomodoro 1h30m     Start a 1 hour 30 minute timer
  pomodoro 90s       Start a 90-second timer (rounded to 2 minutes)

Statistics:
  pomodoro --stats              Show all-time statistics
  pomodoro --stats today        Show today's statistics
  pomodoro --stats week         Show last 7 days statistics
  pomodoro --stats month        Show last 30 days statistics
  pomodoro --stats 2025-01-01:2025-01-31   Custom date range
        """
    )

    parser.add_argument(
        "duration",
        nargs="?",
        default="25",
        help="Timer duration (default: 25 minutes). Examples: 25, 25m, 1h, 1h30m"
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset today's pomodoro count"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Show today's pomodoro count and exit"
    )

    parser.add_argument(
        "--stats",
        nargs="?",
        const="all",
        metavar="PERIOD",
        help="Show statistics. PERIOD: today, week, month, all (default), or YYYY-MM-DD:YYYY-MM-DD"
    )

    args = parser.parse_args()

    if args.reset:
        save_pomodoro_count(0)
        print("🍅 Today's pomodoro count has been reset to 0.")
        return

    if args.status:
        count = load_pomodoro_count()
        print(f"🍅 Pomodoros completed today: {count}")
        return

    if args.stats is not None:
        display_stats(args.stats)
        return

    duration = parse_duration(args.duration)
    print(f"🍅 Starting {duration}-minute pomodoro timer...")
    time.sleep(1)

    run_timer(duration)


if __name__ == "__main__":
    main()
