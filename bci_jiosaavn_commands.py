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

INPUT_FILE = "bci_jiosaavn_commands.json"

# Timing delays to allow UI elements to fully render on screen
DELAY_BETWEEN_EVENTS = 3.0   
DELAY_APP_LAUNCH     = 6.0   
DELAY_SEARCH_TYPING  = 1.0   
DELAY_PAGE_LOAD      = 4.0   # Generous delay to ensure the song layouts load completely

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
# AUTOMATED CURSOR CONTROLLER (SKY-BLUE BUTTON TARGET)
# ---------------------------------------------------------

def move_cursor_to_skyblue_button_and_play(win):
    """
    Automatically moves the physical mouse pointer straight onto the sky-blue 
    'Play' or 'Start Radio' text button using absolute window calculations.
    """
    print("  -> Locking onto sky-blue text button position...")
    
    # Ensure the window is focused and active on screen
    win.set_focus()
    time.sleep(0.5)
    
    # Fetch the exact placement boundary details of the JioSaavn window on your monitor
    window_rect = win.rectangle()
    win_left = window_rect.left
    win_top = window_rect.top
    win_width = window_rect.width()
    win_height = window_rect.height()
    
    # Based on the images, the sky-blue button sits exactly at:
    # 28% from the left side of the window, and 29% from the top side of the window.
    target_x = int(win_left + (win_width * 0.28))
    target_y = int(win_top + (win_height * 0.29))
    
    print(f"  -> Automated move: Sliding cursor to sky-blue button at ({target_x}, {target_y})")
    
    # Physically glides the cursor smoothly across the screen to the button over 0.6 seconds
    pyautogui.moveTo(target_x, target_y, duration=0.6)
    
    # Performs the physical mouse click automatically right on top of the text button
    pyautogui.click()
    print("  -> [Success] Sky-blue button clicked automatically.")


def execute_search_and_play_sequence(win, song_name):
    """
    1. Click search box, types the chosen song name string.
    2. Physically guides the cursor to the first dropdown recommendation item and selects it.
    3. Physically guides the cursor directly onto the sky-blue action button and hits play.
    """
    print(f"\n[Automation Core] Starting automated run for: '{song_name}'")
    
    # --- PHASE 1: SEARCH & DROP-DOWN SELECTION ---
    search_box = win.child_window(auto_id="txtSearch", control_type="Edit")
    search_box.click_input()
    time.sleep(0.3)
    search_box.set_edit_text(song_name)
    
    # Wait for the drop-down selection window to drop open
    time.sleep(1.5) 
    
    # Locate the search box placement to calculate where the first dropdown option is
    search_rect = search_box.rectangle()
    
    # Center horizontally on the search bar, then move down 65 pixels into the first song row
    dropdown_x = int((search_rect.left + search_rect.right) / 2)
    dropdown_y = int(search_rect.bottom + 65)  
    
    print(f"  -> Automated move: Sliding cursor to first dropdown item: ({dropdown_x}, {dropdown_y})")
    pyautogui.moveTo(dropdown_x, dropdown_y, duration=0.5)
    pyautogui.click()
    
    # --- PHASE 2: TRACK PAGE AUTOMATED LOADING & SELECTION ---
    print(f"  -> Waiting {DELAY_PAGE_LOAD}s for the page to render completely...")
    time.sleep(DELAY_PAGE_LOAD)
    
    # Control the pointer to strike the sky-blue action button
    move_cursor_to_skyblue_button_and_play(win)


# ---------------------------------------------------------
# LIFECYCLE MANAGEMENT & LOGIC PROCESSING
# ---------------------------------------------------------

def startup_play():
    """Initializes app on startup."""
    if not is_jiosaavn_running():
        launch_jiosaavn()

    song = random.choice(SONG_LIST)
    print(f"[Startup] Invoking automated startup sequence...")
    try:
        app = Application(backend="uia").connect(title_re=".*JioSaavn.*")
        win = app.window(title_re=".*JioSaavn.*")
        win.set_focus()
        time.sleep(1.0)
        
        execute_search_and_play_sequence(win, song)
        return True
    except Exception as e:
        print(f"  [Startup Error] Routine missed element structural hook: {e}")
        return False


def action_search_macro():
    """Triggered on BCI gesture 'MACRO' command matches."""
    song = random.choice(SONG_LIST)
    try:
        app = Application(backend="uia").connect(title_re=".*JioSaavn.*")
        win = app.window(title_re=".*JioSaavn.*")
        win.set_focus()
        
        execute_search_and_play_sequence(win, song)
    except Exception as e:
        print(f"  [Macro Error] Execution failed: {e}")


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
    EnumWindows         = ctypes.windll.user32.EnumWindows
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
# HARDWARE GLOBAL MEDIA KEY MAPS
# ---------------------------------------------------------

ACTION_HANDLERS = {
    "VK_MEDIA_PLAY_PAUSE": lambda: ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0),
    "VK_MEDIA_NEXT_TRACK": lambda: ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB0, 0, 2, 0),
    "VK_MEDIA_PREV_TRACK": lambda: ctypes.windll.user32.keybd_event(0xB1, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB1, 0, 2, 0),
    "VK_VOLUME_UP": lambda: pyautogui.press("volumeup"),
    "VK_VOLUME_DOWN": lambda: pyautogui.press("volumedown"),
}

def dispatch(action_target):
    if action_target == "MACRO":
        action_search_macro()
        return

    handler = ACTION_HANDLERS.get(action_target)
    if handler:
        handler()
        print(f"  -> [Action] Triggered system event: {action_target}")
    else:
        print(f"  -> [Warning] Action '{action_target}' bypassed.")


def apply_commands(input_path: str):
    print(f"Loading commands from: {input_path}")
    with open(input_path, "r") as f:
        data = json.load(f)

    events = data["jiosaavn_commands"]
    total  = len(events)

    if not startup_play():
        return

    print(f"\n[Executor] Tracking {total} input events...\n")
    for event in events:
        focus_jiosaavn()
        print(f"\n[Event {event['event_id']:02d}/{total}] Processing {event['action_target']}")
        dispatch(event["action_target"])
        time.sleep(DELAY_BETWEEN_EVENTS)


if __name__ == "__main__":
    input_path = Path(__file__).parent / INPUT_FILE
    if not input_path.exists():
        print(f"Missing file error: {input_path}")
    else:
        apply_commands(str(input_path))