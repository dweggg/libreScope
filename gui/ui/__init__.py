"""
UI Module
=======

Provides user interface components for the serial data application.
"""

from gui.ui.focus_manager import FocusManager
from gui.ui.logger_widget import CSVLoggerWidget, TerminalLogWidget
from gui.ui.plot_widget import Plot
from gui.ui.tiling_area import TilingArea
from gui.ui.menu_system import setup_menu_system, MenuSystem

__all__ = [
    'FocusManager',
    'CSVLoggerWidget',
    'TerminalLogWidget',
    'Plot',
    'TilingArea',
    'setup_menu_system',
    'MenuSystem'
]