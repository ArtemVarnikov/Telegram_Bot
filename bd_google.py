"""BACKEND THING"""
import datetime
import pandas as pd
import re
from gspread_pandas import Spread, Client

pd.set_option('mode.chained_assignment', None)

class Database():
    spread=Spread('bd_google')
    theory = 'theory'
    schedule = 'schedule'

    def __init__(self):
        self.data = Database.spread.sheet_to_df(index=None, header_rows=1,
                      start_row=1, unformatted_columns=None, formula_columns=None, sheet=Database.theory)
        self.schedule = Database.spread.sheet_to_df(index=None, header_rows=1,
                      start_row=1, unformatted_columns=None, formula_columns=None, sheet=Database.schedule)

    def save_and_reopen(self):  # helper method
        Database.spread.df_to_sheet(self.data, index=False, sheet=Database.theory)
        Database.spread.df_to_sheet(self.schedule, index=False, sheet=Database.schedule)
        self.data = Database.spread.sheet_to_df(index=None, header_rows=1,
                                                start_row=1, unformatted_columns=None, formula_columns=None,
                                                sheet=Database.theory)
        self.schedule = Database.spread.sheet_to_df(index=None, header_rows=1,
                                                    start_row=1, unformatted_columns=None, formula_columns=None,
                                                    sheet=Database.schedule)

    def all_themes(self, user_id):
        user_data=self.data[self.data['user_id']==str(user_id)]
        user_schedule=self.schedule[self.schedule['user_id']==str(user_id)]
        user_themes=user_data['theme'].tolist()
        themes={ i+1: x for i, x in enumerate(user_themes)}
        return user_data, user_schedule, themes

    def get_theme(self, user_id, theme_id):
        user_data = Database.all_themes(self,user_id)[0]
        themes=Database.all_themes(self, user_id)[2]
        print(user_data, themes, user_data[user_data['theme']==themes[theme_id]])
        return {'user_id' : user_id,
                "theme_id":theme_id,
                "theme": user_data[user_data['theme']==themes[theme_id]]['theme'].tolist()[0],
               'questions' : user_data[user_data['theme']==themes[theme_id]]['questions'].tolist()[0],
               'theory' : user_data[user_data['theme']==themes[theme_id]]['theory'].tolist()[0]}

    def add_theme(self, user_id, theme, questions, theory, schedule):
        schedule=re.sub('[^\d]', '-', schedule)
        self.data.loc[len(self.data)] = [int(round(user_id,0)), datetime.datetime.now(),
                                         theme, questions, theory, schedule]
        for s in schedule.split('-'):
            self.schedule.loc[len(self.schedule)] = [int(user_id), datetime.datetime.now(), theme,
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
        user_schedule = Database.all_themes(self, user_id)[1]
        themes = Database.all_themes(self, user_id)[2]

        if what_needed == 1:
            return user_schedule[user_schedule['theme']==themes[theme_id]]['theme'].tolist()[0], \
                  user_schedule[user_schedule['theme']==themes[theme_id]]['send_at'].tolist()


        if what_needed == 2:
            return {'{}:{}'.format(x, y)
                        for x in user_schedule['theme'].tolist()
                        for y in user_schedule[user_schedule['theme'] == x]['send_at'].tolist()
                    }


    def edit_theme(self, user_id, theme_id, theme, questions, theory):
        themes = Database.all_themes(self, user_id)[2]
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
        themes = Database.all_themes(self, user_id)[2]
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
        day2 = datetime.timedelta(1)
        user_data = Database.all_themes(self, user_id)[0]
        user_schedule = Database.all_themes(self, user_id)[1]
        print(user_schedule)
        user_schedule['send_at']=pd.to_datetime(user_schedule['send_at'])
        send_today = user_schedule[abs(user_schedule['send_at'] - today) < day]
        print(send_today)
        themes_for_today = user_data[user_data['theme'].isin(send_today['theme'])]
        print (themes_for_today)
        print('THERE ARE THEMES FOR TODAY, LORD - {}'.format(dict(zip(themes_for_today['theme'], themes_for_today['questions']))))
        return dict(zip(themes_for_today['theme'], themes_for_today['questions']))


if __name__ == "__main__":
    Database.spread=Spread('bd_test')

    t = Database()
    t.add_theme(1, 'ducks', 'what ducks?', 'aaa, this ducks', '0-3-5-30')
    t.add_theme(2, 'dementors', 'is this real?', 'this shit is real', '10-14-20-100')
    t.all_themes(1)
    t.get_theme(1,1)
    t.read_theme(1, 1, 1)
    t.read_theme(1, 2, 1)
    t.read_theme(2, 3)
    print(t.read_schedule(1, 1, 1))
    print(t.read_schedule(1, 2))
    t.edit_theme(1, 1, 'zzzzz', 'yoyoy', 'fffffffff')
    #print(t.read_schedule(1,1,1)[0])
    t.reminder(1)
    #print(t.reminder(1), len(t.reminder(1)))
    t.delete_theme(1, 1)
    t.delete_theme(2,1)

    # df3=pd.read_excel(test_schedule)
    # df4=pd.read_excel(test_theory)
    # user_schedule=df3[df3['user_id']==1]
    # user_data = df4[df4['user_id'] == 1]
    # user_schedule['theme'].replace('ducks', 'www', inplace=True)
    # print(user_schedule['theme'])
