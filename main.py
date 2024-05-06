import requests
from datetime import datetime, timedelta
import pytz

import os, django
# import schedule, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import User, Text

API_TOKEN = '7183505723:AAEzCfQf1dfEGyCPEpWkmvmx0ZUPv0xgYYk'
CHAT_ID = '4233894523'

params = {
    CHAT_ID: CHAT_ID
}


def job():
    url = f'https://api.telegram.org/bot{API_TOKEN}/getUpdates'

    response = requests.get(url, params=params)
    if response.ok:
        chat_history = response.json()['result']
        print("Sssssss")
        i = 1
        for mes in chat_history:
            a = mes['update_id']
            if 'message' not in mes.keys():
                continue
            else:
                user = mes['message']['from']
                user_id = user['id']

                timestamp = datetime.utcfromtimestamp(mes['message']['date'])
                dt_object = timestamp
                original_timezone = pytz.utc
                dt_object = original_timezone.localize(dt_object)
                original_date = dt_object + timedelta(hours=5)

                if 'last_name' in user.keys():
                    lastname = user['last_name']
                if 'username' in user.keys():
                    username = user['username']

                all_users = User.objects.values('user_id')

                i += 1
                if {"user_id": f"{user_id}"} not in all_users:
                    User.objects.create(user_id=user_id, firstname=user['first_name'], lastname=lastname, username=username)

                text_info = {'text': f"{mes['message']['text']}", "date": f"{original_date}"}

                if text_info not in Text.objects.values("text", "date"):
                    Text.objects.create(user_id=user_id, text=mes['message']['text'], date=original_date)
                    print("Saaaa")
    else:
        print('Failed to retrieve chat history:', response.text)


schedule.every().second.do(job)
while True:
    schedule.run_pending()
    time.sleep(1)


from telegram import ReplyKeyboardMarkup, Update, Bot, KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)

import logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


INFO = "Ma'lumot"


MAIN_KEYBOARD = [[INFO]]


def start(update, context: CallbackContext):

    update.message.reply_text(
        "Assalomu alaykum botga xush kelibsiz",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_KEYBOARD,
            one_time_keyboard=False,
            input_field_placeholder="Quyidagilardan birini tanlang",
            resize_keyboard=True
        ),
    )


def step(update, context: CallbackContext):
    texts = Text.objects.values('date', 'text')
    text = ''

    for x in texts:
        text += x['text'] + ' --- ' + x['date'] + '\n'

    update.message.reply_text(text)


def main():
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(Filters.text(INFO), step)
        ],
        states={
        },
        fallbacks=[

        ],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

