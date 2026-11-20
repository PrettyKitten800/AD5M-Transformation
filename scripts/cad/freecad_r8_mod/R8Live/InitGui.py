"""FreeCAD GUI startup hook loaded via -M to initialize R8_Live_Watcher."""

import os
import sys
from PySide6 import QtCore

_HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else r"C:\Users\PK800\.gemini\antigravity\scratch\AD5M-Transformation\scripts\cad\freecad_r8_mod\R8Live"
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import r8_autostart

QtCore.QTimer.singleShot(1000, r8_autostart.boot)
