"""
Bitcoin Trading Agent - Source Module

This module exports all trading agent components for easy import.
"""

# Import main classes for export
try:
    from .data_collector import DataCollector, standardize_dataframes
    from .trading_engine import TradingEngine, DCAStrategy, ATRStopLossStrategy
    from .notifications import NotificationManager, WhatsAppNotifier, EmailNotifier
    from .config_manager import ConfigManager
    
    __all__ = [
        'DataCollector',
        'standardize_dataframes', 
        'TradingEngine',
        'DCAStrategy',
        'ATRStopLossStrategy',
        'NotificationManager',
        'WhatsAppNotifier',
        'EmailNotifier',
        'ConfigManager'
    ]
    
except ImportError as e:
    # Handle missing dependencies gracefully
    print(f"Warning: Some modules could not be imported: {e}")
    __all__ = []