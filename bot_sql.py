import telebot
import bd_sql
import theory
import time
import schedule
import threading
import re



backend= bd_sql.Database(r'{}'.format(bd_sql.config['bd']))


bot = telebot.TeleBot(bd_sql.config['token'])


def menu_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=4)
    keyboard.row(
        telebot.types.KeyboardButton('\U0001F4DA today'),
        telebot.types.KeyboardButton('\U0001F4D2 read'),
        telebot.types.KeyboardButton('\U0001F4C5 schedule')
    )
    keyboard.row(
        telebot.types.KeyboardButton('\U00010133 add'),
        telebot.types.KeyboardButton('\U0001F528 edit'),
        telebot.types.KeyboardButton('\U0001F3C1 delete')
    )
    keyboard.row(
        telebot.types.KeyboardButton('\U0001F64F help'),
        telebot.types.KeyboardButton('\U0001F52D theory'),
        telebot.types.KeyboardButton('\U0001F64B Пока, друг!')
    )
    return keyboard

def menu_button(*args):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    keyboard.add(telebot.types.KeyboardButton('\U0001F519 Меню'))
    return keyboard

def pass_button():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    keyboard.add(telebot.types.KeyboardButton('\u23E9 Пропустить'), telebot.types.KeyboardButton('\U0001F519 В меню'))
    return keyboard

def printing_func():
    bot.send_chat_action(user_id, 'typing')
    time.sleep(1)

def try_again(message, func): #helper method
    '''Функция, которая обрабатывает некорректный ввод пользователя'''
    func(message)

def to_menu(message): #helper method
    '''Функция, которая обрабатывает некорректный ввод пользователя'''
    if message.text == '\U0001F519 В меню' or message.text == '\U0001F519 Меню' or message.text =='\u26D4 Нет':
        menu(message, type='back')
        return True



@bot.message_handler()
def menu(message, type=None):
    global user_id
    user_id=message.chat.id
    if message.text=='/start':
        start(message)
    else:
        printing_func()
        keyboard=menu_keyboard()
        if type==None:
            printing_func()
            texting='Привет!\nВыбери, пожалуйста, пункт из меню'
        elif type=='circle':
            printing_func()
            texting='Продолжаем?'
        elif type=='back':
            printing_func()
            texting='Ага, забыли, что дальше делаем?'
        bot.send_message(message.from_user.id,
                            texting, reply_markup=keyboard)
        bot.register_next_step_handler(message, next_action)

def next_action(message):
    if message.text=='\U0001F64F help':
        help_command(message)
    elif message.text== '\U0001F52D theory':
        theory_command(message)
    elif message.text == '\U00010133 add':
        add_command(message)
    elif message.text == '\U0001F4D2 read':
        read_command(message)
    elif message.text == '\U0001F528 edit':
        edit_command(message)
    elif message.text == '\U0001F4C5 schedule':
        schedule_command(message)
    elif message.text == '\U0001F3C1 delete':
        delete_command(message)
    elif message.text == '\U0001F4DA today':
        today_command(message.from_user.id)
    elif message.text == '\U0001F64B Пока, друг!':
        bot.send_message(message.from_user.id, 'Отлично поболтали!')
        return
    else:
        keyboard = menu_keyboard()
        printing_func()
        bot.send_message(message.from_user.id,
            'Мой друг, я не волшебник, я только учусь.\nПоэтому выбери что-то из меню, будь добр)', reply_markup=keyboard)
        bot.register_next_step_handler(message, next_action)
        return


def start(message):
    keyboard=menu_keyboard()
    printing_func()
    bot.send_message(message.from_user.id,
    'Привет!\nЭтот бот предназназначен для'+
    'использования техники интервальных повторений (spaced repetitions).\n'+
    'С его помощью можно добавлять себе темы для повторения и получать напоминания по установленному графику.\n'+
    'Выбери интересующий пункт в меню - если хочешь узнать побольше о методе выбери \U0001F52D theory', reply_markup=keyboard)
    bot.register_next_step_handler(message, next_action)

