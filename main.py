import telebot
import pymysql
import re
from telebot import types
import boto3
import os

import config
import db_mysql
from config import host, user, password, db_name

bot = telebot.TeleBot('5250939994:AAE3SyKrxgfxX4dlRWyJUeznzTyEzuOJyEE')

global cursor


src = ""
url_foto = "https://givemepaw.obs.ru-moscow-1.hc.sbercloud.ru/"


# создадим кнопки для общения с пользователями
@bot.message_handler(commands=['start'])
def start(message):
    global cursor
    cursor = db_mysql.connection.cursor()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    hello_button = types.KeyboardButton('👋 Привет!')
    markup.add(hello_button)
    bot.send_message(message.chat.id, 'Здравствуйте!😊', reply_markup=markup)
    chose_role(message)


@bot.message_handler(commands=['stop'])
def stop(message):
    global cursor

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    hello_button = types.KeyboardButton('/start')
    markup.add(hello_button)
    bot.send_message(message.chat.id, 'До скорых встреч!😴', reply_markup=markup)
    cursor.close()
    db_mysql.connection.close()


@bot.message_handler(content_types=['text'])
def chose_role(message):
    if message.chat.type == 'private':
        # выбираем роль
        if message.text == '👋 Привет!' or message.text == 'Выбор роли':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            shelter_button = types.KeyboardButton('Я представитель приюта\nдля животных ✅')
            user_button = types.KeyboardButton('Я обычный пользователь,\nхочу помочь хвостатым ❤️')
            markup.add(user_button, shelter_button)
            bot.send_message(message.chat.id, 'Выберите свою роль в боте ⬇️', reply_markup=markup)

        elif message.text == 'Я представитель приюта\nдля животных ✅':
            what_number(message)

        elif message.text == 'Я обычный пользователь,\nхочу помочь хвостатым ❤️':
            chose_town(message)

        elif message.text == '/stop':
            stop(message=message)


# -----------------------------------Общение с приютом------------------------------------------------
shelter = []


# ОБРАБОТКА ДАННЫХ ПРИЮТА

# просим ввести номер телефона, затем проверяем наличие этого телефона в бд,
# если данный номер телефона имеется в бд, то есть приют уже зарегестрирован,
# предлагаем сразу заполнить анкету животного

@bot.message_handler(content_types=['text'])
def what_number(message):
    name_shelter = bot.send_message(message.chat.id, 'Введите контактный номер телефона✏️️')
    bot.register_next_step_handler(name_shelter, check_phone)


id_shelter = 0
number = 0


