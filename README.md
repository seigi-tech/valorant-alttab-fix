# Valorant Alt-Tab Fix

Playing Valorant in stretched 4:3 (1440×1080, 1280×960…) with two monitors? Then you know the pain:
you alt-tab out and your desktop **stays stretched**, or the game **stays on screen for a second or two**
before going away.

This tiny background program fixes it. As soon as you leave Valorant, it hides the game and puts your
desktop back to its normal resolution, without waiting for the game to do it.

Measured over 9 alt-tabs from Valorant to Chrome on the main monitor, with two monitors:

|                                  | Without                     | With                  |
|----------------------------------|-----------------------------|-----------------------|
| Desktop back to its resolution   | 1 / 9 (stays 4:3 otherwise) | 9 / 9, in ~200 ms     |
| Game hidden, usual case          | ~10 ms                      | ~10 ms                |
| Game hidden, when the game lags  | 0.3 – 2 s                   | 0.25 – 0.35 s         |

The ~200 ms left is the resolution change itself, which no program can speed up.

## Install

1. Download `ValorantAltTabFix.exe` from the [latest release](../../releases/latest).
2. Run it. Nothing shows up: it runs in the background (you can see it in Task Manager).
3. To start it with Windows: press `Win + R`, type `shell:startup`, and put a shortcut to the exe in that folder.

To stop it, end `ValorantAltTabFix.exe` in Task Manager.

Windows may warn about an unknown publisher (click **More info → Run anyway**), and some antivirus tools flag
any program packaged with PyInstaller. The full source is the single file `auto_resolution.py` (~90 lines),
so you can read it or run it directly with Python instead: `pythonw auto_resolution.py`.

## Tip: make resolution changes faster

In the NVIDIA Control Panel → *Adjust desktop size and position*, set scaling mode to **Full-screen** and
**Perform scaling on: GPU**. The monitor then never resyncs when the resolution changes, so every switch
(in and out of the game) is much quicker. On AMD: enable **GPU Scaling** in Adrenalin.

## How it works

- Windows notifies the program each time the active window changes (no polling, 0% CPU, ~15 MB RAM).
- When you leave Valorant, it minimizes the game window. While the game is busy, it keeps the window you
  switched to above it.
- Then it restores the resolution saved in Windows. Valorant still sets its own resolution when you come back.

It doesn't read or touch the game's memory or files, only standard Windows window and display functions
(the same ones Windows uses on alt-tab). It's not affiliated with Riot Games; use it at your own risk.

## En français

Petit programme qui tourne en arrière-plan : quand tu fais alt-tab depuis Valorant en 4:3 étiré, il cache
le jeu et remet tout de suite ton bureau en résolution normale, au lieu d'attendre le jeu (qui, avec deux
écrans, oublie souvent de le faire). Télécharge l'exe dans les releases et lance-le ; pour le démarrage
automatique, mets un raccourci dans `shell:startup`.
