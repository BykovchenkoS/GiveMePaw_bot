import telebot
from telebot import types

bot = telebot.TeleBot('5321799943:AAE4g00gbsVyAYvaGHoQfdAV26Q2be37Pk0')


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    hello_button = types.KeyboardButton('👋 Привет!')
    markup.add(hello_button)
    bot.send_message(message.chat.id, 'Здравствуйте!😊', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def chose_role(message):
    if message.chat.type == 'private':
        if message.text == '👋 Привет!':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            shelter_button = types.KeyboardButton('Я представитель приюта\nдля животных ✅')
            user_button = types.KeyboardButton('Я обычный пользователь\nХочу помочь хвостатым ❤️')
            markup.add(shelter_button, user_button)
            bot.send_message(message.chat.id, 'Выберите свою роль в боте ⬇️', reply_markup=markup)

        elif message.text == 'Я представитель приюта\nдля животных ✅':
                    bot.send_message(message.chat.id, 'Заполните анкету вашего подопечного по следующему образцу:'
                                                      '\n\n1. Вид животного, имя и возраст 🐾'
                                                      '\n2. Расскажите историю жизни💔'
                                                      '\n3. Если требуется лечение, расскажите о болезни и необходимых '
                                                      'препаратах и сумме для лечения💉'
                                                      '\n4. Опишите человека,  который бы мог взять питомца в свой дом🏡'
                                                      '\n5. Оставьте контакты вашего приюта☎️'
                                                      '\n\n!!!Не забудьте прикрепить фотографию хвостатого📸')

        elif message.text == 'Я обычный пользователь\nХочу помочь хвостатым ❤️':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                moscow_button = types.InlineKeyboardButton('Москва')
                piter_button = types.InlineKeyboardButton('Санкт-Петербург')
                krasnodar_button = types.InlineKeyboardButton('Краснодар')
                sochi_button = types.InlineKeyboardButton('Сочи')
                markup.add(moscow_button, piter_button, krasnodar_button, sochi_button)
                bot.send_message(message.chat.id, 'Выберите город, в котором хотите посмотреть животных:️', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Нужно поздороваться! \nНачнём заново.')
            return start(message)


bot.polling(none_stop=True)

