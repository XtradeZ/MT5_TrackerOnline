"""
MT5 Trading Journal - Paquete Principal

Sistema modular para registro y análisis de operaciones de MetaTrader 5.
"""

__version__ = "2.0.0"
__author__ = "MT5 Trading Journal Team"

from .connector import MT5Connector
from .tracker import TradeTracker
from .file_manager import FileManager
from .ui import MT5TrackerApp
from .comments_manager import CommentsManager

__all__ = [
    'MT5Connector',
    'TradeTracker', 
    'FileManager',
    'MT5TrackerApp',
    'CommentsManager'
]
