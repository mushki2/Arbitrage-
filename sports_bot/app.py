import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from handlers import start, handle_home, handle_sports, handle_arbitrage, run_ai_analysis, get_history, handle_event_selection

# It's recommended to set your bot token as an environment variable.
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')

app = Flask(__name__)
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Register handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(handle_home, pattern='^home$'))
dispatcher.add_handler(CallbackQueryHandler(handle_sports, pattern='^sports$'))
dispatcher.add_handler(CallbackQueryHandler(handle_arbitrage, pattern='^arbitrage$'))
dispatcher.add_handler(CallbackQueryHandler(run_ai_analysis, pattern='^run_ai_analysis$'))
dispatcher.add_handler(CallbackQueryHandler(get_history, pattern='^get_history_'))
# A generic callback handler for sport selection (can be expanded)
from handlers import handle_sport_selection
dispatcher.add_handler(CallbackQueryHandler(handle_sport_selection, pattern='^sport_'))
dispatcher.add_handler(CallbackQueryHandler(handle_event_selection, pattern='^event_'))

# A fallback message handler
def unknown(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
dispatcher.add_handler(MessageHandler(Filters.command, unknown))


@app.route('/')
def index():
    return 'Bot is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, updater.bot)
    dispatcher.process_update(update)
    return 'ok'

# It's better practice to set the webhook via a separate script or manually
# rather than in the main app file.
# Webhook URL format: https://<yourusername>.pythonanywhere.com/webhook

if __name__ == '__main__':
    # This block is for local development using polling.
    # On PythonAnywhere, you'll use the webhook.
    print("Starting bot in polling mode for local development...")
    updater.start_polling()
    updater.idle()