def help_command(message):
    keyboard = menu_keyboard()
    printing_func()
    bot.send_message(
        message.chat.id,
        '1) Добавить новую тему\n\U00010133 add.\n' +
        '2) Просмотреть инфо по темам на сегодня\n\U0001F4DA today\n'+
        '3) Просмотреть инфо по ранее добавленным темам\n\U0001F4D2 read.\n' +
        '4) Просмотреть расписание напоминаний (по всем темам или по выбранной)\n\U0001F4C5 schedule.\n' +
        '5) Изменить информацию по конкретной теме\n\U0001F528 edit.\n' +
        '6) Удалить тему из расписания\n\U0001F3C1 delete.',
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, next_action)

def theory_command(message):
    printing_func()
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton('Кривая забывания Эббингауза', url=theory.ebbie  )    )
    keyboard.add(telebot.types.InlineKeyboardButton('Активное вспоминание (eng)', url=theory.rec_eng))
    keyboard.add(telebot.types.InlineKeyboardButton('Активное вспоминание (перевод)', url=theory.rec_ru))
    bot.send_message(
        message.chat.id,
        theory.theory,
        reply_markup=keyboard
    )

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    keyboard.add(telebot.types.KeyboardButton('\U0001F519 В меню'))
    bot.send_message(
        message.chat.id,
        'Если хочешь вернуться в меню, то нажми кнопку \U0001F519 В меню',
        reply_markup=keyboard
    )

def add_command(message):
    printing_func()
    bot.send_message(
        message.chat.id,
        'Давай добавим новую тему для интервальных повторений!\n' +
        'Для этого запишем тему, проверочные вопросы, теорию (вдруг не получится вспомнить) и расписание повторений\n' +
        'Предлагаю начать с темы. Напиши мне как мы назовем эту тему'
    )
    new_theme={'user_id' : message.from_user.id, 'theme' : '', 'questions' : '', 'theory' : '', 'schedule' : ''}
    bot.register_next_step_handler(message, add_theme, new_theme)

def add_theme(message, new_theme):
    printing_func()
    new_theme['theme'] = message.text
    keyboard=pass_button()
    bot.send_message(
        message.chat.id,
        'Отлично! Теперь добавим контрольные вопросы.\n' +
        'С ними будет проще повторять', reply_markup=keyboard
    )
    bot.register_next_step_handler(message, add_questions, new_theme)


def add_questions(message, new_theme):
    if to_menu(message):
        return
    printing_func()
    new_theme['questions'] = message.text
    keyboard=pass_button()
    bot.send_message(
        message.chat.id,
        'Отлично! Теперь теория.\n' +
        'Если не получится вспомнить, то материал будет под рукой\n' +
        'Можем добавить всю теорию сюда, либо сохранить ссылку на источник',
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, add_schedule, new_theme)

def add_schedule(message, new_theme):
    if to_menu(message):
        return
    printing_func()
    keyboard=pass_button()
    new_theme['theory'] = message.text
    bot.send_message(
        message.chat.id,
        'Есть контакт! Финальный шаг - расписание напоминаний.\n' +
        'В установленное время напомню, что пришло время повторений, и пришлю список тем на сегодня  \n' +
        'Расписание по умолчанию 1-3-7-14-30. Если это для тебя неудобно, то пришли ' +
        'расписание в формате 1-3-7-14-30 (через 1, 3, 7, 14, 30 дней от сегодяшней даты я напомню про эту тему)',
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, add_final, new_theme)


def add_final(message, new_theme):
    if to_menu(message):
        return
    printing_func()
    if message.text == '\u23E9 Пропустить':
        new_theme['schedule']='1-3-7-14-30'
    else:
        new_theme['schedule'] = message.text
    print(new_theme)
    backend.add_theme(**new_theme)
    bot.send_message(
        message.chat.id,
        'Готово! Теперь у темы {} нет шансов быть забытой'.format(new_theme['theme'].capitalize()
        )
    )
    if len(backend.get_reminder_time(message.from_user.id)) > 0:
        menu(message, type='circle')
    else:
        keyboard = pass_button()
        bot.send_message(
            message.chat.id,
            'Друг! Давай решим, в какое время я буду напоминать тебе, что пришло время повторений!.\n' +
            'Введи время в формате hh:mm или нажним Пропустить (тогда буду писать тебе в 20:00)', reply_markup=keyboard
        )
        bot.register_next_step_handler(message, add_reminder)

