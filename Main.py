import InputHandler
import pyautogui
import pygetwindow
import time
import os
import keyboard

# Find the Roblox window so all click positions can be offset correctly
# This lets the macro work even if Roblox isn't at (0,0) on the screen
for window in pygetwindow.getAllWindows():
    if window.title == "Roblox":
        rb_window = window
        break

# If Roblox isn't open, immediately stop the script
if not rb_window:
    os._exit(0)

# Top-left corner of the Roblox window
# Every click position below is relative to this offset
dx, dy = (rb_window.left, rb_window.top)

# Keyboard scan codes used by InputHandler.KeyDown / KeyUp
# These are physical key scan codes, not virtual key codes
KEYMAP = {
    "a": 0x1E,
    "s": 0x1F,
    "d": 0x20,
    "f": 0x21,
    "g": 0x22,
    "x": 0x2D,
    "1": 0x02,
    "2": 0x03,
    "3": 0x04,
    "4": 0x05,
    "5": 0x06,
    "6": 0x07,
    "shift": 0x2A
}

# =========================
# Unit placement positions
# =========================
# Predefined world positions where units should be placed
# These are adjusted by the Roblox window offset above
BROOK_POS = (373 + dx, 385 + dy)
ICHIGO_POS = (390 + dx, 318 + dy)
SOKORA_POS = (372 + dx, 185 + dy)
NEWSMAN_P1 = (382 + dx, 337 + dy)
NEWSMAN_P2 = (353 + dx, 336 + dy)

# =========================
# UI positions / references
# =========================
# Screen positions used to interact with menus, abilities, and game state checks
UNIT_CLOSE = (305 + dx, 233 + dy)              # White X close button when a unit panel is open
WAVE_SKIP = (616 + dx, 40 + dy)                # Wave skip white text
ABILITY1 = (333 + dx, 278 + dy)                # First ability button
ABILITY2 = (333 + dx, 338 + dy)                # Second ability button
BROOK_ABILITY_CLOSE = (536 + dx, 139 + dy)     # Close button for brook's ability
STOCK1 = (601 + dx, 41 + dy)                   # First stock indicator
STOCK2 = (459 + dx, 41 + dy)                   # Second stock indicator
STOCK_COLOR = (21, 222, 51)                    # Green color used to detect stock availability
BOSS_ALIVE = (310 + dx, 113 + dy)              # Boss UI indicator still visible = boss alive

def exit(x):
    # Emergency hard stop when ; is pressed
    os._exit(0)

# Register ; as a kill switch for the script
keyboard.on_press_key(";", exit)

def press(key: str) -> None:
    # Simulate a quick key tap using scan codes
    # Press down, wait a tiny amount, then release
    InputHandler.KeyDown(KEYMAP[key])
    time.sleep(0.02)
    InputHandler.KeyUp(KEYMAP[key])

def place(unit: int, pos: tuple[int, int]):
    # Place a unit from the hotbar at a specific map position
    print(f"Placing Unit {unit}")

    # Select unit slot from hotbar
    press(f"{unit}")

    # Click the map position to place the unit
    InputHandler.Click(*pos, delay=0.1)

    # Wait until the unit info panel opens
    # This confirms the unit was actually placed and selected
    while not pyautogui.pixelMatchesColor(*UNIT_CLOSE, expectedRGBColor=(255, 255, 255)):
        time.sleep(0.01)

def select(pos: tuple[int, int]):
    # Select an already placed unit by clicking its map position
    print(f"Selecting Unit at {pos}")

    # First close any currently open unit panel so selection is clean
    InputHandler.Click(*UNIT_CLOSE, delay=0.1)

    # Timer used so we can retry if the click doesn't register
    timedelta = time.time()

    # Attempt initial selection click
    InputHandler.Click(*pos, delay=0.1)

    # Wait until the unit opens, which confirms selection
    while not pyautogui.pixelMatchesColor(*UNIT_CLOSE, expectedRGBColor=(255, 255, 255)):
        # If too much time passes, try clicking the unit again
        if time.time() - timedelta > 0.9:
            InputHandler.Click(*pos, delay=0.1)
            timedelta = time.time()
        time.sleep(0.01)

def brook_buff():
    # Brook Buff
    print(f"Doing Brook Buff")

    start = time.time()
    brook = False
    keys = ["a", "s", "d", "f", "g"]

    # Move cursor on brook X
    InputHandler.MoveTo(*BROOK_ABILITY_CLOSE)

    while not brook:
        # If the Brook prompt is visible (white pixel), the rhythm window is active
        if pyautogui.pixelMatchesColor(*BROOK_ABILITY_CLOSE, (255, 255, 255)):
            # Make sure all keys are released first
            for k in keys:
                InputHandler.KeyUp(KEYMAP[k])

            # Press all rhythm keys
            for k in keys:
                InputHandler.KeyDown(KEYMAP[k])

            time.sleep(0.02)

            # Release all rhythm keys
            for k in keys:
                InputHandler.KeyUp(KEYMAP[k])

            # Wait till 6 seconds to check if wave skip
            if time.time() - start > 6:
                if pyautogui.pixelMatchesColor(*WAVE_SKIP, expectedRGBColor=(255, 255, 255)):
                    print("Waveskip")
                    break
        else:
            # If the prompt isn't visible yet, keep trying to activate ability 1
            InputHandler.Click(*ABILITY1, delay=0.1)

    # Close Brook's ability UI when done
    InputHandler.Click(*BROOK_ABILITY_CLOSE, 0.1)

