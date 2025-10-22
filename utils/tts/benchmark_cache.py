#!/usr/bin/env python3
"""
Benchmark TTS cache performance vs API calls.
Measures time savings from using cached audio.
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from cached_tts import get_cached_audio_path, play_audio, generate_and_cache_audio


def benchmark_cached_playback(message):
    """Measure time to play cached audio."""
    cached_path = get_cached_audio_path(message)

    if not cached_path.exists():
        return None, "Not cached"

    start = time.time()
    success = play_audio(cached_path)
    elapsed = time.time() - start

    if success:
        return elapsed, "Success"
    else:
        return None, "Playback failed"


def benchmark_api_call(message):
    """Measure time to generate audio via API (without playback)."""
    # Check if ElevenLabs API is available
    if not os.getenv('ELEVENLABS_API_KEY'):
        return None, "No API key"

    # Use a temporary file
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        temp_path = Path(f.name)

    try:
        start = time.time()
        success = generate_and_cache_audio(message, temp_path)
        elapsed = time.time() - start

        # Clean up
        if temp_path.exists():
            temp_path.unlink()

        if success:
            return elapsed, "Success"
        else:
            return None, "API call failed"
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        return None, f"Error: {e}"


def main():
    """Run benchmarks and display results."""
    print("⚡ TTS Cache Performance Benchmark")
    print("=" * 70)

    # Test with a cached message
    test_message = "Work complete!"

    print(f"\nTest Message: '{test_message}'")
    print("-" * 70)

    # Benchmark cached playback
    print("\n🎯 Benchmarking CACHED playback (5 runs)...")
    cached_times = []
    for i in range(5):
        elapsed, status = benchmark_cached_playback(test_message)
        if elapsed is not None:
            cached_times.append(elapsed)
            print(f"  Run {i+1}: {elapsed*1000:.1f}ms ({status})")
        else:
            print(f"  Run {i+1}: Failed ({status})")

    # Benchmark API call (without playback, just generation)
    print("\n🌐 Benchmarking API GENERATION (3 runs)...")
    print("   (Measuring API call time only, not playback)")
    api_times = []
    for i in range(3):
        print(f"  Run {i+1}: Calling API...", end=" ", flush=True)
        elapsed, status = benchmark_api_call(test_message)
        if elapsed is not None:
            api_times.append(elapsed)
            print(f"{elapsed*1000:.1f}ms ({status})")
        else:
            print(f"Failed ({status})")
        time.sleep(0.5)  # Small delay between API calls

    # Calculate statistics
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)

    if cached_times:
        avg_cached = sum(cached_times) / len(cached_times)
        min_cached = min(cached_times)
        max_cached = max(cached_times)
        print(f"\n✅ Cached Playback:")
        print(f"   Average: {avg_cached*1000:.1f}ms")
        print(f"   Min:     {min_cached*1000:.1f}ms")
        print(f"   Max:     {max_cached*1000:.1f}ms")
    else:
        print("\n❌ Cached playback failed")
        avg_cached = None

    if api_times:
        avg_api = sum(api_times) / len(api_times)
        min_api = min(api_times)
        max_api = max(api_times)
        print(f"\n🌐 API Generation (not including playback):")
        print(f"   Average: {avg_api*1000:.1f}ms")
        print(f"   Min:     {min_api*1000:.1f}ms")
        print(f"   Max:     {max_api*1000:.1f}ms")
    else:
        print("\n❌ API generation failed")
        avg_api = None

    # Comparison
    if avg_cached and avg_api:
        speedup = avg_api / avg_cached
        time_saved = avg_api - avg_cached
        print(f"\n⚡ PERFORMANCE GAIN:")
        print(f"   Time Saved:  {time_saved*1000:.1f}ms ({time_saved:.2f}s)")
        print(f"   Speedup:     {speedup:.1f}x faster")
        print(f"   Improvement: {((speedup-1)*100):.0f}% faster with cache")

        # Cost analysis
        print(f"\n💰 COST SAVINGS:")
        print(f"   Each cached playback saves 1 API call")
        print(f"   ElevenLabs: ~$0.18 per 1000 characters")
        msg_chars = len(test_message)
        cost_per_call = (msg_chars / 1000) * 0.18
        print(f"   Cost per API call: ${cost_per_call:.6f}")
        print(f"   Cost per cached playback: $0.000000")
        print(f"   Savings per use: ${cost_per_call:.6f}")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
