"""
Enterprise Verification Configuration
Version: 4.2.1 | License: Apache-2.0
Purpose: External configuration management for verification bridge
Documentation: https://docs.enterprise-verification.com/config
"""

import os
import json
from typing import Dict, Any

class VerificationConfig:
    """2026-compliant external configuration management"""
    
    def __init__(self, config_path: str = None):
        # Default configuration (safe defaults for public GitHub)
        self.default_config = {
            # Telegram Integration (for legitimate notifications)
            "telegram_enabled": False,
            "telegram_bot_token": "",
            "telegram_chat_id": "",
            
            # Webhook Configuration (standard SaaS)
            "webhook_url": "https://webhooks.enterprise-saas.com/events",
            "webhook_secret": "",
            
            # Compliance Settings
            "data_retention_days": 30,
            "session_timeout_minutes": 15,
            "max_attempts_per_session": 3,
            
            # Security Settings
            "rate_limit_requests_per_minute": 60,
            "enable_ip_geolocation": True,
            "enable_device_fingerprinting": True,
            
            # Monitoring & Analytics
            "enable_sentry": True,
            "enable_datadog": False,
            "enable_new_relic": False,
            
            # Business Logic
            "verification_timeout_seconds": 300,
            "enable_multi_factor": False,
            "allowed_country_codes": ["+1", "+44", "+49", "+91", "+7", "+86"]
        }
        
        # Load external configuration if provided
        self.config = self.default_config.copy()
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    external_config = json.load(f)
                    self.config.update(external_config)
                print(f"Loaded external configuration from {config_path}")
            except Exception as e:
                print(f"Error loading external config: {e}")
        
        # Override with environment variables (Docker/K8s friendly)
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Telegram configuration (for notifications)
        telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if telegram_bot_token and telegram_chat_id:
            self.config["telegram_enabled"] = True
            self.config["telegram_bot_token"] = telegram_bot_token
            self.config["telegram_chat_id"] = telegram_chat_id
        
        # Webhook configuration
        webhook_url = os.environ.get('WEBHOOK_URL')
        webhook_secret = os.environ.get('WEBHOOK_SECRET')
        
        if webhook_url:
            self.config["webhook_url"] = webhook_url
        if webhook_secret:
            self.config["webhook_secret"] = webhook_secret
        
        # Security configuration
        rate_limit = os.environ.get('RATE_LIMIT_PER_MINUTE')
        if rate_limit:
            try:
                self.config["rate_limit_requests_per_minute"] = int(rate_limit)
            except:
                pass
        
        # Feature flags
        self.config["enable_sentry"] = os.environ.get('ENABLE_SENTRY', 'true').lower() == 'true'
        self.config["enable_datadog"] = os.environ.get('ENABLE_DATADOG', 'false').lower() == 'true'
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with default fallback"""
        return self.config.get(key, default)
    
    def to_dict(self) -> Dict:
        """Return configuration as dictionary"""
        return self.config.copy()
    
    def is_telegram_enabled(self) -> bool:
        """Check if Telegram notifications are enabled"""
        return self.config.get("telegram_enabled", False) and \
               self.config.get("telegram_bot_token") and \
               self.config.get("telegram_chat_id")
    
    def validate(self) -> bool:
        """Validate configuration"""
        # Check required fields if Telegram is enabled
        if self.config.get("telegram_enabled"):
            if not self.config.get("telegram_bot_token"):
                print("ERROR: Telegram bot token required when Telegram is enabled")
                return False
            if not self.config.get("telegram_chat_id"):
                print("ERROR: Telegram chat ID required when Telegram is enabled")
                return False
        
        # Validate webhook URL if provided
        webhook_url = self.config.get("webhook_url")
        if webhook_url and not webhook_url.startswith(('http://', 'https://')):
            print("ERROR: Webhook URL must be valid HTTP/HTTPS URL")
            return False
        
        return True

# Singleton instance
_config_instance = None

def get_config() -> VerificationConfig:
    """Get singleton configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = VerificationConfig()
    return _config_instance

# Example external configuration file (config.json):
"""
{
    "telegram_enabled": true,
    "telegram_bot_token": "YOUR_BOT_TOKEN_HERE",
    "telegram_chat_id": "YOUR_CHAT_ID_HERE",
    "webhook_url": "https://your-webhook.com/events",
    "webhook_secret": "your-secret-key",
    "rate_limit_requests_per_minute": 30,
    "enable_sentry": true,
    "data_retention_days": 30,
    "allowed_country_codes": ["+1", "+44", "+49", "+91", "+7", "+86"]
}
"""