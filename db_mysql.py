import pymysql
from config import host, user, password, db_name


# привязала базу данных к проекту
connection = pymysql.connect(
    host=host,
    port=3306,
    user=user,
    password=password,
    database=db_name,
    cursorclass=pymysql.cursors.DictCursor
)


def check(message):
    # message = '+79281234578'
    select_number = "SELECT shelter_name FROM givemepaw.shelters WHERE phone = %s"
    with connection.cursor() as cursor:
        result = cursor.execute(select_number, message)
    print(result)


check('+79281234578')

# flag_city = '1'
# select = "SELECT name_animals, age_animals, animals.desc, animals.family " \
#          "FROM givemepaw.animals JOIN type_animals on animals.id_type = type_animals.id_type" \
#          " JOIN shelters on  shelters.id_shelter = animals.id_shelter" \
#          " JOIN city on  city.id_city = shelters.id_city WHERE city.id_city = %s"
# with connection.cursor() as cursor:
#     cursor.executemany(select, flag_city)
#     result = cursor.fetchall()
#     for row in result:
#         name = row.get('name_animals')
#         age = row.get('age_animals')
#         desc = row.get('desc')
#         family = row.get('family')
#         f = [name, age, desc, family]
#         anketa = ''
#         space = '\n'
#         for i in range(len(f)):
#             anketa += f[i] + space
#         print(
#             anketa
#         )