def add_reminder(message):
    printing_func()
    if message.text == '\u23E9 Пропустить':
        reminder_time = '20:00'
        backend.set_remainder_time(message.chat.id, reminder_time)
        bot.send_message(message.chat.id, 'Отлично, напомню ровно в срок!')
        printing_func()
        menu(message, type='circle')
    elif re.match('[0-2][0-9]:[0-5][0-9]', message.text) is not None:
        reminder_time = message.text
        backend.set_remainder_time(message.chat.id, reminder_time)
        bot.send_message(message.chat.id, 'Отлично, напомню ровно в срок!')
        printing_func()
        menu(message, type='circle')
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
        keyboard.add(telebot.types.KeyboardButton('\U0001F519 Меню'))
        bot.send_message(message.chat.id, 'Некорректный формат, попробуй еще раз', reply_markup=keyboard)
        bot.register_next_step_handler(message, try_again, add_reminder)



def read_command(message):
    printing_func()
    get_data=''
    print(backend.get_data(message.from_user.id)[0])
    for theme in backend.get_data(message.from_user.id)[0]:
        get_data+='{} - {}\n'.format(theme[0],theme[1])
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    keyboard.add(telebot.types.KeyboardButton('Всё'), telebot.types.KeyboardButton('\U0001F519 Меню'))
    bot.send_message(message.chat.id, 'Вот все темы, которые у нас есть:\n'+ get_data)
    printing_func()
    bot.send_message(message.chat.id, 'Введи, пожалуйста, номер темы, либо нажми Всё, если нужно вернуть все темы с вопросами',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, read_what_return)

def read_what_return(message):
    if to_menu(message):
        return
    printing_func()
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    theme_id = message.text
    if theme_id=='Всё':
        keyboard.add(telebot.types.KeyboardButton('\U0001F519 Меню'))
        i=0
        for key, value in backend.read_theme(message.from_user.id, 3).items():
            if i==0:
                bot.send_message(message.chat.id, 'Вот все что мы с тобой повторяем\n' + '{}\n{}'. format(key,value))
            else:
                bot.send_message(message.chat.id, '{}:\n{}'.format(key, value))
            i+=1
        bot.send_message(message.chat.id, 'Когда закончишь, нажми на кнопку \U0001F519 Меню!', reply_markup=keyboard)
    else:
        try:
            theme_id = int(message.text)
        except:
            keyboard.add(telebot.types.KeyboardButton('\U0001F519 Меню'))
            bot.send_message(message.chat.id, 'Мы же договаривались, что нужна цифра!\nПопробуй еще разок, пожалуйста',
                             reply_markup=keyboard)
            bot.register_next_step_handler(message, try_again, read_what_return)
        try:
            keyboard.add(telebot.types.KeyboardButton('Да!'), telebot.types.KeyboardButton('\U0001F519 Меню'))
            theme, question = backend.read_theme(message.from_user.id, 1, theme_id)
            bot.send_message(message.chat.id, 'Вот вопросы по теме {}:\n{}'.format(theme, question))
            bot.send_message(message.chat.id, 'Если нужна теория, то нажми "Да"', reply_markup=keyboard)
            bot.register_next_step_handler(message, read_final, theme_id)
        except:
            keyboard.add(telebot.types.KeyboardButton('\U0001F519 Меню'))
            bot.send_message(message.chat.id, 'Не нашел тему с таким номером, попробуй еще раз', reply_markup=keyboard)
            bot.register_next_step_handler(message, try_again, read_what_return)

