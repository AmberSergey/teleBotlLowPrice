import os
import sys
import time
import sqlite3
import telebot
from telebot import types
import config
import requests
from bs4 import BeautifulSoup
import time


bot = telebot.TeleBot('1581271848:AAFgtyreUpD9eItxiV7UzemONLwNrINak20'); # @MariaFlowers_bot
nameDB = 'flowers.db'
helpStr = """/Кротоны: посмотреть всю информацию о кротонах (Codiaeum-ах)
"""

fields = [{'name': ('Название',None)},
          {'firstName': ('Имя',None)},
          {'lastName': ('Фамилия',None)},
          {'price': ('Цена',None)},
          {'payment': ('Оплачено',None)},
          {'paypost': ('Почта',None)},
          {'status': ('Статус',None)},
          {'note': ('Примечание',None)},
          {'photo': ('Фото',None)}
         ]


def createDB():
    conn = sqlite3.connect(nameDB)
    cursor = conn.cursor()
# Создание таблицы
    cursor.execute("""CREATE TABLE IF NOT EXISTS flowers (
            id integer,
            name text,
            firstName text,
            lastName text,
            price integer,
            payment integer,
            paypost integer,
            status text,
            note text,
            photo blob
            )""")
    conn.close()
    print ('База данных создана')

def addFloewr(name):
    try:
        conn = sqlite3.connect(nameDB)
        cursor = conn.cursor()
        val = (int (time.time()*1000), name, None, None, None, None, None, 'Активно', None, None)
        cursor.execute('INSERT INTO flowers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',val)
        conn.commit()
        conn.close()
        print ('INSERT INTO flowers VALUES (', val,')')
    except:
        return False
    return True

def getFlowers():
    conn = sqlite3.connect(nameDB)
    cursor = conn.cursor()
    cursor.execute("""SELECT id, name, firstName, lastName FROM flowers """) # WHERE status = 'Активно'
    res = cursor.fetchall()
    conn.close()
    print (res)
    return res

def getFlower(id):
    conn = sqlite3.connect(nameDB)
    cursor = conn.cursor()
    sql=("""SELECT id, name, firstName, lastName, price, payment, paypost, status, note, photo FROM flowers WHERE id = {}""".format (id))
    cursor.execute(sql)
    res = cursor.fetchone()
    conn.close()
    return res

def editFlower(value):
#    try:
        conn = sqlite3.connect(nameDB)
        cursor = conn.cursor()
        print ('UPDATE flowers SET {} = \'{}\' WHERE id = {}'.format(config.currentFlower['field'], value, config.currentFlower['id']))
        cursor.execute('UPDATE flowers SET {} = \'{}\' WHERE id = {}'.format (config.currentFlower['field'], value, config.currentFlower['id']))
        conn.commit()
        conn.close()
#    except:
#        return False
        return True


def infoFlower(f):
    res = ''
    for f,p in zip (fields,f[1:]):
        res = res + f.get (list(f.keys())[0])[0] + ': '
        if p != None:
            res = res + p
        else:
            res = res + 'Не задано'
        res = res + '\n'
    return res

def parsing(m):
    res = 'Привет'
    print ('step = ', config.step)
    if config.step == 'Name':
        if addFloewr(m.text):
            res = 'Добавлен новый цветок ' + m.text
    elif config.step == 'editField':
        if editFlower(m.text):
            res = 'Сделано'
    config.step = None
    return res



def local():
    print ('Не работает пока :(')

@bot.message_handler(commands=['help', 'start'])
def get_help_messages(message):
    bot.send_message(message.chat.id, helpStr)

@bot.message_handler(commands=['add', 'добавить'])
def add_flower(message):
    config.step = 'Name'
    bot.send_message(message.chat.id, text='Как будут звать новый цветок?')


@bot.message_handler(commands=['add', 'добавить'])
def edit_flower(message):
    keyboard = types.InlineKeyboardMarkup(); #наша клавиатура
    for f in fields:
        name = list(f.keys())[0]
        key = types.InlineKeyboardButton(text=f.get(name)[0], callback_data=name); #кнопка name firstName lastName
        keyboard.add(key); #добавляем кнопку в клавиатуру
    bot.send_message(message.chat.id, text='Выбери поле', reply_markup=keyboard)

