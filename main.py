import telebot
import requests
import re
import os
from telebot import types
from dotenv import load_dotenv
import json
from loguru import logger

import methods


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

logger.add('error.log', format='{time} {level} {message}', level='ERROR')

"""Класс отелей. Вносится вся информация полученная от пользователя: первоначальная команда,
словарь с отелями, дистанция  от центра города. Функция 'result' показывает результат пользователю"""


class Hotels():

    def __init__(self, command):
        self.__command = command

    def set_language(self, language):
        rus_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        us_alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if language.text[0] in rus_alphabet:
            self.__language = 'RU'
        elif language.text[0] in us_alphabet:
            self.__language = 'US'

    def get_language(self):
        return self.__language

    def get_command(self):
        return self.__command

    def append_message(self, command):
        self.__command = command

    def answer_count(self, count):
        self.__counter_hotels = int(count.text)

    def answer_distance(self, distance):
        distance = distance.text
        new_distance = ''
        for i_elem in distance:
            if i_elem.isdigit():
                new_distance += i_elem
            elif i_elem == ',' or i_elem == '.':
                new_distance += '.'
        self.__distance = float(new_distance)

    def append_dict_hotels(self, dict_hotels):
        self.__dict_hotels = dict_hotels

    def result(self):
        if self.__command.text == '/lowprice':
            self.__sorted_dict = methods.lowprice_hotels(self.__dict_hotels)
        elif self.__command.text == '/highprice':
            self.__sorted_dict = methods.highprice_hotels(self.__dict_hotels)
        elif self.__command.text == '/bestdeal':
            self.__sorted_dict = methods.bestdeal_hotels(self.__dict_hotels, self.__distance)

        counter = 0
        if self.__language == 'RU':
            for i_hotel in self.__sorted_dict:
                bot.send_message(self.__command.from_user.id, text='Отель: {hotel}\n '
                                                                   'цена: {price} рублей\n'
                                                                   'рейтинг: {rating}\n'
                                                                   'адрес: {adress}\n'
                                                                   'до центра города {distance}'.format(
                    hotel=self.__sorted_dict[i_hotel]['name_hotel'],
                    price=self.__sorted_dict[i_hotel]['price'],
                    rating=self.__sorted_dict[i_hotel]['rating'],
                    adress=self.__sorted_dict[i_hotel]['adress'],
                    distance=self.__sorted_dict[i_hotel]['distance']))
                counter += 1
                if counter == self.__counter_hotels:
                    break
            func_help(self.__command)

        elif self.__language == 'US':
            for i_hotel in self.__sorted_dict:
                bot.send_message(self.__command.from_user.id, text='Hotel: {hotel}\n '
                                                                   'price: $ {price}\n'
                                                                   'rating: {rating}\n'
                                                                   'address: {adress}\n'
                                                                   'to the city center {distance}'.format(
                    hotel=self.__sorted_dict[i_hotel]['name_hotel'],
                    price=self.__sorted_dict[i_hotel]['price'],
                    rating=self.__sorted_dict[i_hotel]['rating'],
                    adress=self.__sorted_dict[i_hotel]['adress'],
                    distance=self.__sorted_dict[i_hotel]['distance']))
                counter += 1
                if counter == self.__counter_hotels:
                    break
            func_help(self.__command)


"""Функция старт. Срабатывает при первом запуске бота и команда /start"""


@bot.message_handler(commands=['start'])
def start_bot(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id,
                     'Привет Я бот туристического агенства Too Easy Travel.\n'
                    'Помогу найти:\n'
                    'Самые дешевые отели(top cheap hotels) - /lowprice\n'
                    'Самые дорогие и роскошные отели(the most expensive hotels) - /highprice\n'
                    'Лучшие предложения близкие к центру города(the best deals in the city center) - /bestdeal\n')


"""Функция помощи, в которой прописываются имеющиеся команды в боте"""


@bot.message_handler(commands=['help'])
def func_help(message: telebot.types.Message) -> None:
    bot.send_message(message.from_user.id,
                     'Что будем делать?\n'
                     'Поиск:\n'
                     'Самые дешевые отели(top cheap hotels) - /lowprice\n'
                     'Самые дорогие и роскошные отели(the most expensive hotels) - /highprice\n'
                     'Лучшие предложения близкие к центру города(the best deals in the city center) - /bestdeal\n')


