# -*- coding: utf-8 -*-
import os
import telebot
import config
from bot_token import TOKEN
import mysql
from flask import Flask, request


bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)



condition = dict()                  #Состояние пользователей(ожидание ввода и т.д.)


business = dict()                   #Список общих дел пользователей



list_business = dict()              #Списки дел



@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, config.start_text)
    condition[message.chat.id] = config.Waiting.STANDART.value          #Пользователь добавляется в БД
    business[message.chat.id] = []
    list_business[message.chat.id] = []
    business_handler(message)


edit_business = None


@bot.callback_query_handler(func=lambda call: True)  #Ответ на кнопки /business
def callback_handler(call):

    global edit_business
    if call.data == "Новое дело":

        bot.send_message(call.from_user.id, 'Введите название дела')
        condition[call.from_user.id] = config.Waiting.WAITING_BUSINESS.value

    elif call.data == "Удалить дело":
        markup = config.create_markup(business[call.from_user.id])

        bot.send_message(call.from_user.id, 'Выберите, какое дело вы хотите удалить:', reply_markup=markup)
        condition[call.from_user.id] = config.Waiting.EDIT_BUSINESS.value

    elif condition[call.from_user.id] == config.Waiting.EDIT_BUSINESS.value:
        markup = config.create_markup(('Удалить', ))
        edit_business = call.data
        bot.send_message(call.from_user.id, 'Вы выбрали дело "{}"'.format(call.data), reply_markup=markup)
        condition[call.from_user.id] = config.Waiting.EDIT_BUSINESS_WAITING_RESPONSE

    elif condition[call.from_user.id] == config.Waiting.EDIT_BUSINESS_WAITING_RESPONSE:
        business[call.from_user.id].remove(edit_business)
        business_handler(call)



@bot.message_handler(commands=['business'])
def business_handler(message):
    try:
        condition[message.chat.id] = config.Waiting.STANDART.value

        markup = config.create_markup(
            ("Новое дело", "Удалить дело", "Мои списки дел (не работает)", "Новый список дел (не работает)"))

        if len(business[message.chat.id]) == 0:

             bot.send_message(message.chat.id, config.business_0, reply_markup=markup)

        else:

            bot.send_message(message.chat.id, config.list_of_business(business[message.chat.id]),reply_markup=markup)
    except:
        condition[message.from_user.id] = config.Waiting.STANDART.value

        markup = config.create_markup(
            ("Новое дело", "Удалить дело", "Мои списки дел (не работает)", "Новый список дел (не работает)"))

        if len(business[message.from_user.id]) == 0:

            bot.send_message(message.from_user.id, config.business_0, reply_markup=markup)

        else:

            bot.send_message(message.from_user.id, config.list_of_business(business[message.chat.id]), reply_markup=markup)




@bot.message_handler(func=lambda message: condition[message.chat.id]  == config.Waiting.WAITING_BUSINESS.value)
def new_business(message):
    try:
        business[message.chat.id]
    except KeyError:
        business[message.chat.id] = []

    business[message.chat.id].append(message.text)
    bot.send_message(message.chat.id, 'Отлично, дело добавлено')
    business_handler(message)

# @bot.message_handler(func=lambda message: condition[message.chat.id]  == config.Waiting.WAITING_LIST.value)

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://telegram-bot-to-do.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))