def main_loop():
    while True:
        # =========================
        # Pre-match setup / lobby
        # =========================

        # If the unit manager is open, close it with F
        # This keeps the macro starting from a clean UI state
        if pyautogui.pixelMatchesColor(615 + dx, 88 + dy, (11, 231, 241)):
            press("f")

        # Wait until the spawn/start UI appears
        print("Waiting for spawn.")
        while not pyautogui.pixelMatchesColor(394 + dx, 123 + dy, expectedRGBColor=(10, 10, 10)):
            time.sleep(0.1)

        # Spam the start button while it is still visible
        # Once it disappears, the match has started
        while pyautogui.pixelMatchesColor(394 + dx, 123 + dy, expectedRGBColor=(10, 10, 10)):
            InputHandler.Click(472 + dx, 127 + dy, 0.1)
            time.sleep(0.3)

        print("Match Started")

        # =========================
        # Early setup
        # =========================

        # Place Brook first
        place(4, BROOK_POS)

        # Place Ichigo next
        place(1, ICHIGO_POS)

        # Select Brook and open ability 1, then buff
        select(BROOK_POS)
        InputHandler.Click(*ABILITY1, delay=0.1)
        brook_buff()

        # =========================
        # Place Newsman (multi-place)
        # =========================

        # Select Newsman slot
        press("5")

        # Hold shift to place multiple units without reselecting the hotbar slot
        InputHandler.KeyDown(KEYMAP["shift"])
        time.sleep(0.3)

        # Place at both positions 
        InputHandler.Click(*NEWSMAN_P1, delay=0.1)
        InputHandler.Click(*NEWSMAN_P2, delay=0.1)

        time.sleep(0.3)
        InputHandler.KeyUp(KEYMAP["shift"])

        # Place Sokora
        place(3, SOKORA_POS)

        # =========================
        # Sokora ability loop -> Ichigo target
        # =========================

        # While stock 1 is available, repeatedly use Sokora's first ability targeting Ichigo
        while pyautogui.pixelMatchesColor(*STOCK1, STOCK_COLOR):
            select(SOKORA_POS)
            InputHandler.Click(*ABILITY1, delay=0.1)
            InputHandler.Click(*ICHIGO_POS, delay=0.1)
            time.sleep(0.4)

        # Open unit manager 
        press("f")

        # Wait until the unit manager is open
        while not pyautogui.pixelMatchesColor(615 + dx, 88 + dy, (11, 231, 241)):
            time.sleep(0.1)

        # =========================
        # Sokora ability loop -> Gohan search
        # =========================

        # Select Sokora again for next target cycle
        select(SOKORA_POS)

        Gohan_Found = False
        while not Gohan_Found:
            print("Gohan")

            # If Sokora somehow becomes deselected / bad UI state, reselect
            if pyautogui.pixelMatchesColor(332 + dx, 317 + dy, expectedRGBColor=(216, 14, 18), tolerance=50):
                select(SOKORA_POS)

            # Activate Sokora's ability
            InputHandler.Click(*ABILITY1, delay=0.1)

            # Search screen region for Gohan image
            gohan_location = pyautogui.locateOnScreen(
                image=os.path.join(os.path.dirname(os.path.abspath(__file__)), "Gohan.png"),
                grayscale=True,
                region=(435 + dx, 76 + dy, 792 + dx, 511 + dy),
                confidence=0.7
            )

            # If found, click gohan
            if gohan_location:
                print("Found")
                InputHandler.Click(*pyautogui.center(gohan_location), delay=0.1)

            time.sleep(0.4)

            # Stop when stock 2 is gone
            if not pyautogui.pixelMatchesColor(*STOCK2, STOCK_COLOR, tolerance=40):
                break

        # Unit Manager
        press("f")

        # Sell Sokora
        select(SOKORA_POS)
        press("x")

        # Select Brook for the boss phase
        select(BROOK_POS)

        # Wait until the boss UI disappears, meaning the boss is dead
        while pyautogui.pixelMatchesColor(*BOSS_ALIVE, (255, 255, 255)):
            time.sleep(0.01)

        # Small delay after boss death
        time.sleep(4)

        # Re-select Brook
        select(BROOK_POS)

        # Keep trying to activate ability 2 match ends
        while not pyautogui.pixelMatchesColor(725 + dx, 169 + dy, (255, 255, 255)):
            InputHandler.Click(*ABILITY2, delay=0.1)
            time.sleep(0.1)

        # While match edned, click retry epeatedly
        while pyautogui.pixelMatchesColor(725 + dx, 169 + dy, (255, 255, 255)):
            InputHandler.Click(374 + dx, 474 + dy, 0.1)
            time.sleep(0.1)

main_loop()