@bot.message_handler(commands=['flowers', 'цветы'])
def get_command(message):
    fs = getFlowers()
    if len(fs) > 0:
        keyboard = types.InlineKeyboardMarkup(); #наша клавиатура
        for f in fs:
            if f[2] == None:
                f2 = 'Не заполнено'
            else:
                f2=f[2]
            if f[3] == None:
                f3 = 'Не заполнено'
            else:
                f3=f[3]

            print (f[0])
            s = 'select:'+str(f[0])
            key = types.InlineKeyboardButton(text=f[1]+' '+f2+' '+f3, callback_data=s)
            keyboard.add(key); #добавляем кнопку в клавиатуру
        bot.send_message(message.chat.id, text='Выбери цветок', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, text='У вас нет цветов на продажу')

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data.find('select') == 0:
        id = int (call.data.split (':')[1])
        config.currentFlower['id'] = id
        f = getFlower(id)
        keyboard = types.InlineKeyboardMarkup(); #наша клавиатура
        key = types.InlineKeyboardButton(text='Редактировать', callback_data='edit');
        keyboard.add(key); #добавляем кнопку в клавиатуру
        bot.send_message(call.message.chat.id, infoFlower(f), reply_markup=keyboard)
    elif call.data == 'edit':
        keyboard = types.InlineKeyboardMarkup(); #наша клавиатура
        for f in fields:
            name = list(f.keys())[0]
            key = types.InlineKeyboardButton(text=f.get(name)[0], callback_data='enterField:'+name)
#            config.currentFlower['field'] = name
            keyboard.add(key); #добавляем кнопку в клавиатуру
        bot.send_message(call.message.chat.id, text='Выбери поле', reply_markup=keyboard)
    elif call.data.find('enterField:') == 0:
        config.currentFlower['field']=call.data.split (':')[1]
        config.step = 'editField'
        bot.send_message(call.message.chat.id,'Заполните поле ')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print (message.chat.id)
    bot.send_message(message.chat.id, parsing(message))

def compareList(l1,l2):
    if [x for x in l1 if x not in l2] != []:
        return True
    if [x for x in l2 if x not in l1] != []:
        return True
    return False

def findChage():
    # bot.polling(none_stop=True, interval=0)
    url = 'https://tumplant.ru/plants/10'  # url для разбора
    headers = {
        'Accept': 'text / h4ml, application / xhtml + xml, application / xml; q = 0.9, image / avif, image / webp, image / apng, * / *;q = 0.8, application / signed - exchange;   v = b3; q = 0.9',
        'Accept - Encoding': 'gzip, deflate, br',
        'Accept - Language':'ru - RU, ru; q = 0.9, en - US; q = 0.8, en; q = 0.7',
        'Cache - Control': 'no-cache',
        'Connection': 'keep - alive',
        'Host': 'tumplant.ru',
#        'Cookie': 'PHPSESSID = 836k8ipobtn6cgcdad25edqu78; _ga = GA1.2.1583605041.1659899024; _gid = GA1.2.1602064112.1659899024; _ym_uid = 1659899024419245744; _ym_d = 1659899024;  _ym_isad = 1',
 #       'Referer': 'https: // click.mail.ru/',
        'Sec - Fetch - Dest': 'document',
        'Sec - Fetch - Mode': 'navigate',
        'Sec - Fetch - Site': 'cross - site',
        'Sec - Fetch - User': '?1',
        'Upgrade - Insecure - Requests': '1',
        'User - Agent': 'Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 103.0.0.0 Safari / 537.36',
#        'sec - ch - ua': '".Not/A)Brand"; v = "99", "Google Chrome"; v = "103", "Chromium"; v = "103"'
#        'sec - ch - ua - mobile': '?0',
#        'sec - ch - ua - platform': '"Windows"'
    }
 #   summary = 'Показано 0 товаров'
    Codiaeums = []

    while (True):
        r = requests.get(url, headers=headers)
#        print (r.text)
        # Beautiful Soup
        soup = BeautifulSoup(r.text,features="html.parser")
#        count = soup.find('div',{'class': 'summary'})
        listFloeers = soup.table.findChildren('tr')
        tempCodiaeums = []
        tempStr = ''
        for floewr in listFloeers:
            ff=floewr.findChildren('td')
            if ff:
                if ff[1].text.find('Codiaeum') >= 0:
                    tempCodiaeums.append({'Name':ff[1].text.replace('\n','').strip(' '),'Price':ff[3].text.replace('\n','').strip(' ')})
                    tempStr = tempStr+'\n' + ff[1].text.replace('\n','').strip(' ') + ' - ' + ff[3].text.replace('\n','').strip(' ')
                    print(ff[1].text.replace('\n','').strip(' '), ' - ', ff[3].text.replace('\n','').strip(' '), '\n')
        if compareList(Codiaeums, tempCodiaeums):
#        mewCodiaeum = r.text.count('Codiaeum')
#        if (summary != count.text or mewCodiaeum != Codiaeum or True):
            #print (count.text, '\nCodiaeum = ', int (mewCodiaeum/2))
#            summary = count.text
            Codiaeums = tempCodiaeums
            bot.send_message(1573504003, 'Данные обновились - ' + tempStr) # для меня
            bot.send_message(1780411375, 'Данные обновились - ' + tempStr) # для меня
            #bot.send_message(1780411375, 'Данные обновились - ' + count.text + '\nCodiaeum = ' + str (mewCodiaeum/2)) # для Маши
        time.sleep(60)

#   with open('test.html', 'w') as output_file:
#       output_file.write(str (r.text))



if __name__ == "__main__":
    findChage()
