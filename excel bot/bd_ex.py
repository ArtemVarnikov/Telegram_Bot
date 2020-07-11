"""BACKEND THING"""
import datetime
import pandas as pd
import numpy as np

pd.set_option('mode.chained_assignment', None)

class Database():
    theory = 'C:/Users/Merso/theory.xlsx'
    schedule = 'C:/Users/Merso/reminder_schedule.xlsx'

    def __init__(self):
        self.data = pd.read_excel(Database.theory)
        self.schedule = pd.read_excel(Database.schedule)

    def save_and_reopen(self):  # helper method
        self.data.to_excel(Database.theory, index=False)
        self.schedule.to_excel(Database.schedule, index=False)
        self.data = pd.read_excel(Database.theory)
        self.schedule = pd.read_excel(Database.schedule)

    def all_themes(self, user_id):
        user_data=self.data[self.data['user_id']==user_id]
        user_schedule=self.schedule[self.schedule['user_id']==user_id]
        user_themes=user_data['theme'].tolist()
        themes={ i+1: x for i, x in enumerate(user_themes)}
        return user_data, user_schedule, themes

    def get_theme(self, user_id, theme_id):
        user_data = Database.all_themes(self,user_id)[0]
        themes=Database.all_themes(self, user_id)[2]
        return {'user_id' : user_id,
                "theme_id":theme_id,
                "theme": user_data[user_data['theme']==themes[theme_id]]['theme'][0],
               'questions' : user_data[user_data['theme']==themes[theme_id]]['questions'][0],
               'theory' : user_data[user_data['theme']==themes[theme_id]]['theory'][0]}

    def add_theme(self, user_id, theme, questions, theory, schedule):
        self.data.loc[len(self.data)] = [user_id, datetime.datetime.now(),
                                         theme, questions, theory, schedule]
        for s in schedule.split('-'):
            self.schedule.loc[len(self.schedule)] = [user_id, datetime.datetime.now(), theme,
                                                     datetime.datetime.today() + datetime.timedelta(days=int(s))]
        Database.save_and_reopen(self)
        print('theme added')

    def read_theme(self, user_id, what_needed, theme_id=None):
        """Параметр what_needed
        1 - вопросы по теме
        2 - теория по теме
        3 - все темы с вопросами
        """
        user_data = Database.all_themes(self, user_id)[0]
        themes= Database.all_themes(self, user_id)[2]
        if what_needed == 1:
            return self.data[(self.data['user_id'] == user_id) &
                             (self.data['theme'] == themes[theme_id])]['theme'].tolist()[0],\
                   self.data[(self.data['user_id'] == user_id) &
                             (self.data['theme'] == themes[theme_id])]['questions'].tolist()[0]

        if what_needed == 2:
            return self.data[(self.data['user_id'] == user_id) &
                             (self.data['theme'] == themes[theme_id])]['theme'].tolist()[0],\
                    self.data[(self.data['user_id'] == user_id) &
                             (self.data['theme'] == themes[theme_id])]['theory'].tolist()[0]

        if what_needed == 3:
            return dict(zip(self.data[self.data['user_id'] == user_id]['theme'].tolist(),
                            self.data[self.data['user_id'] == user_id]['questions']))

    def read_schedule(self, user_id, what_needed, theme_id=None):
        """Параметр what_needed
        1 - расписание по выбранной теме
        2 - все расписание
        """
        user_schedule = Database.all_themes(self, user_id)[1]
        themes = Database.all_themes(self, user_id)[2]

        if what_needed == 1:
            return user_schedule[user_schedule['theme']==themes[theme_id]]['theme'].tolist()[0], \
                  user_schedule[user_schedule['theme']==themes[theme_id]]['send_at'].tolist()


        if what_needed == 2:
            return {'{}:{}'.format(x, y)
                        for x in self.schedule[self.schedule['user_id'] == user_id]['theme_id'].tolist()
                        for y in self.schedule[self.schedule['theme_id'] == x]['send_at'].tolist()
                    }


    def edit_theme(self, user_id, theme_id, theme, questions, theory):
        themes = Database.all_themes(self, user_id)[2]
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
        themes = Database.all_themes(self, user_id)[2]
        self.data = self.data[self.data['theme'] != themes[theme_id]]
        self.schedule = self.schedule[self.schedule['theme'] != themes[theme_id]]
        Database.save_and_reopen(self)
        print('THEME {} is deleted'.format(theme_id))

    def archieve(self):
        today = datetime.datetime.now()
        day = datetime.timedelta(1)
        self.schedule = self.schedule[self.schedule['send_at'] > today]
        self.data = self.data[self.data['theme_id'].isin(self.schedule['theme_id'])]
        Database.save_and_reopen(self)

    def reminder(self, user_id):
        today = datetime.datetime.now()
        day = datetime.timedelta(0.5)
        user_schedule = Database.all_themes(self, user_id)[1]
        user_data = Database.all_themes(self, user_id)[0]
        send_today = user_schedule[user_schedule['send_at'] - today < day]
        themes_for_today = user_data[user_data['theme'].isin(send_today['theme'])]
        print('THERE ARE THEMES FOR TODAY, LORD')
        return dict(zip(themes_for_today['theme'], themes_for_today['questions']))


if __name__ == "__main__":
    test_theory = 'test_theo.xlsx'
    test_schedule = 'test_reminder.xlsx'

    Database.theory = test_theory
    Database.schedule = test_schedule

    df = pd.DataFrame(columns=['user_id', 'created_at', 'theme',
                               'questions', 'theory', 'schedule'])
    df.to_excel(test_theory, index=False)
    df = pd.DataFrame(columns=['user_id', 'created_at', 'theme', 'send_at'])
    df.to_excel(test_schedule, index=False)

    t = Database()
    t.add_theme(1, 'ducks', 'what ducks?', 'aaa, this ducks', '1-3-5-30')
    t.add_theme(2, 'dementors', 'is this real?', 'this shit is real', '10-14-20-100')
    t.read_theme(2, 3)
    t.read_theme(1, 1, 1)
    t.edit_theme(1, 1, 'zzzzz', 'yoyoy', 'fffffffff')
    print(t.all_themes(1)[1])
    print(t.read_schedule(1, 1, 1))
    print(t.read_schedule(1,1,1)[0])
    t.delete_theme(2,1)
    t.reminder(1)
 #   print(t.get_theme(1,1))
    print(t.reminder(1), len(t.reminder(1)))

    # df3=pd.read_excel(test_schedule)
    # df4=pd.read_excel(test_theory)
    # user_schedule=df3[df3['user_id']==1]
    # user_data = df4[df4['user_id'] == 1]
    # user_schedule['theme'].replace('ducks', 'www', inplace=True)
    # print(user_schedule['theme'])
