import json
from pathlib import Path

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

INPUT_FILE  = "bci_dispatched_commands.json"
OUTPUT_FILE = "bci_gesture_events.json"
SAMPLE_RATE = 128  # Hz — used to calculate burst duration in seconds

# ---------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------

def extract_gesture_events(input_path: str, output_path: str):

    # Stage 1: Load dispatched commands JSON
    print(f"[Stage 1] Loading: {input_path}")
    with open(input_path, "r") as f:
        data = json.load(f)

    frames = data["dispatched_commands"]
    print(f"          {len(frames)} dispatched frames loaded.")

    # Stage 2: Group consecutive same-command frames into bursts
    print(f"[Stage 2] Grouping consecutive frames into bursts...")
    bursts = []
    current_burst = [frames[0]]

    for frame in frames[1:]:
        if frame["raw_brain_state"] == current_burst[-1]["raw_brain_state"]:
            current_burst.append(frame)
        else:
            bursts.append(current_burst)
            current_burst = [frame]
    bursts.append(current_burst)

    print(f"          {len(bursts)} distinct gesture bursts found.")

    # Stage 3: Pick highest-confidence frame from each burst
    print(f"[Stage 3] Extracting confidence peak from each burst...")
    gesture_events = []

    for i, burst in enumerate(bursts):
        peak = max(burst, key=lambda x: x["confidence"])
        gesture_events.append({
            "event_id":               i + 1,
            "sample_id":              peak["sample_id"],
            "timestamp":              peak["timestamp"],
            "raw_brain_state":        peak["raw_brain_state"],
            "confidence":             peak["confidence"],
            "burst_length_frames":    len(burst),
            "burst_duration_seconds": round(len(burst) / SAMPLE_RATE, 4),
            "status":                 "verified"
        })

    # Stage 4: Build and write output
    output = {
        "pipeline_summary": {
            "source_file":             Path(input_path).name,
            "total_dispatched_frames": len(frames),
            "distinct_gesture_events": len(gesture_events),
            "extraction_method":       "confidence_peak_per_burst",
            "sample_rate_hz":          SAMPLE_RATE
        },
        "gesture_events": gesture_events
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    # Print summary table
    print(f"\n[Pipeline Summary]")
    print(f"  Total dispatched frames  : {len(frames)}")
    print(f"  Distinct gesture events  : {len(gesture_events)}")
    print(f"\n{'Event':<7} {'Gesture':<8} {'Confidence':<12} {'Duration':>10}  {'Frames':>8}")
    print("-" * 52)
    for e in gesture_events:
        print(f"  {e['event_id']:02d}    {e['raw_brain_state']:<8} {e['confidence']:<12} "
              f"{e['burst_duration_seconds']:>8.2f}s  {e['burst_length_frames']:>7}")

    print(f"\n[Output] Written to: {output_path}")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    input_path  = Path(__file__).parent / INPUT_FILE
    output_path = Path(__file__).parent / OUTPUT_FILE

    if not input_path.exists():
        print(f"Error: Input file not found -> {input_path}")
    else:
        extract_gesture_events(str(input_path), str(output_path))