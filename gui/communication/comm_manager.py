"""
Communication Manager Module
===========================

Barebones protocol interfaces with no built-in implementations.
User code must provide concrete implementations of CommunicationProtocol.
"""

import time
from typing import Optional, Callable

class CommunicationProtocol:
    """Base class for communication protocols."""
    
    def __init__(self):
        self.is_open = False
        self.last_ok_time = 0
        self.on_data_received = None
    
    def connect(self) -> bool:
        """
        Establish connection with the device.
        
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement connect()")
    
    def disconnect(self) -> bool:
        """
        Disconnect from the device.
        
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement disconnect()")
    
    def is_connected(self) -> bool:
        """
        Check if currently connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self.is_open
    
    def send_message(self, key: str, value: float) -> bool:
        """
        Send a message with the given key and value.
        
        Args:
            key: Message identifier
            value: Value to send
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement send_message()")
    
    def set_data_callback(self, callback: Callable[[str, float, float], None]) -> None:
        """
        Set callback for received data.
        
        Args:
            callback: Function to call with (signal_key, value, timestamp)
        """
        self.on_data_received = callback
    # External protocol implementations should call this callback
    # whenever a sample arrives: callback(key, value, timestamp).
    
    def start(self) -> None:
        """Start communication (reader threads, etc.)."""
        raise NotImplementedError("Subclasses must implement start()")
    
    def stop(self) -> None:
        """Stop communication (reader threads, etc.)."""
        raise NotImplementedError("Subclasses must implement stop()")


class CommunicationManager:
    """
    Manages communication protocols and provides a unified interface.
    """
    
    def __init__(self, protocol: Optional[CommunicationProtocol] = None):
        """
        Initialize the communication manager.
        
        Args:
            protocol: Initial communication protocol to use
        """
        self.protocol: Optional[CommunicationProtocol] = protocol
        self.data_callbacks = []
    
    def toggle_connection(self) -> bool:
        """Protocol-agnostic toggle of connection state."""
        if self.is_connected():
            self.disconnect()
            return False
        return self.connect()
    
    def connect(self) -> bool:
        """
        Establish connection with the device.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.protocol:
            return False
        success = self.protocol.connect()
        if success:
            self.protocol.start()
        return success
    
    def disconnect(self) -> bool:
        """
        Disconnect from the device.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.protocol:
            return True
        if self.protocol.is_connected():
            self.protocol.stop()
            return self.protocol.disconnect()
        return True
    
    def is_connected(self) -> bool:
        """
        Check if currently connected.
        
        Returns:
            True if connected, False otherwise
        """
        return bool(self.protocol and self.protocol.is_connected())
    
    def send_message(self, key: str, value: float) -> bool:
        """
        Send a message with the given key and value.
        
        Args:
            key: Message identifier
            value: Value to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.protocol:
            return False
        return self.protocol.send_message(key, value)
    
    def register_data_callback(self, callback: Callable[[str, float, float], None]) -> None:
        """
        Register a callback for data reception.
        
        Args:
            callback: Function to call with (signal_key, value, timestamp)
        """
        if callback not in self.data_callbacks:
            self.data_callbacks.append(callback)
        
        # Set the protocol callback to our dispatcher
        if self.protocol and not self.protocol.on_data_received:
            self.protocol.set_data_callback(self._dispatch_data)
    
    def unregister_data_callback(self, callback: Callable[[str, float, float], None]) -> None:
        """
        Unregister a previously registered callback.
        
        Args:
            callback: Previously registered callback function
        """
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)
    
    def _dispatch_data(self, key: str, value: float, timestamp: float) -> None:
        """
        Dispatch received data to all registered callbacks.
        
        Args:
            key: Signal key
            value: Signal value
            timestamp: Time when the data was received
        """
        for callback in self.data_callbacks:
            try:
                callback(key, value, timestamp)
            except Exception as e:
                print(f"Error in data callback: {e}")
    
    @property
    def last_ok_time(self) -> float:
        """
        Get the timestamp of the last received OK message.
        
        Returns:
            Timestamp of last OK message
        """
        return self.protocol.last_ok_time if self.protocol else 0.0