"""Функция которая принимает команды по поиску отелей"""


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
@logger.catch
def choice_city(message: telebot.types.Message) -> None:
    """Функция которая принимает команды по поиску отелей"""
    try:
        work_message = bot.send_message(message.from_user.id, 'Напишите интересующий Вас город(enter the city to search for)')
        choice_hotels.append_message(command=message)
        bot.register_next_step_handler(work_message, city_search)
    except ValueError:
        get_text_message(message)


"""Функция запроса к API, которая находит все города, 
их id и отправляет пользователю кнопку с выбором города"""


@logger.catch
def city_search(message: telebot.types.Message) -> None:
    try:
        url = "https://hotels4.p.rapidapi.com/locations/search"
        choice_hotels.set_language(message)

        if choice_hotels.get_language() == 'RU':
            querystring = {"query": message.text, "locale": "ru_RU"}
        elif choice_hotels.get_language() == 'US':
            querystring = {"query": message.text, "locale": "en_US"}

        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

        headers = os.getenv('API_query')
        headers = eval(headers)
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=15)
        work_obj = json.loads(response.text)
        first_deepening = work_obj["suggestions"]
        second_deepining = first_deepening[0]
        third_deepining = second_deepining['entities']

        dict_city = dict()
        for i in third_deepining:
            strit = i['caption']
            name_city = re.findall(r"(.*?)<span class='highlighted'>", strit) + \
                        re.findall(r"highlighted'>(.*?)</span>", strit) + re.findall(r'</span>(.*)', strit)
            if name_city == []:
                name_city = i['caption']
            else:
                name_city = name_city[0] + name_city[1] + name_city[2]
            id_city = i['destinationId']
            dict_city[name_city] = [id_city]

        keyboard = types.InlineKeyboardMarkup()
        for i in dict_city.keys():
            obj = str(dict_city[i])[1:-1]
            new_str = ''
            for i_symbol in obj:
                if i_symbol != "'" and i_symbol != ",":
                    new_str += i_symbol
            button_city = types.InlineKeyboardButton(text=str(i), callback_data=new_str)
            keyboard.add(button_city)

        keyboard.add(types.InlineKeyboardButton(text='Другой город(Another city)', callback_data='Другой город'))
        bot.send_message(message.from_user.id, text='Выберете город', reply_markup=keyboard)
    except requests.exceptions.ReadTimeout:
        bot.send_message(message.from_user.id, 'Превышено время ожидания, попробуйте позже\n'
                                               'Timeout exceeded. Try again later')
    except ValueError:
        if choice_hotels.get_language() == 'RU':
            bot.send_message(message.from_user.id, 'Вы что то не так ввели. Попробуйте еще раз.')
        elif choice_hotels.get_language() == 'US':
            bot.send_message(message.from_user.id, 'You entered something wrong. Try again.')
        choice_city(choice_hotels.get_command())

"""Функция получает на вход выбранный город и делает запрос к API по id города"""


