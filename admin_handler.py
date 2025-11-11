"""
Admin Handler Module
Manages admin-only features and settings editing
"""
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from typing import Optional
from settings import config
import logging

logger = logging.getLogger(__name__)

# Conversation states
WAITING_WELCOME_MSG, WAITING_RESPONSE_BUTTON, WAITING_RESPONSE_TEXT = range(3)
WAITING_ADMIN_ID = 4
WAITING_MENU_SELECT, WAITING_MENU_ACTION, WAITING_NEW_TITLE, WAITING_BUTTON_ACTION = range(5, 9)
WAITING_BUTTON_SELECT, WAITING_NEW_BUTTON_TEXT = range(9, 11)


class AdminHandler:
    """Handles admin-only features"""
    
    def __init__(self):
        self.config = config
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin"""
        return user_id in self.config.admin_ids
    
    async def show_admin_menu(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Show admin settings menu"""
        from menu_handler import menu_handler
        
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text(
                "⛔ Access Denied!\n\n"
                "You are not authorized to access admin settings.\n\n"
                f"Your User ID: `{user_id}`\n"
                "Contact the bot owner to get admin access.",
                parse_mode='Markdown'
            )
            return
        
        # Show admin menu
        await menu_handler.show_menu(update, context, 'admin')
    
    async def start_edit_welcome(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start editing welcome message"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("⛔ Access Denied!")
            return ConversationHandler.END
        
        await update.message.reply_text(
            "📝 <b>Edit Welcome Message</b>\n\n"
            f"Current message:\n<code>{self.config.welcome_message}</code>\n\n"
            "Send me the new welcome message, or send /cancel to abort.",
            parse_mode='HTML'
        )
        return WAITING_WELCOME_MSG
    
    async def start_edit_response(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start editing button response"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("⛔ Access Denied!")
            return ConversationHandler.END
        
        await update.message.reply_text(
            "💬 <b>Edit Button Response</b>\n\n"
            "Current responses:\n" + 
            "\n".join([f"• {k}" for k in self.config.responses.keys()]) + "\n\n"
            "Send me the button text you want to edit, or send /cancel to abort.",
            parse_mode='HTML'
        )
        return WAITING_RESPONSE_BUTTON
    
    async def start_add_admin(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start adding admin"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("⛔ Access Denied!")
            return ConversationHandler.END
        
        await update.message.reply_text(
            "➕ <b>Add New Admin</b>\n\n"
            "Send me the Telegram User ID to add as admin.\n\n"
            "💡 Users can find their ID by:\n"
            "1. Messaging @userinfobot\n"
            "2. Or checking when they send /start to this bot\n\n"
            "Send /cancel to abort.",
            parse_mode='HTML'
        )
        context.user_data['adding_admin'] = True
        return WAITING_ADMIN_ID
    
    async def start_remove_admin(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start removing admin"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("⛔ Access Denied!")
            return ConversationHandler.END
        
        if len(self.config.admin_ids) <= 1:
            await update.message.reply_text(
                "⚠️ Cannot remove admin!\n\n"
                "There must be at least one admin."
            )
            return ConversationHandler.END
        
        admin_list = "\n".join([f"• {aid}" for aid in self.config.admin_ids])
        await update.message.reply_text(
            f"➖ <b>Remove Admin</b>\n\n"
            f"Current Admins:\n{admin_list}\n\n"
            "Send me the User ID to remove, or send /cancel to abort.",
            parse_mode='HTML'
        )
        context.user_data['removing_admin'] = True
        return WAITING_ADMIN_ID
    
    async def handle_admin_action(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle non-conversation admin actions"""
        user_id = update.effective_user.id
        button_text = update.message.text
        
        if not self.is_admin(user_id):
            await update.message.reply_text("⛔ Access Denied!")
            return
        
        # Handle different admin actions
        if button_text == "👥 Manage Admins":
            admin_list = self.config.admin_ids
            admin_text = "\n".join([f"• {aid}" for aid in admin_list]) if admin_list else "None"
            
            keyboard = [
                ["➕ Add Admin", "➖ Remove Admin"],
                ["🔙 Back to Settings"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                f"👥 <b>Admin Management</b>\n\n"
                f"Current Admins:\n{admin_text}\n\n"
                f"Your ID: <code>{user_id}</code>\n\n"
                "What would you like to do?",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        
        elif button_text == "🔙 Back to Settings":
            from menu_handler import menu_handler
            await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        
        elif button_text == "🔄 Reload Config":
            try:
                self.config.reload_config()
                await update.message.reply_text(
                    "✅ Configuration reloaded successfully!\n\n"
                    "All changes from menu_config.json have been loaded."
                )
            except Exception as e:
                await update.message.reply_text(
                    f"❌ Error reloading config:\n{str(e)}"
                )
        
        elif button_text == "🔧 Edit Menu":
            # This is now handled by the conversation handler
            pass
        
        elif button_text == "➕ Add Menu" or button_text == "🗑️ Delete Menu":
            await update.message.reply_text(
                "⚠️ <b>Advanced Feature</b>\n\n"
                "Adding/deleting menus requires editing menu_config.json directly.\n\n"
                "This is to prevent accidental menu structure corruption.\n\n"
                "See README.md for instructions on how to add/delete menus.",
                parse_mode='HTML'
            )
    
    async def receive_welcome_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive and save new welcome message"""
        new_message = update.message.text
        
        if self.config.update_welcome_message(new_message):
            from menu_handler import menu_handler
            
            await update.message.reply_text(
                "✅ Welcome message updated successfully!\n\n"
                f"New message: {new_message}"
            )
            await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        else:
            await update.message.reply_text(
                "❌ Failed to save welcome message. Please try again."
            )
        
        return ConversationHandler.END
    
    async def receive_response_button(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive button text for response editing"""
        button_text = update.message.text
        context.user_data['editing_button'] = button_text
        
        current_response = self.config.responses.get(button_text, "Not set")
        
        await update.message.reply_text(
            f"💬 <b>Editing Response for:</b> {button_text}\n\n"
            f"Current response:\n<code>{current_response}</code>\n\n"
            "Send me the new response text, or send /cancel to abort.",
            parse_mode='HTML'
        )
        
        return WAITING_RESPONSE_TEXT
    
    async def receive_response_text(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive and save new response text"""
        button_text = context.user_data.get('editing_button')
        new_response = update.message.text
        
        if self.config.update_response(button_text, new_response):
            from menu_handler import menu_handler
            
            await update.message.reply_text(
                f"✅ Response updated successfully!\n\n"
                f"Button: {button_text}\n"
                f"New response: {new_response}"
            )
            await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        else:
            await update.message.reply_text(
                "❌ Failed to save response. Please try again."
            )
        
        context.user_data.pop('editing_button', None)
        return ConversationHandler.END
    
    async def receive_admin_id(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive and process admin ID"""
        from menu_handler import menu_handler
        
        text = update.message.text
        
        try:
            user_id = int(text)
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid User ID. Please send a numeric ID or /cancel to abort."
            )
            return WAITING_ADMIN_ID
        
        removing = context.user_data.get('removing_admin', False)
        adding = context.user_data.get('adding_admin', False)
        
        if removing:
            if user_id == update.effective_user.id:
                await update.message.reply_text(
                    "⚠️ You cannot remove yourself as admin!"
                )
            elif self.config.remove_admin(user_id):
                await update.message.reply_text(
                    f"✅ Admin removed successfully!\n\n"
                    f"User ID {user_id} is no longer an admin."
                )
            else:
                await update.message.reply_text(
                    f"❌ User ID {user_id} is not an admin."
                )
            context.user_data.pop('removing_admin', None)
        elif adding:
            if self.config.add_admin(user_id):
                await update.message.reply_text(
                    f"✅ Admin added successfully!\n\n"
                    f"User ID {user_id} is now an admin."
                )
            else:
                await update.message.reply_text(
                    f"⚠️ User ID {user_id} is already an admin."
                )
            context.user_data.pop('adding_admin', None)
        
        await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        return ConversationHandler.END
    
    async def start_edit_menu(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start menu editing workflow"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("⛔ Access Denied!")
            return ConversationHandler.END
        
        menu_list = "\n".join([f"• <code>{k}</code>" for k in self.config.menus.keys()])
        await update.message.reply_text(
            "🔧 <b>Edit Menu</b>\n\n"
            f"Available menus:\n{menu_list}\n\n"
            "Send me the menu name you want to edit (e.g., <code>main</code>)\n"
            "Or send /cancel to abort.",
            parse_mode='HTML'
        )
        return WAITING_MENU_SELECT
    
    async def receive_menu_selection(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive which menu to edit"""
        menu_name = update.message.text.strip()
        
        if menu_name not in self.config.menus:
            await update.message.reply_text(
                f"❌ Menu '<code>{menu_name}</code>' not found.\n\n"
                "Please send a valid menu name or /cancel to abort.",
                parse_mode='HTML'
            )
            return WAITING_MENU_SELECT
        
        # Store selected menu
        context.user_data['editing_menu'] = menu_name
        menu_data = self.config.get_menu(menu_name)
        
        # Show menu details
        title = menu_data.get('title', 'No title')
        buttons = menu_data.get('buttons', [])
        button_preview = "\n".join([f"  Row {i+1}: {row}" for i, row in enumerate(buttons[:3])])
        if len(buttons) > 3:
            button_preview += f"\n  ... and {len(buttons)-3} more rows"
        
        keyboard = [
            ["📝 Edit Title"],
            ["🔘 Edit Button Text"],
            ["📋 View All Buttons"],
            ["🔙 Back to Settings"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"🔧 <b>Editing Menu: {menu_name}</b>\n\n"
            f"<b>Current Title:</b>\n{title}\n\n"
            f"<b>Button Preview:</b>\n{button_preview}\n\n"
            "What would you like to do?",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        return WAITING_MENU_ACTION
    
    async def receive_menu_action(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle menu editing action"""
        action = update.message.text
        menu_name = context.user_data.get('editing_menu')
        
        if action == "📝 Edit Title":
            current_title = self.config.get_menu(menu_name).get('title', '')
            await update.message.reply_text(
                f"📝 <b>Edit Title for '{menu_name}'</b>\n\n"
                f"Current title:\n<code>{current_title}</code>\n\n"
                "Send me the new title, or /cancel to abort.",
                parse_mode='HTML'
            )
            return WAITING_NEW_TITLE
        
        elif action == "🔘 Edit Button Text":
            menu_data = self.config.get_menu(menu_name)
            buttons = menu_data.get('buttons', [])
            
            # Create a flat list of all buttons with their positions
            button_list = []
            for row_idx, row in enumerate(buttons):
                for col_idx, button in enumerate(row):
                    button_list.append((button, row_idx, col_idx))
            
            button_text = ""
            for idx, (button, row, col) in enumerate(button_list, 1):
                button_text += f"{idx}. <code>{button}</code> (Row {row+1})\n"
            
            await update.message.reply_text(
                f"🔘 <b>Edit Button in '{menu_name}'</b>\n\n"
                f"Current buttons:\n{button_text}\n"
                "Send me the button text you want to change (exact text), or /cancel to abort.\n\n"
                "Example: <code>Button inside enquiry 1</code>",
                parse_mode='HTML'
            )
            return WAITING_BUTTON_SELECT
        
        elif action == "📋 View All Buttons":
            menu_data = self.config.get_menu(menu_name)
            buttons = menu_data.get('buttons', [])
            
            button_text = ""
            for i, row in enumerate(buttons):
                button_text += f"<b>Row {i+1}:</b> {row}\n"
            
            await update.message.reply_text(
                f"📋 <b>All Buttons in '{menu_name}'</b>\n\n"
                f"{button_text}\n"
                "Tap '🔘 Edit Button Text' to rename a button.",
                parse_mode='HTML'
            )
            return WAITING_MENU_ACTION
        
        elif action == "🔙 Back to Settings":
            from menu_handler import menu_handler
            context.user_data.pop('editing_menu', None)
            await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
            return ConversationHandler.END
        
        return WAITING_MENU_ACTION
    
    async def receive_new_title(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive and save new menu title"""
        from menu_handler import menu_handler
        
        new_title = update.message.text
        menu_name = context.user_data.get('editing_menu')
        
        # Update the menu title
        if menu_name in self.config.config['menus']:
            self.config.config['menus'][menu_name]['title'] = new_title
            
            if self.config.save_config():
                await update.message.reply_text(
                    f"✅ <b>Title updated successfully!</b>\n\n"
                    f"Menu: <code>{menu_name}</code>\n"
                    f"New title: {new_title}",
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    "❌ Failed to save changes. Please try again."
                )
        else:
            await update.message.reply_text(
                f"❌ Menu '{menu_name}' not found."
            )
        
        context.user_data.pop('editing_menu', None)
        await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        return ConversationHandler.END
    
    async def receive_button_selection(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive which button to edit"""
        old_button_text = update.message.text.strip()
        menu_name = context.user_data.get('editing_menu')
        menu_data = self.config.get_menu(menu_name)
        buttons = menu_data.get('buttons', [])
        
        # Find the button
        found = False
        for row_idx, row in enumerate(buttons):
            for col_idx, button in enumerate(row):
                if button == old_button_text:
                    found = True
                    context.user_data['button_to_edit'] = old_button_text
                    context.user_data['button_row'] = row_idx
                    context.user_data['button_col'] = col_idx
                    break
            if found:
                break
        
        if not found:
            await update.message.reply_text(
                f"❌ Button '<code>{old_button_text}</code>' not found in this menu.\n\n"
                "Please send the exact button text, or /cancel to abort.",
                parse_mode='HTML'
            )
            return WAITING_BUTTON_SELECT
        
        # Check if button has special navigation (Back, Main Menu)
        is_special = old_button_text in ["⬅ Back", "⬅️ Back", "🔝 Main Menu"]
        warning = ""
        if is_special:
            warning = "\n\n⚠️ <b>Warning:</b> This is a navigation button. Changing it may affect menu navigation!"
        
        await update.message.reply_text(
            f"🔘 <b>Renaming Button</b>\n\n"
            f"Current text: <code>{old_button_text}</code>{warning}\n\n"
            "Send me the new button text, or /cancel to abort.",
            parse_mode='HTML'
        )
        return WAITING_NEW_BUTTON_TEXT
    
    async def receive_new_button_text(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive and save new button text"""
        from menu_handler import menu_handler
        
        new_button_text = update.message.text.strip()
        old_button_text = context.user_data.get('button_to_edit')
        menu_name = context.user_data.get('editing_menu')
        row_idx = context.user_data.get('button_row')
        col_idx = context.user_data.get('button_col')
        
        # Update the button in the menu
        if menu_name in self.config.config['menus']:
            self.config.config['menus'][menu_name]['buttons'][row_idx][col_idx] = new_button_text
            
            # Update button_mapping if this button was mapped
            if old_button_text in self.config.config['button_mapping']:
                mapped_value = self.config.config['button_mapping'][old_button_text]
                del self.config.config['button_mapping'][old_button_text]
                self.config.config['button_mapping'][new_button_text] = mapped_value
                
            # Update responses if this button had a response
            if 'responses' in self.config.config and old_button_text in self.config.config['responses']:
                response_value = self.config.config['responses'][old_button_text]
                del self.config.config['responses'][old_button_text]
                self.config.config['responses'][new_button_text] = response_value
            
            if self.config.save_config():
                update_info = f"✅ <b>Button renamed successfully!</b>\n\n"
                update_info += f"Menu: <code>{menu_name}</code>\n"
                update_info += f"Old text: <code>{old_button_text}</code>\n"
                update_info += f"New text: <code>{new_button_text}</code>\n"
                
                # Inform about what was updated
                if old_button_text in self.config.button_mapping or new_button_text in self.config.button_mapping:
                    update_info += "\n✓ Button mapping updated"
                if old_button_text in self.config.responses or new_button_text in self.config.responses:
                    update_info += "\n✓ Button response preserved"
                
                await update.message.reply_text(update_info, parse_mode='HTML')
            else:
                await update.message.reply_text(
                    "❌ Failed to save changes. Please try again."
                )
        else:
            await update.message.reply_text(
                f"❌ Menu '{menu_name}' not found."
            )
        
        # Clean up
        context.user_data.pop('editing_menu', None)
        context.user_data.pop('button_to_edit', None)
        context.user_data.pop('button_row', None)
        context.user_data.pop('button_col', None)
        
        await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        return ConversationHandler.END
    
    async def cancel_conversation(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Cancel ongoing conversation"""
        from menu_handler import menu_handler
        
        await update.message.reply_text("❌ Operation cancelled.")
        await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        
        # Clean up user data
        context.user_data.pop('editing_button', None)
        context.user_data.pop('removing_admin', None)
        context.user_data.pop('adding_admin', None)
        context.user_data.pop('editing_menu', None)
        context.user_data.pop('button_to_edit', None)
        context.user_data.pop('button_row', None)
        context.user_data.pop('button_col', None)
        
        return ConversationHandler.END


# Global admin handler instance
admin_handler = AdminHandler()

