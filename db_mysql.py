import pymysql
import telebot
from config import host, user, password, db_name
from main import bot

# привязала базу данных к проекту
connection = pymysql.connect(
    host=host,
    port=3306,
    user=user,
    password=password,
    database=db_name,
    cursorclass=pymysql.cursors.DictCursor
)

#
# select = "SELECT name_animals, age_animals, animals.desc " \
#          "FROM givemepaw.animals JOIN type_animals on animals.id_type = type_animals.id_type" \
#          " JOIN shelters on  shelters.id_shelter = animals.id_shelter" \
#          " JOIN city on  city.id_city = shelters.id_city WHERE city.id_city = 1"
# with connection.cursor() as cursor:
#     cursor.execute(select)
#     result = cursor.fetchall()
#     for row in result:
#         post = row.get('name_animals')
#         print(post)
