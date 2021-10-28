# -*- coding: utf-8 -*-
from telebot import *
import requests
import data_base
import base64
from config import URL_DADATA, TOKEN_DADATA, TOKEN_BOT, URL_LT, TOKEN_LT


bot = telebot.TeleBot(TOKEN_BOT)


def get_request_dadata(message, inn):
    headers_auth = {'Authorization': 'Token ' + TOKEN_DADATA, 'Content-Type': 'application/json'}
    auth = requests.post(URL_DADATA, headers=headers_auth)
    if auth.status_code == 200:
        params = {
            'query': inn,
            'branch_type': "MAIN",
            'status': "ACTIVE"
        }
        try:
            r = requests.get(URL_DADATA, headers=headers_auth, params=params)
            res = r.json()
            return res
        except Exception as e:
            bot.send_message(message.chat.id, e)
    else:
        return False

def get_info_about_org(message):
    try:
        data = get_request_dadata(message, message.text)
        if data == False:
            bot.send_message(message.from_user.id, "Не удалось получить ответ от сервера.")
        else:
            list_info_org = []
            list_info_org.append(data["suggestions"][0]["value"])
            list_info_org.append(
                data["suggestions"][0]["data"]["management"]["post"] + ": " +
                data["suggestions"][0]["data"]["management"][
                    "name"])
            list_info_org.append(data["suggestions"][0]["data"]["address"]["unrestricted_value"])

            bot.send_message(message.from_user.id, list_info_org[0] +
                             "\n{}".format(list_info_org[1]) +
                             "\nАдрес: {}".format(list_info_org[2])
                             )
            buttons_connect_with_org(message)
    except Exception as e:
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "По данному ИНН не нашлось данных.", reply_markup=a)
        message = bot.send_message(message.chat.id, "Введите ИНН:")
        bot.register_next_step_handler(message, get_info_about_org)


def request_api_lt(message, inn):
    headers = {'Authorization': 'Bearer ' + TOKEN_LT, 'Content-Type': 'application/json'}

    query = """
 query{
  allCompanies (filter:{}){
    id
    name
    limit_summ
    limit_count
    contacts{
      id
      name
      city
      post
      city
      tags{
        id
        name
      }
      responsible_user{
        name
        
      }
    }
  }
}
    """
    try:
        query = query.replace("value", "\"" + str(inn) + "\"")
        r = requests.post(URL_LT, json={"query": query}, headers=headers)
    except Exception as e:
        bot.send_message(message.chat.id, e)

    if r.status_code == 200:
        return r.json()
    else:
        return False



def get_info_from_api_lt(message, inn):
        res = request_api_lt(message, str(inn))
        if res == False:
            print("Ошибка! не удалось получить данные.")

        else:
            try:
                list_info_org = []
                list_info_org.append(res['data']['allCompanies'][0]['name'])
                list_info_org.append(res['data']['allCompanies'][0]['contacts'][0]['post'] + ": " +
                                     res['data']['allCompanies'][0]['contacts'][0]['name'])
                list_info_org.append(res['data']['allCompanies'][0]['contacts'][0]['city'])
                list_info_org.append(res['data']['allCompanies'][0]['limit_summ'])
                list_info_org.append(res['data']['allCompanies'][0]['limit_count'])
                list_info_org.append(res['data']['allCompanies'][0]['contacts'][0]['tags'])
                list_info_org.append(res['data']['allCompanies'][0]['contacts'][0]['responsible_user']['name'])

                bot.send_message(message.from_user.id, "Компания: {}".format(list_info_org[0]) +
                                 "\n{}".format(list_info_org[1]) +
                                 "\nГород: {}".format(list_info_org[2]) +
                                 "\nЛимит по сумме: {}".format(list_info_org[3]) +
                                 "\nЛимит по количеству: {}".format(list_info_org[4]) +
                                 "\nТэги: {}".format(list_info_org[5]) +
                                 "\nОтветственный: {}".format(list_info_org[6])
                                 )
                buttons_connect_with_org(message)

            except Exception as e:
                get_info_about_org(message)



def buttons_connect_with_org(message):
    markup_reply = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item_yes = types.KeyboardButton('Да')
    item_no = types.KeyboardButton('Нет')
    markup_reply.add(item_yes,  item_no)
    bot.send_message(message.chat.id, "Отправить заявку по данной организации?", reply_markup=markup_reply)
    
def buttons_change_param(message):
    markup_reply = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item_1 = types.KeyboardButton('Сделать перерасчёт')
    item_2 = types.KeyboardButton('Оформить зявку на лизинг')
    markup_reply.add(item_1,  item_2)
    bot.send_message(message.chat.id, "Выберите дальнейшее действие:", reply_markup=markup_reply)

