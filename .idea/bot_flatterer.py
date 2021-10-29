import telebot
import requests
import re
import os
from telebot import types
from dotenv import load_dotenv
import json
from loguru import logger


bot = telebot.TeleBot('1990309547:AAFE_3sLdKZ3ejd1GIlP9VHEAUL_kyKBKlg')


class User():
    def __init__(self, name_user):
        self.__name_user = name_user

    def setter_name_user(self, name_user):
        self.__name_user = name_user


@bot.message_handler(commands=['start'])
def start_bot(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id,
                     '������, � ���. ���� ������ ��� �������� �����, �� � ������ �����.\n'
                     '����� ������ �������� ����� ������.\n'
                     '����� /search_people')
    print(message)

@bot.message_handler(commands=['help'])
def func_help(message: telebot.types.Message) -> None:
    bot.send_message(message.from_user.id,
                     '��� ����� ������?\n'
                     '����� ������ �������� ����� - /search_people\n')

@bot.message_handler(content_types=['text'])
def get_text_message(message: telebot.types.Message) -> None:
    try:
        if message.text == "������":
            bot.send_message(message.from_user.id, "������, ��� � ���� ���� ������?")
        elif message.text == "help":
            func_help(message)
        else:
            bot.send_message(message.from_user.id, "� ���� �� �������. ������ /help.")
    except:
        func_help(message)



user = User(name_user={})
bot.polling(none_stop=True, interval=0)