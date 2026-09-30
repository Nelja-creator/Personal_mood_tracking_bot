import io
import os
from pathlib import Path
from dotenv import load_dotenv
import sqlite3 
from datetime import datetime
import matplotlib.pyplot as plt
#after installing telegram library in the termianal 
from telegram import Update
from telegram.ext import (ApplicationBuilder,CallbackQueryHandler,CommandHandler,ContextTypes)


# This forces Python to look in the exact folder where bot.py lives
current_dir = Path(__file__).resolve().parent
env_path = current_dir / '.env'
load_dotenv(dotenv_path=env_path)

# This grabs your new token safelys
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# TEMPORARY CHECK: Run your bot and check your terminal for this message!
if not TELEGRAM_BOT_TOKEN:
    print("❌ ERROR: Your token is empty! The script cannot find .env or TELEGRAM_BOT_TOKEN")
else:
    print(f"✅ Token found successfully: {TELEGRAM_BOT_TOKEN[:5]}...{TELEGRAM_BOT_TOKEN[-5:]}")

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

def save_mood(user_id: int, mood_level: int) -> int:
    """Helper to save a mood entry and return total entry count."""
    conn = sqlite3.connect('mood_tracker.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO mood_logs (user_id, mood_level, timestamp)
        VALUES (?, ?, ?)
    ''',
        (user_id, mood_level, datetime.now()),
    )
    conn.commit()

    cursor.execute(
        'SELECT COUNT(*) FROM mood_logs WHERE user_id = ?', (user_id,)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greeting command."""
    await update.message.reply_text(
        "Welcome! I am your Personal Mood Tracker. "
        "Use /log <number> to save your current mood (1-10)."
    )

async def mood_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends inline buttons from 1 to 10."""
    keyboard = [
        [
            InlineKeyboardButton("1 😞", callback_data="mood_1"),
            InlineKeyboardButton("2 😟", callback_data="mood_2"),
            InlineKeyboardButton("3 😐", callback_data="mood_3"),
            InlineKeyboardButton("4 🙂", callback_data="mood_4"),
            InlineKeyboardButton("5 🙂", callback_data="mood_5"),
        ],
        [
            InlineKeyboardButton("6 😊", callback_data="mood_6"),
            InlineKeyboardButton("7 😊", callback_data="mood_7"),
            InlineKeyboardButton("8 😄", callback_data="mood_8"),
            InlineKeyboardButton("9 😁", callback_data="mood_9"),
            InlineKeyboardButton("10 🥳", callback_data="mood_10"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "How are you feeling right now?", reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles inline button clicks."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button click

    user_id = query.from_user.id
    # Extract the score from callback_data string "mood_X"
    mood_level = int(query.data.split("_")[1])

    count = save_mood(user_id, mood_level)
    await query.edit_message_text(
        f"✅ Logged mood: {mood_level}/10. (Total entries: {count})"
    )

async def log_mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saves a mood entry to the SQLite database."""
    user_id = update.effective_user.id
    try:
        # Get the number after the command (e.g., the '8' in /log 8)
        mood_level = int(context.args[0])
        if not (1 <= mood_level <= 10):
            await update.message.reply_text(
                "❌ Please log a number between 1 and 10."
            )
            return
        count = save_mood(user_id, mood_level)
        await update.message.reply_text(
            f"✅ Logged mood: {mood_level}/10. (Total entries: {count})"
        )

    except (IndexError, ValueError):
        await update.message.reply_text(
            "❌ Usage: /log <number> (Example: /log 7)"
        )
        
async def send_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generates a line plot of user's mood over time and sends as photo."""
    user_id = update.effective_user.id

    conn = sqlite3.connect('mood_tracker.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT timestamp, mood_level FROM mood_logs
        WHERE user_id = ?
        ORDER BY timestamp ASC
    ''',
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows or len(rows) < 2:
        await update.message.reply_text(
            "📊 Need at least 2 logged entries to build a chart!"
        )
    return     

# Parse data for plotting
    dates = [
        datetime.strptime(r[0].split('.')[0], '%Y-%m-%d %H:%M:%S') for r in rows
    ]
    scores = [r[1] for r in rows]

    # Plot creation
    plt.figure(figsize=(8, 4))
    plt.plot(dates, scores, marker='o', color='#3498db', linewidth=2)
    plt.ylim(0, 11)
    plt.xlabel("Date & Time")
    plt.ylabel("Mood Score (1-10)")
    plt.title("Your Mood Tracker History")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.gcf().autofmt_xdate()

    # Save chart into in-memory bytes buffer instead of disk
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    await update.message.reply_photo(
        photo=buf, caption="📈 Here is your mood progress over time!"
    )
       
if __name__=='__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('mood', mood_keyboard))
    application.add_handler(CommandHandler('log', log_mood))
    application.add_handler(CommandHandler('stats', send_stats))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot is running...")
    application.run_polling()


