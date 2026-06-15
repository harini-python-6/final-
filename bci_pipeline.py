import json
from pathlib import Path

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

INPUT_FILE = "final_epocx_128hz.json"
OUTPUT_FILE = "bci_dispatched_commands.json"
CONFIDENCE_THRESHOLD = 0.5

# ---------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------

def run_pipeline(input_path: str, output_path: str):
    # Stage 1: Load JSON
    print(f"[Stage 1] Loading: {input_path}")
    with open(input_path, "r") as f:
        bci_data = json.load(f)

    total_frames = len(bci_data)
    print(f"          {total_frames} frames loaded.")

    dispatched = []
    skipped_neutral = 0
    skipped_confidence = 0

    for entry in bci_data:

        # Stage 2: Extract fields
        sample_id  = entry.get("Sample_ID", 0)
        timestamp  = entry.get("Timestamp", 0.0)
        command    = entry.get("Command", "Neutral")
        confidence = entry.get("Confidence", 0.0)

        # Stage 3: Gate 1 — discard Neutral (resting brain state)
        if command == "Neutral":
            skipped_neutral += 1
            continue

        # Stage 4: Gate 2 — discard low-confidence frames
        if confidence < CONFIDENCE_THRESHOLD:
            skipped_confidence += 1
            continue

        # Stage 5: COMMAND_MAP lookup — removed as per requirement

        # Stage 6: Build verified payload
        payload = {
            "sample_id":       sample_id,
            "timestamp":       round(float(timestamp), 7),
             "raw_brain_state": f"Right {command}",
            "confidence":      round(float(confidence), 4),
            "status":          "verified"
        }
        dispatched.append(payload)

    # Build final output structure
    output = {
        "pipeline_summary": {
            "source_file":            Path(input_path).name,
            "total_frames":           total_frames,
            "skipped_neutral":        skipped_neutral,
            "skipped_low_confidence": skipped_confidence,
            "dispatched_count":       len(dispatched),
            "confidence_threshold":   CONFIDENCE_THRESHOLD
        },
        "dispatched_commands": dispatched
    }

    # Write output JSON
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n[Pipeline Summary]")
    print(f"  Total frames         : {total_frames}")
    print(f"  Skipped (Neutral)    : {skipped_neutral}")
    print(f"  Skipped (confidence) : {skipped_confidence}")
    print(f"  Dispatched           : {len(dispatched)}")
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
        run_pipeline(str(input_path), str(output_path))