import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
ADDING_TODO = 1
todo_list = []  # List to store tasks

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Use /help to see available commands. 📝")

# /help command - Lists available commands
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """📌 Available commands:
/start - 🚀 Start the bot
/help - 📖 Show this help message
/addtask - ➕ Start adding tasks
/donetask - ✅ Finish adding tasks
/showtask - 📋 Show all tasks
/deletetask [task_number] - ❌ Delete a specific task or all tasks
"""
    await update.message.reply_text(help_text)

# /addtask command - Start adding tasks
async def addtask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Send me tasks one by one. Type /donetask when finished.")
    return ADDING_TODO

# Handle task addition
async def add_todo_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    todo_list.append(update.message.text)
    await update.message.reply_text(f"✅ Task added: {update.message.text}")
    return ADDING_TODO

# /donetask command - Stop adding tasks
async def donetask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Task entry stopped. Use /showtask to see tasks.")
    return ConversationHandler.END

# /showtask command - Show all tasks
async def showtask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if todo_list:
        tasks = "\n".join(f"{idx+1}. {task} 📝" for idx, task in enumerate(todo_list))
        await update.message.reply_text(f"📋 Your tasks:\n{tasks}")
    else:
        await update.message.reply_text("ℹ️ No tasks available.")

# /deletetask command - Delete a specific task or all tasks
async def deletetask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if not args:
        await update.message.reply_text("⚠️ Usage: /deletetask [task_number] or /deletetask all")
        return

    if args[0].lower() == "all":
        todo_list.clear()
        await update.message.reply_text("🗑️ All tasks deleted.")
    else:
        try:
            task_index = int(args[0]) - 1
            if 0 <= task_index < len(todo_list):
                deleted_task = todo_list.pop(task_index)
                await update.message.reply_text(f"❌ Deleted task: {deleted_task}")
            else:
                await update.message.reply_text("⚠️ Invalid task number.")
        except ValueError:
            await update.message.reply_text("⚠️ Please provide a valid task number.")

# Handle unknown commands
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Sorry, I didn't understand that command. Use /help to see available commands.")

# Handle unknown text messages
async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤔 I'm not sure what you mean. Type /help to see available commands.")

# Main function to set up the bot
def main():
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_token:
        logging.error("❌ Bot token not found in environment variables.")
        return

    app = Application.builder().token(bot_token).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("showtask", showtask))
    app.add_handler(CommandHandler("deletetask", deletetask))

    # Conversation handler for adding tasks
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addtask", addtask)],
        states={ADDING_TODO: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_todo_item)]},
        fallbacks=[CommandHandler("donetask", donetask)]
    )
    app.add_handler(conv_handler)

    # Handle unknown text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text))
    
    # Handle unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    logging.info("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()