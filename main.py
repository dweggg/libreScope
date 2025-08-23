#!/usr/bin/env python3
"""
Generic GUI Shell
=================

Main application entry point for the data visualization shell.
Relies solely on user-provided protocol and signals provider.
"""

import sys
import time
from pathlib import Path
from PyQt6 import QtWidgets, QtCore, QtGui

# Import from the gui package
from gui.utils.config import CONFIG
from gui.data.signals import SignalDefinitions, SignalsList
from gui.data.data_manager import DataManager
from gui.communication.comm_manager import CommunicationManager
from gui.utils.plugins import bootstrap_plugins
from gui.ui.focus_manager import FocusManager
from gui.ui.logger_widget import CSVLoggerWidget, TerminalLogWidget
from gui.ui.plot_widget import Plot
from gui.ui.tiling_area import TilingArea
from gui.ui.menu_system import setup_menu_system


class MainApplication:
    """Main application class for the GUI shell."""

    def __init__(self):
        # App
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setApplicationName("libreScope")

        # Plugins (user-provided only)
        signals_provider, protocol = bootstrap_plugins(CONFIG)

        # Data/Signals
        self.signal_definitions = SignalDefinitions("")
        self.data_manager = DataManager(max_points=CONFIG['max_points'])
        self.data_manager.initialize_signals(self.signal_definitions.get_all_keys())

        # Communication
        self.comm_manager = CommunicationManager(protocol=protocol)
        self.comm_manager.register_data_callback(self._on_data_received)

        # State
        self.freeze_plots = False

        # UI
        self._setup_ui()
        self._setup_timers()

    def _setup_ui(self):
        # Window
        self.main_window = QtWidgets.QMainWindow()
        self.main_window.setWindowTitle("libreScope")
        self.main_window.resize(1400, 800)

        # Central
        self.central_widget = QtWidgets.QWidget()
        self.main_window.setCentralWidget(self.central_widget)
        central_layout = QtWidgets.QHBoxLayout(self.central_widget)

        # Left column
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)

        self.terminal_log = TerminalLogWidget()
        signals_group = QtWidgets.QGroupBox("Signals")
        signals_layout = QtWidgets.QVBoxLayout(signals_group)
        self.signals_list = SignalsList(self.signal_definitions)
        signals_layout.addWidget(self.signals_list)
        self.csv_logger = CSVLoggerWidget(self.data_manager)

        left_layout.addWidget(self.terminal_log, 1)
        left_layout.addWidget(signals_group, 2)
        left_layout.addWidget(self.csv_logger, 1)

        # Right column
        self.tiling_area = TilingArea()
        self.tiling_area.data_manager = self.data_manager
        self.tiling_area.comm_manager = self.comm_manager

        # Splitter
        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        central_layout.addWidget(self.main_splitter)
        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(self.tiling_area)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 3)

        # Menus and indicators
        self.menu_system = setup_menu_system(self.main_window, self.tiling_area)
        self._connect_menu_actions()
        self._setup_indicators()
        self._connect_signals()

        # Logs
        sys.stdout = self.terminal_log
        sys.stderr = self.terminal_log
        print("libreScope started. Provide user_protocol.py and user_database.py to enable IO and signals.")

    def _connect_menu_actions(self):
        for action in self.main_window.findChildren(QtGui.QAction):
            if action.text() == "Clear &All Data":
                action.triggered.connect(self._clear_all_data)

    def _setup_indicators(self):
        self.freeze_indicator = QtWidgets.QLabel()
        self.freeze_indicator.setFixedSize(20, 20)
        self.freeze_indicator.setStyleSheet("background-color: lightgray; border-radius: 10px;")
        self.freeze_indicator.setToolTip("Plot Updates Status: Running")

        self.connection_indicator = QtWidgets.QPushButton("")
        self.connection_indicator.setFixedSize(20, 20)
        self.connection_indicator.setStyleSheet("background-color: red; border-radius: 10px;")
        self.connection_indicator.setFlat(True)
        self.connection_indicator.setToolTip("Connection: Disconnected")

        self.status_label = QtWidgets.QLabel("Ready")

        corner_container = QtWidgets.QWidget()
        corner_layout = QtWidgets.QHBoxLayout(corner_container)
        corner_layout.setContentsMargins(5, 0, 5, 0)
        corner_layout.setSpacing(10)
        corner_layout.addWidget(self.status_label)
        corner_layout.addWidget(self.freeze_indicator)
        corner_layout.addWidget(self.connection_indicator)
        self.main_window.menuBar().setCornerWidget(corner_container, QtCore.Qt.Corner.TopRightCorner)

    def _connect_signals(self):
        self.connection_indicator.clicked.connect(self._toggle_connection)
        self.signals_list.itemDoubleClicked.connect(self._add_variable_to_selected)
        self.original_keyPressEvent = self.main_window.keyPressEvent
        self.main_window.keyPressEvent = self._custom_keyPressEvent

    def _setup_timers(self):
        self.main_timer = QtCore.QTimer()
        self.main_timer.timeout.connect(self._update)
        self.main_timer.start(CONFIG['update_interval_ms'])

        self.plot_timer = QtCore.QTimer()
        self.plot_timer.timeout.connect(self._update_plots)
        self.plot_timer.start(CONFIG['plot_update_interval_ms'])

    def _on_data_received(self, key, value, timestamp):
        self.data_manager.add_data_point(key, value)

    def _update(self):
        self.data_manager.log_data_point()
        self._update_indicators()

    def _update_plots(self):
        if not self.freeze_plots:
            for plot in self.tiling_area.plots:
                plot.update_plot()

    def _update_indicators(self):
        if not self.comm_manager.is_connected():
            self.connection_indicator.setStyleSheet("background-color: red; border-radius: 10px;")
            self.connection_indicator.setToolTip("Connection: Disconnected")
        elif time.time() - self.comm_manager.last_ok_time > 1.0:
            self.connection_indicator.setStyleSheet("background-color: orange; border-radius: 10px;")
            self.connection_indicator.setToolTip("Connection: No heartbeat")
        else:
            self.connection_indicator.setStyleSheet("background-color: green; border-radius: 10px;")
            self.connection_indicator.setToolTip("Connection: Connected")

        if self.freeze_plots:
            self.freeze_indicator.setStyleSheet("background-color: blue; border-radius: 10px;")
            self.freeze_indicator.setToolTip("Plot Updates: Paused (Press Space to resume)")
        else:
            self.freeze_indicator.setStyleSheet("background-color: lightgray; border-radius: 10px;")
            self.freeze_indicator.setToolTip("Plot Updates: Running (Press Space to pause)")

    def _toggle_connection(self):
        is_connected = self.comm_manager.toggle_connection()
        self.status_label.setText("Connected" if is_connected else "Disconnected")

    def _add_variable_to_selected(self, item):
        signal = item.data(QtCore.Qt.ItemDataRole.UserRole)
        active_widget = FocusManager.get_active()
        if active_widget is None:
            self.status_label.setText("Select a plot or logger first")
            return
        if isinstance(active_widget, CSVLoggerWidget):
            active_widget.toggle_signal(signal)
            self.status_label.setText(f"Toggled {signal} in Logger")
        elif isinstance(active_widget, Plot):
            if signal not in active_widget.signal_keys_assigned:
                active_widget.add_signal(signal)
                self.status_label.setText(f"Added {signal} to plot")
            else:
                active_widget.remove_signal(signal)
                self.status_label.setText(f"Removed {signal} from plot")
        else:
            self.status_label.setText("Cannot add signals to this widget")

    def _custom_keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Space:
            self.freeze_plots = not self.freeze_plots
            self.status_label.setText("Plot updates paused" if self.freeze_plots else "Plot updates resumed")
        else:
            self.original_keyPressEvent(event)

    def _clear_all_data(self):
        reply = QtWidgets.QMessageBox.question(
            self.main_window, "Clear All Data",
            "Are you sure you want to clear all data?",
            QtWidgets.QMessageBox.StandardButton.Yes |
            QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.data_manager.clear_data()
            self.status_label.setText("All data cleared")

    def run(self):
        self.main_window.show()
        return self.app.exec()
        

# Entry point
if __name__ == "__main__":
    app = MainApplication()
    sys.exit(app.run())
