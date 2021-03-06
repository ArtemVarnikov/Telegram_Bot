"""BACKEND THING"""
import datetime
import re
import sqlite3
from datetime import datetime, timedelta, date
import logging
import yaml


with open('config.yaml') as f:
    config = yaml.safe_load(f)

logging.basicConfig(filename=config['log'], level=logging.INFO, filemode='w')

class Database():
    users= 'user'
    themes = 'themes'
    schedules = 'schedule'

    def make_query(self, db_name, query, params, type=None, table_name = None):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        res = print('')
        if type == 'reading':
            res = cursor.fetchall()
        elif type == 'insert':
            conn.commit()
            logging.info('{} Данные добавлены в {}'.format(datetime.now().strftime("%Y-%m-%d %H:%M"), table_name))
        elif type == 'delete':
            conn.commit()
            logging.info('{} Данные удалены из {}'.format(datetime.now().strftime("%Y-%m-%d %H:%M"), table_name))
        elif type == 'edit':
            conn.commit()
            logging.info('{} Данные в {} изменены'.format(datetime.now().strftime("%Y-%m-%d %H:%M"), table_name))
        conn.close()
        return res

    def __init__(self, db_name):
        self.db_name = db_name
        logging.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} Database initialized')

    def get_data(self, user_id):
        user_themes= Database.make_query(self, self.db_name,
                                       '''
                                       Select theme_id, theme, questions, theory 
                                       from themes 
                                       where user_id = ? 
                                       and theme_id in (
                                            select theme_id from schedule where send_at >= current_date 
                                       )
                                       ''',
                                         params =(user_id,), type= 'reading')
        user_schedule=Database.make_query(self, self.db_name,
                                       'Select theme_id, theme, send_at from schedule where user_id = ? and send_at >= current_date'
                                          ,  params= (user_id,),type=  'reading')
        logging.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} Query Get Data about user {user_id}')
        return user_themes, user_schedule

    def get_users(self):
        logging.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} Query GET ALL USERS executed')
        return Database.make_query(self, self.db_name,
                                       'Select user_id from user', (), type ='reading')

    def get_theme(self, user_id, theme_id):
        themes=Database.make_query(self, self.db_name,
                                       'Select * from themes where user_id = ? and theme_id = ? limit 1', (user_id, theme_id),
                                          'reading')
        logging.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} Query GET THEME {theme_id} for user {user_id} executed')
        return {'user_id' : user_id,
                "theme_id":theme_id,
                "theme": themes[0][3],
               'questions' : themes[0][4],
               'theory' : themes[0][5]}

    def get_theme_schedule(self, user_id, theme_id):
        theme_schedule=Database.make_query(self, self.db_name,
                                       'Select send_at from schedule where user_id = ? and theme_id = ? and send_at >= current_date',  params= (user_id, theme_id),type=  'reading')
        logging.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} Query GET THEME {theme_id} schedule executed for user {user_id}')
        return [x[0] for x in theme_schedule]

    def get_reminder_time(self, user_id):
        reminder = Database.make_query(self, self.db_name,
                                     'Select remainder_time from user where user_id = ? limit 1',
                                     (user_id,),
                                     'reading')
        logging.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} Query  GET REMINDER TIME executed for user {user_id}')
        if len(reminder) > 0:
            return {'user_id': user_id,
                "reminder_time": reminder[0][0]
                }
        else:
            return reminder

    def set_remainder_time(self, user_id, reminder_time):
        Database.make_query(self, self.db_name, 'DELETE FROM user where user_id = ?', (user_id,) , 'delete', Database.users)
        Database.make_query(self, self.db_name, 'INSERT INTO user (user_id, created_at, remainder_time) VALUES (?, current_timestamp, ?);' ,
                            (user_id, reminder_time), 'insert', Database.users)
        logging.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} Query  SET REMINDER TIME executed for user {user_id}. Reminder time set for {reminder_time}')
        print('Reminder is set, master')

    def check_reminder_time(self, user_id):
        x = Database.make_query(self, self.db_name, "SELECT strftime('%H:%M',time('now', 'localtime')) = remainder_time  FROM user WHERE user_id = ? limit 1",
                            (user_id, ) , 'reading', Database.users)[0][0]
        logging.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} Query  CHECK REMINDER TIME executed for user {user_id}. X == {x}')
        if x == 1:
            return True
        else:
            return False

    def add_theme(self, user_id, theme, questions, theory, schedule):
        schedule=re.sub('[^\d]', '-', schedule)
        theme_id = Database.make_query(self, self.db_name,
                                       'select coalesce(max(theme_id) + 1, 1) from themes where user_id = ?', (user_id,), type ='reading')[0][0]
        add_theme_query = '''
            INSERT INTO themes (user_id, created_at, theme_id, theme, questions, theory, schedule) VALUES 
                (?, datetime(date('now')), ?, ?, ?,? , ?)
            '''

        Database.make_query(self, self.db_name, add_theme_query,   (user_id, theme_id,theme, questions, theory, schedule),
                            type='insert', table_name=Database.themes)
        for s in schedule.split('-'):
            add_schedule_query = '''
            INSERT INTO schedule (user_id, created_at, theme_id, theme, send_at) VALUES 
            (?, datetime(date('now')), ?, ?, ? )
            '''
            Database.make_query(self, self.db_name, add_schedule_query, (user_id, theme_id, theme, date.isoformat(datetime.date(datetime.now()) + timedelta(days=int(s)))),
                                type='insert', table_name=Database.schedules)
        print('theme added')

    def read_theme(self, user_id, what_needed, theme_id=None):
        """Параметр what_needed
        1 - вопросы по теме
        2 - теория по теме
        3 - все темы с вопросами
        """
        if what_needed == 1:
            return Database.get_theme(self, user_id, theme_id)['theme'],\
                   Database.get_theme(self, user_id, theme_id)['questions']

        if what_needed == 2:
            return Database.get_theme(self, user_id, theme_id)['theme'], \
                   Database.get_theme(self, user_id, theme_id)['theory']

        if what_needed == 3:
            return dict(zip([theme[1] for theme in Database.get_data(self, user_id)[0]],
                            [theme[2] for theme in Database.get_data(self, user_id)[0]]))

    def read_schedule(self, user_id, theme_id):
        """
        """
        return Database.get_theme_schedule(self, user_id,theme_id)


    def edit_theme(self, user_id, theme_id, theme, questions, theory):
        update_theme_query = '''
            UPDATE themes
            set theme = :theme, questions = :questions, theory = :theory
            where user_id = :user_id and theme_id = :theme_id
            '''
        Database.make_query(self, self.db_name, update_theme_query, {'theme' : theme, 'questions' : questions, 'theory' : theory,
                                                                     'user_id' : user_id, 'theme_id' : theme_id},
                            type = 'edit', table_name='themes')

        Database.make_query(self, self.db_name, 'update schedule set theme = ? where theme_id = ?', (theme, theme_id), 'edit', 'schedule')
        print('EDITED THEME {} : {} : {}'.format(theme, questions, theory))

    def delete_theme(self, user_id, theme_id):
        Database.make_query(self, self.db_name, 'DELETE FROM themes where theme_id = ? and user_id = ?',
                            (theme_id, user_id), 'delete', 'themes')
        Database.make_query(self, self.db_name, 'DELETE FROM schedule where theme_id = ? and user_id = ?',
                            (theme_id, user_id), 'delete', 'schedule')
        print('THEME {} is deleted'.format(theme_id))

    def reminder(self, user_id):
        theme=Database.make_query(self, self.db_name, 'SELECT distinct theme_id FROM schedule WHERE date(send_at) = current_date and user_id = ?', (user_id,), type='reading')
        theme = tuple([x[0] for x in theme])
        print(theme)
        themes_for_today ={}
        for x in theme:
            new_theme = (Database.make_query(self, self.db_name, 'SELECT theme, questions FROM themes WHERE user_id =? and theme_id = ?', (user_id, x),
                  'reading', 'themes'))[0]
            themes_for_today.setdefault(new_theme[0], new_theme[1])
        print('THERE ARE THEMES FOR TODAY, LORD - {}'.format(themes_for_today))
        return themes_for_today




if __name__ == "__main__":
    # Database.users = 'test_user'
    # Database.themes = 'test_themes'
    # Database.schedules = 'test_schedule'

    t = Database(r'D:\Downloads\testbd.db')
    #t.add_theme(475098368, 'yaks', 'what ducks?', 'aaa, this ducks', '0-3-5-30')
    #t.add_theme(2, 'dementors', 'is this real?', 'this shit is real', '10-14-20-100')


    print(t.get_data(475098368))
    #t.get_theme(475098368,1)
    # t.read_theme(1, 1, 1)
    # t.read_theme(1, 2, 1)
    # t.read_theme(2, 3)
    # print(t.read_schedule(1, 1, 1))
    # print(t.read_schedule(1, 2))
    #t.edit_theme(1, 1, 'zzzzz', 'yoyoy', 'fffffffff')
    # #print(t.read_schedule(1,1,1)[0])475098368
    # #print(t.reminder(1), len(t.reminder(1)))
    #t.delete_theme(475098368, 3)
    t.reminder(475098368)
    #t.set_remainder_time(475098368, '21:45')
    t.get_reminder_time(475098368)
    # t.delete_theme(2,1)

