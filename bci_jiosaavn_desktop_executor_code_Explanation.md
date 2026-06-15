#  JioSaavn Automation System (BCI Controlled)

---

##  Project Overview

This project automates the **JioSaavn Web Music Player** using Python + Selenium.

It reads commands from a **Brain-Computer Interface (BCI) JSON file** and performs actions like:

- ▶ Play / Pause  
- ⏭ Next Track  
- ⏮ Previous Track  
- 🔊 Volume Control  
- 🎵 Smart Search & Play Songs  
- 🤖 Macro (Random Song Playback)  

---
##  Complete Workflow

```text
Start Program
      |
Load JSON Commands
      |
Kill Old Chrome Sessions
      |
Launch Chrome with Profile
      |
Open JioSaavn Website
      |
Initialize Playback
      |
Read Commands One by One
      |
Dispatch Action (Media / Macro)
      |
Execute in Browser
      |
Wait Between Events
      |
Close Browser
      |
End Program
```

---

##  1. Import Statements

```python
import json
import ctypes
import time
import random
import os
import subprocess
from pathlib import Path
import pyautogui

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
```

### Explanation

- `json` → Reads BCI command file  
- `ctypes` → Sends Windows media keys  
- `time` → Adds delays  
- `random` → Picks random songs for MACRO mode  
- `os`, `Path` → File handling  
- `subprocess` → Kills Chrome processes  
- `pyautogui` → Controls volume keys  
- `selenium` → Browser automation  

---

##  2. Configuration

```python
INPUT_FILE = "bci_jiosaavn_commands.json"

DELAY_BETWEEN_EVENTS = 3.0
DELAY_PAGE_LOAD = 5.0

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

driver = None
```

### Explanation

- Input file → command source  
- Delay → prevents UI lag  
- SONG_LIST → used in MACRO mode  
- driver → Selenium browser instance  

---

##  3. Chrome Process Management

```python
def wipe_chrome_processes():
    subprocess.run("taskkill /F /IM chrome.exe /T", shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM chromedriver.exe /T", shell=True, capture_output=True)
```

---

##  4. Browser Cleanup

```python
def cleanup_browser():
    global driver
    if driver:
        try:
            driver.quit()
        except:
            pass

    wipe_chrome_processes()
```

---

##  5. Browser Launch

```python
def launch_and_attach_to_browser():
```

### Explanation

- Opens Chrome with Selenium  
- Uses saved profile (keeps login)  
- Opens JioSaavn  

---

##  6. Play Initialization

```python
def click_homepage_play_button(web_driver):
```

### Logic

- Try Play button  
- If fails → click body  
- If fails → SPACE key  

---

## 🎵 7. Search & Play Engine

```python
def execute_search_and_play_sequence(web_driver, song_name):
```

### Steps

1. Pause current music  
2. Close popups  
3. Open search bar  
4. Type song  
5. Press ENTER  
6. Wait for results  
7. Hover first result  
8. Click Play  
9. Fallback → SPACE  

---

## 8. Macro Function

```python
def action_search_macro():
```

- Picks random song  
- Runs search engine  

---

## 9. Focus Browser

```python
def focus_browser_window():
```

- Brings Chrome to front  

---

##  10. Action Handlers

```python
ACTION_HANDLERS = {
    "VK_MEDIA_PLAY_PAUSE": ...,
    "VK_MEDIA_NEXT_TRACK": ...,
    "VK_MEDIA_PREV_TRACK": ...,
    "VK_VOLUME_UP": ...,
    "VK_VOLUME_DOWN": ...
}
```

### Mapping

| Command | Action |
|--------|--------|
| Play/Pause | Media Key |
| Next | Media Key |
| Previous | Media Key |
| Volume Up | PyAutoGUI |
| Volume Down | PyAutoGUI |

---

##  11. Dispatcher

```python
def dispatch(action_target):
```

- MACRO → random song  
- Else → system media key  

---

##  12. Main Pipeline

```python
def apply_commands(input_path: str):
```

### Flow

1. Load JSON  
2. Launch Chrome  
3. Open JioSaavn  
4. Loop commands  
5. Execute actions  
6. Wait  
7. Cleanup  

---

##  13. Entry Point

```python
if __name__ == "__main__":
```

- Starts script only when run directly  

---

##  FINAL FLOW

```text
JSON → Python → Selenium → JioSaavn → Media Control → Music Output 🎧
```

---

## FINAL SUMMARY

This system acts as:

- Brain-command music controller  
- Selenium automation engine  
- Windows media controller  
- Smart playlist system  