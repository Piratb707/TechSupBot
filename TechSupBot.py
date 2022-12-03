 #-*- coding: utf-8 -*-
# Импортируем библиотеки
import telebot
import time
from telebot import types
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from re import *

# Назначаем боту наш токен
bot = telebot.TeleBot('#######################')

# Указываем какой текст мы будем ждать от бота, все остальное будет вызывать сообщение 'Данные введены неверно'
status = ["Проблема номер 1", "Проблема номер 2", "Проблема номер 3",
          "Проблема номер 4", "Проблема номер 5", "Проблема номер 6", "Проблема номер 7", "Проблема номер 8",
          "Проблема номер 9", "Большая дилемма", "Небольшая дилемма", "Другая дилемма",
          "У меня другой запрос"]

inc_type = []  # Хранит в себе тип заявки
cli_num = []  # Хранит в себе номер телефона заявителя
cli_mail = []  # Хранит в себе почту заявителя
hello_count = []  # Хранит в себе данные о том нужно ли здороваться с пользователем


# Основной хендлер который реагирует на команду страт
@bot.message_handler(commands=['start'])
def statup(message):  # Здороваемся и просим ввести номер или почту
    key1 = types.ReplyKeyboardMarkup(True, False)
    button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    key1.row(button_phone)
    key1.row('Ввести почту для обратной связи')
    key1.one_time_keyboard = True
    if len(hello_count) == 0:  # Проверяем здоровались ли мы ранее
        bot.send_message(message.chat.id,
                         "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот созданный для добрых дел."
                         " Отправте свой номер телефона или почту, чтоб начать работу ".format(
                             message.from_user, bot.get_me()),
                         parse_mode='html', reply_markup=key1)

    elif message.text == 'Ⓜ Главное меню':
        pre_main(message)

    else:
        bot.send_message(message.chat.id,
                         "Выберете средство для обратной связи, чтоб начать работу ".format(
                             message.from_user, bot.get_me()),
                         parse_mode='html', reply_markup=key1)
    hello_count.insert(1, 1)  # Отмечаем факт приветствия


@bot.message_handler(content_types=['text', 'contact'])  # Основной обработчик
def phone_check(message):  # Уточняем у пользователя чем он с нами поделиться
    if message.text == None:  # Если пользователь нажал кнопку "Поделиться контактом" то текс будет None
        if message.contact.user_id == message.chat.id:  # Проверяем свой ли контакт дал пользователь
            cli_num.append(message.contact.phone_number)
            pre_main(message)
        else:
            bot.send_message(message.chat.id, 'Введите правильный номер телефона!')
            statup(message)
    elif message.text == "Ввести почту для обратной связи":  # Перекидывает на ввод почты
        mail_check(message)
    elif message.text == 'Ⓜ Главное меню':
        pre_main(message)
    else:
        statup(message)


def mail_check(message):  # Функция ввода почты
    key1 = telebot.types.ReplyKeyboardMarkup(True, False)
    key1.row("Проверить")
    bot.send_message(message.chat.id, 'Введите вашу почту ⤵')
    if message.text == 'Ввести почту для обратной связи':
        bot.register_next_step_handler(message, mail_check2)
    elif message.text == 'Ⓜ Главное меню':
        pre_main(message)


def mail_check2(message):  # Проверка потчы на валидность
    pattern = compile('(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')  # Проверяем совпадает ли паттерк
    is_valid = pattern.match(message.text)
    if is_valid:
        cli_mail.append(message.text)  # Записываем полученную почту
        pre_main(message)
    elif message.text == 'Ⓜ Главное меню':
        pre_main(message)
    else:
        bot.send_message(message.chat.id, "Почта введена неверно.")
        statup(message)


def pre_main(message):  # Основная функция
    inc_type.clear()  # Очищаем словарь с типом заявки
    key = types.ReplyKeyboardMarkup(True, False)
    key.row('У меня проблема')
    key.row('У меня дилемма', "У меня другой запрос")
    key.one_time_keyboard = True
    try:  # Спрашиваем что за инцент
        bot.send_message(message.chat.id,
                         "Итак, {0.first_name}!, что у вас случилось?.".format(
                             message.from_user, bot.get_me()),
                         parse_mode='html', reply_markup=key)
        print('No problem detected. Message send')
    except OSError:  # Спрашиваем что за инцент если предидущий вызвал ошибку таймаута
        print("ConnectionError - Sending again after 5 seconds!!!")
        time.sleep(5)
        bot.send_message(message.chat.id,
                         "Итак, {0.first_name}, что у вас случилось?.".format(
                             message.from_user, bot.get_me()),
                         parse_mode='html', reply_markup=key)
        print('Problem solved')
    bot.register_next_step_handler(message, main)


