"""
User Protocol Template
----------------------

Drop this file next to `main.py` to provide a custom protocol implementation
without touching the GUI internals. Delete or rename this file if you don't
need it. It's a template showing the required shape.

Implement either:
- create_protocol(config) -> CommunicationProtocol
or
- class UserProtocol(CommunicationProtocol)
"""
from typing import Callable, Optional
import time
from gui.communication.comm_manager import CommunicationProtocol


class UserProtocol(CommunicationProtocol):
    """Example: a fake protocol that generates a ramp for demo/testing."""

    def __init__(self, config: dict):
        super().__init__()
        self._running = False
        self._t0 = time.time()
        self._timer = None

    def connect(self) -> bool:
        self.is_open = True
        self.last_ok_time = time.time()
        return True

    def disconnect(self) -> bool:
        self.is_open = False
        return True

    def start(self) -> None:
        # Simple timer-based generator using Qt timer if available
        try:
            from PyQt6 import QtCore
        except Exception:
            return

        if self._timer:
            self._timer.stop()
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(20)
        self._running = True

    def stop(self) -> None:
        if self._timer:
            self._timer.stop()
            self._timer = None
        self._running = False

    def send_message(self, key: str, value: float) -> bool:
        # Echo back immediately as if device confirmed
        if self.on_data_received:
            self.on_data_received(key, value, time.time())
        return True

    def _tick(self):
        if not self._running:
            return
        t = time.time() - self._t0
        self.last_ok_time = time.time()
        # produce some RX values
        if self.on_data_received:
            for k in ("rx.signal1", "rx.signal2"):
                self.on_data_received(k, (t % 10) - 5.0, time.time())


def create_protocol(config: dict) -> CommunicationProtocol:
    return UserProtocol(config)
