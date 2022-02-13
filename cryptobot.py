from coinbase.wallet.client import Client
from telegram import ParseMode
from telegram.ext import CommandHandler, Defaults, Updater

COINBASE_KEY = '<YOUR COINBASE KEY>'
COINBASE_SECRET = '<YOUR COINBASE SECRET>'
TELEGRAM_TKN = '<YOUR TELEGRAM TOKEN>'

#initialising coinbase API
coinbase_client = Client(COINBASE_KEY, COINBASE_SECRET)


def startCommand(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Hello!\nI am a Crypto Alert Bot created by Shaunak Inamdar.\nI send you alerts when your cryptocurrency reaches a certain price.\nAll cryptos listed on Coinbase India are supported for now.\nUsage: <i>/alert {crypto code} {> / &lt;} {price}</i>')

def priceAlert(update, context):
    if len(context.args) > 2:
        crypto = context.args[0].upper()
        sign = context.args[1]
        price = context.args[2]

        context.job_queue.run_repeating(priceAlertCallback, interval=15, first=15, context=[crypto, sign, price, update.message.chat_id])

        response = f" I will send you a message when the price of {crypto} reaches ₹{price}, \n"
        response += f"the current price of {crypto} is ₹{coinbase_client.get_spot_price(currency_pair=crypto + '-INR')['amount']}"

    else:
        response = 'Please provide a crypto code and a price value: \n<i>/alert {crypto code} {> / &lt;} {price}</i>'
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)

def priceAlertCallback(context):
    crypto = context.job.context[0]
    sign = context.job.context[1]
    price = context.job.context[2]
    chat_id = context.job.context[3]

    send = False
    spot_price = coinbase_client.get_spot_price(currency_pair=crypto + '-INR')["amount"]

    if sign == '<':
        if float(price) >= float(spot_price):
            send = True
    
    else:
        if float(price) <= float(spot_price):
            send=True

    if send:
        response = f"Hey! {crypto} has surpassed ₹{price} and has just reached <b>₹{spot_price}</b>!"

        context.job.schedule_removal()

        context.bot.send_message(chat_id=chat_id, text=response)

if __name__ == '__main__':
    upadater = Updater(token=TELEGRAM_TKN, defaults=Defaults(parse_mode=ParseMode.HTML))
    # default parsemode of HTML to add HTML elements in response messages
    dispacher = upadater.dispatcher

    dispacher.add_handler(CommandHandler('start', startCommand)) # bot is accessed via '/start'
    dispacher.add_handler(CommandHandler('alert', priceAlert)) # bot is accessed via '/alert'

    upadater.start_polling() # starts bot

    upadater.idle() # stops the bot
    
