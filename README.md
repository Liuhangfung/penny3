# 🤖 Telegram Menu Bot

A complete and modular Telegram bot with a customizable button menu system using ReplyKeyboardMarkup. Perfect for non-coders who want to create interactive menu-driven Telegram bots.

## 📋 Features

- ✅ **Easy Configuration**: Edit menus via JSON file - no coding required
- ✅ **Admin Panel** 🆕: Edit bot content directly through Telegram!
- ✅ **Live Editing** 🆕: Change messages and responses without restarting
- ✅ **Dynamic Menus**: Create unlimited menus and submenus
- ✅ **Navigation History**: Built-in back button functionality
- ✅ **Custom Responses**: Define custom messages for each button
- ✅ **Reply Keyboard**: Uses Telegram's ReplyKeyboardMarkup for native feel
- ✅ **Multi-Admin Support** 🆕: Multiple users can have admin access
- ✅ **Modular Design**: Clean separation of concerns
- ✅ **Error Handling**: Robust error handling and logging
- ✅ **Python 3.8+**: Modern async/await syntax

## 📁 Project Structure

```
telegram_bot/
├── bot.py               # Main entry point and polling loop
├── menu_handler.py      # Menu logic and user interaction
├── admin_handler.py     # Admin features and live editing (NEW!)
├── settings.py          # Configuration loader and constants
├── menu_config.json     # Editable menu configuration (NO CODING!)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))

### 2. Installation

Clone or download this project, then install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configuration

Edit `menu_config.json` and update your bot token:

```json
{
  "bot_token": "YOUR_BOT_TOKEN_HERE",
  ...
}
```

**Important**: Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token from BotFather.

### 4. Run the Bot

```bash
python bot.py
```

You should see:

```
==================================================
  Menu Demo Chat Bot
==================================================

