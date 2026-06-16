# JioSaavn Automation Code Explanation

This document explains the JioSaavn automation script in a beginner-friendly way. A new user should be able to understand what the script does, how the parts are connected, and where to make changes if needed.

---

# What This Script Does

This script connects brain-state commands (stored in a JSON file) with JioSaavn music playback using Google Chrome.

In simple terms:

- It reads automation commands from `jiosaavn_commands.json`.
- It opens Google Chrome and automatically logs you into JioSaavn using a saved profile.
- It ensures music is playing as soon as the browser opens.
- It maps each command to a specific music action.
- It can press Play/Pause, skip tracks, and adjust volume using low-level Windows hardware keys.
- If instructed to search, it opens a random Telugu playlist and uses an advanced `ActionChains` macro to click the Big Green Play button.
- It safely closes the browser when all commands are finished.

---

# 1) Imports

```python
import json
import ctypes
import time
import random
import os
from pathlib import Path
import pyautogui

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
```

These imports load everything the script needs.

- **json**: Reads the command file.
- **ctypes**: Sends Windows media key events.
- **time**: Adds delays.
- **random**: Chooses a random playlist.
- **os** and **Path**: Locate the Chrome profile folder.
- **pyautogui**: Controls volume keys.
- **selenium**: Opens Chrome and controls the web page.

---

# 2) Configuration

```python
INPUT_FILE = "jiosaavn_commands.json"
DELAY_BETWEEN_EVENTS = 3.0
DELAY_PAGE_LOAD = 3.0

PLAYLIST_LIST = [
    "playlist_url_1",
    "playlist_url_2"
]

driver = None
```

These values make the program easier to configure.

- `INPUT_FILE` – JSON file containing commands.
- `DELAY_BETWEEN_EVENTS` – Wait time between commands.
- `DELAY_PAGE_LOAD` – Wait time for page loading.
- `PLAYLIST_LIST` – List of playlists used by the search macro.

---

# 3) Mandatory Startup Clicker

```python
def click_homepage_play_button(web_driver):
    print("Starting the current song...")
```

This function makes sure music starts playing before commands are processed.

---

# 4) Bulletproof Mouse Movement (Green Play Button)

```python
def click_green_play_button(web_driver):
    wait = WebDriverWait(web_driver, 15)
```

This function finds and clicks the Big Green Play button using Selenium's `ActionChains`.

---

# 5) Playlist Navigation & Browser Setup

```python
def execute_playlist_search_and_play(web_driver, playlist_url):
    web_driver.get(playlist_url)
```

This function opens a playlist and starts playing it.

---

# 6) Action Handlers (Key Mapping)

```python
ACTION_HANDLERS = {
    "VK_MEDIA_PLAY_PAUSE": ...,
    "VK_VOLUME_UP": ...
}
```

This dictionary maps commands to keyboard actions.

---

# 7) Main Execution Pipeline

```python
def apply_commands(input_path):
    with open(input_path, "r") as f:
        data = json.load(f)
```

This is the main function that:

1. Reads the JSON file.
2. Opens Chrome.
3. Starts music.
4. Processes each command.
5. Closes the browser.

---

# Full Command Flow

```text
Start Script
     |
Load jiosaavn_commands.json
     |
Open Google Chrome
     |
Start Current Music
     |
For each command:
     |
     |-- Search Macro
     |-- Media Key Action
     |
Wait 3 Seconds
     |
Close Browser
```

---

# Important Design Points

- **Persistent Login** using a saved Chrome profile.
- **DPI Scaling Immunity** using `ActionChains`.
- **Safe Fallbacks** if buttons are not found.

---

# Where to Modify the Script

| What You Want to Change | Where to Look |
|-------------------------|--------------|
| Add new playlist URLs | `PLAYLIST_LIST` |
| Change command delay | `DELAY_BETWEEN_EVENTS` |
| Change page load delay | `DELAY_PAGE_LOAD` |
| Add new macro triggers | `dispatch()` |
| Add new keyboard keys | `ACTION_HANDLERS` |

---

# Final Summary

This script acts as a bridge between brain-state commands and JioSaavn music playback. It uses Selenium for browser automation and Windows media keys for playback control, making the system reliable and easy to extend.