#!/usr/bin/env python3
"""
Check and play all cached TTS messages.
Shows which messages are cached and plays each one.
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path to import cached_tts
sys.path.insert(0, str(Path(__file__).parent))
from cached_tts import get_cached_audio_path, play_audio, speak_with_cache


def get_all_messages():
    """Return all static messages used in Claude hooks."""
    messages = []

    # Messages from notification.py
    messages.append("Your agent needs your input")

    # Messages from stop.py (completion messages)
    messages.extend([
        "Work complete!",
        "All done!",
        "Task finished!",
        "Job complete!",
        "Ready for next task!",
        "Mission accomplished!",
        "Task complete!",
        "Finished successfully!",
        "All set!",
        "Done and dusted!",
        "Wrapped up!",
        "Job well done!",
        "That's a wrap!",
        "Successfully completed!",
        "All finished!",
        "Task accomplished!",
        "Good to go!",
        "Completed successfully!",
        "Everything's done!",
        "Ready when you are!"
    ])

    # Get engineer name if available for personalized message, fallback to USER
    engineer_name = os.getenv('ENGINEER_NAME', '').strip()
    if not engineer_name:
        engineer_name = os.getenv('USER', '').strip()
    if engineer_name:
        messages.append(f"{engineer_name}, your agent needs your input")

    return messages


def main():
    """Check and play all cached messages."""
    messages = get_all_messages()

    print("🎵 TTS Cache Checker & Player")
    print("=" * 60)
    print(f"Checking {len(messages)} messages...\n")

    for i, message in enumerate(messages, 1):
        cached_path = get_cached_audio_path(message)
        is_cached = cached_path.exists()

        # Status indicator
        status = "✅ CACHED" if is_cached else "❌ NOT CACHED"

        print(f"[{i}/{len(messages)}] {status}: {message}")

        if is_cached:
            size_kb = cached_path.stat().st_size / 1024
            print(f"         📁 File: {cached_path.name} ({size_kb:.1f} KB)")
            print(f"         🔊 Playing...")

            # Play the cached audio
            if play_audio(cached_path):
                print(f"         ✓ Playback complete")
            else:
                print(f"         ⚠️  Playback failed (no audio player available)")
        else:
            print(f"         ⚠️  Not in cache, would require API call")

        print()

        # Small delay between messages for better UX
        if i < len(messages):
            time.sleep(1)

    print("=" * 60)
    print("🏁 Done checking and playing all messages!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
