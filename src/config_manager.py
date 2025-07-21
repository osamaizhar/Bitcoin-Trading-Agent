"""
Bitcoin Trading Agent - Configuration Management Module

This module handles configuration from multiple sources:
- Google Sheets integration
- Local .env file fallback
- Runtime configuration updates
"""

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ConfigManager:
    """Configuration manager with Google Sheets integration"""
    
    def __init__(self):
        self.service_account_path = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT')
        self.sheets_id = os.getenv('GOOGLE_SHEETS_ID')
        self.local_config = self._load_local_config()
        self.cached_config = self.local_config.copy()
        self.last_update = None
        
    def _load_local_config(self):
        """Load configuration from environment variables"""
        return {
            # Trading parameters
            'budget': float(os.getenv('DEFAULT_BUDGET', 1000)),
            'dca_percentage': float(os.getenv('DCA_PERCENTAGE', 3.0)),
            'atr_multiplier': float(os.getenv('ATR_MULTIPLIER', 1.5)),
            'position_size_pct': float(os.getenv('POSITION_SIZE_PCT', 2.0)),
            'max_drawdown': float(os.getenv('MAX_DRAWDOWN', 25.0)),
            
            # Strategy toggles
            'enable_dca': os.getenv('ENABLE_DCA', 'true').lower() == 'true',
            'enable_atr_stops': os.getenv('ENABLE_ATR_STOPS', 'true').lower() == 'true',
            'trading_mode': os.getenv('TRADING_MODE', 'paper').lower(),
            
            # Technical indicators
            'rsi_oversold': int(os.getenv('RSI_OVERSOLD', 30)),
            'rsi_overbought': int(os.getenv('RSI_OVERBOUGHT', 70)),
            
            # Risk management
            'max_daily_trades': int(os.getenv('MAX_DAILY_TRADES', 5)),
            'min_time_between_trades': int(os.getenv('MIN_TIME_BETWEEN_TRADES', 1800)),  # 30 minutes
            
            # Notification settings
            'whatsapp_enabled': os.getenv('WHATSAPP_ENABLED', 'true').lower() == 'true',
            'email_enabled': os.getenv('EMAIL_ENABLED', 'true').lower() == 'true',
            'notification_rate_limit': int(os.getenv('NOTIFICATION_RATE_LIMIT', 30)),  # seconds
            
            # Bot settings
            'cycle_interval': int(os.getenv('CYCLE_INTERVAL', 1800)),  # 30 minutes
            'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', 3600)),  # 1 hour
            
            # Metadata
            'last_updated': datetime.now().isoformat(),
            'config_source': 'local'
        }
    
    def get_config(self, force_refresh=False):
        """Get configuration with optional refresh from Google Sheets"""
        if force_refresh or self._should_refresh():
            return self._refresh_config()
        
        return self.cached_config
    
    def _should_refresh(self):
        """Check if configuration should be refreshed"""
        if not self.last_update:
            return True
        
        # Refresh every hour
        time_since_update = datetime.now() - self.last_update
        return time_since_update.total_seconds() > 3600
    
    def _refresh_config(self):
        """Refresh configuration from Google Sheets"""
        try:
            if self.service_account_path and self.sheets_id:
                sheets_config = self._fetch_from_sheets()
                if sheets_config:
                    # Merge with local config (sheets override local)
                    self.cached_config.update(sheets_config)
                    self.cached_config['config_source'] = 'google_sheets'
                    self.cached_config['last_updated'] = datetime.now().isoformat()
                    self.last_update = datetime.now()
                    
                    logger.info("Configuration updated from Google Sheets")
                    return self.cached_config
            
            # Fallback to local config
            logger.info("Using local configuration")
            self.cached_config = self.local_config.copy()
            self.last_update = datetime.now()
            return self.cached_config
            
        except Exception as e:
            logger.error(f"Config refresh error: {e}")
            return self.cached_config
    
    def _fetch_from_sheets(self):
        """Fetch configuration from Google Sheets"""
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            # Authenticate
            credentials = Credentials.from_service_account_file(
                self.service_account_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            
            service = build('sheets', 'v4', credentials=credentials)
            
            # Read configuration range
            range_name = 'Config!A:B'  # Column A: Parameter, Column B: Value
            result = service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("Empty Google Sheets configuration")
                return None
            
            config = {}
            
            # Parse configuration
            for row in values[1:]:  # Skip header row
                if len(row) >= 2:
                    param = row[0].lower().replace(' ', '_').replace('-', '_')
                    value = row[1]
                    
                    # Type conversion based on parameter name
                    try:
                        if param in ['budget', 'dca_percentage', 'atr_multiplier', 'position_size_pct', 'max_drawdown']:
                            config[param] = float(value)
                        elif param in ['rsi_oversold', 'rsi_overbought', 'max_daily_trades', 'min_time_between_trades', 
                                      'notification_rate_limit', 'cycle_interval', 'health_check_interval']:
                            config[param] = int(value)
                        elif param in ['enable_dca', 'enable_atr_stops', 'whatsapp_enabled', 'email_enabled']:
                            config[param] = str(value).lower() in ['true', '1', 'yes', 'on', 'enabled']
                        else:
                            config[param] = str(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid value for {param}: {value}")
                        continue
            
            logger.info(f"Loaded {len(config)} parameters from Google Sheets")
            return config
            
        except ImportError:
            logger.warning("Google API client not installed")
            return None
        except FileNotFoundError:
            logger.warning(f"Service account file not found: {self.service_account_path}")
            return None
        except Exception as e:
            logger.error(f"Google Sheets fetch error: {e}")
            return None
    
    def update_config(self, updates):
        """Update configuration parameters"""
        try:
            # Validate updates
            validated_updates = self._validate_config_updates(updates)
            
            # Update cached config
            self.cached_config.update(validated_updates)
            self.cached_config['last_updated'] = datetime.now().isoformat()
            
            logger.info(f"Configuration updated: {list(validated_updates.keys())}")
            return True
            
        except Exception as e:
            logger.error(f"Config update error: {e}")
            return False
    
    def _validate_config_updates(self, updates):
        """Validate configuration updates"""
        validated = {}
        
        for key, value in updates.items():
            try:
                # Validate based on parameter type
                if key in ['budget', 'dca_percentage', 'atr_multiplier', 'position_size_pct', 'max_drawdown']:
                    validated[key] = float(value)
                    
                    # Additional validation
                    if key == 'budget' and validated[key] <= 0:
                        raise ValueError("Budget must be positive")
                    elif key == 'dca_percentage' and not (0.1 <= validated[key] <= 50):
                        raise ValueError("DCA percentage must be between 0.1 and 50")
                    elif key == 'atr_multiplier' and not (0.5 <= validated[key] <= 5.0):
                        raise ValueError("ATR multiplier must be between 0.5 and 5.0")
                    elif key == 'position_size_pct' and not (0.1 <= validated[key] <= 10):
                        raise ValueError("Position size must be between 0.1 and 10 percent")
                    elif key == 'max_drawdown' and not (5 <= validated[key] <= 50):
                        raise ValueError("Max drawdown must be between 5 and 50 percent")
                        
                elif key in ['rsi_oversold', 'rsi_overbought']:
                    validated[key] = int(value)
                    if key == 'rsi_oversold' and not (10 <= validated[key] <= 40):
                        raise ValueError("RSI oversold must be between 10 and 40")
                    elif key == 'rsi_overbought' and not (60 <= validated[key] <= 90):
                        raise ValueError("RSI overbought must be between 60 and 90")
                        
                elif key in ['enable_dca', 'enable_atr_stops', 'whatsapp_enabled', 'email_enabled']:
                    if isinstance(value, bool):
                        validated[key] = value
                    else:
                        validated[key] = str(value).lower() in ['true', '1', 'yes', 'on', 'enabled']
                        
                elif key == 'trading_mode':
                    if str(value).lower() in ['paper', 'live', 'demo']:
                        validated[key] = str(value).lower()
                    else:
                        raise ValueError("Trading mode must be 'paper', 'live', or 'demo'")
                        
                else:
                    validated[key] = value
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid update for {key}: {e}")
                continue
        
        return validated
    
    def save_config_to_file(self, filepath):
        """Save current configuration to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.cached_config, f, indent=2, default=str)
            
            logger.info(f"Configuration saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def load_config_from_file(self, filepath):
        """Load configuration from file"""
        try:
            with open(filepath, 'r') as f:
                file_config = json.load(f)
            
            # Validate and update
            validated_config = self._validate_config_updates(file_config)
            self.cached_config.update(validated_config)
            self.cached_config['config_source'] = f'file:{filepath}'
            self.cached_config['last_updated'] = datetime.now().isoformat()
            
            logger.info(f"Configuration loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load config from file: {e}")
            return False
    
    def get_config_summary(self):
        """Get configuration summary for display"""
        config = self.get_config()
        
        return {
            'source': config.get('config_source', 'unknown'),
            'last_updated': config.get('last_updated', 'unknown'),
            'trading_mode': config.get('trading_mode', 'paper'),
            'budget': config.get('budget', 0),
            'dca_enabled': config.get('enable_dca', False),
            'atr_enabled': config.get('enable_atr_stops', False),
            'notifications_enabled': config.get('whatsapp_enabled', False) or config.get('email_enabled', False),
            'key_parameters': {
                'DCA Trigger': f"{config.get('dca_percentage', 3):.1f}% drop",
                'ATR Multiplier': f"{config.get('atr_multiplier', 1.5):.1f}x",
                'Position Size': f"{config.get('position_size_pct', 2):.1f}% of budget",
                'Max Drawdown': f"{config.get('max_drawdown', 25):.1f}%"
            }
        }
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.cached_config = self._load_local_config()
        self.last_update = datetime.now()
        logger.info("Configuration reset to defaults")
        return True


# Utility functions for configuration management
def create_sample_google_sheet_template():
    """Create sample Google Sheets template data"""
    return [
        ['Parameter', 'Value', 'Description'],
        ['budget', '1000', 'Total trading budget in USD'],
        ['dca_percentage', '3.0', 'DCA trigger percentage drop'],
        ['atr_multiplier', '1.5', 'ATR stop-loss multiplier'],
        ['position_size_pct', '2.0', 'Position size as % of budget'],
        ['max_drawdown', '25.0', 'Maximum portfolio drawdown %'],
        ['enable_dca', 'true', 'Enable DCA strategy'],
        ['enable_atr_stops', 'true', 'Enable ATR stop-losses'],
        ['trading_mode', 'paper', 'Trading mode: paper/live'],
        ['rsi_oversold', '30', 'RSI oversold threshold'],
        ['rsi_overbought', '70', 'RSI overbought threshold'],
        ['whatsapp_enabled', 'true', 'Enable WhatsApp notifications'],
        ['email_enabled', 'true', 'Enable email reports'],
        ['cycle_interval', '1800', 'Trading cycle interval in seconds'],
        ['max_daily_trades', '5', 'Maximum trades per day']
    ]


def export_config_template(filepath='config_template.csv'):
    """Export configuration template to CSV"""
    import csv
    
    template_data = create_sample_google_sheet_template()
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(template_data)
        
        print(f"Configuration template exported to {filepath}")
        return True
        
    except Exception as e:
        print(f"Failed to export template: {e}")
        return False


def validate_google_sheets_setup(service_account_path, sheets_id):
    """Validate Google Sheets configuration"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        # Test authentication
        credentials = Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        
        # Test sheet access
        result = service.spreadsheets().values().get(
            spreadsheetId=sheets_id,
            range='Config!A1:B1'
        ).execute()
        
        print("✅ Google Sheets configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets validation failed: {e}")
        return False