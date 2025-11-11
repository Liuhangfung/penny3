"""
Menu Handler Module
Manages menu navigation and button interactions
"""
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from typing import List, Dict, Any
from settings import config
import logging

logger = logging.getLogger(__name__)


class MenuHandler:
    """Handles menu creation and navigation"""
    
    def __init__(self):
        self.config = config
        # Track user navigation history for back button functionality
        self.user_history: Dict[int, List[str]] = {}
    
    def create_keyboard(self, menu_name: str, user_id: int = None) -> ReplyKeyboardMarkup:
        """
        Create a ReplyKeyboardMarkup from menu configuration
        
        Args:
            menu_name: Name of the menu in menu_config.json
            user_id: User ID to check for admin status
            
        Returns:
            ReplyKeyboardMarkup object
        """
        from admin_handler import admin_handler
        
        menu_data = self.config.get_menu(menu_name)
        
        if not menu_data:
            logger.error(f"Menu '{menu_name}' not found in configuration")
            # Return default main menu
            menu_data = self.config.get_menu('main')
        
        buttons = menu_data.get('buttons', [])
        
        # Add Settings button to main menu for admins
        if menu_name == 'main' and user_id and admin_handler.is_admin(user_id):
            # Check if settings button already exists
            has_settings = any("⚙️ Settings" in str(row) for row in buttons)
            if not has_settings:
                buttons = buttons + [["⚙️ Settings"]]
        
        # Create keyboard buttons
        keyboard = []
        for row in buttons:
            keyboard_row = [KeyboardButton(button) for button in row]
            keyboard.append(keyboard_row)
        
        # Create ReplyKeyboardMarkup with resize and one-time options
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=False
        )
        
        return reply_markup
    
    def get_menu_title(self, menu_name: str) -> str:
        """Get the title/message for a menu"""
        menu_data = self.config.get_menu(menu_name)
        return menu_data.get('title', 'Menu')
    
    def add_to_history(self, user_id: int, menu_name: str) -> None:
        """Add menu to user's navigation history"""
        if user_id not in self.user_history:
            self.user_history[user_id] = []
        self.user_history[user_id].append(menu_name)
    
    def get_previous_menu(self, user_id: int) -> str:
        """Get previous menu from user's history"""
        if user_id not in self.user_history or len(self.user_history[user_id]) < 2:
            return 'main'
        
        # Remove current menu
        self.user_history[user_id].pop()
        
        # Get previous menu
        if self.user_history[user_id]:
            previous = self.user_history[user_id][-1]
            return previous
        
        return 'main'
    
    def clear_history(self, user_id: int) -> None:
        """Clear user's navigation history"""
        if user_id in self.user_history:
            self.user_history[user_id] = []
    
    async def show_menu(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE,
        menu_name: str = 'main',
        add_to_history: bool = True
    ) -> None:
        """
        Display a menu to the user
        
        Args:
            update: Telegram update object
            context: Telegram context object
            menu_name: Name of the menu to display
            add_to_history: Whether to add this menu to navigation history
        """
        user_id = update.effective_user.id
        
        # Add to navigation history
        if add_to_history:
            self.add_to_history(user_id, menu_name)
        
        # Get menu keyboard and title (pass user_id for admin check)
        keyboard = self.create_keyboard(menu_name, user_id)
        title = self.get_menu_title(menu_name)
        
        # Send message with keyboard
        await update.message.reply_text(
            title,
            reply_markup=keyboard
        )
        
        logger.info(f"User {user_id} navigated to menu: {menu_name}")
    
    async def handle_button_press(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle button press from user
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        from admin_handler import admin_handler
        
        user_id = update.effective_user.id
        button_text = update.message.text
        
        logger.info(f"User {user_id} pressed button: {button_text}")
        
        # Check if this is an admin non-conversation button
        admin_action_buttons = [
            "👥 Manage Admins", "🔄 Reload Config",
            "➕ Add Menu", "🗑️ Delete Menu", "🔙 Back to Settings"
        ]
        
        if button_text in admin_action_buttons:
            await admin_handler.handle_admin_action(update, context)
            return
        
        # Check if button is mapped to a menu
        button_mapping = self.config.button_mapping
        
        if button_text in button_mapping:
            action = button_mapping[button_text]
            
            # Handle special actions
            if action == 'back':
                # Navigate back
                previous_menu = self.get_previous_menu(user_id)
                await self.show_menu(update, context, previous_menu, add_to_history=False)
                return
            
            elif action == 'main':
                # Go to main menu
                self.clear_history(user_id)
                await self.show_menu(update, context, 'main')
                return
            
            elif action == 'admin':
                # Show admin menu (with auth check)
                await admin_handler.show_admin_menu(update, context)
                return
            
            else:
                # Navigate to submenu
                await self.show_menu(update, context, action)
                return
        
        # Check if button has a custom response
        responses = self.config.responses
        if button_text in responses:
            response_text = responses[button_text]
            await update.message.reply_text(response_text)
            logger.info(f"Sent custom response for button: {button_text}")
            return
        
        # Default response for unmapped buttons
        await update.message.reply_text(
            f"You selected: {button_text}"
        )
    
    async def handle_start(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle /start command
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        logger.info(f"User {user_id} ({user_name}) started the bot")
        
        # Clear navigation history
        self.clear_history(user_id)
        
        # Send welcome message with user ID (helpful for admin setup)
        welcome_text = self.config.welcome_message
        welcome_text += f"\n\n<i>Your User ID: <code>{user_id}</code></i>"
        await update.message.reply_html(welcome_text)
        
        # Show main menu
        await self.show_menu(update, context, 'main')
    
    async def handle_help(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle /help command
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        help_text = (
            "🤖 <b>Bot Help</b>\n\n"
            "Commands:\n"
            "/start - Start the bot and show main menu\n"
            "/help - Show this help message\n"
            "/menu - Return to main menu\n\n"
            "Navigation:\n"
            "• Use the buttons to navigate through menus\n"
            "• Press '⬅ Back' to go to the previous menu\n"
            "• Press '🔝 Main Menu' to return to the main menu\n"
        )
        
        await update.message.reply_html(help_text)
    
    async def handle_menu_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle /menu command - return to main menu
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        user_id = update.effective_user.id
        self.clear_history(user_id)
        await self.show_menu(update, context, 'main')


# Global menu handler instance
menu_handler = MenuHandler()

