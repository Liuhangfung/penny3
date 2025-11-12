"""
Settings module for Telegram Bot
Loads configuration from menu_config.json
"""
import json
import os
from typing import Dict, Any


class Config:
    """Configuration loader and storage"""
    
    def __init__(self, config_file: str = "menu_config.json"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"Configuration file '{self.config_file}' not found. "
                "Please create it based on the sample in README.md"
            )
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Validate required fields
        required_fields = ['bot_token', 'welcome_message', 'menus', 'button_mapping']
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field '{field}' in {self.config_file}")
        
        # Validate bot token
        if self.config['bot_token'] == "YOUR_BOT_TOKEN_HERE":
            raise ValueError(
                "Please update 'bot_token' in menu_config.json with your actual bot token"
            )
    
    def reload_config(self) -> None:
        """Reload configuration from file (useful for runtime updates)"""
        self.load_config()
    
    @property
    def bot_token(self) -> str:
        """Get bot token"""
        return self.config['bot_token']
    
    @property
    def welcome_message(self) -> str:
        """Get welcome message"""
        return self.config['welcome_message']
    
    @property
    def menus(self) -> Dict[str, Any]:
        """Get all menus"""
        return self.config['menus']
    
    @property
    def button_mapping(self) -> Dict[str, str]:
        """Get button to menu mapping"""
        return self.config['button_mapping']
    
    @property
    def responses(self) -> Dict[str, str]:
        """Get button responses"""
        return self.config.get('responses', {})
    
    @property
    def admin_ids(self) -> list:
        """Get list of admin user IDs"""
        return self.config.get('admin_ids', [])
    
    def get_menu(self, menu_name: str) -> Dict[str, Any]:
        """Get specific menu by name"""
        return self.menus.get(menu_name, {})
    
    def save_config(self) -> bool:
        """Save current configuration back to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def update_welcome_message(self, message: str) -> bool:
        """Update welcome message"""
        self.config['welcome_message'] = message
        return self.save_config()
    
    def add_admin(self, user_id: int) -> bool:
        """Add admin user ID"""
        if user_id not in self.config['admin_ids']:
            self.config['admin_ids'].append(user_id)
            return self.save_config()
        return False
    
    def remove_admin(self, user_id: int) -> bool:
        """Remove admin user ID"""
        if user_id in self.config['admin_ids']:
            self.config['admin_ids'].remove(user_id)
            return self.save_config()
        return False
    
    def update_response(self, button_text: str, response: str) -> bool:
        """Update or add a button response"""
        if 'responses' not in self.config:
            self.config['responses'] = {}
        self.config['responses'][button_text] = response
        return self.save_config()
    
    def delete_response(self, button_text: str) -> bool:
        """Delete a button response"""
        if button_text in self.config.get('responses', {}):
            del self.config['responses'][button_text]
            return self.save_config()
        return False
    
    def add_menu(self, menu_name: str, menu_title: str) -> bool:
        """Add a new menu"""
        if menu_name in self.config['menus']:
            return False  # Menu already exists
        
        # Create new menu with basic structure
        self.config['menus'][menu_name] = {
            "title": menu_title,
            "buttons": [
                ["⬅ Back", "🔝 Main Menu"]
            ]
        }
        return self.save_config()
    
    def delete_menu(self, menu_name: str) -> bool:
        """Delete a menu"""
        # Don't allow deleting essential menus
        if menu_name in ['main', 'admin']:
            return False
        
        if menu_name in self.config['menus']:
            del self.config['menus'][menu_name]
            
            # Clean up button mappings that point to this menu
            mappings_to_remove = []
            for button, target in self.config.get('button_mapping', {}).items():
                if target == menu_name:
                    mappings_to_remove.append(button)
            
            for button in mappings_to_remove:
                del self.config['button_mapping'][button]
            
            return self.save_config()
        return False


# Global configuration instance
config = Config()

# Admin IDs (optional - add your Telegram user ID here for admin features)
ADMIN_IDS = []

# Bot constants
BOT_NAME = "Menu Demo Chat Bot"

