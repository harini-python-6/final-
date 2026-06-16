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
from selenium.webdriver.common.action_chains import ActionChains

# ---------------------------------------------------------
# CONFIGURATION & CONSTANTS
# ---------------------------------------------------------

INPUT_FILE = "jiosaavn_commands.json"

DELAY_BETWEEN_EVENTS = 4.0  
DELAY_PAGE_LOAD      = 4.0

PLAYLIST_LIST = [
    {
        "name": "Mahesh", 
        "url": "https://www.jiosaavn.com/featured/mahesh-babu-spotlight/oCbSB9rm9GrufxkxMEIbIw__"
    },
    {
        "name": "Varun Tej", 
        "url": "https://www.jiosaavn.com/artist/varun-tej-songs/cNPSpkbNtTo_"
    },
    {
        "name": "Ilaiyaraaja", 
        "url": "https://www.jiosaavn.com/featured/ilaiyaraaja-sad-songs-telugu/m,OEZBuEk6FTHgJw1pi47A__"
    },
    {
        "name": "Nani", 
        "url": "https://www.jiosaavn.com/featured/lets-play-nani-telugu/bV-AtS0lEsQ_"
    },
    {
        "name": "DSP", 
        "url": "https://www.jiosaavn.com/artist/devi-sri-prasad-songs/M0dlT,PMjDs_"
    },
    {
        "name": "chiranjeevi playlist", 
        "url": "https://www.jiosaavn.com/artist/chiranjeevi-songs/6HmPTKrqZR8_"
    }
]

WARMUP_PLAYLIST_LIST = [
    {
        "name": "Trending Today Hindi",
        "url": "https://www.jiosaavn.com/featured/trending-today/I3kvhipIy73uCJW60TJk1Q__"
    },
    {
        "name": "Telugu Superhits Top 50",
        "url": "https://www.jiosaavn.com/featured/telugu-india-superhits-top-50/4O6DwO-qteN613W6L-cCSw__"
    }
]

driver = None

# ---------------------------------------------------------
# LOGIN STATUS MONITOR
# ---------------------------------------------------------

def is_user_logged_in(web_driver):
    print("[Session Check] Verifying login status...")
    try:
        login_selectors = [
            "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'log in')]",
            "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in')]",
            "//a[contains(@class, 'login') or contains(@class, 'signin')]"
        ]
        
        for selector in login_selectors:
            elements = web_driver.find_elements(By.XPATH, selector)
            for el in elements:
                if el.is_displayed():
                    print(f"  -> Result: ❌ Guest Session detected via element: '{el.text}'")
                    return False
                    
        print("  -> Result:  Logged In user session detected.")
        return True
    except Exception:
        return False


# ---------------------------------------------------------
# STARTUP ROUTING CONTROLLER
# ---------------------------------------------------------

def handle_startup_playback(web_driver):
    if is_user_logged_in(web_driver):
        print("\n[Startup] Resuming user's existing playback history...")
        click_homepage_play_button(web_driver)
    else:
        print("\n[Startup] Empty Guest State! Initiating Warm-Up trending routine...")
        warmup_target = random.choice(WARMUP_PLAYLIST_LIST)
        execute_playlist_search_and_play(web_driver, warmup_target["name"], warmup_target["url"])


def click_homepage_play_button(web_driver):
    try:
        try:
            pause_btn = web_driver.find_element(By.CSS_SELECTOR, "button[title='Pause'], button[aria-label='Pause']")
            if pause_btn.is_displayed():
                print("  -> SUCCESS: Track is already active.")
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
                print("  -> SUCCESS: Base player started.")
                break
            except Exception:
                continue

        if not button_clicked:
            body_element = web_driver.find_element(By.TAG_NAME, "body")
            web_driver.execute_script("arguments[0].click();", body_element)
            time.sleep(0.5)
            body_element.send_keys(Keys.SPACE)
    except Exception:
        pass


# ---------------------------------------------------------
# RELIABLE INTERACTION TARGETING
# ---------------------------------------------------------

def click_green_play_button(web_driver):
    print("  -> Locating the master Play button on page canvas...")
    try:
        wait = WebDriverWait(web_driver, 8)
        target_css = "a.c-btn.c-btn--primary.js-play-button"
        
        play_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target_css)))
        web_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", play_btn)
        time.sleep(1.5)
        
        actions = ActionChains(web_driver)
        actions.move_to_element(play_btn).pause(0.5).click().perform()
        print("  -> ✅ SUCCESS: Content loaded and playing.")
        return True
    except Exception:
        try:
            play_btn = web_driver.find_element(By.CSS_SELECTOR, "a.c-btn.c-btn--primary")
            web_driver.execute_script("arguments[0].click();", play_btn)
            return True
        except:
            return False