def main(message):  # Определяем тип инцидента и уточняем его подтип
    if message.text == 'У меня проблема':
        keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        keyboard.row('Большая проблема')
        keyboard.row('Небольшая проблема')
        keyboard.row('Другая проблема')
        keyboard.row('Ⓜ Главное меню')
        bot.send_message(message.chat.id, 'Выберите действие ⤵', reply_markup=keyboard)
        bot.register_next_step_handler(message, incedent)
    elif message.text == 'У меня дилемма':
        keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        keyboard.row('Большая дилемма', 'Небольшая дилемма')
        keyboard.row('Другая дилемма')
        keyboard.row('Ⓜ Главное меню')
        keyboard.one_time_keyboard = True
        bot.send_message(message.chat.id, 'Выберите действие ⤵', reply_markup=keyboard)
        bot.register_next_step_handler(message, info)
    elif message.text == 'У меня другой запрос':
        task = message.text
        vvod(message)
    elif message.text == 'Ⓜ Главное меню':
        pre_main(message)

    else:
        bot.send_message(message.chat.id, '🚫 Данные введены неверно 🚫')
        pre_main(message)


def incedent(message):  # Обрабатываем подтип инцедента
    keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
    keyboard.add('Ⓜ Главное меню')

    if message.text == 'Большая проблема':
        keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        keyboard.row('Проблема номер 1')
        keyboard.row('Проблема номер 2')
        keyboard.row('Проблема номер 3')
        keyboard.add('Ⓜ Главное меню')
        keyboard.one_time_keyboard = True
        bot.send_message(message.chat.id, 'Укажите вашу проблему ⤵', reply_markup=keyboard)
        bot.register_next_step_handler(message, vvod)

    elif message.text == 'Небольшая проблема':
        keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        keyboard.row('Проблема номер 4')
        keyboard.row('Проблема номер 5')
        keyboard.row('Проблема номер 6')
        keyboard.add('Ⓜ Главное меню')
        keyboard.one_time_keyboard = True
        bot.send_message(message.chat.id, 'Укажите вашу проблему ⤵', reply_markup=keyboard)
        bot.register_next_step_handler(message, vvod)

    elif message.text == 'Другая проблема':
        keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        keyboard.row('Проблема номер 7')
        keyboard.row('Проблема номер 8')
        keyboard.row('Проблема номер 9')
        keyboard.add('Ⓜ Главное меню')
        keyboard.one_time_keyboard = True
        bot.send_message(message.chat.id, 'Укажите вашу проблему ⤵', reply_markup=keyboard)
        bot.register_next_step_handler(message, vvod)

    elif message.text == 'Ⓜ Главное меню':
        pre_main(message)

    else:
        bot.send_message(message.chat.id, 'Данные введены неверно 😢')
        pre_main(message)


def info(message):  # Обработываем подтип запроса информации
    if message.text == 'Ⓜ Главное меню':
        pre_main(message)
    elif message.text == 'Большая дилемма':
        global task
        task = message.text
        vvod(message)
    elif message.text == 'Небольшая дилемма':
        task = message.text
        vvod(message)
    elif message.text == 'Другая дилемма':
        task = message.text
        vvod(message)
    else:
        text(message)
        bot.send_message(message.chat.id, 'Данные введены неверно')
        pre_main(message)


def vvod(message):  # Запрашиваем дополнительную информацию
    inc_type.append(message.text)
    global task
    if message.text in status:
        task = message.text
        bot.send_message(message.chat.id, 'Введите детали вашего запроса в строку ввода 😊')
        bot.register_next_step_handler(message, text)
    else:
        bot.send_message(message.chat.id, 'Данные введены неверно')
        pre_main(message)


def text(message):  # Отправляем письмо
    if message.text == 'Ⓜ Главное меню':
        pre_main(message)
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        keyboard.row('Ⓜ Главное меню')
        bot.send_message(message.chat.id, 'Ваше запрос \"' + message.text +
                         '\" получен. Можете вернуться в главное меню ⤵', reply_markup=keyboard)
        addr_from = "mail@gmail.com"
        addr_to = "mail@gmail.com"
        password = "password"
        msg = MIMEMultipart()  # Создаем сообщение
        msg['From'] = addr_from
        msg['To'] = addr_to
        msg['Subject'] = ("$$$" + message.text)
        body = (f'''
      Автор заявки {message.from_user.first_name},{message.from_user.last_name},

      Телефон {cli_num}

      Тип заявки: {inc_type},

      Текст заявки: {message.text}
      ''')
        msg.attach(MIMEText(body, 'plain'))  # Добавляем в сообщение текст
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)  # Создаем объект SMTP
        smtpObj.starttls()  # Начинаем шифрованный обмен по TLS
        smtpObj.login(addr_from, password)  # Получаем доступ
        smtpObj.send_message(msg)  # Отправляем сообщение
        smtpObj.quit()  # Выходим


while True:  # Запускаем бота
    try:
        bot.polling(none_stop=True)
    except OSError:
        bot.polling(none_stop=True)