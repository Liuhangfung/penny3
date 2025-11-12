"""
Main Telegram Bot Entry Point
Initializes and runs the bot with polling
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from settings import config, BOT_NAME
from menu_handler import menu_handler
from admin_handler import (
    admin_handler,
    WAITING_WELCOME_MSG,
    WAITING_RESPONSE_BUTTON,
    WAITING_RESPONSE_TEXT,
    WAITING_ADMIN_ID,
    WAITING_MENU_SELECT,
    WAITING_MENU_ACTION,
    WAITING_NEW_TITLE,
    WAITING_BUTTON_SELECT,
    WAITING_NEW_BUTTON_TEXT,
    WAITING_NEW_MENU_NAME,
    WAITING_NEW_MENU_TITLE,
    WAITING_DELETE_MENU_CONFIRM,
    WAITING_NEW_BUTTON_NAME,
    WAITING_ADD_TO_MAIN,
    WAITING_MAIN_BUTTON_TEXT
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors that occur during bot operation
    
    Args:
        update: Telegram update object
        context: Telegram context object
    """
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    # Optionally notify user of error
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred while processing your request. Please try again."
        )


async def post_init(application: Application) -> None:
    """
    Called after the bot is initialized
    """
    bot_info = await application.bot.get_me()
    logger.info(f"Bot started: @{bot_info.username}")
    logger.info(f"Bot ID: {bot_info.id}")
    logger.info("Bot is ready to receive messages!")


def main() -> None:
    """
    Main function to start the bot
    """
    try:
        # Create the Application
        logger.info(f"Initializing {BOT_NAME}...")
        # Disable job_queue for Python 3.13 compatibility
        application = (
            Application.builder()
            .token(config.bot_token)
            .post_init(post_init)
            .job_queue(None)
            .build()
        )
        
        # Register command handlers
        application.add_handler(CommandHandler("start", menu_handler.handle_start))
        application.add_handler(CommandHandler("help", menu_handler.handle_help))
        application.add_handler(CommandHandler("menu", menu_handler.handle_menu_command))
        
        # Register admin conversation handlers (must be before general message handler)
        # These handlers catch specific admin button presses that start conversations
        
        # Edit Welcome Message conversation
        welcome_conv = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^📝 Edit Welcome Message$"), admin_handler.start_edit_welcome)
            ],
            states={
                WAITING_WELCOME_MSG: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_welcome_message)
                ],
            },
            fallbacks=[CommandHandler("cancel", admin_handler.cancel_conversation)],
            per_user=True,
            per_chat=True
        )
        application.add_handler(welcome_conv)
        
        # Edit Response conversation
        response_conv = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^💬 Edit Response$"), admin_handler.start_edit_response)
            ],
            states={
                WAITING_RESPONSE_BUTTON: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_response_button)
                ],
                WAITING_RESPONSE_TEXT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_response_text)
                ],
            },
            fallbacks=[CommandHandler("cancel", admin_handler.cancel_conversation)],
            per_user=True,
            per_chat=True
        )
        application.add_handler(response_conv)
        
        # Add Admin conversation
        add_admin_conv = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^➕ Add Admin$"), admin_handler.start_add_admin)
            ],
            states={
                WAITING_ADMIN_ID: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_admin_id)
                ],
            },
            fallbacks=[CommandHandler("cancel", admin_handler.cancel_conversation)],
            per_user=True,
            per_chat=True
        )
        application.add_handler(add_admin_conv)
        
        # Remove Admin conversation
        remove_admin_conv = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^➖ Remove Admin$"), admin_handler.start_remove_admin)
            ],
            states={
                WAITING_ADMIN_ID: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_admin_id)
                ],
            },
            fallbacks=[CommandHandler("cancel", admin_handler.cancel_conversation)],
            per_user=True,
            per_chat=True
        )
        application.add_handler(remove_admin_conv)
        
        # Edit Menu conversation
        edit_menu_conv = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^🔧 Edit Menu$"), admin_handler.start_edit_menu)
            ],
            states={
                WAITING_MENU_SELECT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_menu_selection)
                ],
                WAITING_MENU_ACTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_menu_action)
                ],
                WAITING_NEW_TITLE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_new_title)
                ],
                WAITING_BUTTON_SELECT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_button_selection)
                ],
                WAITING_NEW_BUTTON_TEXT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_new_button_text)
                ],
                WAITING_NEW_BUTTON_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_new_button_name)
                ],
            },
            fallbacks=[CommandHandler("cancel", admin_handler.cancel_conversation)],
            per_user=True,
            per_chat=True
        )
        application.add_handler(edit_menu_conv)
        
        # Add Menu conversation
        add_menu_conv = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^➕ Add Menu$"), admin_handler.start_add_menu)
            ],
            states={
                WAITING_NEW_MENU_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_new_menu_name)
                ],
                WAITING_NEW_MENU_TITLE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_new_menu_title)
                ],
                WAITING_ADD_TO_MAIN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_add_to_main_choice)
                ],
                WAITING_MAIN_BUTTON_TEXT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_main_button_text)
                ],
            },
            fallbacks=[CommandHandler("cancel", admin_handler.cancel_conversation)],
            per_user=True,
            per_chat=True
        )
        application.add_handler(add_menu_conv)
        
        # Delete Menu conversation
        delete_menu_conv = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^🗑️ Delete Menu$"), admin_handler.start_delete_menu)
            ],
            states={
                WAITING_DELETE_MENU_CONFIRM: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.receive_delete_menu_confirm)
                ],
            },
            fallbacks=[CommandHandler("cancel", admin_handler.cancel_conversation)],
            per_user=True,
            per_chat=True
        )
        application.add_handler(delete_menu_conv)
        
        # Register message handler for button presses (text messages)
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                menu_handler.handle_button_press
            )
        )
        
        # Register error handler
        application.add_error_handler(error_handler)
        
        # Start the bot with polling
        logger.info("Starting polling...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}")
        print("Please check your menu_config.json file.\n")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")


if __name__ == '__main__':
    print("=" * 50)
    print(f"  {BOT_NAME}")
    print("=" * 50)
    print()
    main()

