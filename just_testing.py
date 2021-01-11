#import gspread_pandas
#print(gspread_pandas.conf.get_config())
#spread=gspread_pandas.Spread('bd_google')

# import re
#
# s='1.3!5a6/7,10'
#
# print(re.sub('[^\d]', '-', s))
#
#
#
# ,
#         telebot.types.KeyboardButton(
#             'read'
#         ),
#         telebot.types.KeyboardButton(
#                 ' edit'
#         ),
#         telebot.types.KeyboardButton(
#                 'delete'
#         )
#
#
# calculate_theme_id_query = '''
#             UPDATE t
#             SET t.theme_id = cte.position_id
#             FROM {0} t
#             INNER JOIN (select user_id, created_at, row_number() over (partition by user_id order by created_at) position_id
#                     from {0} ) cte\n
#             ON {0}.user_id = cte.user_id AND {0}.created_at = cte.created_at'''.format(Database.themes)



st= ''
l=[1,2,3]
l= tuple(l)
print(type(st + str(l)))
print(str(l))