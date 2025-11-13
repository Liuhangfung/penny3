"""
Menu Handler Module
Manages menu navigation and button interactions
"""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
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
    
    def create_main_reply_keyboard(self, user_id: int = None) -> ReplyKeyboardMarkup:
        """
        Create a persistent reply keyboard for the main menu
        This keyboard stays at the bottom for quick access
        Displays in 2-column layout
        
        Args:
            user_id: User ID to check for admin status
            
        Returns:
            ReplyKeyboardMarkup object
        """
        from admin_handler import admin_handler
        
        # Get main menu buttons (they are in 1 column in config)
        menu_data = self.config.get_menu('main')
        buttons = menu_data.get('buttons', [])
        
        # Flatten the buttons list
        flat_buttons = []
        for row in buttons:
            flat_buttons.extend(row)
        
        # Arrange in 2 columns:
        # Row 1: "What is UTGL?" (full width)
        # Row 2: "Trust Plans & Benefits" | "How to Apply"
        # Row 3: "Collaboration Opportunities" | "Other Enquiries"
        keyboard = []
        
        if len(flat_buttons) > 0:
            # First button full width
            keyboard.append([KeyboardButton(flat_buttons[0])])
            
            # Remaining buttons in pairs of 2
            for i in range(1, len(flat_buttons), 2):
                if i + 1 < len(flat_buttons):
                    keyboard.append([KeyboardButton(flat_buttons[i]), KeyboardButton(flat_buttons[i + 1])])
                else:
                    keyboard.append([KeyboardButton(flat_buttons[i])])
        
        # Add Settings button for admins (full width at bottom)
        if user_id and admin_handler.is_admin(user_id):
            keyboard.append([KeyboardButton("⚙️ Settings")])
        
        return ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=False  # Keep keyboard visible
        )
    
    def create_keyboard(self, menu_name: str, user_id: int = None) -> InlineKeyboardMarkup:
        """
        Create an InlineKeyboardMarkup from menu configuration
        
        Args:
            menu_name: Name of the menu in menu_config.json
            user_id: User ID to check for admin status
            
        Returns:
            InlineKeyboardMarkup object
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
        
        # Create inline keyboard buttons with callback_data
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button_text in row:
                # Use button text as callback data
                keyboard_row.append(InlineKeyboardButton(button_text, callback_data=f"btn:{button_text}"))
            keyboard.append(keyboard_row)
        
        # Create InlineKeyboardMarkup
        reply_markup = InlineKeyboardMarkup(keyboard)
        
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
        
        # Check if this is from a callback query or a message
        if update.callback_query:
            # Edit existing message (inline keyboard only)
            await update.callback_query.edit_message_text(
                title,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            # Send new message with inline keyboard
            await update.message.reply_html(
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
    
    async def handle_callback_query(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle callback queries from inline keyboard buttons
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        from admin_handler import admin_handler
        
        query = update.callback_query
        await query.answer()  # Answer callback query
        
        user_id = update.effective_user.id
        callback_data = query.data
        
        # Extract button text from callback data
        if callback_data.startswith("btn:"):
            button_text = callback_data[4:]  # Remove "btn:" prefix
        else:
            button_text = callback_data
        
        logger.info(f"User {user_id} pressed inline button: {button_text}")
        
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
            # Send response as a new message
            await query.message.reply_html(response_text)
            logger.info(f"Sent custom response for button: {button_text}")
            return
        
        # Default response for unmapped buttons
        await query.message.reply_text(f"You selected: {button_text}")
    
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
        
        # Create persistent reply keyboard
        reply_keyboard = self.create_main_reply_keyboard(user_id)
        
        # Send welcome message with persistent keyboard
        welcome_text = (
            f"👋 Hello <b>{user_name}</b>!\n\n"
            f"{self.config.welcome_message}"
        )
        await update.message.reply_html(
            welcome_text,
            reply_markup=reply_keyboard
        )
        
        # Show main menu with inline buttons
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
            "📋 <b>Commands:</b>\n"
            "• /start - Start the bot\n"
            "• /help - Show this message\n"
            "• /menu - Return to main menu\n\n"
            "🧭 <b>Navigation:</b>\n"
            "• Tap buttons to navigate\n"
            "• <b>⬅ Back</b> - Previous menu\n"
            "• <b>🔝 Main Menu</b> - Home\n\n"
            "💡 Use the keyboard buttons below for easy navigation!"
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