def buttons_regisrtation(message):
    markup_reply = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item_1 = types.KeyboardButton('Заказать обратный звонок')
    item_2 = types.KeyboardButton('Просмотреть решение по заявке')
    markup_reply.add(item_1,  item_2)
    bot.send_message(message.chat.id, "Выберите дальнейшее действие:", reply_markup=markup_reply)


def check_inn(message):
    if message.text=="/start":
        welcome(message)

    elif message.text.isdigit() and len(message.text) == 10 or len(message.text) == 12:
        #dict_inn_photo_doc['inn'] = []
        #dict_inn_photo_doc['inn'].append(message.text)
        #get_info_from_api_lt(message, message.text)

        get_info_about_org(message)
    else:
        message = bot.send_message(message.from_user.id, "ИНН не корректен. Попробуйте ввести снова.")
        bot.register_next_step_handler(message, check_inn)

def get_phone_user(message):
    bot.send_message(message.chat.id, "Ваша заявка направлена на рассмотрение.\nОжидайте решения в течение 5 минут.")
    bot.register_next_step_handler(message, welcome)

def get_lead(message):
    bot.send_message(message.chat.id, "Специалист свяжется с Вами в ближайшее время.")
    bot.send_message(chat.id='@LeadSmartLeasing', "Новая заявка ;)")
    bot.register_next_step_handler(message, send_telegram)
    
dict_user = {}
def surname_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['surname'] = []
        dict_user['surname'].append(message.text)
        bot.send_message(message.chat.id, "Имя: ")
        bot.register_next_step_handler(message, firstname_user)

def firstname_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['firstname'] =[]
        dict_user['firstname'].append(message.text)
        message = bot.send_message(message.from_user.id, "Отчетство: ")
        bot.register_next_step_handler(message, secondname_user)

def secondname_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['secondname_user'] =[]
        dict_user['secondname_user'].append(message.text)
        message = bot.send_message(message.from_user.id, "Дата рождения: ")
        bot.register_next_step_handler(message, birthdaydate_user)

def birthdaydate_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['birthdaydate_user'] =[]
        dict_user['birthdaydate_user'].append(message.text)
        message = bot.send_message(message.from_user.id, "Место рождения: ")
        bot.register_next_step_handler(message, birthdaylocate_user)

def birthdaylocate_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['birthdaylocate_user'] =[]
        dict_user['birthdaylocate_user'].append(message.text)
        message = bot.send_message(message.from_user.id, "ИНН руководителя: ")
        bot.register_next_step_handler(message, inn_user)
def inn_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['inn_user'] =[]
        dict_user['inn_user'].append(message.text)
        message = bot.send_message(message.from_user.id, "Серия и номер паспорта (без пробелов): ")
        bot.register_next_step_handler(message, passportumber_user)
def passportumber_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['passportumber_user'] =[]
        dict_user['passportumber_user'].append(message.text)
        message = bot.send_message(message.from_user.id, "Дата выдачи паспорта: ")
        bot.register_next_step_handler(message, passportdate_user)
def passportdate_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['passportdate_user'] =[]
        dict_user['passportdate_user'].append(message.text)
        message = bot.send_message(message.from_user.id, "Место выдачи паспорта: ")
        bot.register_next_step_handler(message, passportplace_user)
def passportplace_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['passportplace_user'] =[]
        dict_user['passportplace_user'].append(message.text)
        message = bot.send_message(message.from_user.id, "Код подразделения: ")
        bot.register_next_step_handler(message, passportcode_user)
def passportcode_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['passportcode_user'] =[]
        dict_user['passportcode_user'].append(message.text)
        message = bot.send_message(message.from_user.id, "Адрес регистрации руководителя: ")
        bot.register_next_step_handler(message, address_user)
def address_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['address_user'] =[]
        dict_user['address_user'].append(message.text)
        message = bot.send_message(message.from_user.id, "Мобильный телефон: ")
        bot.register_next_step_handler(message, phone_user)

def phone_user(message):
    if message.text == "/start":
        welcome(message)
    else:
        dict_user['phone'] = []
        dict_user['phone'].append(message.text)
        #data_base.table_user(message, dict_user['surname'][0], dict_user['firstname'][0], dict_user['secondname'][0], dict_user['birthdaydate'][0], dict_user['birthdaylocate'][0], dict_user['inn'][0], dict_user['passportumber'][0], dict_user['passportdate'][0], dict_user['passportplace'][0], dict_user['passportcode'][0], dict_user['address'][0], dict_user['phone'][0])
        message = bot.send_message(message.from_user.id, "Введите ИНН организации: ")
        bot.register_next_step_handler(message, check_inn)