def read_final(message, theme_id):
    if to_menu(message):
        return
    elif message.text=='Да!':
        printing_func()
        theme , theory = backend.read_theme(message.from_user.id, 2, theme_id)
        bot.send_message(message.chat.id, 'Вот теория по теме {}:\n{}'.format(theme, theory))
        menu(message, 'circle')



def schedule_command(message):
    printing_func()
    get_data = ''
    for theme in backend.get_data(message.from_user.id)[0]:
        get_data += '{} - {}\n'.format(theme[0], theme[1])
    keyboard=menu_button()
    bot.send_message(message.chat.id, 'Вот все темы, которые у нас есть:\n' + get_data)
    printing_func()
    bot.send_message(message.chat.id, 'По какой теме прислать расписание? Введи номер', reply_markup=keyboard)
    bot.register_next_step_handler(message, schedule_return)

def schedule_return(message):
    if to_menu(message):
        return
    printing_func()
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    try:
        theme_id=int(message.text)

        try:
            theme= backend.get_theme(message.from_user.id, theme_id)['theme']
            schedule = backend.get_theme_schedule(message.from_user.id, theme_id)
            normal_dates= ''
            for x in schedule:
                normal_dates += '-'.join(x.split('-')[::-1]) + '\n'
            if len(normal_dates)== 0:
                bot.send_message(message.chat.id, 'Эту тему мы уже повторили от и до!')
            else:
                bot.send_message(message.chat.id, 'Вот когда мы будем повторять тему {}:\n{}'.format(theme, normal_dates))
            printing_func()
            menu(message, 'circle')
        except:
            keyboard.add(telebot.types.KeyboardButton('\U0001F519 Меню'))
            bot.send_message(message.chat.id, 'Не нашел тему с таким номером, попробуй еще раз', reply_markup=keyboard)
            bot.register_next_step_handler(message, try_again, schedule_return)

    except:
        keyboard.add(telebot.types.KeyboardButton('\U0001F519 Меню'))
        bot.send_message(message.chat.id, 'Цифрой, пожалуйста', reply_markup=keyboard)
        bot.register_next_step_handler(message, try_again, schedule_return)

def edit_command(message):
    printing_func()
    get_data = ''
    for theme in backend.get_data(message.from_user.id)[0]:
        get_data += '{} - {}\n'.format(theme[0], theme[1])
    bot.send_message(message.chat.id, 'Мы можем изменить информацию по заданной теме или выбрать новое время напоминаний!' )
    printing_func()
    keyboard = menu_button()
    bot.send_message(message.chat.id, 'Вот все темы, которые у нас есть:\n' + get_data)
    printing_func()
    bot.send_message(message.chat.id, 'Что редактировать будем?\nВведи номер темы или 1000 для смены времени напоминалок',reply_markup=keyboard)
    bot.register_next_step_handler(message, edit_theme)

def edit_theme(message):
    if to_menu(message):
        return
    if message.text =='1000':
        printing_func()
        keyboard = pass_button()
        bot.send_message(
            message.chat.id,
            'Друг! Давай решим, в какое время я буду напоминать тебе, что пришло время повторений!.\n' +
            'Введи время в формате hh:mm или нажним Пропустить (тогда буду писать тебе в 20:00)', reply_markup=keyboard
        )
        bot.register_next_step_handler(message, add_reminder)
    else:
        printing_func()
        keyboard = pass_button()
        try:
            theme=int(message.text)
            try:
                current_info=backend.get_theme(message.from_user.id, theme)
                bot.send_message(message.chat.id, 'Введи новое название для темы {}'.format(current_info['theme']),
                                 reply_markup=keyboard)
                bot.register_next_step_handler(message, edit_questions, current_info)
            except:
                bot.send_message(message.chat.id, 'Не нашел тему с таким номером, попробуй еще раз', reply_markup=keyboard)
                bot.register_next_step_handler(message, try_again, edit_theme)

        except:
            bot.send_message(message.chat.id, 'Цифрой, пожалуйста')
            bot.register_next_step_handler(message, try_again, edit_theme)

