import telebot
import bd_ex


backend= bd_ex.Database()

bot = telebot.TeleBot('995622302:AAHzpN0DOglWKCx7lPgrCpWWml_bxgKIs10')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id,
'Привет! Этот бот предназназначен для'+
'использования техники интервальных повторений (spaced repetitions).\n'+
'С его помощью можно добавлять себе темы для повторения и получать напоминания по установленному графику.\n'+
'Чтобы добавить тему, выбери команду /add\n' +
'Чтобы просмотреть ранее добавленные темы выбери /read\n '+
'Если хочешь подробно узнать про этот метод /theory\n ' +
'Для полного списка команд выбери /help\n')


@bot.message_handler(commands=['help'])
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

def try_again(message, func): #helper method
    '''Функция, которая обрабатывает некорректный ввод пользователя'''
    func(message)

@bot.message_handler(commands=['add'])
def add_command(message):
    bot.send_message(
        message.chat.id,
        'Давай добавим новую тему для интервальных повторений!\n' +
        'Для этого запишем тему, проверочные вопросы, теорию (вдруг не получится вспомнить) и расписание повторений\n' +
        'Предлагаю начать с темы. Напиши мне как мы назовем эту тему'
    )
    new_theme={'user_id' : message.from_user.id, 'theme' : '', 'questions' : '', 'theory' : '', 'schedule' : '1-3-7-14-30'}
    bot.register_next_step_handler(message, get_theme, new_theme)

def get_theme(message, new_theme):
    new_theme['theme'] = message.text
    bot.send_message(
        message.chat.id,
        'Отлично! Теперь добавим контрольные вопросы.\n' +
        'С ними будет проще повторять'
    )
    bot.register_next_step_handler(message, get_questions, new_theme)

def get_questions(message, new_theme):
    new_theme['questions'] = message.text
    bot.send_message(
        message.chat.id,
        'Отлично! Теперь теория.\n' +
        'Если не получится вспомнить, то материал будет под рукой\n' +
        'Можем добавить всю теорию сюда, либо сохранить ссылку на источник'
    )
    bot.register_next_step_handler(message, get_schedule, new_theme)

def get_schedule(message, new_theme):
    new_theme['theory'] = message.text
    bot.send_message(
        message.chat.id,
        'Есть контакт! Финальный шаг - расписание напоминаний.\n' +
        'В установленное время напомню, что пришло время повторений, и пришлю список тем на сегодня  \n' +
        'Пришли расписание в формате 1-3-7-14-30 (через 1, 3, 7, 14, 30 дней от сегодяшней даты я напомню про эту тему)'
    )
    bot.register_next_step_handler(message, add_final, new_theme)


def add_final(message, new_theme):
    new_theme['schedule']=message.text
    bot.send_message(
        message.chat.id,
        'Готово! Теперь у темы {} нет шансов быть забытой'.format(new_theme['theme'].capitalize())
    )
    print (new_theme)
    backend.add_theme(**new_theme)

@bot.message_handler(commands=['read'])
def read_start(message):
    all_themes=''
    for key, value in backend.all_themes(message.from_user.id)[2].items():
        all_themes+='{} - {}\n'.format(key,value)

    bot.send_message(message.chat.id, 'Вот все темы, которые у нас есть:\n'+ all_themes)
    bot.send_message(message.chat.id, 'Введи, пожалуйста, номер темы, либо введи 1000, если нужно вернуть все темы с вопросами')
    bot.register_next_step_handler(message, read_what_return)

def read_what_return(message):
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
        else:
            try:
                theme=backend.read_theme(message.from_user.id, 2, theme_id)[0]
                question=backend.read_theme(message.from_user.id, 2, theme_id)[1]
                bot.send_message(message.chat.id, 'Вот вопросы по теме {}:\n{}'.format(theme, question))
                bot.send_message(message.chat.id, 'Если нужна теория, то напиши "Да"')
                bot.register_next_step_handler(message, read_final, theme_id)
            except:
                bot.send_message(message.chat.id, 'Не нашел тему с таким номером, попробуй еще раз')
                bot.register_next_step_handler(message, try_again, read_what_return)
    except:
        bot.send_message(message.chat.id, 'Цифрой, пожалуйста')
        bot.register_next_step_handler(message, try_again, read_what_return)

def read_final(message, theme_id):
    if message.text=='Да':
        theme = backend.read_theme(message.from_user.id, 2, theme_id)[0]
        theory = backend.read_theme(message.from_user.id, 2, theme_id)[1]
        bot.send_message(message.chat.id, 'Вот теория по теме {}:\n{}'.format(theme, theory))
    else:
        pass #добавить кнопку возврата в меню


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



