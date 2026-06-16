import json
import time
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

INPUT_FILE = "bci_jiosaavn_commands.json"
JIOSAAVN_WEB_URL = "https://www.jiosaavn.com"

# Timing delays to let the browser pages load comfortably
DELAY_BETWEEN_EVENTS = 3.0   
DELAY_PAGE_LOAD      = 4.0   # Ensures web player components stabilize

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
# WEB AUTOMATION CORE HANDLER (SELENIUM ENGINE)
# ---------------------------------------------------------

def execute_web_search_and_play(driver, song_name):
    """
    1. Locates the website search input field, clears it, and types the song.
    2. Waits for the drop-down to appear, selects the top recommended result.
    3. Scans the website HTML code to locate and click either the 'Play' or 'Start Radio' sky-blue buttons.
    """
    print(f"\n[Web Automation] Initializing target routine for: '{song_name}'")
    wait = WebDriverWait(driver, 10)

    try:
        # --- PHASE 1: WEB SEARCH & DROP-DOWN SELECTION ---
        # Locate JioSaavn web search bar input field
        search_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.search-input, input[type='search']")))
        search_input.click()
        
        # Clear any previous text cleanly using keyboard shortcuts
        search_input.send_keys(Keys.CONTROL + "a")
        search_input.send_keys(Keys.DELETE)
        
        # Type the song name row item string
        search_input.send_keys(song_name)
        print("  -> Text typed into web search field. Waiting for drop-down suggestions...")
        time.sleep(1.5)

        # Press Down arrow to jump focus into the first web recommendation element, then press Enter
        search_input.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.3)
        search_input.send_keys(Keys.ENTER)
        
        # --- PHASE 2: TARGETING WEB BUTTON BY ITS HTML CONTENT ---
        print(f"  -> Waiting {DELAY_PAGE_LOAD}s for web player page to stabilize...")
        time.sleep(DELAY_PAGE_LOAD)

        # Look directly for the structural text inside the webpage buttons to find our targets
        # This completely avoids clicking the big poster image overlay on the left
        button_found = False
        possible_web_targets = [
            "//a[contains(text(), 'Start Radio') or contains(., 'Start Radio')]",
            "//button[contains(text(), 'Start Radio') or contains(., 'Start Radio')]",
            "//a[contains(text(), 'Play') or contains(., 'Play')]",
            "//button[contains(text(), 'Play') or contains(., 'Play')]"
        ]

        for xpath in possible_web_targets:
            try:
                # Search for elements currently visible on screen
                elements = driver.find_elements(By.XPATH, xpath)
                for element in elements:
                    if element.is_displayed():
                        # Force browser engine to target and trigger this specific sky-blue block element
                        element.click()
                        print(f"     [Web Inspection Success] Clicked web button element matching: {xpath}")
                        button_found = True
                        break
            except Exception:
                continue
            if button_found:
                break

        if not button_found:
            print("  -> [Web Notice] Text-based button click missed. Attempting global play shortcut fallback...")
            # Fallback to standard web player media activation key shortcut
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SPACE)

    except Exception as e:
        print(f"  -> [Automation Error] Flow interrupted on webpage element: {e}")


# ---------------------------------------------------------
# SYSTEM EXECUTION & LOOP PIPELINE
# ---------------------------------------------------------

def startup_web_session():
    """Initializes the automated Chrome web browser session."""
    print("[Web Launcher] Initializing Chrome Driver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications") # Blocks annoying popups
    
    # Automatic driver management setup
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Open JioSaavn Web Application Home
    driver.get(JIOSAAVN_WEB_URL)
    time.sleep(DELAY_BETWEEN_EVENTS)
    
    # Run an initial sample track playback setup routine
    initial_song = random.choice(SONG_LIST)
    execute_web_search_and_play(driver, initial_song)
    return driver


def apply_web_commands(input_path: str):
    print(f"Loading incoming macro command maps from: {input_path}")
    with open(input_path, "r") as f:
        data = json.load(f)

    events = data["jiosaavn_commands"]
    total  = len(events)

    # Fire up the automated web environment window session
    try:
        driver = startup_web_session()
    except Exception as e:
        print(f"[Fatal Startup Error] Web engine launch failure: {e}")
        return

    print(f"\n[Executor] Tracking {total} input framework pipeline events...\n")
    try:
        for event in events:
            print(f"\n[Event {event['event_id']:02d}/{total}] Processing {event['action_target']}")
            
            # If BCI signals a MACRO match, trigger our exact search and dynamic click sequence
            if event["action_target"] == "MACRO":
                next_song = random.choice(SONG_LIST)
                execute_web_search_and_play(driver, next_song)
            else:
                # Basic media keys fallback behavior inside web page sandbox context
                body = driver.find_element(By.TAG_NAME, "body")
                if event["action_target"] == "VK_MEDIA_PLAY_PAUSE":
                    body.send_keys(Keys.SPACE)
                    print("  -> [Action] Pressed Spacebar shortcut to Play/Pause track.")
                elif event["action_target"] == "VK_MEDIA_NEXT_TRACK":
                    body.send_keys(Keys.SHIFT, "n") # Standard web player media skip shortcut mapping
                    print("  -> [Action] Triggered Next Track shortcut sequence.")
                else:
                    print(f"  -> [Warning] Action '{event['action_target']}' skipped in web instance environment.")
            
            time.sleep(DELAY_BETWEEN_EVENTS)
            
    except KeyboardInterrupt:
        print("\n[Shutting Down] Session interrupted by terminal user.")
    finally:
        print("\n[Pipeline Complete] Retaining open automated window framework instance layout.")
        # Keeping browser open so you can monitor status safely. Change to driver.quit() if auto-closing is preferred.


if __name__ == "__main__":
    input_path = Path(__file__).parent / INPUT_FILE
    if not input_path.exists():
        print(f"Missing configuration properties file error: {input_path}")
    else:
        apply_web_commands(str(input_path))