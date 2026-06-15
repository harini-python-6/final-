
import json
import ctypes
import time
import random
import os
import subprocess
from pathlib import Path
import pyautogui

# Web Automation Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

INPUT_FILE = "bci_jiosaavn_commands.json"

DELAY_BETWEEN_EVENTS = 3.0   
DELAY_PAGE_LOAD      = 5.0   

SONG_LIST = [
    "Oo Antava", 
    "Butta Bomma", 
    "Adiye", 
    "Samajavaragamana", 
    "Phir Se",
    "Naatu Naatu",
    "Enjoy Enjaami",
    "Jimikki Ponnu",
]

# Global driver reference
driver = None

# ---------------------------------------------------------
# BROWSER PROCESS MANAGEMENT (The Fix for Zombie Audio)
# ---------------------------------------------------------

def wipe_chrome_processes():
    """Forcefully kills any hidden Chrome/ChromeDriver tasks in Windows."""
    subprocess.run("taskkill /F /IM chrome.exe /T", shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM chromedriver.exe /T", shell=True, capture_output=True)

def cleanup_browser():
    """Safely destroys the driver and wipes hidden processes to stop audio."""
    global driver
    print("\n[Cleanup] Shutting down browser and wiping background processes...")
    if driver:
        try:
            driver.quit() # Explicitly tells ChromeDriver to destroy all linked windows and audio
        except Exception:
            pass
    # Double-tap: Guarantee no zombie processes survive to play music
    wipe_chrome_processes()
    print("  -> Cleanup complete. All music strictly stopped.")

# ---------------------------------------------------------
# MANDATORY STARTUP CLICKER
# ---------------------------------------------------------

def click_homepage_play_button(web_driver):
    """Clicks the global player bar at the bottom to initialize audio."""
    print("\n[Mandatory Startup] Attempting to click the bottom player bar Play button...")
    try:
        bottom_player_selectors = [
            "//div[@id='player']//button[@id='play']",
            "//footer//button[@title='Play']",
            "//button[@aria-label='Play']",
            "//footer//*[contains(@class, 'play') or @id='play']"
        ]
        
        button_clicked = False
        for xpath in bottom_player_selectors:
            try:
                play_btn = WebDriverWait(web_driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if play_btn.is_displayed():
                    web_driver.execute_script("arguments[0].click();", play_btn)
                    print("  -> [Success] Bottom player bar Play button clicked successfully!")
                    button_clicked = True
                    break
            except:
                continue
                
        if not button_clicked:
            print("  -> [Notice] Could not target bottom button element; clicking body and forcing a spacebar event.")
            body_element = web_driver.find_element(By.TAG_NAME, "body")
            web_driver.execute_script("arguments[0].click();", body_element)
            time.sleep(0.5)
            body_element.send_keys(Keys.SPACE)
            
    except Exception as e:
        print(f"  -> [Warning] Error executing startup play command: {e}")


# ---------------------------------------------------------
# CORE WEB AUTOMATION HANDLER (Fast + Debounce)
# ---------------------------------------------------------

def execute_search_and_play_sequence(web_driver, song_name):
    print(f"\n[Automated Search] Processing sequence for track: '{song_name}'")
    try:
        # AUTO-PAUSE BACKGROUND MUSIC QUICKLY
        try:
            pause_btn = web_driver.find_element(By.XPATH, "//footer//button[@title='Pause'] | //button[@aria-label='Pause'] | //div[@id='player']//button[@id='pause']")
            if pause_btn.is_displayed():
                web_driver.execute_script("arguments[0].click();", pause_btn)
        except Exception:
            pass

        # DISMISS POPUPS QUICKLY
        popup_xpaths = [
            "//button[contains(text(), 'Save')]",
            "//button[contains(text(), 'Done')]",
            "//*[contains(@class, 'modal-close')]"
        ]
        for xpath in popup_xpaths:
            try:
                btn = web_driver.find_element(By.XPATH, xpath)
                if btn.is_displayed():
                    web_driver.execute_script("arguments[0].click();", btn)
            except Exception:
                pass

        # STEP 1: Fast clear, instant type, and Debounce Time
        try:
            search_input = WebDriverWait(web_driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#search, input[placeholder*='Search']"))
            )
            search_input.click() 
            
            actions = ActionChains(web_driver)
            actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).perform()
            
            # Type the whole song name instantly
            ActionChains(web_driver).send_keys(song_name).perform()
            print("  -> Typed query. Waiting for UI debounce...")
            
            # DEBOUNCE TIME: Wait precisely 0.8s for JioSaavn's search suggestions to catch up
            time.sleep(0.8) 
            
            # Press Enter
            ActionChains(web_driver).send_keys(Keys.ENTER).perform()
            
        except Exception as e:
            print(f"  -> [Error] Search input failed: {e}")
            return

        web_driver.execute_script("document.activeElement.blur()")

        # STEP 2 & 3 MERGED: Dynamic Wait and Inline Click (No unnecessary sleeps)
        print("  -> Targeting the inline Play icon on Row #1...")
        
        try:
            # Dynamically wait for the first row to render instead of sleeping
            first_row = WebDriverWait(web_driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ol.u-list-bare li:first-child, .track-list li:first-child"))
            )
            # Hover over it to expose the play button
            ActionChains(web_driver).move_to_element(first_row).perform()
            time.sleep(0.2) # Micro-debounce for hover animation
        except Exception:
            pass

        inline_play_selectors = [
            "ol.u-list-bare li:first-child figure button",
            "ol.u-list-bare li:first-child button[title='Play']",
            "ol.u-list-bare li:first-child i[class*='play']",
            ".track-list li:first-child figure button",
            ".track-list li:first-child button[title='Play']",
            "ol li:first-child div[role='button']"
        ]

        play_clicked = False
        for selector in inline_play_selectors:
            try:
                play_btn = web_driver.find_element(By.CSS_SELECTOR, selector)
                web_driver.execute_script("arguments[0].click();", play_btn)
                print(f"  -> SUCCESS: Clicked inline Play icon via: '{selector}'")
                play_clicked = True
                break
            except Exception:
                continue

        # Fallback using XPath if CSS misses it
        if not play_clicked:
            try:
                play_btn_xpath = web_driver.find_element(By.XPATH, "(//ol//li)[1]//button | (//ol//li)[1]//i[contains(@class, 'play')]")
                web_driver.execute_script("arguments[0].click();", play_btn_xpath)
                print("  -> SUCCESS: Clicked inline Play icon via fallback XPath.")
                play_clicked = True
            except Exception:
                pass

        if not play_clicked:
            print("  -> Could not hook inline play icon. Sending Spacebar fallback...")
            web_driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SPACE)

        web_driver.execute_script("document.activeElement.blur()")
        print("  -> Song pipeline complete! Continuing to next command.")

    except Exception as e:
        print(f"  -> [Automation Error] Flow blocked: {e}")
        try:
            web_driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SPACE)
        except Exception:
            pass