def edit_questions(message, current_info):
    if to_menu(message):
        return
    printing_func()
    if message.text!='\u23E9 Пропустить' :
        current_info['theme']=message.text
    bot.send_message(message.chat.id, 'Так, c темой разобрались.\n' +
        'Вот какие вопросы к ней у нас были раньше\n' +
        '{}'.format(current_info['questions']))

    keyboard=pass_button()
    bot.send_message(message.chat.id, 'Теперь введи отредактированный текст вопросов', reply_markup=keyboard)
    bot.register_next_step_handler(message, edit_theory, current_info)

def edit_theory(message, current_info):
    if to_menu(message):
        return
    printing_func()
    if message.text!='\u23E9 Пропустить' :
        current_info['questions'] = message.text
    bot.send_message(message.chat.id, 'Покончили с вопросами, теперь давай ответы.\n' +
                     'Вот, что мы сохранили по теории\n' +
                     '{}'.format(current_info['theory']))
    keyboard = pass_button()
    printing_func()
    bot.send_message(message.chat.id, 'Теперь пришли мне новый вариант', reply_markup=keyboard)
    printing_func()
    bot.register_next_step_handler(message, edit_final, current_info)

def edit_final(message, current_info):
    if to_menu(message):
        return
    printing_func()
    if message.text!='\u23E9 Пропустить' :
        current_info['theory'] = message.text
    backend.edit_theme(**current_info)
    bot.send_message(message.chat.id, 'Я все сохранил, честно-честно!')
    menu(message, 'circle')

def delete_command(message):
    printing_func()
    get_data = ''
    for theme in backend.get_data(message.from_user.id)[0]:
        get_data += '{} - {}\n'.format(theme[0], theme[1])
    keyboard=menu_button()
    bot.send_message(message.chat.id, 'Вот все темы, которые у нас есть:\n' + get_data)
    printing_func()
    bot.send_message(message.chat.id, 'Кто лишний? Введи номер темы\n' +
                     'Только подумой хорошенько, восстанавливать не буду! Нажми \U0001F519 Меню, если передумал', reply_markup=keyboard)
    bot.register_next_step_handler(message, delete_theme)

def delete_theme(message):
    if to_menu(message):
        return
    printing_func()
    keyboard = menu_button()
    try:
        theme=int(message.text)
        try:
            backend.delete_theme(message.from_user.id, theme)
            bot.send_message(message.chat.id, 'Ну все, прощай бесполезная тема!')
            menu(message, 'circle')

        except:
            bot.send_message(message.chat.id, 'Не нашел тему с таким номером, попробуй еще раз', reply_markup=keyboard)
            bot.register_next_step_handler(message, try_again, edit_theme)

    except:
        bot.send_message(message.chat.id, 'Цифрой, пожалуйста', reply_markup=keyboard)
        bot.register_next_step_handler(message, try_again, edit_theme)


def today_command(user):
    global user_id
    user_id = user
    printing_func()
    today=backend.reminder(user_id)
    keyboard = menu_button()
    if len(today)==0:
        bot.send_message(user_id, 'Нечего повторять! Приходи завтра!', reply_markup=keyboard)
    else:
        printing_func()
        bot.send_message(user_id, 'Вот темы, которые мы будем сегодня повторять:\n')
        for k, v in today.items():
            bot.send_message(user_id, '{}:\n{}'.format(k, v), reply_markup=keyboard)
            printing_func()




def cron_func():
    userlist = backend.get_users()
    userlist = [x[0] for x in userlist]
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    keyboard.add(telebot.types.KeyboardButton('Да'), telebot.types.KeyboardButton('Нет'))
    for user in userlist:
        if backend.check_reminder_time(user):
            today_command(user)


def runBot():
    bot.polling(none_stop=True, interval=0)

def runSchedulers():
    schedule.every(45).seconds.do(cron_func).tag(cron_func.__name__)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    t1 = threading.Thread(target=runBot)
    t2 = threading.Thread(target=runSchedulers)
    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()



