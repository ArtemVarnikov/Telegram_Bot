#import gspread_pandas
#print(gspread_pandas.conf.get_config())
#spread=gspread_pandas.Spread('bd_google')

import re

s='1.3!5a6/7,10'

print(re.sub('[^\d]', '-', s))



,
        telebot.types.KeyboardButton(
            'read'
        ),
        telebot.types.KeyboardButton(
                ' edit'
        ),
        telebot.types.KeyboardButton(
                'delete'
        )