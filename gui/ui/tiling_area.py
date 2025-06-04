"""
Tiling Area Module
================

Provides a simple layout manager for arranging multiple plots using nested splitters.
"""

import json
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
from PyQt6 import QtWidgets, QtCore

from gui.ui.plot_widget import Plot


class TilingArea(QtWidgets.QWidget):
    """
    Widget that manages plots using a simple splitter-based layout system.
    Supports adding rows and splitting plots horizontally.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the tiling area.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # References to data and communication managers (set by caller)
        self.data_manager = None
        self.comm_manager = None
        
        # Track all plots in this simple list
        self.plots = []
        
        # Create main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Main vertical splitter to hold rows
        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.main_layout.addWidget(self.main_splitter)
    
    def add_row(self) -> None:
        """
        Add a new row with a single plot at the bottom of the layout.
        """
        # Create a new plot
        new_plot = Plot(
            f"Plot {len(self.plots) + 1}",
            parent=self,
            tiling_area=self,
            data_manager=self.data_manager,
            comm_manager=self.comm_manager
        )
        
        # Add the plot to our list
        self.plots.append(new_plot)
        
        # Add the plot to the main splitter
        self.main_splitter.addWidget(new_plot)
        
        # Make all rows equal size
        sizes = [1] * self.main_splitter.count()
        self.main_splitter.setSizes(sizes)
    
    def split_horizontal(self, plot: Plot) -> None:
        """
        Split a plot horizontally by replacing it with a horizontal splitter 
        containing the original plot and a new plot.
        
        Args:
            plot: Plot widget to split
        """
        if plot not in self.plots:
            return
        
        # Find the index of the plot in the main splitter or its parent splitter
        plot_parent = plot.parent()
        index = -1
        
        if isinstance(plot_parent, QtWidgets.QSplitter):
            # Find the index in the parent splitter
            for i in range(plot_parent.count()):
                if plot_parent.widget(i) == plot:
                    index = i
                    break
        
        if index == -1:
            return
        
        # Create a horizontal splitter to replace the plot
        h_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        
        # Create a new plot
        new_plot = Plot(
            f"Plot {len(self.plots) + 1}",
            parent=self,
            tiling_area=self,
            data_manager=self.data_manager,
            comm_manager=self.comm_manager
        )
        
        # Add the new plot to our list
        self.plots.append(new_plot)
        
        # Take the plot out of its parent without deleting it
        plot.setParent(None)
        
        # Add both the original and new plot to the horizontal splitter
        h_splitter.addWidget(plot)
        h_splitter.addWidget(new_plot)
        
        # Make both sides equal size
        h_splitter.setSizes([1, 1])
        
        # Insert the horizontal splitter where the plot used to be
        if isinstance(plot_parent, QtWidgets.QSplitter):
            plot_parent.insertWidget(index, h_splitter)
    
    def remove_plot(self, plot: Plot) -> None:
        """
        Remove a plot from the layout.
        
        Args:
            plot: Plot to remove
        """
        if plot not in self.plots:
            return
            
        # Remove from our list
        self.plots.remove(plot)
        
        # Remove from layout and delete
        plot.setParent(None)
        plot.deleteLater()
    
    def save_layout(self, filename: Optional[str] = None) -> bool:
        """
        Save the current layout configuration to a file.
        
        Args:
            filename: Path to save the layout to, or None to prompt
            
        Returns:
            True if successful, False otherwise
        """
        if not filename:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save Layout", "", "JSON Files (*.json)"
            )
            
        if not filename:
            return False
            
        # Simple layout format - just save plot signals
        layout_data = {
            "plots": []
        }
        
        # Export each plot's assigned signals
        for plot in self.plots:
            plot_data = {
                "signals": list(plot.signal_keys_assigned)
            }
            layout_data["plots"].append(plot_data)
            
        try:
            with open(filename, 'w') as f:
                json.dump(layout_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving layout: {e}")
            return False
    
    def load_layout(self, filename: Optional[str] = None) -> bool:
        """
        Load a layout configuration from a file.
        
        Args:
            filename: Path to load the layout from, or None to prompt
            
        Returns:
            True if successful, False otherwise
        """
        if not filename:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Load Layout", "", "JSON Files (*.json)"
            )
            
        if not filename or not Path(filename).exists():
            return False
            
        try:
            with open(filename, 'r') as f:
                layout_data = json.load(f)
                
            # Clear existing layout
            self.clear_layout()
                
            # Create plots and add signals based on saved data
            plots_data = layout_data.get("plots", [])
            
            # Create one row per plot in the saved layout
            for plot_data in plots_data:
                # Add a row with a new plot
                self.add_row()
                
                # Get the last plot we just added
                if self.plots:
                    plot = self.plots[-1]
                    
                    # Add each signal to the plot
                    for signal in plot_data.get("signals", []):
                        plot.add_signal(signal)
            
            return True
        except Exception as e:
            print(f"Error loading layout: {e}")
            return False
    
    def clear_layout(self) -> None:
        """Clear all plots and reset the layout."""
        # Remove all plots
        for plot in self.plots:
            plot.setParent(None)
            plot.deleteLater()
        self.plots.clear()
        
        # Remove all widgets from the main splitter
        for i in reversed(range(self.main_splitter.count())):
            widget = self.main_splitter.widget(i)
            if widget:
                widget.setParent(None)
                widget.deleteLater()