#after installing telegram library in the termianal 
from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,ContextTypes

#replace token from botfather
TOKEN="8774608930:AAH9qZ1fC1eaVQSRXIkLFOfJltqMuqVKbSE"

# 'async' means the bot can do other things while waiting for a message to send.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm your mood tracker how are you feeling?")

if __name__=='__main__':
    app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))
print("Bot is running....")
app.run_polling()