# ---------------------------------------------------------
# VISUAL SEARCH & NAVIGATION FLOW
# ---------------------------------------------------------

def execute_playlist_search_and_play(web_driver, playlist_name, playlist_url):
    print(f"\n[Automated Queue] Processing Playlist Target: {playlist_name}")
    
    # Always drop back to home page to expose a clean, active search layout context
    try:
        web_driver.get("https://www.jiosaavn.com/")
        time.sleep(3.0)
    except:
        pass

    search_box = None
    search_strategies = [
        (By.CSS_SELECTOR, "input.search-input"),
        (By.XPATH, "//input[@placeholder='Search']"),
        (By.ID, "search"),
        (By.XPATH, "//input[@type='text' or @type='search']")
    ]
    
    for by_type, locator in search_strategies:
        try:
            el = WebDriverWait(web_driver, 5).until(EC.presence_of_element_located((by_type, locator)))
            search_box = el
            break
        except Exception:
            continue

    search_success = False
    if search_box:
        try:
            # Step 1: Physically target and click inside the box using ActionChains to gain hard focus
            web_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_box)
            time.sleep(0.5)
            
            click_action = ActionChains(web_driver)
            click_action.move_to_element(search_box).click().perform()
            time.sleep(0.8)
            
            print("  -> 🧹 Clearing search bar visually via focused shortcut selection...")
            # Step 2: Clear old text visually using keyboard commands on the active focus ring
            clear_action = ActionChains(web_driver)
            clear_action.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).perform()
            time.sleep(0.5)
            
            print(f"  -> ⌨️  Guaranteed Visual Typing: Rendering '{playlist_name}' character-by-character...")
            # Step 3: Loop and feed keys via ActionChains context to bypass background DOM injection completely
            for character in playlist_name:
                type_action = ActionChains(web_driver)
                type_action.send_keys(character).perform()
                time.sleep(0.35)  # Deliberate pause to let browser UI frames render the key press
                
            time.sleep(0.6)
            
            # Step 4: Submit search physically via focus ring execution
            submit_action = ActionChains(web_driver)
            submit_action.send_keys(Keys.RETURN).perform()
            print("  -> Search query submitted visibly.")
            search_success = True
            time.sleep(4.5)  
        except Exception as err:
            print(f"  -> [Notice] Search target input layout bypassed: {err}")
    else:
        print("  -> [Notice] UI Search input framework container not located.")

    # Select the matching item from the search results grid
    ui_click_success = False
    if search_success:
        print(f"  -> 🔍 Mapping UI layouts to locate your playlist match for: '{playlist_name}'")
        match_selectors = [
            f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{playlist_name.lower()}')]",
            f"//h3[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{playlist_name.lower()}')]",
            "section.playlists a",
            "section.artists a",
            "div.c-card a"
        ]
        for xpath_selector in match_selectors:
            try:
                if xpath_selector.startswith("//"):
                    elements = web_driver.find_elements(By.XPATH, xpath_selector)
                else:
                    elements = web_driver.find_elements(By.CSS_SELECTOR, xpath_selector)
                
                for element in elements:
                    if element.is_displayed():
                        web_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(1.0)
                        web_driver.execute_script("arguments[0].click();", element)
                        print(f"  -> ✅ Successfully matched and selected your playlist from search results.")
                        ui_click_success = True
                        time.sleep(4.0)
                        break
                if ui_click_success:
                    break
            except Exception:
                continue

    # Safety URL fallback only if the item absolutely couldn't be mapped visually on-screen
    if not ui_click_success:
        print(f"  -> [Fallback] Direct match mapping missed. Direct loading destination URL link: {playlist_url}")
        try:
            web_driver.get(playlist_url)
            time.sleep(4.5)
        except Exception as e:
            print(f"  -> [Warning] Navigation endpoint error encountered: {e}")

    # Fire the playlist playback engine
    success = click_green_play_button(web_driver)
    if not success:
        print("  -> [Warning] Play button unreachable. Triggering keyboard space fallback...")
        try:
            body = web_driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.SPACE)
        except Exception:
            pass


# ---------------------------------------------------------
# SOFT RETURN HOME LOGIC (PREVENTS AUDIO TERMINATION)
# ---------------------------------------------------------

