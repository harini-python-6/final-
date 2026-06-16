import json
import ctypes
import time
import random
import subprocess
import pyautogui
from pathlib import Path
from pywinauto.application import Application

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

INPUT_FILE = "jiosaavn_commands.json"

# Timing delays to allow UI elements to fully render on screen
DELAY_BETWEEN_EVENTS = 3.0   
DELAY_APP_LAUNCH     = 6.0   
DELAY_SEARCH_TYPING  = 1.0   
DELAY_PAGE_LOAD      = 3.5   # Slightly increased to guarantee poster plays cleanly

SONG_LIST = [
    "Oo Antava", 
    "Butta Bomma", 
    "Adiye", 
    "Samajavaragamana", 
    "Phir Se",
    "Naatu Naatu",
    "Enjoy Enjaami",
    "Jimikki Ponnu",
    "Why This Kolaveri Di"
]

# ---------------------------------------------------------
# CORE AUTOMATION HANDLER (MOUSE CURSOR SCANNING & CLICKING)
# ---------------------------------------------------------

def execute_search_and_play_sequence(win, song_name):
    """
    1. Finds the search box, types the song.
    2. Moves cursor to the first dropdown recommended item and clicks it.
    3. Waits for page load, moves cursor to the big poster play button and clicks it.
    """
    print(f"\n[Automation Core] Initiating tracking routine for: '{song_name}'")
    
    # --- PHASE 1: SEARCH & DROPDOWN SELECTION ---
    search_box = win.child_window(auto_id="txtSearch", control_type="Edit")
    search_box.click_input()
    time.sleep(0.5)
    search_box.set_edit_text(song_name)
    
    # Wait for the recommended dropdown list to pop open on screen
    time.sleep(1.5) 
    
    # Fetch the coordinates of the search box to calculate dropdown offset
    search_rect = search_box.rectangle()
    
    # The first recommended song sits directly underneath the search bar box
    dropdown_x = int((search_rect.left + search_rect.right) / 2) # Center horizontally
    dropdown_y = int(search_rect.bottom + 65)                    # Move down 65 pixels into 1st row
    
    print(f"  -> Moving cursor to First Recommended Song entry: ({dropdown_x}, {dropdown_y})")
    pyautogui.moveTo(dropdown_x, dropdown_y, duration=0.5)
    pyautogui.click()
    
    # --- PHASE 2: ALBUM POSTER MAIN PLAY BUTTON ---
    print(f"  -> Waiting {DELAY_PAGE_LOAD}s for main track poster page to render...")
    time.sleep(DELAY_PAGE_LOAD)
    
    # Grab window bounds right now in case the app shifted position
    window_rect = win.rectangle()
    win_left = window_rect.left
    win_top = window_rect.top
    win_width = window_rect.width()
    win_height = window_rect.height()
    
    # Calculate target on the big button sitting over the album art poster
    poster_play_x = int(win_left + (win_width * 0.14))
    poster_play_y = int(win_top + (win_height * 0.26))
    
    print(f"  -> Moving cursor directly to the Big Poster Play Button: ({poster_play_x}, {poster_play_y})")
    pyautogui.moveTo(poster_play_x, poster_play_y, duration=0.6)
    pyautogui.click()
    print("  -> [Success] Sequence complete. Music triggered.")


# ---------------------------------------------------------
# WRAPPERS & EXECUTION PIPELINE
# ---------------------------------------------------------

def startup_play():
    """App startup lifecycle initialization."""
    if not is_jiosaavn_running():
        launch_jiosaavn()

    song = random.choice(SONG_LIST)
    print(f"[Startup] Setting up initial song playback...")
    try:
        # THE FIX: Added found_index=0 to bypass hidden ghost windows
        app = Application(backend="uia").connect(title_re=".*JioSaavn.*", found_index=0)
        win = app.window(title_re=".*JioSaavn.*", found_index=0)
        win.set_focus()
        time.sleep(1.0)
        
        execute_search_and_play_sequence(win, song)
        return True
    except Exception as e:
        print(f"  [Startup Error] Failed to complete baseline sequence: {e}")
        return False


