"""
Communication Module
=================

Manages communication protocols for serial data.
"""

from gui.communication.comm_manager import (
    CommunicationProtocol,
    SerialProtocol,
    CommunicationManager
)

__all__ = ['CommunicationProtocol', 'SerialProtocol', 'CommunicationManager']