@bot.message_handler(commands=['start'])
def welcome(message):
    text_start = "Добрый день, {}!\n\t-Мы поможем сформировать заявку на лизинг\n\n\n (потребуется внести реквизиты компании \nи заполнить паспортные данные руководителя.\n\n\t-Для действующих Клиентов отобразим доступный лимит.".format(message.from_user.first_name)
    bot.send_message(message.chat.id, text_start)
    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_leasing_payment = types.KeyboardButton('Доступный лимит')
    item_call = types.KeyboardButton('Оформить заявку')
    markup_reply.add(item_leasing_payment, item_call)
    bot.send_message(message.chat.id, "Нажмите на кнопку, чтобы начать", reply_markup=markup_reply)

def send_telegram(message):
    text1 = dict_user[surname]
    text2 = dict_user[firstname]
    text3 = dict_user[secondname]
    text4 = dict_user[birthdaydate]
    text5 = dict_user[address]
    text6 = dict_user[phone]
    bot.send_message(chat.id='@LeadSmartLeasing', "Новая заявка" '\n'text1'\n' + text2'\n' + text3'\n' + text4'\n' + text5'\n' + text6)
    
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Оформить заявку":
        a = telebot.types.ReplyKeyboardRemove()
        message = bot.send_message(message.from_user.id, "Введите данные руководителя\n\nФамилия: ", reply_markup=a)
        bot.register_next_step_handler(message, surname_user)
        
    elif message.text == "Да":
        a = telebot.types.ReplyKeyboardRemove()
        message = bot.send_message(message.from_user.id, 'На указанный номер мобильного телефона направлен код подтверждения.\nВведите код подтверждения: ', reply_markup=a)
        bot.register_next_step_handler(message, get_phone_user)

    elif message.text == "Нет":
        a = telebot.types.ReplyKeyboardRemove()
        message = bot.send_message(message.from_user.id, "Проверьте верно ли вы указали ИНН. Введите снова: ", reply_markup=a)
        bot.register_next_step_handler(message, check_inn)

    elif message.text == 'Доступный лимит':
        a = telebot.types.ReplyKeyboardRemove()
        message = bot.send_message(message.from_user.id, "Введите ИНН:", reply_markup=a)
        bot.register_next_step_handler(message, check_inn)

    elif message.text == 'Заказать обратный звонок':
        a = telebot.types.ReplyKeyboardRemove()
        message = bot.send_message(message.from_user.id, "Введите стоимость в рублях", reply_markup=a)
        bot.register_next_step_handler(message, get_lead)
    elif message.text == 'Просмотреть решение по заявке':
        a = telebot.types.ReplyKeyboardRemove()
        message = bot.send_message(message.from_user.id, "Введите ИНН:", reply_markup=a)
        bot.register_next_step_handler(message, get_info_from_api_lt)
    elif message.text == 'Отменить зявку':
        pass
        data_base.delete_from_data_user()

    # Инлайн кнопки
    # markup_inline = types.InlineKeyboardMarkup()
    # item_yes = types.InlineKeyboardButton(text='Да', callback_data='yes', one_time_keyboard=True)
    # item_no = types.InlineKeyboardButton(text='Нет', callback_data='no',  one_time_keyboard=True)
    # markup_inline.add(item_yes, item_no)
    # bot.send_message(message.chat.id, "Вас интересует данная организация?", reply_markup=markup_inline)




bot.polling(none_stop=True, interval=0)



#Конвертация фото из бд
# @bot.message_handler(commands=['img'])
# def ext_photo(message):
#     conn = sqlite3.connect("new_base3.db")
#     cursor = conn.cursor()
#     cursor.execute("""CREATE TABLE IF NOT EXISTS data_user(
#                chat_id INTEGER,
#                org_inn TEXT,
#                photo_passport_1 BLOB,
#                photo_passport_2 BLOB,
#                doc_personal_data BLOB,
#                FOREIGN KEY (chat_id) REFERENCES users(id)
#            )""")
#     img = conn.execute(f'SELECT doc_personal_data FROM data_user WHERE  chat_id = {message.chat.id}').fetchone()
#     print("img: ", img, "\ntype(img): ", type(img))
#     if img is None:
#         conn.close()
#         return None
#     else:
#         conn.close()
#
#         # сохраним base64 в картинку и отправим пользователю
#         with open("files/imageToSave.jpg", "wb") as fh:
#             fh.write(base64.decodebytes(img[0]))
#             bot.send_photo(message.chat.id, open("files/imageToSave.jpg", "rb"))