def action_search_macro():
    """BCI Macro trigger wrapper."""
    song = random.choice(SONG_LIST)
    try:
        # THE FIX: Added found_index=0 to bypass hidden ghost windows
        app = Application(backend="uia").connect(title_re=".*JioSaavn.*", found_index=0)
        win = app.window(title_re=".*JioSaavn.*", found_index=0)
        win.set_focus()
        
        execute_search_and_play_sequence(win, song)
    except Exception as e:
        print(f"  [Macro Error] Execution interrupted: {e}")


def is_jiosaavn_running():
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq JioSaavn.exe'], capture_output=True, text=True)
    return "JioSaavn.exe" in result.stdout


def launch_jiosaavn():
    app_id = "Saavn.SaavnMusicRadio_ax02tpqam95xr!App"
    print(f"  Launching JioSaavn via App ID: {app_id}")
    try:
        subprocess.run(["powershell", "-Command", f"Start-Process shell:AppsFolder\\{app_id}"])
        time.sleep(DELAY_APP_LAUNCH)
        return True
    except Exception as e:
        print(f"  [Error] Launch failure: {e}")
        return False


def focus_jiosaavn():
    EnumWindows        = ctypes.windll.user32.EnumWindows
    EnumWindowsProc    = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText      = ctypes.windll.user32.GetWindowTextW
    IsWindowVisible    = ctypes.windll.user32.IsWindowVisible
    SetForegroundWindow= ctypes.windll.user32.SetForegroundWindow

    found_hwnd = []
    def callback(hwnd, lParam):
        if IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(512)
            GetWindowText(hwnd, buf, 512)
            if "jiosaavn" in buf.value.lower() or "jio saavn" in buf.value.lower():
                found_hwnd.append(hwnd)
        return True

    EnumWindows(EnumWindowsProc(callback), 0)
    if found_hwnd:
        try:
            SetForegroundWindow(found_hwnd[0])
            time.sleep(0.3)
            return True
        except Exception:
            pass
    return False

# ---------------------------------------------------------
# DISPATCHER & SYSTEM KEYMAPS (Mapped to raw_brain_state)
# ---------------------------------------------------------

ACTION_HANDLERS = {
    "right push":  lambda: ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0),
    "right left":  lambda: ctypes.windll.user32.keybd_event(0xB1, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB1, 0, 2, 0),
    "right right": lambda: ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB0, 0, 2, 0),
    "right lift":  lambda: pyautogui.press("volumeup"),
    "right drop":  lambda: pyautogui.press("volumedown"),
}

def dispatch(brain_state, action_target):
    clean_state = str(brain_state).lower().strip()
    
    # Route to macro search
    if clean_state == "right pull" or action_target == "Search Random Song":
        action_search_macro()
        return

    handler = ACTION_HANDLERS.get(clean_state)
    if handler:
        handler()
        print(f"  -> [Action] Triggered system event: {action_target}")
    else:
        print(f"  -> [Warning] Brain State '{brain_state}' bypassed or unmapped.")


def apply_commands(input_path: str):
    print(f"Loading commands from: {input_path}")
    with open(input_path, "r") as f:
        data = json.load(f)

    # Automatically handle either "commands" or "jiosaavn_commands" root keys
    events = data.get("commands", data.get("jiosaavn_commands", []))
    total  = len(events)
    
    if total == 0:
        print("[!] No commands found in JSON file.")
        return

    if not startup_play():
        return

    print(f"\n[Executor] Tracking {total} input events...\n")
    for event in events:
        if event.get("status") == "unmapped":
            continue
            
        focus_jiosaavn()
        
        # Extract both variables safely from JSON
        brain_state = event.get("raw_brain_state")
        action_target = event.get("action_target")
        
        print(f"\n[Event {event.get('event_id', '?'):02d}/{total}] Processing {action_target} (BCI: {brain_state})")
        dispatch(brain_state, action_target)
        time.sleep(DELAY_BETWEEN_EVENTS)


if __name__ == "__main__":
    input_path = Path(__file__).parent / INPUT_FILE
    
    if not input_path.exists():
        input_path = Path.cwd() / INPUT_FILE
        
    if not input_path.exists():
        print(f"Missing file error: Could not trace target input file path {INPUT_FILE}")
    else:
        apply_commands(str(input_path))