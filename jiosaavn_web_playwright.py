import json
import ctypes
import time
import random
import os
from pathlib import Path
import pyautogui

# Web Automation Imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains  # NEW IMPORT ADDED HERE

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

INPUT_FILE = "jiosaavn_commands.json"

DELAY_BETWEEN_EVENTS = 3.0
DELAY_PAGE_LOAD      = 3.0

# Your specific JioSaavn playlist URLs
PLAYLIST_LIST = [
    "https://www.jiosaavn.com/s/playlist/0c04e920d8cffe5e323fc9e9361e01f0/dsp/upHBtf3F7OtFMb4ZdYSGfQ__",
    "https://www.jiosaavn.com/s/playlist/0c04e920d8cffe5e323fc9e9361e01f0/chitanjeevi/6J8Af9YbBDvnZqie6EVsAw__"
]

driver = None

# ---------------------------------------------------------
# MANDATORY STARTUP CLICKER
# ---------------------------------------------------------

def click_homepage_play_button(web_driver):
    print("\n[Startup] Starting the current song before processing commands...")
    try:
        try:
            pause_btn = web_driver.find_element(
                By.CSS_SELECTOR, "button[title='Pause'], button[aria-label='Pause']"
            )
            if pause_btn.is_displayed():
                print("  -> SUCCESS: Current song is already actively playing.")
                return
        except Exception:
            pass

        play_selectors = [
            "//div[@id='player']//button[@title='Play']",
            "//footer//button[@title='Play']",
            "//button[@aria-label='Play']"
        ]
        button_clicked = False
        for xpath in play_selectors:
            try:
                play_btn = web_driver.find_element(By.XPATH, xpath)
                web_driver.execute_script("arguments[0].click();", play_btn)
                button_clicked = True
                print("  -> SUCCESS: Clicked bottom Play button. Music started.")
                break
            except Exception:
                continue

        if not button_clicked:
            print("  -> [Notice] Could not find Play button. Forcing spacebar.")
            body_element = web_driver.find_element(By.TAG_NAME, "body")
            web_driver.execute_script("arguments[0].click();", body_element)
            time.sleep(0.5)
            body_element.send_keys(Keys.SPACE)

    except Exception as e:
        print(f"  -> [Warning] Startup play sequence encountered an error: {e}")


# ---------------------------------------------------------
# BULLETPROOF MOUSE MOVEMENT (NO WINDOW MATH)
# ---------------------------------------------------------

def click_green_play_button(web_driver):
    print("  -> Locating the Big Green 'Play' button beside the poster...")
    try:
        wait = WebDriverWait(web_driver, 15)
        
        # Targets EXACTLY the HTML structure from your screenshot
        target_css = "a.c-btn.c-btn--primary.js-play-button[data-btn-icon='q']"
        
        play_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target_css)))
        
        # Scroll the button into view so it's on the screen
        web_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", play_btn)
        time.sleep(1.0)
        
        # USE ACTIONCHAINS: This locks onto the element in the code.
        # It handles the mouse movement and click natively, so it NEVER breaks when sizes change.
        actions = ActionChains(web_driver)
        actions.move_to_element(play_btn).pause(0.5).click().perform()
        
        print("  -> ✅ SUCCESS: Moved to and clicked the Big Green Play Button securely!")
        return True

    except Exception as e:
        print(f"  -> [Error] Failed to accurately place cursor: {e}")
        # Final fallback just in case
        try:
            web_driver.execute_script("arguments[0].click();", play_btn)
            return True
        except:
            return False


# ---------------------------------------------------------
# CORE PLAYLIST URL LOADING
# ---------------------------------------------------------

def execute_playlist_search_and_play(web_driver, playlist_url):
    print(f"\n[Automated Queue] Navigating to playlist: {playlist_url}")
    try:
        web_driver.get(playlist_url)
        time.sleep(4.0)   # Ensure page assets are fully loaded
        
        success = click_green_play_button(web_driver)

        if not success:
            print("  -> [Warning] Using Spacebar as backup alternative...")
            try:
                body = web_driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.SPACE)
            except:
                pass

    except Exception as e:
        print(f"  -> [Error] Playlist execution failed: {e}")


