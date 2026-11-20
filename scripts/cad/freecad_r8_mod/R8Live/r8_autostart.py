"""Persistent autostart module kept in sys.modules to boot R8_Live_Watcher in FreeCAD GUI."""

from __future__ import annotations

from pathlib import Path
from PySide6 import QtCore
import FreeCAD as App
import FreeCADGui as Gui

WATCHER_MACRO = Path(r"C:\Users\PK800\.gemini\antigravity\scratch\AD5M-Transformation\scripts\cad\R8_Live_Watcher.FCMacro")
WORKSPACE_PATH = Path(r"C:\Users\PK800\.gemini\antigravity\scratch\AD5M-Transformation\outputs\BambuMod_Orbiter25_Remix_R8\R8_Live_Workspace.FCStd")


def boot(attempt: int = 0) -> None:
    """Wait until R8_Live_Workspace is open in GUI, then execute R8_Live_Watcher.FCMacro."""
    doc = App.getDocument("R8_Live_Workspace")
    if doc is None:
        if attempt < 25:
            QtCore.QTimer.singleShot(400, lambda n=attempt + 1: boot(n))
            return
        if WORKSPACE_PATH.exists():
            doc = App.openDocument(str(WORKSPACE_PATH))
    if doc is None or not WATCHER_MACRO.exists():
        return
    try:
        ns: dict = {"__name__": "__main__", "__file__": str(WATCHER_MACRO)}
        exec(compile(WATCHER_MACRO.read_text(encoding="utf-8"), str(WATCHER_MACRO), "exec"), ns)
        view = Gui.ActiveDocument.ActiveView if Gui.ActiveDocument else None
        if view is not None:
            view.viewIsometric()
            view.fitAll()
    except Exception as exc:
        App.Console.PrintError(f"[R8Live autostart] Failed: {exc}\n")
