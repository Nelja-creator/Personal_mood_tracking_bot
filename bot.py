import os
from dotenv import load_dotenv

#after installing telegram library in the termianal 
from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,ContextTypes

# This looks for the .env file and loads the variables
load_dotenv()

# This grabs your new token safely
TOKEN = os.getenv('TELEGRAM_TOKEN')

# 'async' means the bot can do other things while waiting for a message to send.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm your mood tracker how are you feeling?")

if __name__=='__main__':
    app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))
print("Bot is running....")
app.run_polling()