@bot.callback_query_handler(func=lambda call: True)
@logger.catch
def iq_callback(query):
    try:
        if query.data != 'Другой город':
            if choice_hotels.get_language() == 'RU':
                bot.send_message(query.from_user.id, 'Подождите...')
            elif choice_hotels.get_language() == 'US':
                bot.send_message(query.from_user.id, 'Wait...')
            work_obj = (query.data).split()
            all_hotels = dict()
            for j_id in work_obj:
                url = "https://hotels4.p.rapidapi.com/properties/list"
                if choice_hotels.get_language() == 'RU':
                    querystring = {"destinationId": j_id, "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
                               "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU",
                               "currency": "RUB"}
                elif choice_hotels.get_language() == 'US':
                    querystring = {"destinationId": j_id, "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
                                   "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE", "locale": "eu_US",
                                   "currency": "USD"}
                headers = os.getenv('API_query')
                headers = eval(headers)
                response = requests.request("GET", url, headers=headers, params=querystring, timeout=15)
                work_obj = json.loads(response.text)
                first_deepining = work_obj['data']
                second_deepining = first_deepining['body']
                third_deepining = second_deepining["searchResults"]
                fourth_deepining = third_deepining['results']

                for i_hotels in fourth_deepining:
                    if i_hotels['id'] in all_hotels.keys():
                        break
                    else:
                        dict_hotel = dict()
                        dict_hotel['name_hotel'] = i_hotels['name']

                        try:
                            dict_hotel['price'] = i_hotels['ratePlan']['price']['exactCurrent']
                        except:
                            dict_hotel['price'] = 'нет данных'

                        try:
                            dict_hotel['rating'] = i_hotels['guestReviews']['rating']
                        except:
                            dict_hotel['rating'] = 'нет'

                        try:
                            dict_hotel['adress'] = i_hotels['address']['streetAddress']
                        except:
                            dict_hotel['adress'] = 'нет данных'

                        try:
                            dict_hotel['distance'] = i_hotels['landmarks'][0]['distance']
                        except:
                            dict_hotel['distance'] = 'нет данных'

                        all_hotels[i_hotels['id']] = dict_hotel

            choice_hotels.append_dict_hotels(dict_hotels=all_hotels)
            answer_choice_counter(query)

        else:
            func_help(query)
    except requests.exceptions.ReadTimeout:
        bot.send_message(query.from_user.id, 'Превышено время ожидания, попробуйте позже\n'
                                               'Timeout exceeded. Try again later')
    except ValueError:
        get_text_message(query)


"""Функция запрашивает у пользователя 'сколько вывести результатов' 
и полученный результат отправляет в функцию 'choice_counter'"""


def answer_choice_counter(query: telebot.types.Message) -> None:
    if choice_hotels.get_language() == 'RU':
        user_count = bot.send_message(query.from_user.id, 'Сколько вывести результатов')
    elif choice_hotels.get_language() == 'US':
        user_count = bot.send_message(query.from_user.id, 'How many results can I output')
    bot.register_next_step_handler(user_count, choice_counter)


"""Функция отправляет запрос от пользователя 'количество показанных отелей' в класс Hotels,
если первоначальная команда 'bestdeal', то запускается функция 'answer_choice_distance',
иначе запускается функция 'result' класса Hotels"""


@logger.catch
def choice_counter(count: telebot.types.Message) -> None:
    try:
        choice_hotels.answer_count(count=count)
        if (choice_hotels.get_command()).text == '/bestdeal':
            answer_choice_distance(count)
        else:
            choice_hotels.result()
    except ValueError:
        if choice_hotels.get_language() == 'RU':
            bot.send_message(count.from_user.id, 'Ты чего то не то ввел')
        if choice_hotels.get_language() == 'US':
            bot.send_message(count.from_user.id, 'Incorrect input')
        answer_choice_counter(count)


"""Функция запрашивает у пользователя дистанцию до центра города и полученное значение отправляет в 
функцию 'choice_distance'"""


def answer_choice_distance(query: telebot.types.Message) -> None:
    if choice_hotels.get_language() == 'RU':
        user_distance = bot.send_message(query.from_user.id, 'На каком расстоянии(в км) от центра искать отели?')
    elif choice_hotels.get_language() == 'US':
        user_distance = bot.send_message(query.from_user.id, 'At what distance (in miles) from the center to look for hotels?')
    bot.register_next_step_handler(user_distance, choice_distance)


"""Функция отправляет запрос от пользователя 'дистанция до центра города', 
в класс Hotels и запускает функцию 'result' того же класса"""


@logger.catch
def choice_distance(distance: telebot.types.Message) -> None:
    try:
        choice_hotels.answer_distance(distance)
        choice_hotels.result()
    except ValueError:
        if choice_hotels.get_language() == 'RU':
            bot.send_message(distance.from_user.id, 'Ты чего то не то ввел')
        if choice_hotels.get_language() == 'US':
            bot.send_message(distance.from_user.id, 'Incorrect input')
        answer_choice_distance(distance)


"""Функция предназначена для обработки письменных запросов от пользователя"""


@bot.message_handler(content_types=['text'])
@logger.catch
def get_text_message(message: telebot.types.Message) -> None:
    try:
        if message.text == "Привет":
            bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?(Can I help you?)")
        elif message.text == "help":
            func_help(message)
        else:
            bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")
    except ValueError:
        func_help(message)


if __name__ == "__main__":
    choice_hotels = Hotels(command='')
    bot.polling(none_stop=True, interval=0)








