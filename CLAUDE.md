# auto-resolution

Publié sur GitHub sous le nom `valorant-alttab-fix` : quand on quitte Valorant par alt-tab, réduit le jeu et remet tout de suite la résolution enregistrée dans Windows, sans attendre le jeu.

## Notes

- Tout le code est dans `auto_resolution.py` (Python standard + ctypes, aucune dépendance).
- Exe : `python -m PyInstaller --onefile --noconsole --name ValorantAltTabFix auto_resolution.py` → `dist/`, publié en release GitHub.
- `.bench.py` (non versionné) mesure des alt-tab Valorant → Chrome ; il faut que Valorant et une fenêtre Chrome sur l'écran principal soient ouverts.
