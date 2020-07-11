import telebot
import bd_google
import theory

backend= bd_google.Database()

bot = telebot.TeleBot('995622302:AAHzpN0DOglWKCx7lPgrCpWWml_bxgKIs10')

def menu_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=4)
    keyboard.row(
        telebot.types.KeyboardButton('today'),
        telebot.types.KeyboardButton('read'),
        telebot.types.KeyboardButton('schedule')
    )
    keyboard.row(
        telebot.types.KeyboardButton('add'),
        telebot.types.KeyboardButton('edit'),
        telebot.types.KeyboardButton('delete')
    )
    keyboard.row(
        telebot.types.KeyboardButton('help'),
        telebot.types.KeyboardButton('theory')
    )
    return keyboard

def menu_button():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    keyboard.add(telebot.types.KeyboardButton('Меню'))
    return keyboard

def pass_button():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    keyboard.add(telebot.types.KeyboardButton('Пропустить'))
    keyboard.add(telebot.types.KeyboardButton('В меню'))
    return keyboard

@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def menu(message, type=None):
    if message.text=='/start':
        start(message)
    else:
        keyboard=menu_keyboard()
        if type==None:
            texting='Выбери, пожалуйста, пункт из меню'
        elif type=='circle':
            texting='Продолжаем?'
        elif type=='back':
            texting='Ага, забыли, что дальше делаем?'
        bot.send_message(message.from_user.id,
        texting, reply_markup=keyboard)
        bot.register_next_step_handler(message, next_action)

def next_action(message):
    if message.text=='help':
        help_command(message)
    elif message.text== 'theory':
        theory_command(message)
    elif message.text == 'add':
        add_command(message)
    elif message.text == 'read':
        read_command(message)
    elif message.text == 'edit':
        edit_command(message)
    elif message.text == 'delete':
        delete_command(message)
    elif message.text == 'today':
        today_command(message)
    elif message.text == 'Пока, друг!':
        bot.send_message(message.from_user.id, 'Отлично поболтали!')
        return
    else:
        keyboard = menu_keyboard()
        bot.send_message(message.from_user.id,
            'На такое я пока еще не могу отреагировать как следует, поэтому выбери что-то из меню, будь добр)', reply_markup=keyboard)
        bot.register_next_step_handler(message, next_action)


def start(message):
    keyboard=menu_keyboard()
    bot.send_message(message.from_user.id,
'Привет!\nЭтот бот предназназначен для'+
'использования техники интервальных повторений (spaced repetitions).\n'+
'С его помощью можно добавлять себе темы для повторения и получать напоминания по установленному графику.\n'+
'Выбери интересующий пункт в меню - если хочешь узнать побольше о методе выбери "theory"', reply_markup=keyboard)


def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            'Message the developer', url='telegram.me/varnikov_a'
  )
    )
    bot.send_message(
        message.chat.id,
        '1) Добавить новую тему /add.\n' +
        '2) Просмотреть инфо по темам на сегодня /today\n'+
        '3) Просмотреть инфо по ранее добавленным темам /read.\n' +
        '4) Просмотреть расписание напоминаний (по всем темам или по выбранной) /schedule.\n' +
        '5) Изменить информацию по конкретной теме /edit.\n' +
        '6) Удалить тему из расписания /delete.',
        reply_markup=keyboard
    )


def theory_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton('Кривая забывания Эббингауза', url=theory.ebbie  )    )
    keyboard.add(telebot.types.InlineKeyboardButton('Активное вспоминание (eng)', url=theory.rec_eng))
    keyboard.add(telebot.types.InlineKeyboardButton('Активное вспоминание (перевод)', url=theory.rec_ru))
    bot.send_message(
        message.chat.id,
        theory.theory,
        reply_markup=keyboard
    )

def try_again(message, func): #helper method
    '''Функция, которая обрабатывает некорректный ввод пользователя'''
    func(message)

def to_menu(message): #helper method
    '''Функция, которая обрабатывает некорректный ввод пользователя'''
    if message.text == 'В меню' or message.text == 'Меню':
        menu(message, type='back')
        return True


def add_command(message):
    bot.send_message(
        message.chat.id,
        'Давай добавим новую тему для интервальных повторений!\n' +
        'Для этого запишем тему, проверочные вопросы, теорию (вдруг не получится вспомнить) и расписание повторений\n' +
        'Предлагаю начать с темы. Напиши мне как мы назовем эту тему'
    )
    new_theme={'user_id' : message.from_user.id, 'theme' : '', 'questions' : '', 'theory' : '', 'schedule' : ''}
    bot.register_next_step_handler(message, add_theme, new_theme)

