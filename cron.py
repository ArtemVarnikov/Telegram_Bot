
import time


def cron_remainder():
    print ('Croniiiiee')
    userlist = backend.get_users()
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    keyboard.add(telebot.types.KeyboardButton('Да'), telebot.types.KeyboardButton('Нет'))
    for user in userlist:
        bot.send_message(user, 'Время повторения! Ты готов?', reply_markup=keyboard)
        bot.register_next_step_handler(message, today_command)


def cron_job(func, timer: str, *args):
    schedule.every().day.at(timer).do(func, args).tag(func.__name__)

schedule.every().day.at('04:00').do(backend.archieve).tag(backend.archieve.__name__)
schedule.every(1).minutes.do(cron_remainder).tag(cron_remainder.__name__)

while True:
    schedule.run_pending()
    time.sleep(1)

