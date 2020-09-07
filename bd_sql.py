"""BACKEND THING"""
import datetime
import re
import sqlite3
from datetime import datetime, timedelta, date



class Database():
    users= 'user'
    themes = 'themes'
    schedules = 'schedule'

    def make_query(self, db_name, query, params, type=None, table_name = None):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        if type == 'reading':
            res = cursor.fetchall()
        elif type == 'insert':
            conn.commit()
            res = print('Данные добавлены в {}'.format(table_name))
        elif type == 'delete':
            conn.commit()
            res = print('Данные удалены из {}'.format(table_name))
        elif type == 'edit':
            conn.commit()
            res = print('Данные в {} изменены'.format(table_name))
        conn.close()
        return res

    def __init__(self, db_name):
        self.db_name = db_name


    def get_data(self, user_id):
        user_data= Database.make_query(self, self.db_name,
                                       'Select * from user where user_id = ?', params =(user_id,), type= 'reading')
        user_schedule=Database.make_query(self, self.db_name,
                                       'Select * from schedule where user_id = ?',  params= (user_id,),type=  'reading')
        return user_data, user_schedule

    def get_users(self):
        return Database.make_query(self, self.db_name,
                                       'Select user_id from user',  type ='reading')

    def get_theme(self, user_id, theme_id):
        themes=Database.make_query(self, self.db_name,
                                       'Select * from themes where user_id = ? and theme_id = ? limit 1', (user_id, theme_id),
                                          'reading')
        print(themes)
        return {'user_id' : user_id,
                "theme_id":theme_id,
                "theme": themes[0][3],
               'questions' : themes[0][4],
               'theory' : themes[0][5]}

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
        user_data = Database.get_data(self, user_id)[0]
        themes= Database.get_data(self, user_id)[2]
        if what_needed == 1:
            return user_data[user_data['theme'] == themes[theme_id]]['theme'].tolist()[0],\
                   user_data[user_data['theme'] == themes[theme_id]]['questions'].tolist()[0]

        if what_needed == 2:
            return user_data[user_data['theme'] == themes[theme_id]]['theme'].tolist()[0],\
                   user_data[user_data['theme'] == themes[theme_id]]['theory'].tolist()[0]

        if what_needed == 3:
            return dict(zip(user_data['theme'].tolist(),
                            user_data['questions'].tolist()))

    def read_schedule(self, user_id, what_needed, theme_id=None):
        """Параметр what_needed
        1 - расписание по выбранной теме
        2 - все расписание
        """
        user_schedule = Database.get_data(self, user_id)[1]
        themes = Database.get_data(self, user_id)[2]

        if what_needed == 1:
            return user_schedule[user_schedule['theme']==themes[theme_id]]['theme'].tolist()[0], \
                  user_schedule[user_schedule['theme']==themes[theme_id]]['send_at'].tolist()


        if what_needed == 2:
            return {'{}:{}'.format(x, y)
                        for x in user_schedule['theme'].tolist()
                        for y in user_schedule[user_schedule['theme'] == x]['send_at'].tolist()
                    }


    def edit_theme(self, user_id, theme_id, theme, questions, theory):
        themes = Database.get_data(self, user_id)[2]
        user_id=str(user_id)
        index_d = self.data.index[(self.data['user_id']==user_id) &
            (self.data['theme'] == themes[theme_id])][0]
        index_s = self.schedule.index[(self.schedule['user_id'] == user_id) &
                                  (self.schedule['theme'] == themes[theme_id])]
        self.data['questions'][index_d] = questions
        self.data['theory'][index_d] = theory
        self.data['theme'][index_d] = theme
        for i in index_s:
            self.schedule['theme'][i]=theme
        Database.save_and_reopen(self)
        print('NEW THEME {} : {} : {}'.format(theme, questions, theory))

    def delete_theme(self, user_id, theme_id):
        themes = Database.get_data(self, user_id)[2]
        self.data = self.data[self.data['theme'] != themes[theme_id]]
        self.schedule = self.schedule[self.schedule['theme'] != themes[theme_id]]
        Database.save_and_reopen(self)
        print('THEME {} is deleted'.format(theme_id))

    def archieve(self):
        today = datetime.datetime.now()
        self.schedule = self.schedule[self.schedule['send_at'] > today]
        self.data = self.data[self.data['theme_id'].isin(self.schedule['theme_id'])]
        Database.save_and_reopen(self)
        print('Archieve get new staff')

    def reminder(self, user_id):
        today = datetime.datetime.now()
        day = datetime.timedelta(0.5)
        user_data = Database.get_data(self, user_id)[0]
        user_schedule = Database.get_data(self, user_id)[1]
        user_schedule['send_at']=pd.to_datetime(user_schedule['send_at'])
        send_today = user_schedule[abs(user_schedule['send_at'] - today) < day]
        themes_for_today = user_data[user_data['theme'].isin(send_today['theme'])]
        print('THERE ARE THEMES FOR TODAY, LORD - {}'.format(dict(zip(themes_for_today['theme'], themes_for_today['questions']))))
        return dict(zip(themes_for_today['theme'], themes_for_today['questions']))




if __name__ == "__main__":
    Database.users = 'test_user'
    Database.themes = 'test_themes'
    Database.schedules = 'test_schedule'

    t = Database(r'D:\Downloads\testbd.db')
   # t.add_theme(1, 'ducks', 'what ducks?', 'aaa, this ducks', '0-3-5-30')
    #t.add_theme(2, 'dementors', 'is this real?', 'this shit is real', '10-14-20-100')


    t.get_data(475098368)
    t.get_theme(475098368,1)
    # t.read_theme(1, 1, 1)
    # t.read_theme(1, 2, 1)
    # t.read_theme(2, 3)
    # print(t.read_schedule(1, 1, 1))
    # print(t.read_schedule(1, 2))
    # t.edit_theme(1, 1, 'zzzzz', 'yoyoy', 'fffffffff')
    # #print(t.read_schedule(1,1,1)[0])
    # t.reminder(1)
    # #print(t.reminder(1), len(t.reminder(1)))
    # t.delete_theme(1, 1)
    # t.delete_theme(2,1)

    # df3=pd.read_excel(test_schedule)
    # df4=pd.read_excel(test_theory)
    # user_schedule=df3[df3['user_id']==1]
    # user_data = df4[df4['user_id'] == 1]
    # user_schedule['theme'].replace('ducks', 'www', inplace=True)
    # print(user_schedule['theme'])
