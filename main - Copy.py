import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "7803374926:AAGjE3xKXsf0u9alxFr1KyuJ-e73SgwtJMY"
API_KEY = "4ae4ca2948a8aa229d43ecf6"

daily_number = None  # Global variable to store daily number

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_text = (
        "Hello! I am your calculator bot. Send me a calculation to perform or a currency amount to convert.\n\n"
        "Here's how you can use this bot:\n\n"
        "/start - Start the bot and get a welcome message.\n"
        "/help - Get this help message with instructions on how to use the bot.\n"
        "/setdaily <number> - Set a daily number that you can use in calculations.\n"
        "Examples: /setdaily 50\n"
        "calculate <operation> - Perform calculations using the daily number.\n"
        "Examples: calculate + 10, calculate * 5, calculate - 3\n"
        "<amount> RUB - Convert RUB to USD.\n"
        "Examples: 100 RUB\n"
        "<amount> USD - Convert USD to RUB.\n"
        "Examples: 100 USD\n\n"
        "Feel free to send me a calculation to perform or a currency amount to convert!"
    )
    await update.message.reply_text(start_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Hello! Here's how you can use this bot:\n\n"
        "/start - Start the bot and get a welcome message.\n"
        "/help - Get this help message with instructions on how to use the bot.\n"
        "/setdaily <number> - Set a daily number that you can use in calculations.\n"
        "Examples: /setdaily 50\n"
        "calculate <operation> - Perform calculations using the daily number.\n"
        "Examples: calculate + 10, calculate * 5, calculate - 3\n"
        "<amount> RUB - Convert RUB to USD.\n"
        "Examples: 100 RUB\n"
        "<amount> USD - Convert USD to RUB.\n"
        "Examples: 100 USD\n\n"
        "Feel free to send me a calculation to perform or a currency amount to convert!"
    )
    await update.message.reply_text(help_text)

def get_exchange_rate(base_currency, target_currency):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['conversion_rates'].get(target_currency, None)
    else:
        logging.error(f"Error fetching exchange rates: {response.status_code}")
        return None

async def set_daily_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global daily_number
    try:
        daily_number = float(update.message.text.split()[1])
        await update.message.reply_text(f'Daily number set to {daily_number}')
    except (ValueError, IndexError):
        await update.message.reply_text('Please send a valid number using the format: /setdaily <number>')

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global daily_number
    expression = update.message.text
    try:
        if 'RUB' in expression:
            amount = float(expression.replace('RUB', '').strip())
            exchange_rate = get_exchange_rate('RUB', 'USD')
            if exchange_rate:
                result = amount * exchange_rate
                await update.message.reply_text(f'{amount} RUB is {result:.2f} USD')
            else:
                await update.message.reply_text('Error: Unable to fetch exchange rate for RUB to USD.')
        elif 'USD' in expression:
            amount = float(expression.replace('USD', '').strip())
            exchange_rate = get_exchange_rate('USD', 'RUB')
            if exchange_rate:
                result = amount * exchange_rate
                await update.message.reply_text(f'{amount} USD is {result:.2f} RUB')
            else:
                await update.message.reply_text('Error: Unable to fetch exchange rate for USD to RUB.')
        elif daily_number is not None and 'calculate' in expression:
            # Replace 'calculate' with the daily number in the expression
            modified_expression = expression.replace('calculate', str(daily_number))
            result = eval(modified_expression)
            await update.message.reply_text(f'The result of {expression} is {result}')
            daily_number = result  # Update daily number to the result
        else:
            # Evaluate general mathematical expressions
            result = eval(expression)
            await update.message.reply_text(f'The result of {expression} is {result}')
            daily_number = result  # Update daily number to the result
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('setdaily', set_daily_number))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

    app.run_polling()
