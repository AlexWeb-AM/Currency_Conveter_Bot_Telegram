from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import telebot
from currency_converter import CurrencyConverter


c = CurrencyConverter()
bot = telebot.TeleBot("8027128151:AAG2Jjp85LV7iw4JWSqt9thBGNVrLVdozsk")

user_data = {}

def is_valid_number(value):
    try:
        value = value.replace(',', '.')
        float(value)
        return True
    except ValueError:
        return False



@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_photo(message.chat.id, open('images/start.webp', 'rb'), caption='Bot started successfully 😊')
    bot.send_message(message.chat.id, "Bot created for currency conversion 💵.")
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Convert", callback_data="convert")
    markup.add(button)
    bot.send_message(message.chat.id, "Click the button to start converting💲", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "convert")
def accept_currency_first(call):
    user_data[call.from_user.id] = {'state': 'awaiting_first_currency'}
    bot.send_message(call.message.chat.id, 'Write the first currency (e.g., USD)')

@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    user_id = message.from_user.id
    user_state = user_data.get(user_id, {}).get('state')

    if user_state == 'awaiting_first_currency':
        currency1 = message.text.upper()
        user_data[user_id]['currency1'] = currency1
        user_data[user_id]['state'] = 'awaiting_second_currency'
        bot.send_message(message.chat.id, f"First currency: {currency1}. Now write the second currency (e.g., EUR).")

    elif user_state == 'awaiting_second_currency':
        currency2 = message.text.upper()
        user_data[user_id]['currency2'] = currency2
        user_data[user_id]['state'] = 'awaiting_amount'
        bot.send_message(message.chat.id, f"Second currency: {currency2}. Now write the amount you want to convert.")

    elif user_state == 'awaiting_amount':
        amount_text = message.text
        if is_valid_number(amount_text):
            amount = float(amount_text.replace(',', '.'))
            currency1 = user_data[user_id]['currency1']
            currency2 = user_data[user_id]['currency2']

            try:
                converted_amount = c.convert(amount, currency1, currency2)
                bot.send_message(
                    message.chat.id,
                    f"{amount} {currency1} -> {converted_amount:.2f} {currency2}"
                )
                user_data[user_id] = None
            except Exception as e:
                bot.send_message(message.chat.id, f"Error in conversion: {e}")
        else:
            bot.send_message(message.chat.id, "Please enter a valid numeric amount.")

bot.polling()