def safe_return_to_home(web_driver):
    print("\n[Navigation] Hard loading a fresh Home page interface environment...")
    try:
        web_driver.get("https://www.jiosaavn.com/")
        print("  -> ✅ SUCCESS: Fresh homepage view reload completed smoothly.")
    except Exception as e:
        print(f"  -> [Warning] Fresh reload tracking alert: {e}")
            
    time.sleep(3.5)
    
    try:
        body = web_driver.find_element(By.TAG_NAME, "body")
        web_driver.execute_script("arguments[0].click();", body)
    except Exception:
        pass
        
    print("  -> Resuming initial track audio on homepage frame...")
    click_homepage_play_button(web_driver)


# ---------------------------------------------------------
# CORE BROWSER RUNTIME UTILITIES
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
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        driver.get("https://www.jiosaavn.com/")
        time.sleep(DELAY_PAGE_LOAD)
        return True
    except Exception as e:
        print(f"  [Connection Error] Unable to instantiate Chrome context: {e}")
        return False

def action_search_macro():
    global driver
    # Picks a completely random playlist from your personal list mapping array
    target_playlist = random.choice(PLAYLIST_LIST)
    if driver:
        execute_playlist_search_and_play(driver, target_playlist["name"], target_playlist["url"])


def focus_browser_window():
    global driver
    if driver:
        try:
            driver.execute_script("window.focus();")
        except:
            pass


def close_browser():
    global driver
    if driver:
        try:
            print("\n[Cleanup] Closing Chrome browser window context...")
            driver.quit()
            driver = None
            print("  -> Clean termination complete.")
        except Exception:
            pass


# ---------------------------------------------------------
# VIRTUAL KEY KEYBOARD HANDLERS & MACROS
# ---------------------------------------------------------

ACTION_HANDLERS = {
    "Play / Pause":
        lambda: ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0)
        or time.sleep(0.05)
        or ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0),

    "Next Track":
        lambda: ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0)
        or time.sleep(0.05)
        or ctypes.windll.user32.keybd_event(0xB0, 0, 2, 0),

    "Previous Track":
        lambda: ctypes.windll.user32.keybd_event(0xB1, 0, 0, 0)
        or time.sleep(0.05)
        or ctypes.windll.user32.keybd_event(0xB1, 0, 2, 0),

    "Volume Up":
        lambda: pyautogui.press("volumeup"),

    "Volume Down":
        lambda: pyautogui.press("volumedown"),

    "Return to Home":
        lambda: safe_return_to_home(driver),

    "Search Album/Playlist":
        lambda: action_search_macro(),
}

def dispatch(brain_state, action_target):
    handler = ACTION_HANDLERS.get(action_target)

    if handler:
        try:
            handler()
            print(f"  -> [Action] Executed: {action_target}")
        except Exception as e:
            print(f"  -> [Error] {action_target}: {e}")
    else:
        print(f"  -> [Warning] No handler for '{action_target}'")


# ---------------------------------------------------------
# MASTER RUNTIME ENGINE
# ---------------------------------------------------------

def apply_commands(input_path: str):
    print(f"Loading commands from: {input_path}")
    with open(input_path, "r") as f:
        data = json.load(f)

    events = data.get("commands", data.get("jiosaavn_commands", []))
    total = len(events)

    if total == 0:
        print("[!] Execution manifest contains no readable instructions.")
        return

    if not launch_and_attach_to_browser():
        return

    try:
        handle_startup_playback(driver)
        print("  -> Holding process loop for 5s to establish initialization stream...")
        time.sleep(5.0)

        for idx, event in enumerate(events, start=1):
            if event.get("status") == "unmapped":
                continue
                
            if event.get("confidence", 0) < 0.5:
                continue

            focus_browser_window()
            
            brain_state = event["raw_brain_state"]
            action_target = event["action_target"]

            print(
                f"\n[Event {idx:02d}/{total:02d}] "
                f"{brain_state} "
                f"(Confidence={event.get('confidence',0):.3f})"
            )
            dispatch(brain_state, action_target)
            time.sleep(DELAY_BETWEEN_EVENTS)

        print("\n[Finished] Core automation event queue successfully resolved!")

    except Exception as e:
        print(f"Fatal stack exception encountered inside engine loop: {e}")
    finally:
        close_browser()


if __name__ == "__main__":
    input_path = Path(__file__).parent / INPUT_FILE
    if not input_path.exists():
        input_path = Path.cwd() / INPUT_FILE

    if not input_path.exists():
        print(f"System error: Initialization manifest file missing: {INPUT_FILE}")
    else:
        apply_commands(str(input_path))