INFO - Initializing Menu Demo Chat Bot...
INFO - Bot started: @your_bot_name
INFO - Bot is ready to receive messages!
```

### 5. Test Your Bot

Open Telegram and send `/start` to your bot. You should see the welcome message and main menu!

## 🎨 Customizing Your Bot

All customization is done in `menu_config.json` - **no Python coding required!**

### Basic Structure

```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "welcome_message": "👋 Welcome! Please choose an option below.",
  "menus": { ... },
  "button_mapping": { ... },
  "responses": { ... }
}
```

### Adding a New Menu

1. Add your menu to the `menus` section:

```json
"menus": {
  "my_new_menu": {
    "title": "🎉 My New Menu 🎉",
    "buttons": [
      ["Option 1", "Option 2"],
      ["Option 3"],
      ["⬅ Back", "🔝 Main Menu"]
    ]
  }
}
```

2. Add button mapping to link it from another menu:

```json
"button_mapping": {
  "🎉 My Menu Button 🎉": "my_new_menu"
}
```

3. Add the button to parent menu:

```json
"main": {
  "title": "Main Menu",
  "buttons": [
    ["💎 Enquiry 💎"],
    ["🎉 My Menu Button 🎉"],
    ...
  ]
}
```

### Adding Custom Responses

Define what happens when a button is pressed:

```json
"responses": {
  "Option 1": "You selected Option 1! Here's some helpful info...",
  "Option 2": "Thanks for choosing Option 2!"
}
```

### Button Types

#### Navigation Buttons
- Map to other menus in `button_mapping`
- Example: `"💎 Enquiry 💎": "enquiry"`

#### Action Buttons
- Have custom responses in `responses`
- Example: `"Email Support": "📧 Email us at: support@example.com"`

#### Special Buttons
- `"⬅ Back": "back"` - Goes to previous menu
- `"🔝 Main Menu": "main"` - Goes to main menu

## 📖 Menu Configuration Reference

### Menu Object

```json
"menu_name": {
  "title": "Text shown when menu opens",
  "buttons": [
    ["Button Row 1 Col 1", "Button Row 1 Col 2"],
    ["Button Row 2 Col 1"],
    ["⬅ Back", "🔝 Main Menu"]
  ]
}
```

- Each array in `buttons` is a row
- Each string in a row is a button
- Buttons automatically resize to fit screen

### Button Mapping

```json
"button_mapping": {
  "Button Text": "menu_name_or_action"
}
```

Actions can be:
- Menu name (e.g., `"enquiry"`)
- `"back"` - Navigate to previous menu
- `"main"` - Go to main menu

### Custom Responses

```json
"responses": {
  "Button Text": "Message to send when button is pressed"
}
```

## 💡 Examples

### Example 1: Restaurant Menu Bot

```json
{
  "menus": {
    "main": {
      "title": "🍽️ Welcome to our Restaurant!",
      "buttons": [
        ["📋 Menu"],
        ["📍 Location"],
        ["📞 Contact"]
      ]
    },
    "menu": {
      "title": "📋 Our Menu",
      "buttons": [
        ["🍕 Pizza", "🍔 Burgers"],
        ["🥗 Salads", "🍰 Desserts"],
        ["⬅ Back", "🔝 Main Menu"]
      ]
    }
  },
  "button_mapping": {
    "📋 Menu": "menu",
    "⬅ Back": "back",
    "🔝 Main Menu": "main"
  },
  "responses": {
    "🍕 Pizza": "Check our pizza menu at: www.example.com/pizza",
    "📍 Location": "We're located at: 123 Main St, City",
    "📞 Contact": "Call us: +1-234-567-8900"
  }
}
```

### Example 2: Support Bot

```json
{
  "menus": {
    "main": {
      "title": "👋 How can we help?",
      "buttons": [
        ["📚 Documentation"],
        ["🐛 Report Bug"],
        ["💬 Live Chat"]
      ]
    }
  },
  "responses": {
    "📚 Documentation": "Visit our docs: https://docs.example.com",
    "🐛 Report Bug": "Email bugs to: bugs@example.com",
    "💬 Live Chat": "Chat with us: https://chat.example.com"
  }
}
```

## ⚙️ Admin Settings (NEW!)

Admins can now edit the bot content **directly through Telegram** without editing files!

### Setting Up Your First Admin

1. Start your bot and send `/start`
2. Copy your User ID from the welcome message
3. Stop the bot (`Ctrl+C`)
4. Edit `menu_config.json` and add your User ID to `admin_ids`:

```json
{
  "admin_ids": [123456789],
  ...
}
```

5. Restart the bot
6. Send `/start` again - you'll now see a ⚙️ **Settings** button!

### Admin Features

Once you're an admin, tap **⚙️ Settings** to access:

#### 📝 Edit Welcome Message
- Change the greeting message users see when they start the bot
- Updates instantly without restarting

#### 💬 Edit Response
- Modify what the bot says when users press specific buttons
- Perfect for updating info without touching code

#### 👥 Manage Admins
- **Add Admin**: Give admin access to other users
- **Remove Admin**: Revoke admin access
- You cannot remove yourself as admin

#### 🔄 Reload Config
- Reload changes from `menu_config.json` without restarting the bot
- Useful after manual file edits

#### 🔧 Edit Menu / ➕ Add Menu / 🗑️ Delete Menu
- These require editing `menu_config.json` directly
- Prevents accidental menu corruption

### Admin Commands

- `/cancel` - Cancel any ongoing editing operation

### Example Admin Workflow

1. User reports wrong phone number in Contact button
2. Admin taps **⚙️ Settings** → **💬 Edit Response**
3. Bot shows list of current responses
4. Admin sends: `Phone Support`
5. Bot asks for new response
6. Admin sends: `📱 Call us at: +1-234-567-8901`
7. ✅ Updated! No restart needed!

## 🔧 Bot Commands

Users can use these commands in your bot:

- `/start` - Start the bot and show welcome + main menu (also shows your User ID)
- `/help` - Display help information
- `/menu` - Return to main menu from anywhere
- `/cancel` - (Admin only) Cancel ongoing editing operation

## 📝 Logging

The bot logs important events to console:

- User actions (button presses, menu navigation)
- Errors and exceptions
- Bot startup information

Logs include timestamps and severity levels for easy debugging.

## 🛠️ Advanced: Editing Python Code

While most users won't need to edit Python code, here's what each file does:

### `bot.py`
- Main entry point
- Initializes bot and starts polling
- Registers command and message handlers
- Registers admin conversation handlers
- Error handling

### `menu_handler.py`
- Menu creation from JSON config
- Navigation logic (history, back button)
- Button press handling
- Command handlers (/start, /help, /menu)
- Dynamic Settings button for admins

### `admin_handler.py` 🆕
- Admin authentication
- Live content editing (welcome messages, responses)
- Admin management (add/remove admins)
- Configuration reloading
- Conversation handlers for editing workflows

### `settings.py`
- Loads and validates `menu_config.json`
- Provides config access to other modules
- Save configuration back to JSON
- Configuration update methods
- Admin ID management

## 🐛 Troubleshooting

### Bot doesn't start

**Error**: `Please update 'bot_token' in menu_config.json`
- **Solution**: Replace `YOUR_BOT_TOKEN_HERE` with your actual token from BotFather

**Error**: `Configuration file 'menu_config.json' not found`
- **Solution**: Ensure `menu_config.json` is in the same folder as `bot.py`

### Menu doesn't appear

- Check that menu name in `button_mapping` matches menu name in `menus`
- Verify JSON syntax (use a JSON validator)
- Check bot logs for errors

### Button doesn't work

- Ensure button text in menu matches exactly in `button_mapping` or `responses`
- Button text is case-sensitive and must match exactly (including emojis and spaces)

## 📦 Dependencies

- `python-telegram-bot` (v21.0.1) - Main bot framework
- Python 3.8+ required

## 📄 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Feel free to fork and customize this bot for your needs!

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review `menu_config.json` for syntax errors
3. Check bot logs in console
4. Refer to [python-telegram-bot documentation](https://docs.python-telegram-bot.org/)

---

**Happy Bot Building! 🚀**

