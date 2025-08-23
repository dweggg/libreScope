"""
Signals Module
=============

Barebones signals provider hook and a list widget. No built-in definitions.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6 import QtWidgets, QtCore, QtGui

_GLOBAL_SIGNALS_PROVIDER = None


def set_signals_provider(provider):
    """Set a global signals provider used by helper functions and UI widgets."""
    global _GLOBAL_SIGNALS_PROVIDER
    _GLOBAL_SIGNALS_PROVIDER = provider


def get_signal_direction(signal_key: str) -> Optional[str]:
    """Global helper routing to the installed signals provider."""
    if _GLOBAL_SIGNALS_PROVIDER is None:
        return None
    try:
        return _GLOBAL_SIGNALS_PROVIDER.get_signal_direction(signal_key)
    except Exception:
        return None


def get_signal_name(signal_key: str) -> str:
    """Global helper routing to the installed signals provider."""
    if _GLOBAL_SIGNALS_PROVIDER is None:
        return signal_key
    try:
        return _GLOBAL_SIGNALS_PROVIDER.get_signal_name(signal_key)
    except Exception:
        return signal_key


class SignalDefinitions:
    """Deprecated JSON-backed definitions removed; kept for compatibility."""
    def __init__(self, database_file: str):
        self.signal_dict: Dict[str, Dict[str, str]] = {}
    def get_signal_direction(self, signal_key: str) -> Optional[str]:
        return None
    def get_signal_name(self, signal_key: str) -> str:
        return signal_key
    def get_all_keys(self) -> Dict[str, Dict[str, str]]:
        return {}


class SignalsList(QtWidgets.QListWidget):
    """Widget that displays a draggable list of available signals."""
    
    def __init__(self, signal_definitions: SignalDefinitions | None, parent=None):
        """
        Initialize the signals list widget.
        
        Args:
            signal_definitions: SignalDefinitions instance with signal metadata
            parent: Parent widget
        """
        super().__init__(parent)
        self.signal_definitions = signal_definitions
        self.setDragEnabled(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.populate_list()
    
    def populate_list(self) -> None:
        """Populate the list with signal names from the definitions."""
        self.clear()
        signals = {}
        if _GLOBAL_SIGNALS_PROVIDER is not None:
            try:
                signals = _GLOBAL_SIGNALS_PROVIDER.get_all_keys()
            except Exception:
                signals = {}
        for signal, info in signals.items():
            item_text = f"{info['name']}"  # Show human-readable name
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, signal)  # Store signal key as metadata
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsDragEnabled)
            self.addItem(item)
    
    def startDrag(self, supportedActions):
        """Override startDrag to customize drag behavior."""
        if self.currentItem() is None:
            return
            
        drag = QtGui.QDrag(self)
        mime_data = QtCore.QMimeData()
        
        # Get the signal key (not the display name)
        signal_key = self.currentItem().data(QtCore.Qt.ItemDataRole.UserRole)
        mime_data.setText(signal_key)
        
        drag.setMimeData(mime_data)
        
        # Set a transparent pixmap for cleaner drag experience
        pixmap = QtGui.QPixmap(1, 1)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        drag.setPixmap(pixmap)
        
        # Execute the drag
        drag.exec(supportedActions)