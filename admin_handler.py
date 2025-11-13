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
WAITING_NEW_MENU_NAME, WAITING_NEW_MENU_TITLE, WAITING_DELETE_MENU_CONFIRM = range(11, 14)
WAITING_NEW_BUTTON_NAME = 14
WAITING_ADD_TO_MAIN, WAITING_MAIN_BUTTON_TEXT = range(15, 17)
WAITING_MAPPING_BUTTON, WAITING_MAPPING_TARGET = range(17, 19)


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
        
        # Determine if this is from callback query or message
        message = update.callback_query.message if update.callback_query else update.message
        
        if not self.is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("⛔ Access Denied", show_alert=True)
                await message.reply_html(
                    "⛔ <b>Access Denied</b>\n\n"
                    "🚫 You are not authorized to access admin settings.\n\n"
                    "💡 Contact the bot owner to get admin access."
                )
            else:
                await message.reply_html(
                    "⛔ <b>Access Denied</b>\n\n"
                    "🚫 You are not authorized to access admin settings.\n\n"
                    "💡 Contact the bot owner to get admin access."
                )
            return
        
        # Show fancy admin welcome
        admin_count = len(self.config.admin_ids)
        menu_count = len(self.config.menus)
        
        admin_welcome = (
            "╔═══════════════════════════════╗\n"
            "║    ⚙️ <b>ADMIN PANEL</b> ⚙️         ║\n"
            "╚═══════════════════════════════╝\n\n"
            "📊 <b>STATUS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🟢 Bot: <b>Online</b>\n"
            f"👥 Admins: <b>{admin_count}</b>\n"
            f"📋 Menus: <b>{menu_count}</b>\n\n"
            "🎨 <b>CONTENT MANAGEMENT</b>\n"
            "Use buttons below to manage\n"
            "your bot settings."
        )
        
        # Answer callback query if it's from inline button
        if update.callback_query:
            await update.callback_query.answer()
        
        await message.reply_html(admin_welcome)
        
        # Show admin menu
        await menu_handler.show_menu(update, context, 'admin')
    
    async def start_edit_welcome(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start editing welcome message"""
        user_id = update.effective_user.id
        
        # Get message object from either callback_query or regular message
        message = update.callback_query.message if update.callback_query else update.message
        
        if not self.is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("⛔ Access Denied", show_alert=True)
            await message.reply_html("⛔ <b>Access Denied!</b>")
            return ConversationHandler.END
        
        # Answer callback query if from inline button
        if update.callback_query:
            await update.callback_query.answer()
        
        current_msg = self.config.welcome_message
        await message.reply_html(
            "╔═══════════════════════════════╗\n"
            "║   📝 <b>EDIT WELCOME</b> 📝        ║\n"
            "╚═══════════════════════════════╝\n\n"
            "📄 <b>CURRENT MESSAGE:</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>{current_msg}</i>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✏️ <b>INSTRUCTIONS:</b>\n"
            "Send your new welcome message\n\n"
            "💡 <b>TIP:</b> You can use HTML:\n"
            "• &lt;b&gt;bold&lt;/b&gt;\n"
            "• &lt;i&gt;italic&lt;/i&gt;\n"
            "• &lt;code&gt;monospace&lt;/code&gt;\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Type /cancel to abort"
        )
        return WAITING_WELCOME_MSG
    
    async def start_edit_response(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start editing button response"""
        user_id = update.effective_user.id
        message = update.callback_query.message if update.callback_query else update.message
        
        if not self.is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("⛔ Access Denied", show_alert=True)
            await message.reply_html("⛔ <b>Access Denied!</b>")
            return ConversationHandler.END
        
        if update.callback_query:
            await update.callback_query.answer()
        
        button_list = "\n".join([f"  • {k}" for k in self.config.responses.keys()])
        button_count = len(self.config.responses)
        
        await message.reply_html(
            "╔═══════════════════════════════╗\n"
            "║   💬 <b>EDIT RESPONSE</b> 💬       ║\n"
            "╚═══════════════════════════════╝\n\n"
            f"📊 <b>AVAILABLE BUTTONS ({button_count}):</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{button_list}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✏️ Send the button text you\n"
            "   want to edit\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Type /cancel to abort"
        )
        return WAITING_RESPONSE_BUTTON
    
    async def start_add_admin(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start adding admin"""
        user_id = update.effective_user.id
        message = update.callback_query.message if update.callback_query else update.message
        
        if not self.is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("⛔ Access Denied", show_alert=True)
            await message.reply_html("⛔ <b>Access Denied!</b>")
            return ConversationHandler.END
        
        if update.callback_query:
            await update.callback_query.answer()
        
        admin_list = ', '.join(f"<code>{id}</code>" for id in self.config.admin_ids)
        admin_count = len(self.config.admin_ids)
        
        await message.reply_html(
            "╔═══════════════════════════════╗\n"
            "║     ➕ <b>ADD ADMIN</b> ➕          ║\n"
            "╚═══════════════════════════════╝\n\n"
            f"👥 <b>CURRENT ADMINS ({admin_count}):</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{admin_list}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✏️ <b>INSTRUCTIONS:</b>\n"
            "Send the User ID of the\n"
            "new admin\n\n"
            "💡 <b>TIP:</b> Users can see their\n"
            "   ID when they /start the bot\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Type /cancel to abort"
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
        message = update.callback_query.message if update.callback_query else update.message
        
        if not self.is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("⛔ Access Denied", show_alert=True)
            await message.reply_html("⛔ <b>Access Denied!</b>")
            return ConversationHandler.END
        
        if update.callback_query:
            await update.callback_query.answer()
        
        if len(self.config.admin_ids) <= 1:
            await message.reply_html(
                "╔═══════════════════════════════╗\n"
                "║     ⚠️ <b>WARNING!</b> ⚠️          ║\n"
                "╚═══════════════════════════════╝\n\n"
                "❌ Cannot remove admin!\n\n"
                "There must be at least one admin."
            )
            return ConversationHandler.END
        
        admin_list = "\n".join([f"  • <code>{aid}</code>" for aid in self.config.admin_ids])
        admin_count = len(self.config.admin_ids)
        
        await message.reply_html(
            "╔═══════════════════════════════╗\n"
            "║    ➖ <b>REMOVE ADMIN</b> ➖        ║\n"
            "╚═══════════════════════════════╝\n\n"
            f"👥 <b>CURRENT ADMINS ({admin_count}):</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{admin_list}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✏️ Send the User ID to remove\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Type /cancel to abort"
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
        
        # Get button text from either message or callback query
        if update.callback_query:
            button_text = update.callback_query.data.replace("btn:", "")
            message = update.callback_query.message
        else:
            button_text = update.message.text
            message = update.message
        
        if not self.is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("⛔ Access Denied", show_alert=True)
            else:
                await message.reply_text("⛔ Access Denied!")
            return
        
        # Handle different admin actions
        if button_text == "👥 Manage Admins":
            admin_list = self.config.admin_ids
            admin_text = "\n".join([f"  • <code>{aid}</code>" for aid in admin_list]) if admin_list else "None"
            admin_count = len(admin_list)
            
            keyboard = [
                ["➕ Add Admin", "➖ Remove Admin"],
                ["🔙 Back to Settings"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            # Answer callback query if from inline button
            if update.callback_query:
                await update.callback_query.answer()
            
            await message.reply_html(
                "╔═══════════════════════════════╗\n"
                "║   👥 <b>ADMIN MANAGER</b> 👥       ║\n"
                "╚═══════════════════════════════╝\n\n"
                f"📊 <b>CURRENT ADMINS ({admin_count}):</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{admin_text}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>YOUR ID:</b> <code>{user_id}</code>\n\n"
                "❓ What would you like to do?",
                reply_markup=reply_markup
            )
        
        elif button_text == "🔙 Back to Settings":
            from menu_handler import menu_handler
            # Answer callback query if from inline button
            if update.callback_query:
                await update.callback_query.answer()
            await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        
        elif button_text == "🔄 Reload Config":
            try:
                self.config.reload_config()
                # Answer callback query if from inline button
                if update.callback_query:
                    await update.callback_query.answer("✅ Config reloaded!", show_alert=True)
                
                await message.reply_html(
                    "╔═══════════════════════════════╗\n"
                    "║      ✅ <b>SUCCESS!</b> ✅          ║\n"
                    "╚═══════════════════════════════╝\n\n"
                    "🔄 Configuration reloaded!\n\n"
                    "All changes from\n"
                    "<code>menu_config.json</code>\n"
                    "have been loaded."
                )
            except Exception as e:
                if update.callback_query:
                    await update.callback_query.answer("❌ Error reloading config", show_alert=True)
                    
                await message.reply_html(
                    "╔═══════════════════════════════╗\n"
                    "║       ❌ <b>ERROR!</b> ❌           ║\n"
                    "╚═══════════════════════════════╝\n\n"
                    f"⚠️ <b>Error reloading config:</b>\n"
                    f"<code>{str(e)}</code>"
                )
        
        elif button_text == "🔧 Edit Menu":
            # This is now handled by the conversation handler
            pass
        
        # These are handled by conversation handlers now
        elif button_text == "➕ Add Menu" or button_text == "🗑️ Delete Menu":
            pass
    
    async def receive_welcome_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive and save new welcome message"""
        new_message = update.message.text
        
        if self.config.update_welcome_message(new_message):
            from menu_handler import menu_handler
            
            await update.message.reply_html(
                "╔═══════════════════════════════╗\n"
                "║      ✅ <b>SUCCESS!</b> ✅          ║\n"
                "╚═══════════════════════════════╝\n\n"
                "🎉 Welcome message updated!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "📄 <b>NEW MESSAGE:</b>\n"
                f"<i>{new_message}</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        else:
            await update.message.reply_html(
                "╔═══════════════════════════════╗\n"
                "║       ❌ <b>ERROR!</b> ❌           ║\n"
                "╚═══════════════════════════════╝\n\n"
                "⚠️ Failed to save welcome\n"
                "   message. Please try again."
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
        
        await update.message.reply_html(
            "╔═══════════════════════════════╗\n"
            "║   💬 <b>EDIT RESPONSE</b> 💬       ║\n"
            "╚═══════════════════════════════╝\n\n"
            f"🔘 <b>BUTTON:</b> {button_text}\n\n"
            "📄 <b>CURRENT RESPONSE:</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>{current_response}</i>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✏️ Send the new response text\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Type /cancel to abort"
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
            
            await update.message.reply_html(
                "╔═══════════════════════════════╗\n"
                "║      ✅ <b>SUCCESS!</b> ✅          ║\n"
                "╚═══════════════════════════════╝\n\n"
                "🎉 Response updated!\n\n"
                f"🔘 <b>BUTTON:</b> {button_text}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "📄 <b>NEW RESPONSE:</b>\n"
                f"<i>{new_response}</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        else:
            await update.message.reply_html(
                "╔═══════════════════════════════╗\n"
                "║       ❌ <b>ERROR!</b> ❌           ║\n"
                "╚═══════════════════════════════╝\n\n"
                "⚠️ Failed to save response.\n"
                "   Please try again."
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
            await update.message.reply_html(
                "╔═══════════════════════════════╗\n"
                "║      ❌ <b>INVALID ID!</b> ❌        ║\n"
                "╚═══════════════════════════════╝\n\n"
                "⚠️ Please send a numeric User ID\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Type /cancel to abort"
            )
            return WAITING_ADMIN_ID
        
        removing = context.user_data.get('removing_admin', False)
        adding = context.user_data.get('adding_admin', False)
        
        if removing:
            if user_id == update.effective_user.id:
                await update.message.reply_html(
                    "╔═══════════════════════════════╗\n"
                    "║     ⚠️ <b>WARNING!</b> ⚠️          ║\n"
                    "╚═══════════════════════════════╝\n\n"
                    "❌ You cannot remove yourself\n"
                    "   as admin!"
                )
            elif self.config.remove_admin(user_id):
                await update.message.reply_html(
                    "╔═══════════════════════════════╗\n"
                    "║      ✅ <b>SUCCESS!</b> ✅          ║\n"
                    "╚═══════════════════════════════╝\n\n"
                    "👤 Admin removed successfully!\n\n"
                    f"User ID <code>{user_id}</code> is no\n"
                    "longer an admin."
                )
            else:
                await update.message.reply_html(
                    "╔═══════════════════════════════╗\n"
                    "║       ❌ <b>ERROR!</b> ❌           ║\n"
                    "╚═══════════════════════════════╝\n\n"
                    f"User ID <code>{user_id}</code> is\n"
                    "not an admin."
                )
            context.user_data.pop('removing_admin', None)
        elif adding:
            if self.config.add_admin(user_id):
                await update.message.reply_html(
                    "╔═══════════════════════════════╗\n"
                    "║      ✅ <b>SUCCESS!</b> ✅          ║\n"
                    "╚═══════════════════════════════╝\n\n"
                    "👤 Admin added successfully!\n\n"
                    f"User ID <code>{user_id}</code> is now\n"
                    "an admin."
                )
            else:
                await update.message.reply_html(
                    "╔═══════════════════════════════╗\n"
                    "║     ⚠️ <b>WARNING!</b> ⚠️          ║\n"
                    "╚═══════════════════════════════╝\n\n"
                    f"User ID <code>{user_id}</code> is\n"
                    "already an admin."
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
        message = update.callback_query.message if update.callback_query else update.message
        
        if not self.is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("⛔ Access Denied", show_alert=True)
            await message.reply_html("⛔ <b>Access Denied!</b>")
            return ConversationHandler.END
        
        if update.callback_query:
            await update.callback_query.answer()
        
        menu_list = "\n".join([f"  • <code>{k}</code>" for k in self.config.menus.keys()])
        menu_count = len(self.config.menus)
        
        await message.reply_html(
            "╔═══════════════════════════════╗\n"
            "║     🔧 <b>EDIT MENU</b> 🔧         ║\n"
            "╚═══════════════════════════════╝\n\n"
            f"📊 <b>AVAILABLE MENUS ({menu_count}):</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{menu_list}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✏️ Send the menu name to edit\n"
            "   (e.g., <code>main</code>)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Type /cancel to abort"
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
            ["➕ Add Button"],
            ["➖ Remove Button"],
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
        
        elif action == "➕ Add Button":
            await update.message.reply_text(
                f"➕ <b>Add Button to '{menu_name}'</b>\n\n"
                "Send me the new button text.\n"
                "Example: <code>📞 Contact Us</code> or <code>🏠 Home</code>\n\n"
                "Send /cancel to abort.",
                parse_mode='HTML'
            )
            return WAITING_NEW_BUTTON_NAME
        
        elif action == "➖ Remove Button":
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
                f"➖ <b>Remove Button from '{menu_name}'</b>\n\n"
                f"Current buttons:\n{button_text}\n"
                "Send me the exact button text to remove, or /cancel to abort.\n\n"
                "⚠️ <b>Warning:</b> Navigation buttons (Back/Main Menu) should not be removed!",
                parse_mode='HTML'
            )
            context.user_data['removing_button'] = True
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
                "Tap '🔘 Edit Button Text' to rename a button.\n"
                "Tap '➕ Add Button' to add a new button.",
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
        """Receive which button to edit or remove"""
        old_button_text = update.message.text.strip()
        menu_name = context.user_data.get('editing_menu')
        menu_data = self.config.get_menu(menu_name)
        buttons = menu_data.get('buttons', [])
        
        # Check if we're removing a button
        if context.user_data.get('removing_button'):
            # Find and remove the button
            found = False
            for row_idx, row in enumerate(buttons):
                if old_button_text in row:
                    row.remove(old_button_text)
                    # If row is now empty, remove it
                    if not row:
                        buttons.pop(row_idx)
                    found = True
                    break
            
            if not found:
                await update.message.reply_text(
                    f"❌ Button '<code>{old_button_text}</code>' not found in this menu.\n\n"
                    "Please send the exact button text, or /cancel to abort.",
                    parse_mode='HTML'
                )
                return WAITING_BUTTON_SELECT
            
            # Save the updated menu
            if menu_name in self.config.config['menus']:
                self.config.config['menus'][menu_name]['buttons'] = buttons
                
                # Remove button mapping if exists
                if old_button_text in self.config.config.get('button_mapping', {}):
                    del self.config.config['button_mapping'][old_button_text]
                
                # Remove response if exists
                if old_button_text in self.config.config.get('responses', {}):
                    del self.config.config['responses'][old_button_text]
                
                if self.config.save_config():
                    from menu_handler import menu_handler
                    await update.message.reply_text(
                        f"✅ <b>Button removed!</b>\n\n"
                        f"Removed: <code>{old_button_text}</code>\n"
                        f"From menu: <code>{menu_name}</code>",
                        parse_mode='HTML'
                    )
                    context.user_data.pop('removing_button', None)
                    context.user_data.pop('editing_menu', None)
                    await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
                    return ConversationHandler.END
            
            await update.message.reply_text("❌ Failed to remove button.")
            return WAITING_BUTTON_SELECT
        
        # Otherwise, we're editing a button
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
    
    async def start_add_menu(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start adding a new menu"""
        user_id = update.effective_user.id
        message = update.callback_query.message if update.callback_query else update.message
        
        if not self.is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("⛔ Access Denied", show_alert=True)
            await message.reply_text("⛔ Access Denied!")
            return ConversationHandler.END
        
        if update.callback_query:
            await update.callback_query.answer()
        
        current_menus = ", ".join([f"<code>{m}</code>" for m in self.config.menus.keys()])
        
        await message.reply_text(
            "➕ <b>Create New Menu</b>\n\n"
            f"Current menus: {current_menus}\n\n"
            "Send me the menu <b>name</b> (lowercase, no spaces).\n"
            "Example: <code>services</code> or <code>products</code>\n\n"
            "Send /cancel to abort.",
            parse_mode='HTML'
        )
        return WAITING_NEW_MENU_NAME
    
    async def receive_new_menu_name(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive the new menu name"""
        menu_name = update.message.text.strip().lower().replace(' ', '_')
        
        # Validate menu name
        if not menu_name.replace('_', '').isalnum():
            await update.message.reply_text(
                "❌ Invalid menu name. Use only letters, numbers, and underscores.\n\n"
                "Try again or send /cancel to abort."
            )
            return WAITING_NEW_MENU_NAME
        
        if menu_name in self.config.menus:
            await update.message.reply_text(
                f"❌ Menu '<code>{menu_name}</code>' already exists!\n\n"
                "Choose a different name or send /cancel to abort.",
                parse_mode='HTML'
            )
            return WAITING_NEW_MENU_NAME
        
        # Store menu name for next step
        context.user_data['new_menu_name'] = menu_name
        
        await update.message.reply_text(
            f"✅ Menu name: <code>{menu_name}</code>\n\n"
            "Now send me the menu <b>title</b> (what users will see).\n"
            "Example: <code>🛠️ Our Services</code> or <code>📦 Products</code>\n\n"
            "Send /cancel to abort.",
            parse_mode='HTML'
        )
        return WAITING_NEW_MENU_TITLE
    
    async def receive_new_menu_title(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive the menu title and create the menu"""
        menu_title = update.message.text.strip()
        menu_name = context.user_data.get('new_menu_name')
        
        if self.config.add_menu(menu_name, menu_title):
            # Store menu info for next step
            context.user_data['new_menu_title'] = menu_title
            
            # Ask if they want to add button to main menu
            keyboard = [
                ["✅ Yes, add to main menu"],
                ["❌ No, I'll do it manually"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                f"✅ <b>Menu Created!</b>\n\n"
                f"Name: <code>{menu_name}</code>\n"
                f"Title: {menu_title}\n\n"
                f"❓ <b>Add button to main menu?</b>\n\n"
                f"This will create a button in your main menu that links to this new menu.\n\n"
                f"Recommended: <b>Yes</b> ✅",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return WAITING_ADD_TO_MAIN
        else:
            from menu_handler import menu_handler
            await update.message.reply_text("❌ Failed to create menu. Try again.")
            context.user_data.pop('new_menu_name', None)
            await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
            return ConversationHandler.END
    
    async def start_delete_menu(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start deleting a menu"""
        user_id = update.effective_user.id
        message = update.callback_query.message if update.callback_query else update.message
        
        if not self.is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("⛔ Access Denied", show_alert=True)
            await message.reply_text("⛔ Access Denied!")
            return ConversationHandler.END
        
        if update.callback_query:
            await update.callback_query.answer()
        
        # Get deletable menus (not main or admin)
        deletable_menus = [m for m in self.config.menus.keys() if m not in ['main', 'admin']]
        
        if not deletable_menus:
            await message.reply_text(
                "❌ No menus available to delete!\n\n"
                "You cannot delete 'main' or 'admin' menus."
            )
            return ConversationHandler.END
        
        menu_list = "\n".join([f"• <code>{m}</code>" for m in deletable_menus])
        
        await message.reply_text(
            "🗑️ <b>Delete Menu</b>\n\n"
            f"Available menus:\n{menu_list}\n\n"
            "⚠️ <b>Warning:</b> This will permanently delete the menu!\n\n"
            "Send the menu name to delete, or /cancel to abort.",
            parse_mode='HTML'
        )
        return WAITING_DELETE_MENU_CONFIRM
    
    async def receive_delete_menu_confirm(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Confirm and delete the menu"""
        from menu_handler import menu_handler
        
        menu_name = update.message.text.strip().lower()
        
        # Check if menu exists and is deletable
        if menu_name not in self.config.menus:
            await update.message.reply_text(
                f"❌ Menu '<code>{menu_name}</code>' does not exist!\n\n"
                "Try again or send /cancel to abort.",
                parse_mode='HTML'
            )
            return WAITING_DELETE_MENU_CONFIRM
        
        if menu_name in ['main', 'admin']:
            await update.message.reply_text(
                f"❌ Cannot delete essential menu '<code>{menu_name}</code>'!",
                parse_mode='HTML'
            )
            return WAITING_DELETE_MENU_CONFIRM
        
        # Delete the menu
        if self.config.delete_menu(menu_name):
            await update.message.reply_text(
                f"✅ <b>Menu Deleted!</b>\n\n"
                f"Menu '<code>{menu_name}</code>' has been removed.\n\n"
                f"💡 Button mappings pointing to this menu were also removed.",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text("❌ Failed to delete menu. Try again.")
        
        await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        return ConversationHandler.END
    
    async def receive_new_button_name(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive new button name and add it to menu"""
        from menu_handler import menu_handler
        
        new_button_text = update.message.text.strip()
        menu_name = context.user_data.get('editing_menu')
        
        if menu_name in self.config.config['menus']:
            # Add button as a new row (before the last row which usually has Back/Main Menu)
            buttons = self.config.config['menus'][menu_name]['buttons']
            
            # Insert before the last row (navigation buttons)
            if len(buttons) > 0:
                buttons.insert(-1, [new_button_text])
            else:
                buttons.append([new_button_text])
            
            if self.config.save_config():
                await update.message.reply_text(
                    f"✅ <b>Button added successfully!</b>\n\n"
                    f"Menu: <code>{menu_name}</code>\n"
                    f"New button: <code>{new_button_text}</code>\n\n"
                    f"💡 <b>Next Steps:</b>\n"
                    f"• Use '💬 Edit Response' to set what happens when clicked\n"
                    f"• Or edit menu_config.json to map it to another menu",
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text("❌ Failed to add button.")
        else:
            await update.message.reply_text(f"❌ Menu '{menu_name}' not found.")
        
        context.user_data.pop('editing_menu', None)
        await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        return ConversationHandler.END
    
    async def receive_add_to_main_choice(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive choice about adding to main menu"""
        from menu_handler import menu_handler
        
        choice = update.message.text.strip()
        menu_name = context.user_data.get('new_menu_name')
        
        if "Yes" in choice or "yes" in choice or "✅" in choice:
            # Ask for button text
            await update.message.reply_text(
                f"🔘 <b>Button Text for Main Menu</b>\n\n"
                f"Send me the text for the button that will open this menu.\n\n"
                f"Example: <code>🛠️ {menu_name.title()}</code>\n\n"
                f"Send /cancel to abort.",
                parse_mode='HTML'
            )
            return WAITING_MAIN_BUTTON_TEXT
        else:
            # User chose not to add to main menu
            await update.message.reply_text(
                f"✅ <b>Menu created!</b>\n\n"
                f"Menu '<code>{menu_name}</code>' is ready.\n\n"
                f"💡 To access it, you'll need to manually:\n"
                f"1. Add a button to another menu\n"
                f"2. Map it in button_mapping in menu_config.json",
                parse_mode='HTML'
            )
            context.user_data.pop('new_menu_name', None)
            context.user_data.pop('new_menu_title', None)
            await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
            return ConversationHandler.END
    
    async def receive_main_button_text(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive button text and add to main menu with mapping"""
        from menu_handler import menu_handler
        
        button_text = update.message.text.strip()
        menu_name = context.user_data.get('new_menu_name')
        
        # Add button to main menu
        if 'main' in self.config.config['menus']:
            buttons = self.config.config['menus']['main']['buttons']
            
            # Insert before the last row (navigation buttons)
            if len(buttons) > 0:
                buttons.insert(-1, [button_text])
            else:
                buttons.append([button_text])
            
            # Add button mapping
            if 'button_mapping' not in self.config.config:
                self.config.config['button_mapping'] = {}
            
            self.config.config['button_mapping'][button_text] = menu_name
            
            # Save config
            if self.config.save_config():
                await update.message.reply_text(
                    f"🎉 <b>All Done!</b>\n\n"
                    f"✅ Menu created: <code>{menu_name}</code>\n"
                    f"✅ Button added to main menu: <code>{button_text}</code>\n"
                    f"✅ Button mapping created\n\n"
                    f"Your new menu is now accessible from the main menu!\n\n"
                    f"💡 <b>Next Steps:</b>\n"
                    f"• Use '🔧 Edit Menu' → '<code>{menu_name}</code>' to add more buttons\n"
                    f"• Test it by going to main menu and tapping the new button!",
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text("❌ Failed to save configuration.")
        else:
            await update.message.reply_text("❌ Main menu not found!")
        
        # Cleanup
        context.user_data.pop('new_menu_name', None)
        context.user_data.pop('new_menu_title', None)
        await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        return ConversationHandler.END
    
    async def start_edit_button_mapping(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start editing button mappings"""
        user_id = update.effective_user.id
        message = update.callback_query.message if update.callback_query else update.message
        
        if not self.is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("⛔ Access Denied", show_alert=True)
            await message.reply_html("⛔ <b>Access Denied!</b>")
            return ConversationHandler.END
        
        if update.callback_query:
            await update.callback_query.answer()
        
        # Get all button mappings
        mappings = self.config.button_mapping
        mapping_count = len(mappings)
        
        # Format mappings list
        mapping_list = ""
        for idx, (button_text, target) in enumerate(mappings.items(), 1):
            mapping_list += f"{idx}. <code>{button_text}</code> → <code>{target}</code>\n"
        
        await message.reply_html(
            "╔═══════════════════════════════╗\n"
            "║  🔗 <b>EDIT BUTTON MAPPING</b> 🔗  ║\n"
            "╚═══════════════════════════════╝\n\n"
            f"📊 <b>CURRENT MAPPINGS ({mapping_count}):</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{mapping_list}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✏️ Send the <b>button text</b> you want to remap\n"
            "   (exact text from list above)\n\n"
            "💡 <b>TIP:</b> Button mappings link button text\n"
            "   to a menu name or action (main, back, admin)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Type /cancel to abort"
        )
        return WAITING_MAPPING_BUTTON
    
    async def receive_mapping_button(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive which button mapping to edit"""
        button_text = update.message.text.strip()
        
        mappings = self.config.button_mapping
        
        if button_text not in mappings:
            await update.message.reply_html(
                f"❌ Button '<code>{button_text}</code>' not found in mappings.\n\n"
                "Please send exact button text or /cancel to abort."
            )
            return WAITING_MAPPING_BUTTON
        
        # Store button being edited
        context.user_data['mapping_button'] = button_text
        current_target = mappings[button_text]
        
        # Get available menus
        menu_list = "\n".join([f"  • <code>{k}</code>" for k in self.config.menus.keys()])
        
        await update.message.reply_html(
            f"🔗 <b>Editing Mapping for:</b>\n"
            f"<code>{button_text}</code>\n\n"
            f"📍 <b>Current Target:</b> <code>{current_target}</code>\n\n"
            f"📋 <b>Available Menus:</b>\n"
            f"{menu_list}\n\n"
            f"✨ <b>Special Actions:</b>\n"
            f"  • <code>main</code> - Main menu\n"
            f"  • <code>back</code> - Previous menu\n"
            f"  • <code>admin</code> - Admin panel\n\n"
            f"✏️ Send the new target (menu name or action)\n"
            f"   Example: <code>trust_plans</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Type /cancel to abort"
        )
        return WAITING_MAPPING_TARGET
    
    async def receive_mapping_target(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive new target for button mapping"""
        from menu_handler import menu_handler
        
        new_target = update.message.text.strip()
        button_text = context.user_data.get('mapping_button')
        
        if not button_text:
            await update.message.reply_text("❌ Error: No button selected")
            return ConversationHandler.END
        
        # Update button mapping
        self.config.config['button_mapping'][button_text] = new_target
        
        if self.config.save_config():
            await update.message.reply_html(
                "╔═══════════════════════════════╗\n"
                "║    ✅ <b>SUCCESS!</b> ✅           ║\n"
                "╚═══════════════════════════════╝\n\n"
                f"🔗 <b>Button Mapping Updated</b>\n\n"
                f"📝 Button: <code>{button_text}</code>\n"
                f"🎯 New Target: <code>{new_target}</code>\n\n"
                f"✨ Changes saved successfully!"
            )
        else:
            await update.message.reply_text("❌ Failed to save configuration.")
        
        # Cleanup
        context.user_data.pop('mapping_button', None)
        await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        return ConversationHandler.END
    
    async def cancel_conversation(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Cancel ongoing conversation"""
        from menu_handler import menu_handler
        
        await update.message.reply_html(
            "╔═══════════════════════════════╗\n"
            "║    ❌ <b>CANCELLED</b> ❌          ║\n"
            "╚═══════════════════════════════╝\n\n"
            "🔙 Operation cancelled.\n"
            "No changes were made."
        )
        await menu_handler.show_menu(update, context, 'admin', add_to_history=False)
        
        # Clean up user data
        context.user_data.pop('editing_button', None)
        context.user_data.pop('removing_admin', None)
        context.user_data.pop('adding_admin', None)
        context.user_data.pop('editing_menu', None)
        context.user_data.pop('button_to_edit', None)
        context.user_data.pop('button_row', None)
        context.user_data.pop('button_col', None)
        context.user_data.pop('new_menu_name', None)
        context.user_data.pop('removing_button', None)
        context.user_data.pop('mapping_button', None)
        
        return ConversationHandler.END


# Global admin handler instance
admin_handler = AdminHandler()

