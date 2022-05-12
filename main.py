import telebot
import pymysql
import re
import update as update
from telebot import types
from config import host, user, password, db_name
from telegram.ext import CommandHandler, MessageHandler, Filters

# привязала базу данных к проекту
connection = pymysql.connect(
    host=host,
    port=3306,
    user=user,
    password=password,
    database=db_name,
    cursorclass=pymysql.cursors.DictCursor
)

bot = telebot.TeleBot('5250939994:AAE3SyKrxgfxX4dlRWyJUeznzTyEzuOJyEE')

form_animal = 'Заполните анкету вашего подопечного по следующему образцу:' \
              '\n\n1. Вид животного, имя и возраст 🐾' \
              '\n2. Расскажите историю жизни💔' \
              '\n3. Если требуется лечение, расскажите о болезни, необходимых ' \
              'препаратах и сумме для лечения💉' \
              '\n4. Опишите человека,  который бы мог взять питомца в свой дом🏡' \
              '\n\n!!!Не забудьте прикрепить фотографию хвостатого📸'


# создадим кнопки для общения с пользователями
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    hello_button = types.KeyboardButton('👋 Привет!')
    markup.add(hello_button)
    bot.send_message(message.chat.id, 'Здравствуйте!😊', reply_markup=markup)
    chose_role(message)


@bot.message_handler(content_types=['text'])
def chose_role(message):
    if message.chat.type == 'private':
        # выбираем роль
        if message.text == '👋 Привет!' or message.text == 'Выбор роли':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            shelter_button = types.KeyboardButton('Я представитель приюта\nдля животных ✅')
            user_button = types.KeyboardButton('Я обычный пользователь\nХочу помочь хвостатым ❤️')
            markup.add(shelter_button, user_button)
            bot.send_message(message.chat.id, 'Выберите свою роль в боте ⬇️', reply_markup=markup)

        elif message.text == 'Я представитель приюта\nдля животных ✅':
            what_name(message)

        elif message.text == 'Я обычный пользователь\nХочу помочь хвостатым ❤️':
            chose_town(message)


# -----------------------------------Общение с приютом------------------------------------------------
shelter = []


# ОБРАБОТКА ДАННЫХ ПРИЮТА
# обработка имени приюта
@bot.message_handler(content_types=['text'])
def what_name(message):
    name_shelter = bot.send_message(message.chat.id, 'Введите название приюта:️')
    bot.register_next_step_handler(name_shelter, check_name)