def add_theme(message, new_theme):
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

    if message.text == 'Пропустить':
        new_theme['schedule']='1-3-7-14-30'
    else:
        new_theme['schedule'] = message.text
    backend.add_theme(**new_theme)
    bot.send_message(
        message.chat.id,
        'Готово! Теперь у темы {} нет шансов быть забытой'.format(new_theme['theme'].capitalize()
        )
    )
    menu(message, type='circle')


def read_command(message):
    all_themes=''
    for key, value in backend.all_themes(message.from_user.id)[2].items():
        all_themes+='{} - {}\n'.format(key,value)
    keyboard=menu_button()
    keyboard.add(telebot.types.KeyboardButton('1000'))
    bot.send_message(message.chat.id, 'Вот все темы, которые у нас есть:\n'+ all_themes)
    bot.send_message(message.chat.id, 'Введи, пожалуйста, номер темы, либо нажми 1000, если нужно вернуть все темы с вопросами',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, read_what_return)

def read_what_return(message):
    if to_menu(message):
        return
    keyboard = menu_button()
    try:
        theme_id=int(message.text)

        if theme_id==1000:
            i=0
            for key, value in backend.read_theme(message.from_user.id, 3).items():
                if i==0:
                    bot.send_message(message.chat.id, 'Вот все что мы с тобой повторяем\n' + '{}\n{}'. format(key,value))
                else:
                    bot.send_message(message.chat.id, '{}:\n{}'.format(key, value))
                i+=1
            bot.send_message(message.chat.id, 'Когда закончишь, нажми на кнопку Меню!', reply_markup=keyboard)
        else:
            try:
                theme=backend.read_theme(message.from_user.id, 2, theme_id)[0]
                question=backend.read_theme(message.from_user.id, 2, theme_id)[1]
                keyboard.row(telebot.types.KeyboardButton('Да'))
                bot.send_message(message.chat.id, 'Вот вопросы по теме {}:\n{}'.format(theme, question))
                bot.send_message(message.chat.id, 'Если нужна теория, то нажми "Да"', reply_markup=keyboard)
                bot.register_next_step_handler(message, read_final, theme_id)
            except:
                bot.send_message(message.chat.id, 'Не нашел тему с таким номером, попробуй еще раз')
                bot.register_next_step_handler(message, try_again, read_what_return)
    except:
        bot.send_message(message.chat.id, 'Цифрой, пожалуйста', reply_markup=keyboard)
        bot.register_next_step_handler(message, try_again, read_what_return)

def read_final(message, theme_id):
    if to_menu(message):
        return
    elif message.text=='Да':
        theme = backend.read_theme(message.from_user.id, 2, theme_id)[0]
        theory = backend.read_theme(message.from_user.id, 2, theme_id)[1]
        bot.send_message(message.chat.id, 'Вот теория по теме {}:\n{}'.format(theme, theory))
        menu(message, 'circle')


@bot.message_handler(commands=['schedule'])
def schedule_command(message):
    all_themes = ''
    for key, value in backend.all_themes(message.from_user.id)[2].items():
        all_themes += '{} - {}\n'.format(key, value)

    bot.send_message(message.chat.id, 'Вот все темы, которые у нас есть:\n' + all_themes)
    bot.send_message(message.chat.id, 'По какой теме прислать расписание? Введи номер')
    bot.register_next_step_handler(message, schedule_return)

def schedule_return(message):
    try:
        theme_id=int(message.text)

        try:
            theme= backend.read_schedule(message.from_user.id, 1, theme_id)[0]
            schedule = backend.read_schedule(message.from_user.id, 1, theme_id)[1]
            normal_dates= ''
            for x in schedule:
                normal_dates+=x.strftime("%d-%m-%Y") + '\n'
            bot.send_message(message.chat.id, 'Вот когда мы будем повторять тему {}:\n{}'.format(theme, normal_dates))
        except:
            bot.send_message(message.chat.id, 'Не нашел тему с таким номером, попробуй еще раз')
            bot.register_next_step_handler(message, try_again, schedule_return)

    except:
        bot.send_message(message.chat.id, 'Цифрой, пожалуйста')
        bot.register_next_step_handler(message, try_again, schedule_return)

