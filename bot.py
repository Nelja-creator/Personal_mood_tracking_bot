import os
from dotenv import load_dotenv
import sqlite3 
from datetime import datetime
#after installing telegram library in the termianal 
from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,ContextTypes

# This looks for the .env file and loads the variables
load_dotenv()

# This grabs your new token safely
TOKEN = os.getenv('TELEGRAM_TOKEN')

# TEMPORARY CHECK: Run your bot and check your terminal for this message!
if not TOKEN:
    print("❌ ERROR: Your token is empty! The script cannot find .env or TELEGRAM_TOKEN")
else:
    print(f"✅ Token found successfully: {TOKEN[:5]}...{TOKEN[-5:]}")

def init_db():
    """Creates the database and table if they don't exist already."""
    conn = sqlite3.connect('mood_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mood_level INTEGER,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greeting command."""
    await update.message.reply_text(
        "Welcome! I am your Personal Mood Tracker. "
        "Use /log <number> to save your current mood (1-10)."
    )

async def log_mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saves a mood entry to the SQLite database."""
    user_id = update.effective_user.id
    try:
        # Get the number after the command (e.g., the '8' in /log 8)
        mood_level = int(context.args[0])
        
        # Database Operation
        conn = sqlite3.connect('mood_tracker.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO mood_logs (user_id, mood_level, timestamp)
            VALUES (?, ?, ?)
        ''', (user_id, mood_level, datetime.now()))
        conn.commit()
        
        # Get a quick count of total entries for this user
        cursor.execute('SELECT COUNT(*) FROM mood_logs WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()[0]
        conn.close()

        await update.message.reply_text(f"✅ Logged mood: {mood_level}/10. (Total entries: {count})")
    
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Usage: /log <number> (Example: /log 7)")

if __name__=='__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('log', log_mood))
    
    print("Bot is running...")
    application.run_polling()


