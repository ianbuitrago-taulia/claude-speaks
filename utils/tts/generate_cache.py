#!/usr/bin/env python3
"""
Pre-generate cached audio files for all known TTS messages.
This saves API costs and reduces latency for common notifications.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path to import cached_tts
sys.path.insert(0, str(Path(__file__).parent))
from cached_tts import speak_with_cache, get_cached_audio_path


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
    """Generate cache files for all messages."""
    messages = get_all_messages()

    print("🎵 TTS Cache Generator")
    print("=" * 50)
    print(f"Generating cache for {len(messages)} messages...\n")

    success_count = 0
    skip_count = 0
    fail_count = 0

    for i, message in enumerate(messages, 1):
        cached_path = get_cached_audio_path(message)

        # Check if already cached
        if cached_path.exists():
            print(f"[{i}/{len(messages)}] ⏭️  CACHED: {message}")
            skip_count += 1
            continue

        print(f"[{i}/{len(messages)}] 🔊 Generating: {message}")

        # Generate and cache
        if speak_with_cache(message):
            # Verify cache was created
            if cached_path.exists():
                size_kb = cached_path.stat().st_size / 1024
                print(f"            ✅ Cached ({size_kb:.1f} KB): {cached_path.name}")
                success_count += 1
            else:
                print(f"            ⚠️  Generated but not cached (non-ElevenLabs TTS)")
                success_count += 1
        else:
            print(f"            ❌ Failed to generate")
            fail_count += 1

    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"   ✅ Generated: {success_count}")
    print(f"   ⏭️  Skipped (already cached): {skip_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   📁 Cache location: {get_cached_audio_path('').parent}")

    if fail_count > 0:
        print("\n⚠️  Some messages failed. Check your API keys:")
        print("   - ELEVENLABS_API_KEY (for caching support)")
        print("   - OPENAI_API_KEY (fallback, no caching)")

    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