@bot.message_handler(content_types=['text'])
def check_name(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить название✔')
    return_button = types.KeyboardButton('Изменить название️🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы ввели название приюта.\nХотите сохранить его?', reply_markup=markup)
    shelter.append(message.text)
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

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить город✔️')
    return_button = types.KeyboardButton('Изменить город️🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(answer.chat.id, 'Вы выбрали город.\nХотите сохранить его?', reply_markup=markup)
    bot.register_next_step_handler(msg, write_inf)


# обработка информацию о приюте
@bot.message_handler(content_types=['text'])
def write_inf(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить город✔️' or message.text == 'Изменить информацию️🔁':
            inf_shelter = bot.send_message(message.chat.id,
                                           'Введите информацию о вашем приюте (не забудьте указать адрес).')
            bot.register_next_step_handler(inf_shelter, reg_inf)
        elif message.text == 'Изменить город️🔁':
            shelter.pop(-1)
            add_town(message)


def reg_inf(message):
    shelter.append(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить информацию✔')
    return_button = types.KeyboardButton('Изменить информацию️🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы ввели информацию о приюте.\nХотите сохранить её?', reply_markup=markup)
    shelter.append(message.text)
    bot.register_next_step_handler(msg, what_number)


# обработка номера телефона шелтера
@bot.message_handler(content_types=['text'])
def what_number(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить информацию✔' or \
                message.text == 'Сейчас исправлю' \
                or message.text == 'Изменить телефон🔁':
            numb_shelter = bot.send_message(message.chat.id, 'Введите контактный номер телефона.')
            bot.register_next_step_handler(numb_shelter, check_phone)
        elif message.text == 'Изменить информацию️🔁':
            shelter.pop(-1)
            write_inf(message)


def check_phone(message):
    if re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', message.text):
        # message.connection.cursor.execute("INSERT INTO `givemepaw`.`shelters` (`phone`) VALUES (?)", (message,))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        add_button = types.KeyboardButton('Сохранить телефон✔')
        return_button = types.KeyboardButton('Изменить телефон🔁')
        markup.add(add_button, return_button)
        msg_ = bot.send_message(message.chat.id, 'Вы ввели контактный номер телефона приюта.\nХотите сохранить его?',
                                reply_markup=markup)
        shelter.append(message.text)
        bot.register_next_step_handler(msg_, step_for_anketa)
        print(shelter)
    else:
        shelter.pop(-1)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        error_button = types.KeyboardButton('Сейчас исправлю')
        markup.add(error_button)
        error = bot.send_message(message.chat.id, 'Номер должен содержать только цифры!', reply_markup=markup)
        bot.register_next_step_handler(error, what_number)


# загружаем шелтера в базу данных
# def insert_shelter():
#     print(shelter)
#     sql = "INSERT INTO `givemepaw`.`shelters` (`shelter_name`, `id_city`, `desc_shelter`, `phone`)
#     VALUES (%s, %s, %s, %s)"
#     cursor = db_mysql.
#     cursor.executemany(sql, shelter)
#     connection.commit()


# АНКЕТА ЖИВОТНОГО
animal = []


@bot.message_handler(content_types=['text'])
def step_for_anketa(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить телефон✔' or message.text == 'Добавить ещё анкету':
            markup_anketa_shelter = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            yes_button_sh = types.InlineKeyboardButton(text='Да!')
            no_button_sh = types.InlineKeyboardButton(text='Нет')
            markup_anketa_shelter.add(yes_button_sh, no_button_sh)

            chose_anketa = bot.send_message(message.chat.id, 'Вы готовы заполнить анкету животного?',
                                            reply_markup=markup_anketa_shelter)
            bot.register_next_step_handler(chose_anketa, what_view)

        elif message.text == 'Изменить телефон🔁':
            what_number(message)


# Спрашиваем вид животного
@bot.message_handler(content_types=['text'])
def what_view(message):
    if message.chat.type == 'private':
        if message.text == 'Да!' or 'Изменить вид️🔁':
            markup_view_shelter = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            dog_button_sh = types.InlineKeyboardButton(text='Собака')
            cat_button_sh = types.InlineKeyboardButton(text='Кошка')
            markup_view_shelter.add(dog_button_sh, cat_button_sh)
            chose_view = bot.send_message(message.chat.id, 'Выберите вид животного:️',
                                          reply_markup=markup_view_shelter)
            bot.register_next_step_handler(chose_view, check_view)

        elif message.text == 'Нет':
            bot.stop_polling()


@bot.message_handler(content_types=['text'])
def check_view(message):
    animal.append(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить вид✔')
    return_button = types.KeyboardButton('Изменить вид️🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы выбрали вид животного.\nХотите сохранить его?', reply_markup=markup)
    bot.register_next_step_handler(msg, write_name_animal)


# Спрашиваем кличку
@bot.message_handler(content_types=['text'])
def write_name_animal(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить вид✔' or message.text == 'Изменить кличку🔁':
            add_name_animal = bot.send_message(message.chat.id, 'Введите кличку.')
            bot.register_next_step_handler(add_name_animal, reg_name_animal)
        elif message.text == 'Изменить вид️🔁':
            what_view(message)


def reg_name_animal(message):
    animal.append(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить кличку✔')
    return_button = types.KeyboardButton('Изменить кличку🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы ввели кличку животного.\nХотите сохранить её?', reply_markup=markup)
    bot.register_next_step_handler(msg, write_age)


# Спрашиваем возраст
@bot.message_handler(content_types=['text'])
def write_age(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить кличку✔' or message.text == 'Изменить возраст🔁':
            add_name_animal = bot.send_message(message.chat.id, 'Введите возраст.')
            bot.register_next_step_handler(add_name_animal, reg_age_animal)
        elif message.text == 'Изменить кличку🔁':
            write_name_animal(message)


def reg_age_animal(message):
    animal.append(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить возраст✔')
    return_button = types.KeyboardButton('Изменить возраст🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы ввели возраст животного.\nХотите сохранить его?', reply_markup=markup)
    bot.register_next_step_handler(msg, write_life)


# Спрашиваем историю жизни
@bot.message_handler(content_types=['text'])
def write_life(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить возраст✔' or message.text == 'Изменить историю🔁':
            add_name_animal = bot.send_message(message.chat.id, 'Опишите историю жизни хвостатого.')
            bot.register_next_step_handler(add_name_animal, reg_life_animal)
        elif message.text == 'Изменить возраст🔁':
            write_age(message)


def reg_life_animal(message):
    animal.append(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить историю✔')
    return_button = types.KeyboardButton('Изменить историю🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы ввели историю жизни хвостатого.\nХотите сохранить её?',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, write_requirements)


# Узнаём требования к будущим владельцам
@bot.message_handler(content_types=['text'])
def write_requirements(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить историю✔' or message.text == 'Изменить требования🔁':
            add_requirements = bot.send_message(message.chat.id, 'Укажите требования к будущим владельцам.')
            bot.register_next_step_handler(add_requirements, reg_requirements)
        elif message.text == 'Изменить историю🔁':
            write_life(message)


def reg_requirements(message):
    animal.append(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить требования✔')
    return_button = types.KeyboardButton('Изменить требования🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы указали требования к будущим владельцам.'
                                            '\nХотите сохранить их?', reply_markup=markup)
    bot.register_next_step_handler(msg, upload_photo)


# Просим загрузить фото
@bot.message_handler(content_types=['text'])
def upload_photo(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить требования✔' or message.text == 'Изменить фото🔁':
            add_foto = bot.send_message(message.chat.id, 'Загрузите фото хвостатого.')
            bot.register_next_step_handler(add_foto, check_photo)
        elif message.text == 'Изменить требования🔁':
            write_requirements(message)


def check_photo(message):
    animal.append(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton('Сохранить фото✔')
    return_button = types.KeyboardButton('Изменить фото🔁')
    markup.add(add_button, return_button)
    msg = bot.send_message(message.chat.id, 'Вы загрузили фото хвостатого.'
                                            '\nХотите сохранить его?', reply_markup=markup)
    bot.register_next_step_handler(msg, last_step)


# Финишная прямая
@bot.message_handler(content_types=['text'])
def last_step(message):
    if message.chat.type == 'private':
        if message.text == 'Сохранить фото✔':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            role_button = types.KeyboardButton('Выбор роли')
            add_button = types.KeyboardButton('Добавить ещё анкету')
            stop_button = types.KeyboardButton('STOP')
            markup.add(role_button, add_button, stop_button)
            add_finish = bot.send_message(message.chat.id, 'Ура!!!\nВы заполнили анкету хвостатого.\n'
                                                           'Выберите следующее действие.', reply_markup=markup)
            bot.register_next_step_handler(add_finish, last_step_check)
        elif message.text == 'Изменить фото🔁':
            upload_photo(message)


@bot.message_handler(content_types=['text'])
def last_step_check(message):
    if message.chat.type == 'private':
        if message.text == 'Выбор роли':
            chose_role(message)
        elif message.text == 'Добавить ещё анкету':
            step_for_anketa(message)
        elif message.text == 'STOP':
            bot.stop_polling(message)


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
    markup_view_shelter = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
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


@bot.message_handler(content_types=['text'])
def content_moscow(message):
    flag_city = '1'
    if message.chat.type == 'private':
        if message.text == 'Собака':
            flag_type = '1'
        elif message.text == 'Кошка':
            flag_type = '2'

    select = "SELECT name_animals, age_animals, animals.desc, animals.family " \
             "FROM givemepaw.animals JOIN type_animals on animals.id_type = type_animals.id_type" \
             " JOIN shelters on  shelters.id_shelter = animals.id_shelter" \
             " JOIN city on  city.id_city = shelters.id_city WHERE city.id_city = %s"
    with connection.cursor() as cursor:
        cursor.executemany(select, flag_city)
        result = cursor.fetchall()
        for row in result:
            name = row.get('name_animals')
            age = row.get('age_animals')
            desc = row.get('desc')
            family = row.get('family')
            f = [name, age, desc, family]
            anketa = ''
            space = '\n'
            for i in range(len(f)):
                anketa += f[i] + space
            bot.send_message(message.chat.id, anketa)


@bot.message_handler(content_types=['text'])
def content_spb(message):
    flag_city = '2'
    if message.chat.type == 'private':
        if message.text == 'Собака':
            flag_type = '1'
        elif message.text == 'Кошка':
            flag_type = '2'
    select = ''


@bot.message_handler(content_types=['text'])
def content_krasnodar(message):
    flag_city = '3'
    if message.chat.type == 'private':
        if message.text == 'Собака':
            flag_type = '1'
        elif message.text == 'Кошка':
            flag_type = '2'
    select = ''


@bot.message_handler(content_types=['text'])
def content_sochi(message):
    flag_city = '4'
    if message.chat.type == 'private':
        if message.text == 'Собака':
            flag_type = '1'
        elif message.text == 'Кошка':
            flag_type = '2'
    select = ''


bot.polling(none_stop=True, interval=0)
