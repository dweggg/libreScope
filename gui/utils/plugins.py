"""
Plugin Loader Utilities
=======================

This module discovers optional, user-provided protocol and signal database
implementations placed next to `main.py` (top-level of the repo) without
requiring changes inside the GUI codebase.

Discovery rules:
- Protocol: import module `user_protocol` (if present) and call
  `create_protocol(config)` or use `UserProtocol` class.
  Must implement `gui.communication.comm_manager.CommunicationProtocol`.

- Signals provider: import module `user_database` (if present) and call
  `create_signals_provider(config)` or use `UserSignalsProvider` class.
  Must expose methods: `get_all_keys() -> Dict[str, Dict[str, str]]`,
  `get_signal_name(key) -> str`, `get_signal_direction(key) -> Optional[str]`.

If not present, do not fallback. The app remains inactive until the user
provides implementations next to `main.py`.
"""

from __future__ import annotations

import importlib
import sys
from typing import Any

from gui.communication.comm_manager import CommunicationProtocol
from gui.data.signals import set_signals_provider


def _import_optional(module_name: str):
    """Try importing a module; return None if it doesn't exist."""
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        return None


def load_protocol(config: dict) -> CommunicationProtocol | None:
    """Load a user protocol if available; else return None."""
    mod = _import_optional("user_protocol")
    if mod is not None:
        # Factory function takes precedence
        if hasattr(mod, "create_protocol") and callable(mod.create_protocol):
            proto = mod.create_protocol(config)
            if not isinstance(proto, CommunicationProtocol):
                raise TypeError("create_protocol() must return a CommunicationProtocol")
            return proto
        # Otherwise try a known class
        if hasattr(mod, "UserProtocol"):
            cls = getattr(mod, "UserProtocol")
            inst = cls(config) if callable(getattr(cls, "__call__", None)) else cls
            if not isinstance(inst, CommunicationProtocol):
                raise TypeError("UserProtocol must subclass CommunicationProtocol")
            return inst

    # No fallback
    return None


class _SignalsProviderAdapter:
    """
    Adapter ensuring an object provides the minimal signals interface used by the UI:
    - get_all_keys() -> Dict[str, Dict[str, str]]
    - get_signal_name(key) -> str
    - get_signal_direction(key) -> Optional[str]
    """

    def __init__(self, provider: Any):
        self._provider = provider

    def get_all_keys(self):
        if hasattr(self._provider, "get_all_keys"):
            return self._provider.get_all_keys()
        # Accept alternative attribute (e.g., `.all_signals` dict)
        data = getattr(self._provider, "all_signals", None)
        return data if isinstance(data, dict) else {}

    def get_signal_name(self, key: str) -> str:
        if hasattr(self._provider, "get_signal_name"):
            return self._provider.get_signal_name(key)
        # best-effort fallback
        d = self.get_all_keys().get(key, {})
        return d.get("name", key)

    def get_signal_direction(self, key: str):
        if hasattr(self._provider, "get_signal_direction"):
            return self._provider.get_signal_direction(key)
        d = self.get_all_keys().get(key, {})
        return d.get("dir")


def load_signals_provider(config: dict):
    """Load a user database provider if available; else return a no-op adapter."""
    mod = _import_optional("user_database")
    if mod is not None:
        if hasattr(mod, "create_signals_provider") and callable(mod.create_signals_provider):
            provider = mod.create_signals_provider(config)
            return _SignalsProviderAdapter(provider)
        if hasattr(mod, "UserSignalsProvider"):
            provider = mod.UserSignalsProvider(config)
            return _SignalsProviderAdapter(provider)

    # Fallback: empty provider
    return _SignalsProviderAdapter(type("Empty", (), {"get_all_keys": lambda self: {}})())


def bootstrap_plugins(config: dict):
    """
    Convenience to set the global signals provider used throughout the UI and
    return a protocol instance ready for the CommunicationManager.
    """
    signals_provider = load_signals_provider(config)
    set_signals_provider(signals_provider)
    protocol = load_protocol(config)
    return signals_provider, protocol
