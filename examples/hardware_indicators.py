"""Example demonstrating hardware status indicators (Windows NumLock and volume feedback).

Isolated as an optional example to avoid altering system volume or keyboard state in the core library.
"""

import sys

if sys.platform != "win32":
    print("This hardware demo requires Windows.")
    sys.exit(0)

import ctypes

dll = ctypes.WinDLL("User32.dll")


def set_numlock(action: str) -> None:
    """Toggle NumLock LED on or off."""
    numlock = 0x90
    current_state = dll.GetKeyState(numlock) & 0x0001
    if action == "on" and not current_state:
        dll.keybd_event(numlock, 0x45, 0x1, 0)
        dll.keybd_event(numlock, 0x45, 0x1 | 0x2, 0)
    elif action == "off" and current_state:
        dll.keybd_event(numlock, 0x45, 0x1, 0)
        dll.keybd_event(numlock, 0x45, 0x1 | 0x2, 0)


def is_numlock_on() -> bool:
    VK_NUMLOCK = 0x90
    return ctypes.windll.user32.GetKeyState(VK_NUMLOCK) & 1 != 0


def main() -> None:
    print(f"NumLock is currently: {'ON' if is_numlock_on() else 'OFF'}")
    print("Toggling NumLock as a hardware feedback signal...")
    set_numlock("on" if not is_numlock_on() else "off")
    print(f"NumLock is now: {'ON' if is_numlock_on() else 'OFF'}")


if __name__ == "__main__":
    main()