@bot.message_handler(commands=['edit'])
def edit_command(message):
    all_themes = ''
    for key, value in backend.all_themes(message.from_user.id)[2].items():
        all_themes += '{} - {}\n'.format(key, value)

    bot.send_message(message.chat.id, 'Вот все темы, которые у нас есть:\n' + all_themes)
    bot.send_message(message.chat.id, 'Что редактировать будем? Введи номер темы')
    bot.register_next_step_handler(message, edit_theme)

def edit_theme(message):
    try:
        theme=int(message.text)
        try:
            current_info=backend.get_theme(message.from_user.id, theme)
            bot.send_message(message.chat.id, 'Введи новое название для темы {}'.format(current_info['theme']))
            #добавить кнопку Пропустить
            bot.register_next_step_handler(message, edit_questions, current_info)
        except:
            bot.send_message(message.chat.id, 'Не нашел тему с таким номером, попробуй еще раз')
            bot.register_next_step_handler(message, try_again, edit_theme)

    except:
        bot.send_message(message.chat.id, 'Цифрой, пожалуйста')
        bot.register_next_step_handler(message, try_again, edit_theme)

def edit_questions(message, current_info):
    current_info['theme']=message.text
    bot.send_message(message.chat.id, 'Так, тему исправили.\n' +
        'Вот какие вопросы к ней у нас были раньше\n' +
        '{}'.format(current_info['questions']))
    bot.send_message(message.chat.id, 'Теперь введи отредактированный текст вопросов')
    # добавить кнопку Пропустить
    bot.register_next_step_handler(message, edit_theory, current_info)

def edit_theory(message, current_info):
    current_info['questions'] = message.text
    bot.send_message(message.chat.id, 'Покончили с вопросами, теперь давай ответы.\n' +
                     'Вот, что мы сохранили по теории\n' +
                     '{}'.format(current_info['theory']))
    bot.send_message(message.chat.id, 'Теперь пришли мне новый вариант')
    # добавить кнопку Пропустить
    bot.register_next_step_handler(message, edit_final, current_info)

def edit_final(message, current_info):
    current_info['theory'] = message.text
    backend.edit_theme(**current_info)
    bot.send_message(message.chat.id, 'Я все сохранил, честно-честно!')

@bot.message_handler(commands=['delete'])
def delete_command(message):
    all_themes = ''
    for key, value in backend.all_themes(message.from_user.id)[2].items():
        all_themes += '{} - {}\n'.format(key, value)

    bot.send_message(message.chat.id, 'Вот все темы, которые у нас есть:\n' + all_themes)
    bot.send_message(message.chat.id, 'Кто лишний? Введи номер темы\n' + 'Только подумой хорошенько, восстанавливать не буду! Введи Нет, если передумал')
    bot.register_next_step_handler(message, delete_theme)

def delete_theme(message):
    if message.text=='Нет':
        bot.send_message(message.chat.id, 'Ладно, забыли!')
        return

    try:
        theme=int(message.text)
        try:
            backend.delete_theme(message.from_user.id, theme)
            bot.send_message(message.chat.id, 'Ну все, прощай бесполезная тема!')
            #добавить кнопку меню

        except:
            bot.send_message(message.chat.id, 'Не нашел тему с таким номером, попробуй еще раз')
            bot.register_next_step_handler(message, try_again, edit_theme)

    except:
        bot.send_message(message.chat.id, 'Цифрой, пожалуйста')
        bot.register_next_step_handler(message, try_again, edit_theme)

@bot.message_handler(commands=['today'])
def today_command(message):
    today=backend.reminder(message.from_user.id)
    if len(today)==0:
        bot.send_message(message.chat.id, 'Нечего повторять! Приходи завтра!')
        return
    today_str=''
    for s in today.keys():
        today_str+= s + '\n'
    bot.send_message(message.chat.id, 'Вот темы, которые мы будем сегодня повторять:\n' + today_str )
    bot.send_message(message.chat.id, 'Если готов к вопросам, то пришли Да')
    bot.register_next_step_handler(message, today_questions, today)

def today_questions(message, today):
    if message.text=='Да':
        bot.send_message(message.chat.id, 'Отлично, а вот и они!')
        for k, v in today.items():
            bot.send_message(message.chat.id, '{}:\n{}'.format(k,v))
    else:
        bot.send_message(message.chat.id, 'Ну как хочешь!')



bot.polling(none_stop=True, interval=0)



