"""
Communication Module
=================

Exports the abstract protocol interface and the manager only. No built-ins.
"""

from gui.communication.comm_manager import (
    CommunicationProtocol,
    CommunicationManager,
)

__all__ = [
    'CommunicationProtocol',
    'CommunicationManager',
]