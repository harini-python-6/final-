import json
from pathlib import Path

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
INPUT_BCAST_FILE = "bci_gesture_events.json"
OUTPUT_COMMANDS_FILE = "jiosaavn_commands.json"
CONFIDENCE_THRESHOLD = 0.5

# ---------------------------------------------------------
# JIOSAAVN ACTION MAP
# ---------------------------------------------------------
JIOSAAVN_ACTION_MAP = {
    "Right Push": "Play / Pause",
    "Right Left": "Previous Track",
    "Right Right": "Next Track",
    "Right Neutral": "Volume Down",
    "Right Drop": "Volume Up",
    "Right Lift": "Return to Home",
    "Right Pull": "Search Album/Playlist"
}


def generate_and_map_commands():
    # Resolve file paths
    script_directory = Path(__file__).parent.resolve()
    input_path = script_directory / INPUT_BCAST_FILE
    output_path = script_directory / OUTPUT_COMMANDS_FILE

    print(f"\n[Stage 1] Looking for input data file at: {input_path}")

    if not input_path.exists():
        print(f"[-] ERROR: '{INPUT_BCAST_FILE}' not found.")
        return

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("[-] ERROR: Invalid JSON format.")
        return

    # -----------------------------------------------------
    # Extract gesture events
    # -----------------------------------------------------
    raw_data = data.get("gesture_events", [])

    if not raw_data:
        print("[-] No gesture events found in JSON file.")
        return

    total_frames = len(raw_data)
    print(f"[+] Successfully loaded {total_frames} gesture events.")

    mapped_commands_list = []
    skipped_low_confidence = 0
    neutral_count = 0

    print("[Stage 2] Mapping gesture events to JioSaavn commands...")

    for entry in raw_data:
        sample_id = entry.get("sample_id", 0)
        timestamp = entry.get("timestamp", 0.0)
        brain_state = entry.get("raw_brain_state", "Right Neutral")
        confidence = entry.get("confidence", 0.0)

        # Confidence filter
        if confidence < CONFIDENCE_THRESHOLD:
            skipped_low_confidence += 1
            continue

        if brain_state == "Right Neutral":
            neutral_count += 1

        action_target = JIOSAAVN_ACTION_MAP.get(
            brain_state,
            "No Action"
        )

        payload = {
            "sample_id": sample_id,
            "timestamp": round(float(timestamp), 3),
            "raw_brain_state": brain_state,
            "action_target": action_target,
            "confidence": round(float(confidence), 4),
            "status": "verified"
        }

        mapped_commands_list.append(payload)

    # -----------------------------------------------------
    # Final Output Structure
    # -----------------------------------------------------
    final_output_structure = {
        "pipeline_summary": {
            "source_file": input_path.name,
            "total_events_evaluated": total_frames,
            "neutral_events_retained": neutral_count,
            "low_confidence_events_dropped": skipped_low_confidence,
            "total_commands_generated": len(mapped_commands_list)
        },
        "jiosaavn_commands": mapped_commands_list
    }

    print(f"[Stage 3] Writing output to: {output_path}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output_structure, f, indent=2)

    print("\n" + "=" * 55)
    print("      SUCCESS: BCI → JIOSAAVN COMMAND GENERATION")
    print("=" * 55)
    print(f"Total Events Processed       : {total_frames}")
    print(f"'Right Neutral' Retained    : {neutral_count}")
    print(f"Low Confidence Dropped      : {skipped_low_confidence}")
    print(f"Commands Generated          : {len(mapped_commands_list)}")
    print("=" * 55)
    print(f"[DONE] File saved as: {output_path.name}\n")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    generate_and_map_commands()