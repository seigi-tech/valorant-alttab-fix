"""Remet l'écran principal en résolution native dès qu'on quitte Valorant (alt-tab).

Valorant gère lui-même le passage en 4:3 ; ce script ne fait que le retour, sans attendre le jeu.
Lancer sans console : pythonw auto_resolution.py
"""
import ctypes
import os
from ctypes import wintypes

GAME_EXE = "valorant-win64-shipping.exe"
GAME_WIDTH = 1440  # largeur de la résolution 4:3 utilisée dans Valorant
EVENT_SYSTEM_FOREGROUND = 0x0003
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.SetProcessDPIAware()  # sinon GetSystemMetrics renvoie une largeur mise à l'échelle

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


@WinEventProc
def on_foreground(hook, event, hwnd, *_):
    if user32.GetSystemMetrics(0) == GAME_WIDTH and exe_name(hwnd) != GAME_EXE:
        user32.ChangeDisplaySettingsW(None, 0)  # remet la résolution enregistrée dans Windows


if __name__ == "__main__":
    # Windows appelle on_foreground à chaque changement de fenêtre active, sans délai
    user32.SetWinEventHook(EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_FOREGROUND, None, on_foreground, 0, 0, 0)
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        pass