# ---------------------------------------------------------
# BROWSER INITIALIZATION PIPELINE
# ---------------------------------------------------------

def launch_and_attach_to_browser():
    global driver
    
    print("[Startup] Wiping previous sessions...")
    wipe_chrome_processes()
    time.sleep(1.0)
    
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
        driver = webdriver.Chrome(options=options)
        print("  -> Loading JioSaavn Web Player Homepage...")
        driver.get("https://www.jiosaavn.com/")
        time.sleep(DELAY_PAGE_LOAD)
        return True
    except Exception as e:
        print(f"  [Connection Error] Could not initialize Chrome session: {e}")
        return False


def action_search_macro():
    global driver
    song = random.choice(SONG_LIST)
    if driver:
        execute_search_and_play_sequence(driver, song)
    else:
        print("  -> [Macro Error] Execution failed: Browser instance uninitialized.")


def focus_browser_window():
    global driver
    if driver:
        try:
            driver.execute_script("window.focus();")
            return True
        except Exception:
            pass
    return False

# ---------------------------------------------------------
# DISPATCHER & SYSTEM KEYMAPS
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

    if not launch_and_attach_to_browser():
        return

    try:
        # Click the targeted bottom player button to unlock Chrome audio
        click_homepage_play_button(driver)
        time.sleep(2.0)

        print(f"\n[Executor] Tracking {total} input events...\n")
        for event in events:
            focus_browser_window()
            print(f"\n[Event {event['event_id']:02d}/{total}] Processing {event['action_target']}")
            dispatch(event["action_target"])
            time.sleep(DELAY_BETWEEN_EVENTS)
            
        print("\n[Finished] All commands executed in sync!")
        
    finally:
        # THE FIX: No matter what happens, wipe everything when the script is done!
        cleanup_browser()


if __name__ == "__main__":
    input_path = Path(__file__).parent / INPUT_FILE
    
    if not input_path.exists():
        input_path = Path.cwd() / INPUT_FILE

    if not input_path.exists():
        print(f"Missing file error: Could not trace target input file path {INPUT_FILE}")
    else:
        apply_commands(str(input_path))