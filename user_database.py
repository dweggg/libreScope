"""
User Signals Database Template
-----------------------------

Drop this file next to `main.py` to provide a custom signals database/provider
without touching the GUI internals. Delete or rename this file if you don't
need it. It's a template showing the required shape.

Implement either:
- create_signals_provider(config) -> provider
or
- class UserSignalsProvider:
    - get_all_keys() -> Dict[str, Dict[str, str]] with entries like:
        { "key": {"name": "Human Name", "dir": "RX"|"TX"} }
    - get_signal_name(key) -> str
    - get_signal_direction(key) -> Optional[str]
"""
from typing import Dict, Optional


class UserSignalsProvider:
    def __init__(self, config: dict):
        # Example: static definitions. Replace with your own loader (DBC, YAML, etc.)
        self._signals: Dict[str, Dict[str, str]] = {
            "rx.signal1": {"name": "RX Signal 1", "dir": "RX"},
            "rx.signal2": {"name": "RX Signal 2", "dir": "RX"},
            "tx.setpoint": {"name": "Setpoint", "dir": "TX"},
        }

    def get_all_keys(self) -> Dict[str, Dict[str, str]]:
        return self._signals

    def get_signal_name(self, key: str) -> str:
        return self._signals.get(key, {}).get("name", key)

    def get_signal_direction(self, key: str) -> Optional[str]:
        return self._signals.get(key, {}).get("dir")


def create_signals_provider(config: dict):
    return UserSignalsProvider(config)
