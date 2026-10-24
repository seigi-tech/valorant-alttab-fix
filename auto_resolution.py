"""Valorant alt-tab fix: when you alt-tab out of Valorant, hide the game and restore your desktop resolution
instantly instead of waiting for the game (which, with two monitors, often leaves the desktop stretched).

Valorant still switches to its own resolution when you come back; this only handles leaving the game.
"""
import ctypes
import os
import time
from ctypes import wintypes

GAME_EXE = "valorant-win64-shipping.exe"
EVENT_SYSTEM_FOREGROUND = 0x0003
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SW_SHOWMINNOACTIVE = 7  # minimize without giving the window focus back
GWL_EXSTYLE, WS_EX_TOPMOST = -20, 0x8
HWND_TOPMOST, HWND_NOTOPMOST = -1, -2
SWP_KEEP = 0x0001 | 0x0002 | 0x0010 | 0x4000  # no size, no move, no activate, async (never blocks on a busy app)

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.ShowWindowAsync.argtypes = [wintypes.HWND, ctypes.c_int]
user32.IsIconic.argtypes = [wintypes.HWND]
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_uint]

WinEventProc = ctypes.WINFUNCTYPE(None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,
                                  wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD)


def exe_name(hwnd):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return ""
    buf = ctypes.create_unicode_buffer(260)
    size = wintypes.DWORD(len(buf))
    kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size))
    kernel32.CloseHandle(handle)
    return os.path.basename(buf.value).lower()


game_hwnd = None
in_game = False


@WinEventProc
def on_foreground(hook, event, hwnd, *_):
    global game_hwnd, in_game
    if exe_name(hwnd) == GAME_EXE:
        game_hwnd, in_game = hwnd, True
        return
    if not in_game:
        return
    in_game = False
    # The game is always-on-top while playing and, when busy, can take ~2 s to minimize and drop that.
    # Minimize it ourselves, and until it is, lift whatever window you switched to above it.
    user32.ShowWindowAsync(game_hwnd, SW_SHOWMINNOACTIVE)
    start = time.perf_counter()
    lifted = []
    resolution_restored = False
    while not user32.IsIconic(game_hwnd) and time.perf_counter() - start < 3:
        fg = user32.GetForegroundWindow() or hwnd  # no foreground for a moment while the game is busy
        if fg == game_hwnd:
            break  # back in the game
        if fg and fg not in lifted and not user32.GetWindowLongW(fg, GWL_EXSTYLE) & WS_EX_TOPMOST:
            user32.SetWindowPos(fg, HWND_TOPMOST, 0, 0, 0, 0, SWP_KEEP)
            lifted.append(fg)
        if not resolution_restored and time.perf_counter() - start > 0.5:
            # restoring before the game is minimized makes it handle the resolution change first
            user32.ChangeDisplaySettingsW(None, 0)
            resolution_restored = True
        time.sleep(0.002)
    for w in lifted:
        user32.SetWindowPos(w, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_KEEP)
    if not resolution_restored and user32.GetForegroundWindow() != game_hwnd:
        user32.ChangeDisplaySettingsW(None, 0)  # back to the resolution saved in Windows; no-op if already there


if __name__ == "__main__":
    # Windows calls on_foreground on every active window change, with no polling
    user32.SetWinEventHook(EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_FOREGROUND, None, on_foreground, 0, 0, 0)
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        pass