# ---------------------------------------------------------
# BROWSER INITIALIZATION
# ---------------------------------------------------------

def launch_and_attach_to_browser():
    global driver
    local_app_data = os.getenv('LOCALAPPDATA', os.path.expanduser('~'))
    profile_path = os.path.join(local_app_data, "JioSaavn_Automation_Profile")

    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-allow-origins=*")
    options.add_argument("--disable-gpu")

    try:
        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(
            service=service,
            options=options
        )

        driver.get("https://www.jiosaavn.com/")
        time.sleep(DELAY_PAGE_LOAD)
        return True

    except Exception as e:
        print(f"  [Connection Error] Could not initialize Chrome: {e}")
        return False

def action_search_macro():
    global driver
    target_playlist = random.choice(PLAYLIST_LIST)
    if driver:
        execute_playlist_search_and_play(driver, target_playlist)


def focus_browser_window():
    global driver
    if driver:
        try:
            driver.execute_script("window.focus();")
            return True
        except:
            pass
    return False


def close_browser():
    global driver
    if driver:
        try:
            print("\n[Cleanup] Closing Chrome browser...")
            driver.quit()
            driver = None
            print("  -> Chrome closed successfully.")
        except Exception as e:
            print(f"  -> [Warning] Could not close Chrome: {e}")


# ---------------------------------------------------------
# DISPATCHER
# ---------------------------------------------------------

ACTION_HANDLERS = {
    "VK_MEDIA_PLAY_PAUSE": lambda: ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0),
    "VK_MEDIA_NEXT_TRACK": lambda: ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB0, 0, 2, 0),
    "VK_MEDIA_PREV_TRACK": lambda: ctypes.windll.user32.keybd_event(0xB1, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB1, 0, 2, 0),
    "VK_VOLUME_UP":        lambda: pyautogui.press("volumeup"),
    "VK_VOLUME_DOWN":      lambda: pyautogui.press("volumedown"),

    "Play / Pause":   lambda: ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0),
    "Next Track":     lambda: ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB0, 0, 2, 0),
    "Previous Track": lambda: ctypes.windll.user32.keybd_event(0xB1, 0, 0, 0) or time.sleep(0.05) or ctypes.windll.user32.keybd_event(0xB1, 0, 2, 0),
    "Volume Up":      lambda: pyautogui.press("volumeup"),
    "Volume Down":    lambda: pyautogui.press("volumedown"),
}


def dispatch(brain_state, action_target):
    if action_target in ["MACRO", "search_random_song", "Search Random Song"]:
        action_search_macro()
        return

    handler = ACTION_HANDLERS.get(action_target)
    if handler:
        handler()
        print(f"  -> [Action] Triggered: {action_target}")
    else:
        print(f"  -> [Warning] Action '{action_target}' not mapped.")


# ---------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------

def apply_commands(input_path: str):
    print(f"Loading commands from: {input_path}")
    with open(input_path, "r") as f:
        data = json.load(f)

    events = data.get("commands", data.get("jiosaavn_commands", []))
    total = len(events)

    if total == 0:
        print("[!] No commands found.")
        return

    if not launch_and_attach_to_browser():
        return

    try:
        click_homepage_play_button(driver)
        print("  -> Waiting 5 seconds for initial playback...")
        time.sleep(5.0)

        for idx, event in enumerate(events):
            if event.get("status") == "unmapped":
                continue

            focus_browser_window()
            action_target = event.get("action_target", "Unknown")
            brain_state = event.get("raw_brain_state", "Unknown")

            print(f"\n[Event {idx + 1:02d}/{total:02d}] {str(brain_state).title()}")
            dispatch(brain_state, action_target)
            time.sleep(DELAY_BETWEEN_EVENTS)

        print("\n[Finished] All commands executed!")

    except Exception as e:
        print(f"Pipeline crashed: {e}")
    finally:
        close_browser()


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    input_path = Path(__file__).parent / INPUT_FILE
    if not input_path.exists():
        input_path = Path.cwd() / INPUT_FILE

    if not input_path.exists():
        print(f"Missing file: {INPUT_FILE}")
    else:
        apply_commands(str(input_path))