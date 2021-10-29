# Travel Telegram Bot
Бот написан на версии Python 3.9.2
Перед работой импортированы библиотеки:
- import telebot
- import requests
- import re
- import os
- from telebot import types
- from dotenv import load_dotenv
- import pytz
- import json
- from loguru import logger

Так же в рабочий файл бота импортирован написанный файл "methods.py" в котором так же использованы библиотека collections:
- import collections

## Написание бота
Получение токена происходило по обращению к @BotFather
В рабочем файле имеется класс Hotels в который последовательно добавляются первоначальная команда пользователя('lowprice', 'highprice', 'bestdeal'), необходимое количество отелей, дистанция от центра города и словарь отелей. Так же есть функция "result" которая собирает все полученные данные собранные в классе Hotels и вызавает одну из функций написанных в файле "methods.py"

###Функции:
- start_bot (принимает команду /start и отправляет сообщение пользователю с возможностями бота)
- func_help(принимает команду /help и отправляет сообщение пользователю с возможностями бота)

Далее начинается логика бота после получения одной из команд от пользователя 'lowprice', 'highprice', 'bestdeal' срабатывает функция choice_city, в которой в свою очередь срабатывает функция append_message класса Hotels. В класс добавляется выбранная команда, которая используется позднее. Пользователю отправляется сообщении "Напишите интересующий Вас город". После ввода интересующего города. Отправляется запрос на сайт rapidapi.com. Затем начинает работать функция city_search, которая исключает повторения городов, но сохраняет их ID.

Функция city_search завершается, когда на экране пользователя появляются Callback клавиатура с кнопками выбора городов.

При нажатии нужной кнопки, отлавливает запрос при помощи декоратора "@bot.callback_query_handler(func=lambda call: True)", после запускается функция "id_callback", в которую отправляется запрос ID городов и составляется словарь в котором ключи это ID отелей, а значения - рейтинг, стоимость, названия, расстояние до цетра города.

Затем следуют функции "answer_choice_counter", "choice_counter", "answer_choice_distance", "choice_distance". Сначала запрашивается "Сколько вывести отелей", это значение отправляется в класс Hotels. Запрашивется дистанция до центра города(если первоначально выбрана команда 'bestdeal'), это значение так же отправляется в класс Hotels.

Последней запускается функция "result" класса Hotels. Функция выводит на экран пользователя нужную ему информацию в зависимости от предыдущих выборов. После запускается функция "func_help"

Так же есть функция "get_text_message" необходимая, если пользователь введет какое либо текстовое сообщение.