#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import argparse
import json
import os
import sys
import subprocess
import random
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(Path.home() / '.env')
except ImportError:
    pass  # dotenv is optional


def get_tts_script_path():
    """
    Get the cached TTS script path.
    Uses cached audio files when available to save API costs and reduce latency.
    """
    # Get current script directory and construct utils/tts path
    script_dir = Path(__file__).parent
    tts_dir = script_dir / "utils" / "tts"

    # Use cached TTS wrapper (supports all TTS backends with caching)
    cached_tts_script = tts_dir / "cached_tts.py"
    if cached_tts_script.exists():
        return str(cached_tts_script)

    # Fallback to non-cached scripts if cached_tts doesn't exist
    # Check for ElevenLabs API key (highest priority)
    if os.getenv('ELEVENLABS_API_KEY'):
        elevenlabs_script = tts_dir / "elevenlabs_tts.py"
        if elevenlabs_script.exists():
            return str(elevenlabs_script)

    # Check for OpenAI API key (second priority)
    if os.getenv('OPENAI_API_KEY'):
        openai_script = tts_dir / "openai_tts.py"
        if openai_script.exists():
            return str(openai_script)

    # Fall back to system voice (no API key required)
    system_voice_script = tts_dir / "system_voice_tts.py"
    if system_voice_script.exists():
        return str(system_voice_script)

    return None


def announce_notification():
    """Announce that the agent needs user input. Returns TTS metadata dict."""
    tts_metadata = {
        "tts_triggered": False,
        "message": None,
        "personalized": False
    }

    try:
        tts_script = get_tts_script_path()
        if not tts_script:
            return tts_metadata  # No TTS scripts available

        # Get engineer name if available, fallback to USER
        engineer_name = os.getenv('ENGINEER_NAME', '').strip()
        if not engineer_name:
            engineer_name = os.getenv('USER', '').strip()

        # Create notification message with 30% chance to include name
        personalized = engineer_name and random.random() < 0.3
        if personalized:
            notification_message = f"{engineer_name}, your agent needs your input"
        else:
            notification_message = "Your agent needs your input"

        tts_metadata["message"] = notification_message
        tts_metadata["personalized"] = personalized
        tts_metadata["tts_triggered"] = True

        # Call the TTS script with the notification message and capture metadata
        result = subprocess.run([
            "python3", tts_script, notification_message, "--json"
        ],
        capture_output=True,
        text=True,
        timeout=10
        )

        # Parse TTS backend metadata if available
        if result.returncode == 0 and result.stdout.strip():
            try:
                tts_details = json.loads(result.stdout.strip())
                tts_metadata.update(tts_details)
            except json.JSONDecodeError:
                pass

    except subprocess.TimeoutExpired:
        tts_metadata["error"] = "TTS timeout"
    except FileNotFoundError as e:
        tts_metadata["error"] = f"TTS script not found: {type(e).__name__}"
    except subprocess.SubprocessError as e:
        tts_metadata["error"] = f"TTS subprocess error: {type(e).__name__}"
    except Exception as e:
        tts_metadata["error"] = f"Unexpected error: {type(e).__name__}"

    return tts_metadata


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--notify', action='store_true', help='Enable TTS notifications')
        args = parser.parse_args()
        
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        # Ensure log directory exists relative to this script
        script_dir = Path(__file__).parent
        log_dir = script_dir / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'notification.json'
        
        # Read existing log data or initialize empty list
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        # Append new data with timestamp
        input_data['timestamp'] = datetime.now().isoformat()

        # Announce notification via TTS only if --notify flag is set
        # Skip TTS for the generic "Claude is waiting for your input" message
        if args.notify and input_data.get('message') != 'Claude is waiting for your input':
            tts_metadata = announce_notification()
            input_data['tts_metadata'] = tts_metadata

        log_data.append(input_data)

        # Write back to file with formatting
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)

if __name__ == '__main__':
    main()