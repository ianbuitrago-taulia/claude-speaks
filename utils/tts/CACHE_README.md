# TTS Cache System

## Overview

The TTS cache system stores pre-generated audio files for common messages to:
- **Reduce API costs** by reusing audio files instead of regenerating them
- **Improve latency** with instant playback from cached files
- **Ensure reliability** by having audio ready even during API issues

## How It Works

1. **Caching Wrapper** (`cached_tts.py`):
   - Generates MD5 hash of message text as cache key
   - Checks if cached MP3 exists before calling API
   - Falls back to regular TTS if cache not available

2. **Cache Storage**:
   - Location: `~/.claude/hooks/utils/tts/cache/`
   - Format: `{md5_hash}.mp3`
   - Only ElevenLabs TTS supports caching (returns MP3 data)

3. **Pre-generated Messages**:
   - "Your agent needs your input"
   - "Work complete!"
   - "All done!"
   - "Task finished!"
   - "Job complete!"
   - "Ready for next task!"

## Files

- **cached_tts.py**: Main caching wrapper script
- **generate_cache.py**: Pre-generates cache for all known messages
- **cache/**: Directory containing cached MP3 files

## Usage

### Play Cached TTS
```bash
python3 ~/.claude/hooks/utils/tts/cached_tts.py "Your message here"
```

### Regenerate Cache
```bash
python3 ~/.claude/hooks/utils/tts/generate_cache.py
```

### View Cached Files
```bash
ls -lh ~/.claude/hooks/utils/tts/cache/
```

### Clear Cache
```bash
rm -f ~/.claude/hooks/utils/tts/cache/*.mp3
```

## Integration

Both `notification.py` and `stop.py` hooks automatically use the cached TTS system.
The hooks prioritize `cached_tts.py` and fall back to direct TTS scripts if unavailable.

## Benefits

- **API Cost Savings**: Common messages play from cache, no API calls needed
- **Faster Response**: Instant playback from cached files (~0.1s vs ~1-2s API call)
- **Offline Support**: Cached messages work without internet (if file exists)
- **Consistent Quality**: Same audio every time for the same message