@bot.message_handler(content_types=['text'])
def check_phone(message):
    global id_shelter
    global cursor
    global number
    number = message.text
    if re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', number):
        sql_count = "SELECT COUNT(*)  as count FROM givemepaw.shelters WHERE phone = %s"
        select_id = cursor.execute(sql_count, number)
        count_shelter = cursor.fetchone()['count']
        if count_shelter > 0:
            sql_shelter = "SELECT id_shelter FROM givemepaw.shelters WHERE phone = %s"
            select_id = cursor.execute(sql_shelter, number)
            id_shelter = cursor.fetchone()['id_shelter']
            shelter.append(number)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            anketa_button = types.KeyboardButton('Перейти к заполнению анкеты😼')
            return_button = types.KeyboardButton('Изменить телефон🔁')
            markup.add(anketa_button, return_button)
            error = bot.send_message(message.chat.id, 'Ранее вы заполняли информацию о вашем приюте🔍',
                                     reply_markup=markup)
            bot.register_next_step_handler(error, next_numb)
            return id_shelter

        else:
            shelter.append(message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            add_button = types.KeyboardButton('Сохранить телефон✔')
            return_button = types.KeyboardButton('Изменить телефон🔁')
            markup.add(add_button, return_button)
            msg_ = bot.send_message(message.chat.id, 'Вы ввели контактный номер телефона приюта☎️'
                                                     '\nХотите сохранить его?', reply_markup=markup)
            bot.register_next_step_handler(msg_, next_numb)

    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        error_button = types.KeyboardButton('Сейчас исправлю')
        markup.add(error_button)
        error = bot.send_message(message.chat.id, 'Введён некорректный номер телефона❌', reply_markup=markup)
        bot.register_next_step_handler(error, what_number)


def next_numb(message):
    if message.text == 'Перейти к заполнению анкеты😼':
        step_for_anketa(message)
    elif message.text == 'Сохранить телефон✔':
        what_name(message)
    elif message.text == 'Изменить телефон🔁':
        what_number(message)
        shelter.pop(-1)
    elif message.text == '/stop':
        stop(message=message)


# обработка имени приюта
@bot.message_handler(content_types=['text'])
def what_name(message):
    if message.chat.type == 'private':
        if message.text == 'Перейти к заполнению анкеты😼' or 'Сохранить телефон✔':
            name_shelter = bot.send_message(message.chat.id, 'Введите название приюта✏')
            bot.register_next_step_handler(name_shelter, check_name)
        elif message.text == 'Изменить телефон🔁':
            what_number(message)
        elif message.text == '/stop':
            stop(message=message)


@bot.message_handler(content_types=['text'])
def check_name(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить название✔')
    return_button = types.KeyboardButton('Изменить название️🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы ввели название приюта\nХотите сохранить его?', reply_markup=markup)
    shelter.append(message.text)

    if message.text == '/stop':
        stop(message=message)

    bot.register_next_step_handler(msg, add_town)


# обработка города
@bot.message_handler(content_types=['text'])
def add_town(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить название✔' or message.text == 'Изменить город️🔁':
            markup_towns_shelter = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            moscow_button_sh = types.InlineKeyboardButton(text='Москва', callback_data='moscow')
            piter_button_sh = types.InlineKeyboardButton(text='Санкт-Петербург', callback_data='spb')
            krasnodar_button_sh = types.InlineKeyboardButton(text='Краснодар', callback_data='krd')
            sochi_button_sh = types.InlineKeyboardButton(text='Сочи', callback_data='sochi')
            markup_towns_shelter.add(moscow_button_sh, piter_button_sh, krasnodar_button_sh, sochi_button_sh)

            inf_town = bot.send_message(message.chat.id, 'Выберите город, в котором  находится приют:️',
                                        reply_markup=markup_towns_shelter)
            bot.register_next_step_handler(inf_town, reg_town)

        elif message.text == 'Изменить название️🔁':
            shelter.pop(-1)
            what_name(message)

        elif message.text == '/stop':
            stop(message=message)


@bot.message_handler(content_types=['text'])
def reg_town(answer):
    if answer.text == 'Москва':
        shelter.append('1')
    elif answer.text == 'Санкт-Петербург':
        shelter.append('2')
    elif answer.text == 'Краснодар':
        shelter.append('3')
    elif answer.text == 'Сочи':
        shelter.append('4')

    elif answer.text == '/stop':
        stop(message=answer)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить город✔️')
    return_button = types.KeyboardButton('Изменить город️🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(answer.chat.id, 'Вы выбрали город🏙\nХотите сохранить его?', reply_markup=markup)
    bot.register_next_step_handler(msg, write_inf)


# обработка информацию о приюте
@bot.message_handler(content_types=['text'])
def write_inf(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить город✔️' or message.text == 'Изменить информацию️🔁':
            inf_shelter = bot.send_message(message.chat.id,
                                           'Введите информацию о вашем приюте✏\n'
                                           '❗️❗️❗️Не забудьте указать название и адрес')
            bot.register_next_step_handler(inf_shelter, reg_inf)
        elif message.text == 'Изменить город️🔁':
            shelter.pop(-1)
            add_town(message)

        elif message.text == '/stop':
            stop(message=message)


def reg_inf(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить информацию✔')
    return_button = types.KeyboardButton('Изменить информацию️🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы ввели информацию о приюте📝\nХотите сохранить её?', reply_markup=markup)
    bot.register_next_step_handler(msg, step_for_anketa)
    shelter.append(message.text)


# АНКЕТА ЖИВОТНОГО
animal = []


@bot.message_handler(content_types=['text'])
def step_for_anketa(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить информацию✔':
            markup_anketa_shelter = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            yes_button_sh = types.InlineKeyboardButton(text='Да!')
            no_button_sh = types.InlineKeyboardButton(text='/stop')
            markup_anketa_shelter.add(yes_button_sh, no_button_sh)

            chose_anketa = bot.send_message(message.chat.id, 'Вы готовы заполнить анкету животного?',
                                            reply_markup=markup_anketa_shelter)
            bot.register_next_step_handler(chose_anketa, what_view)

        elif message.text == 'Перейти к заполнению анкеты😼' or message.text == 'Добавить ещё анкету':
            markup_anketa_shelter = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            yess_button_sh = types.InlineKeyboardButton(text='Да!!!')
            noo_button_sh = types.InlineKeyboardButton(text='/stop')
            markup_anketa_shelter.add(yess_button_sh, noo_button_sh)

            chose_anketa = bot.send_message(message.chat.id, 'Вы готовы заполнить анкету животного?',
                                            reply_markup=markup_anketa_shelter)
            bot.register_next_step_handler(chose_anketa, what_view)

        elif message.text == 'Изменить информацию️🔁':
            shelter.pop(-1)
            write_inf(message)

        elif message.text == '/stop':
            stop(message=message)


# Спрашиваем вид животного
@bot.message_handler(content_types=['text'])
def what_view(message):
    global id_shelter
    global cursor

    if message.chat.type == 'private':
        if message.text == '/stop':
            stop(message=message)

        elif message.text == 'Да!!!':
            markup_view_shelter = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            dog_button_sh = types.InlineKeyboardButton(text='Собака🐶')
            cat_button_sh = types.InlineKeyboardButton(text='Кошка🐱')
            markup_view_shelter.add(dog_button_sh, cat_button_sh)
            chose_view = bot.send_message(message.chat.id, 'Выберите вид животного:️',
                                          reply_markup=markup_view_shelter)
            bot.register_next_step_handler(chose_view, check_view)
            select_number = "SELECT  max(id_shelter) as id_shelter FROM givemepaw.shelters WHERE phone = %s"
            select_id = cursor.execute(select_number, shelter[0])
            id_shelter = cursor.fetchone()['id_shelter']

        elif message.text == 'Да!' or 'Изменить вид️🔁':
            markup_view_shelter = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            dog_button_sh = types.InlineKeyboardButton(text='Собака🐶')
            cat_button_sh = types.InlineKeyboardButton(text='Кошка🐱')
            markup_view_shelter.add(dog_button_sh, cat_button_sh)
            chose_view = bot.send_message(message.chat.id, 'Выберите вид животного:️',
                                          reply_markup=markup_view_shelter)
            bot.register_next_step_handler(chose_view, check_view)

            select_sh = "INSERT INTO `givemepaw`.`shelters` (`phone`, `shelter_name`, `id_city`, `desc_shelter`)" \
                        " VALUES (%s, %s, %s, %s);"
            cursor = db_mysql.connection.cursor()
            cursor.executemany(select_sh, [shelter])
            db_mysql.connection.commit()

        elif message.text == '/stop':
            stop(message=message)


@bot.message_handler(content_types=['text'])
def check_view(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить вид✔')
    return_button = types.KeyboardButton('Изменить вид️🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы выбрали вид животного\nХотите сохранить его?', reply_markup=markup)

    if message.text == 'Собака🐶':
        animal.append(1)
    elif message.text == 'Кошка🐱':
        animal.append(2)

    elif message.text == '/stop':
        stop(message=message)

    bot.register_next_step_handler(msg, write_name_animal)


# Спрашиваем кличку
@bot.message_handler(content_types=['text'])
def write_name_animal(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить вид✔' or message.text == 'Изменить кличку🔁':
            add_name_animal = bot.send_message(message.chat.id, 'Введите кличку✏️')
            bot.register_next_step_handler(add_name_animal, reg_name_animal)
        elif message.text == 'Изменить вид️🔁':
            what_view(message)

        elif message.text == '/stop':
            stop(message=message)


def reg_name_animal(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить кличку✔')
    return_button = types.KeyboardButton('Изменить кличку🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы ввели кличку животного📝\nХотите сохранить её?', reply_markup=markup)
    animal.append(message.text)
    bot.register_next_step_handler(msg, write_age)


# Спрашиваем возраст
@bot.message_handler(content_types=['text'])
def write_age(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить кличку✔' or message.text == 'Изменить возраст🔁':
            add_name_animal = bot.send_message(message.chat.id, 'Введите возраст✏️')
            bot.register_next_step_handler(add_name_animal, reg_age_animal)
        elif message.text == 'Изменить кличку🔁':
            write_name_animal(message.text)

        elif message.text == '/stop':
            stop(message=message)


def reg_age_animal(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить возраст✔')
    return_button = types.KeyboardButton('Изменить возраст🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы ввели возраст животного📝\nХотите сохранить его?', reply_markup=markup)
    animal.append(message.text)
    bot.register_next_step_handler(msg, write_life)


# Спрашиваем историю жизни
@bot.message_handler(content_types=['text'])
def write_life(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить возраст✔' or message.text == 'Изменить историю🔁':
            add_name_animal = bot.send_message(message.chat.id, 'Опишите историю жизни хвостатого✏')
            bot.register_next_step_handler(add_name_animal, reg_life_animal)
        elif message.text == 'Изменить возраст🔁':
            write_age(message)

        elif message.text == '/stop':
            stop(message=message)


def reg_life_animal(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить историю✔')
    return_button = types.KeyboardButton('Изменить историю🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы ввели историю жизни хвостатого📝\nХотите сохранить её?',
                           reply_markup=markup)
    animal.append(message.text)
    bot.register_next_step_handler(msg, write_requirements)


# Узнаём требования к будущим владельцам
@bot.message_handler(content_types=['text'])
def write_requirements(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить историю✔' or message.text == 'Изменить требования🔁':
            add_requirements = bot.send_message(message.chat.id, 'Укажите требования к будущим владельцам✏')
            bot.register_next_step_handler(add_requirements, reg_requirements)
        elif message.text == 'Изменить историю🔁':
            write_life(message)

        elif message.text == '/stop':
            stop(message=message)


def reg_requirements(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить требования✔')
    return_button = types.KeyboardButton('Изменить требования🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы указали требования к будущим владельцам📝'
                                            '\nХотите сохранить их?', reply_markup=markup)
    animal.append(message.text)
    bot.register_next_step_handler(msg, upload_photo)


# Просим загрузить фото
@bot.message_handler(content_types=['text'])
def upload_photo(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить требования✔' or message.text == 'Изменить фото🔁':
            add_foto = bot.send_message(message.chat.id, 'Загрузите фото хвостатого📸')
            bot.register_next_step_handler(add_foto, check_photo)
        elif message.text == 'Изменить требования🔁':
            write_requirements(message)

        elif message.text == '/stop':
            stop(message=message)


@bot.message_handler(content_types=['photo', 'document'])
def check_photo(message):
    from pathlib import Path
    global src
    Path(f'tmp/').mkdir(parents=True, exist_ok=True)
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f'tmp/' + file_info.file_path.replace('photos/', '')

        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить фото✔')
    return_button = types.KeyboardButton('Изменить фото🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы загрузили фото хвостатого🖼'
                                            '\nХотите сохранить его?', reply_markup=markup)
    # animal.append(message.text)
    bot.register_next_step_handler(msg, last_step)


# Финишная прямая
@bot.message_handler(content_types=['text'])
def last_step(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить фото✔':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            role_button = types.KeyboardButton('Выбор роли')
            add_button = types.KeyboardButton('Добавить ещё анкету')
            stop_button = types.KeyboardButton('/stop')
            markup.add(role_button, add_button, stop_button)
            add_finish = bot.send_message(message.chat.id, 'Ура!!!\nВы заполнили анкету хвостатого.\n'
                                                           'Выберите следующее действие.', reply_markup=markup)
            bot.register_next_step_handler(add_finish, last_step_check)
        elif message.text == 'Изменить фото🔁':
            upload_photo(message)

        elif message.text == '/stop':
            stop(message=message)


@bot.message_handler(content_types=['text'])
def last_step_check(message):
    global id_shelter
    global shelter
    global cursor
    global animal

    select_id = "SELECT id_shelter FROM givemepaw.shelters WHERE phone = %s"
    select_execute_id = cursor.execute(select_id, shelter[0])
    id_shelter = cursor.fetchone()['id_shelter']

    animal.append(id_shelter)
    select_animal = "INSERT INTO `givemepaw`.`animals` " \
                    "(`id_type`, `name_animals`, `age_animals`, `desc`, `family`, `id_shelter`) " \
                    "VALUES (%s, %s, %s, %s, %s, %s);"

    cursor.executemany(select_animal, [animal])
    db_mysql.connection.commit()
    sber_cloud()

    if message.chat.type == 'private':
        if message.text == 'Выбор роли':
            animal = []
            shelter = []
            chose_role(message)
        elif message.text == 'Добавить ещё анкету':
            animal = []
            step_for_anketa(message)

        elif message.text == '/stop':
            stop(message=message)


# -----------------------------------Sber cloud------------------------------------------------
def sber_cloud():
    global src
    global cursor
    global id_shelter

    sql_id_an = "SELECT max(id_animals) as id_animals FROM givemepaw.animals where id_shelter = %s " \
                "ORDER BY date_edit desc"
    select_id_animal = cursor.execute(sql_id_an, id_shelter)
    id_animal = cursor.fetchone()['id_animals']
    target_foto = str(id_shelter) + '/' + str(id_animal) + '_0.jpg'

    # Загрузить объекты в корзину из строки
    config.s3.upload_file(src, 'givemepaw', target_foto,
                          ExtraArgs={'ContentType': "image/jpeg;charset=UTF-8", 'ACL': "public-read"})
    # Удаляем из tmp
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), src)
    os.remove(path)

    # Обновление url
    add_sql_url = "UPDATE `givemepaw`. `animals` SET `foto_url` = %s WHERE(`id_animals` = %s)"
    sql_url = [target_foto, id_animal]
    cursor.executemany(add_sql_url, [sql_url])
    db_mysql.connection.commit()


# -----------------------------------Общение с пользователем------------------------------------------------
# Спрашиваем город
@bot.message_handler(content_types=['text'])
def chose_town(message):
    markup_towns_user = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    moscow_button_usr = types.InlineKeyboardButton(text='Москва🐾', callback_data='1')
    piter_button_usr = types.InlineKeyboardButton(text='Санкт-Петербург🐾', callback_data='2')
    krasnodar_button_usr = types.InlineKeyboardButton(text='Краснодар🐾', callback_data='3')
    sochi_button_usr = types.InlineKeyboardButton(text='Сочи🐾', callback_data='4')
    markup_towns_user.add(moscow_button_usr, piter_button_usr, krasnodar_button_usr, sochi_button_usr)

    inf_town = bot.send_message(message.chat.id, 'Выберите город, в котором  находится приют:️',
                                reply_markup=markup_towns_user)
    bot.register_next_step_handler(inf_town, show_type)


# Спрашиваем вид животного
@bot.message_handler(content_types=['text'])
def show_type(message):
    markup_view_shelter = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    dog_button_sh = types.InlineKeyboardButton(text='Собака')
    cat_button_sh = types.InlineKeyboardButton(text='Кошка')
    markup_view_shelter.add(dog_button_sh, cat_button_sh)

    if message.chat.type == 'private':
        if message.text == 'Москва🐾':
            chose_view = bot.send_message(message.chat.id, 'Выберите вид животного:️',
                                          reply_markup=markup_view_shelter)
            bot.register_next_step_handler(chose_view, content_moscow)

        elif message.text == 'Санкт-Петербург🐾':
            chose_view = bot.send_message(message.chat.id, 'Выберите вид животного:️',
                                          reply_markup=markup_view_shelter)
            bot.register_next_step_handler(chose_view, content_spb)

        elif message.text == 'Краснодар🐾':
            chose_view = bot.send_message(message.chat.id, 'Выберите вид животного:️',
                                          reply_markup=markup_view_shelter)
            bot.register_next_step_handler(chose_view, content_krasnodar)

        elif message.text == 'Сочи🐾':
            chose_view = bot.send_message(message.chat.id, 'Выберите вид животного:️',
                                          reply_markup=markup_view_shelter)
            bot.register_next_step_handler(chose_view, content_sochi)

        elif message.text == '/stop':
            stop(message=message)


@bot.message_handler(content_types=['text'])
def show_animals(flag_city, flag_type, message):
    global cursor
    flag = [flag_city, flag_type]
    select = "SELECT name_animals, age_animals, animals.desc, animals.family, " \
             "animals.foto_url, shelters.desc_shelter, shelters.phone " \
             "FROM givemepaw.animals JOIN type_animals on animals.id_type = type_animals.id_type" \
             " JOIN shelters on  shelters.id_shelter = animals.id_shelter" \
             " JOIN city on  city.id_city = shelters.id_city WHERE city.id_city = %s AND animals.id_type= %s"
    with db_mysql.connection.cursor() as cursor:
        cursor.executemany(select, [flag])
        result = cursor.fetchall()
        for row in result:
            name = row.get('name_animals')
            age = row.get('age_animals')
            desc = row.get('desc')
            family = row.get('family')
            desc_shelter = row.get('desc_shelter')
            phone_shelter = row.get('phone')

            adress_url = 'https://givemepaw.obs.ru-moscow-1.hc.sbercloud.ru/'
            url = adress_url + row.get('foto_url')

            space = ' '

            f = [name, space, age, space, desc, space, family, space, desc_shelter, space, phone_shelter, space, url]
            anketa = ''
            space = '\n'
            for i in range(len(f)):
                anketa += f[i] + space
            bot.send_message(message.chat.id, anketa)


@bot.message_handler(content_types=['text'])
def content_moscow(message):
    flag_city = '1'
    if message.chat.type == 'private':
        if message.text == 'Собака':
            flag_type = '1'
        elif message.text == 'Кошка':
            flag_type = '2'

        elif message.text == '/stop':
            stop(message=message)

    show_animals(flag_city, flag_type, message)


@bot.message_handler(content_types=['text'])
def content_spb(message):
    flag_city = '2'
    if message.chat.type == 'private':
        if message.text == 'Собака':
            flag_type = '1'
        elif message.text == 'Кошка':
            flag_type = '2'

        elif message.text == '/stop':
            stop(message=message)

    show_animals(flag_city, flag_type, message)


@bot.message_handler(content_types=['text'])
def content_krasnodar(message):
    flag_city = '3'
    if message.chat.type == 'private':
        if message.text == 'Собака':
            flag_type = '1'
        elif message.text == 'Кошка':
            flag_type = '2'

        elif message.text == '/stop':
            stop(message=message)

    show_animals(flag_city, flag_type, message)


@bot.message_handler(content_types=['text'])
def content_sochi(message):
    flag_city = '4'
    if message.chat.type == 'private':
        if message.text == 'Собака':
            flag_type = '1'
        elif message.text == 'Кошка':
            flag_type = '2'

        elif message.text == '/stop':
            stop(message=message)
    show_animals(flag_city, flag_type, message)


bot.polling(none_stop=True, interval=0)
