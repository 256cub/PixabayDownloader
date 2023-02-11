#!/usr/bin/python
import datetime
import os
import re
import requests
import config
import random
import logging
import mysql.connector

# import boto3
# from botocore.exceptions import ClientError

from datetime import datetime
from os.path import basename
from os.path import exists
from zipfile import ZipFile
from os import walk

from telegram.ext import MessageHandler, Filters, CallbackContext, CallbackQueryHandler, Updater, CommandHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.update import Update

from Main import MySQL

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


KEYWORD = 'nature'
MEDIA_TYPE = 'image'
LIMIT = 1


def download(url, media_id, path):
    now = datetime.now()
    if exists(path):
        print('{} | {} | {} | {}'.format(add_beauty_space(media_id), add_beauty_space('EXIST'), add_beauty_space(now.strftime('%Y-%m-%d %H:%M:%S')), url))
    else:
        result = requests.get(url).content
        with open(path, 'wb') as handler:
            handler.write(result)
            print('{} | {} | {} | {}'.format(add_beauty_space(media_id), add_beauty_space('DOWNLOAD'), add_beauty_space(now.strftime('%Y-%m-%d %H:%M:%S')), url))


def get_media(update, context, keyword, media_type, page, limit):
    urls = []
    if media_type == 'image':
        url = config.PIXABAY_IMAGE_URL.format(config.PIXABAY_API, keyword, page, config.PIXABAY_LIMIT_PER_PAGE)
    elif media_type == 'video':
        url = config.PIXABAY_VIDEO_URL.format(config.PIXABAY_API, keyword, page, config.PIXABAY_LIMIT_PER_PAGE)
    else:
        url = False
        print('WRONG MEDIA TYPE')

    response = requests.get(url)
    data = response.json()

    context.bot.send_message(chat_id=update.effective_chat.id, text='Match {} {}'.format(data['total'], media_type.title() + 's'))

    context.bot.send_message(chat_id=update.effective_chat.id, text='Prepare to download {} {}'.format(limit, media_type.title() + 's'))

    to_wait = limit
    if media_type == 'video':
        to_wait = to_wait * 4

    context.bot.send_message(chat_id=update.effective_chat.id, text='Please wait... up to {} seconds '.format(to_wait))

    print('MATCH {} {}'.format(data['total'], media_type.title() + 's'))

    if not os.path.exists(media_type):
        os.makedirs(media_type)

    random.shuffle(data['hits'])

    for nr, hit in enumerate(data['hits']):

        if media_type == 'image':
            path = '{}{}/{}.jpg'.format(config.APP_PATH, media_type, hit['id'])
        elif media_type == 'video':
            path = '{}{}/{}.mp4'.format(config.APP_PATH, media_type, hit['id'])
        else:
            path = False
            print('WRONG MEDIA TYPE')

        if media_type == 'image':
            download(hit['largeImageURL'], hit['id'], path)
        elif media_type == 'video':
            download(re.search("(?P<url>https?://[^\s]+)", hit['videos']['large']['url']).group("url"), hit['id'], path)

        urls.append(path)

        if nr + 1 >= limit:
            break

    if len(urls) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text='No match for keyword "{}", please type an other keyword'.format(KEYWORD))
        return

    now = datetime.now()
    zip_file_name = '{}{}_{}_{}.zip'.format(config.APP_PATH, now.strftime('%Y%m%d%H%M%S'), KEYWORD, limit)
    create_zip_archive(zip_file_name, urls)

    return zip_file_name


def get_random_media(media_type, limit):
    urls = []
    filenames = next(walk(config.APP_PATH + media_type), (None, None, []))[2]  # [] if no file
    random.shuffle(filenames)
    for nr, filename in enumerate(filenames):
        urls.append(config.APP_PATH + media_type + '/' + filename)

        if nr + 1 >= limit:
            break

    now = datetime.now()
    zip_file_name = '{}{}_{}_{}.zip'.format(config.APP_PATH, now.strftime('%Y%m%d%H%M%S'), KEYWORD, limit)
    create_zip_archive(zip_file_name, urls)

    return zip_file_name


def create_zip_archive(zip_file_name, files):
    with ZipFile(zip_file_name, 'w') as zip_object:
        for file in files:
            if exists(file):
                zip_object.write(file, basename(file))


############################### Bot ############################################
def start(bot, update):
    query = "INSERT INTO images (text) VALUES (\"{}\")".format(update)
    MySQL().update(query)
    bot.message.reply_text(menu_4_message(), reply_markup=menu_4_keyboard())


def menu_main(bot, update):
    bot.callback_query.message.edit_text(menu_1_message(), reply_markup=menu_1_keyboard())


def menu_1_1(bot, update):
    menu_2(bot, update, 'image')


def menu_1_2(bot, update):
    menu_2(bot, update, 'video')


def menu_2(bot, update, media_type):
    global MEDIA_TYPE
    MEDIA_TYPE = media_type
    bot.callback_query.message.edit_text(menu_1_message(), reply_markup=menu_2_keyboard(media_type))


def menu_2_1(bot, update):
    bot.callback_query.message.edit_text(menu_2_1_message())


def menu_3(bot, update):
    bot.callback_query.message.edit_text(menu_3_message(), reply_markup=menu_3_keyboard())


def menu_3_1(bot, update):
    bot.callback_query.message.edit_text(menu_3_message(), reply_markup=menu_3_keyboard())


def menu_4(bot, update):
    bot.callback_query.message.edit_text(menu_4_message(), reply_markup=menu_4_keyboard())


def error(update, context):
    print(f'Update {update} caused error {context.error}')


def menu_1_keyboard():
    keyboard = [[InlineKeyboardButton('Download Images', callback_data='menu_1_1')],
                [InlineKeyboardButton('Download Videos', callback_data='menu_1_2')]]
    return InlineKeyboardMarkup(keyboard)


def menu_2_keyboard(media_type):
    keyboard = [
        [InlineKeyboardButton('Download Random ' + media_type.title() + 's', callback_data='menu_3')],
        [InlineKeyboardButton('Download ' + media_type.title() + 's by Keyword', callback_data='menu_2_1')],
        [InlineKeyboardButton('Go Back', callback_data='menu_main'), InlineKeyboardButton('Main Menu', callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)


def menu_2_1_keyboard():
    keyboard = [[InlineKeyboardButton('Type Keyword to search', callback_data='menu_3')]]
    return InlineKeyboardMarkup(keyboard)


def menu_3_keyboard():
    global MEDIA_TYPE
    keyboard = [
        [InlineKeyboardButton('Download Original ' + MEDIA_TYPE.title() + ' Size', callback_data='menu_4')],
        [InlineKeyboardButton('Resize ' + MEDIA_TYPE.title(), callback_data='menu_3_1')],
        [InlineKeyboardButton('Go Back', callback_data='menu_2'), InlineKeyboardButton('Main Menu', callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)


def menu_3_1_keyboard():
    keyboard = [[InlineKeyboardButton('Type new size w and h', callback_data='menu_4')]]
    return InlineKeyboardMarkup(keyboard)


def menu_4_keyboard():
    keyboard = [
        [InlineKeyboardButton('1', callback_data='one'), InlineKeyboardButton('5', callback_data='five'), InlineKeyboardButton('10', callback_data='ten')],
        [InlineKeyboardButton('20', callback_data='twenty'), InlineKeyboardButton('50', callback_data='fifty')],
        [InlineKeyboardButton('100', callback_data='hundred')]
        # [InlineKeyboardButton('Go Back', callback_data='menu_3'), InlineKeyboardButton('Main Menu', callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)


def menu_1_message():
    return 'Choose media type you need'


def menu_2_message():
    return 'Choose total number of files you need\nYou can type any keyword to search by2'


def menu_2_1_message():
    return 'Choose total number of files you need\nYou can type any keyword to search by2_1'


def menu_3_message():
    return 'Choose media size'


def menu_3_1_message():
    return 'Type new size you need(format: 720x640)'


def menu_4_message():
    return 'Choose total number of files you need\nYou can type any keyword to search by'


def final_link():
    return 'Zip Archive Link: '


def hello(update: Update, context: CallbackContext) -> None:
    # print(update)
    update.message.reply_text(f'Hello {update.effective_user.first_name}')

    query = "INSERT INTO images (text) VALUES (\"{}\")".format(update)
    MySQL().update(query)


def text(update, context):
    global KEYWORD, LIMIT
    KEYWORD = update.message.text
    process(update, context, LIMIT)

    query = "INSERT INTO images (text) VALUES (\"{}\")".format(update)
    MySQL().update(query)


def one(update: Update, context: CallbackContext) -> None:
    global LIMIT
    LIMIT = 1
    process(update, context, LIMIT)


def five(update: Update, context: CallbackContext) -> None:
    global LIMIT
    LIMIT = 5
    process(update, context, LIMIT)


def ten(update: Update, context: CallbackContext) -> None:
    global LIMIT
    LIMIT = 10
    process(update, context, LIMIT)


def twenty(update: Update, context: CallbackContext) -> None:
    global LIMIT
    LIMIT = 20
    process(update, context, LIMIT)


def fifty(update: Update, context: CallbackContext) -> None:
    global LIMIT
    LIMIT = 50
    process(update, context, LIMIT)


def hundred(update: Update, context: CallbackContext) -> None:
    global LIMIT
    LIMIT = 100
    process(update, context, LIMIT)


def process(update: Update, context: CallbackContext, limit) -> None:
    query = "INSERT INTO images (text) VALUES (\"{}\")".format(update)
    MySQL().update(query)
    if KEYWORD == 'random':
        zip_path = get_random_media(MEDIA_TYPE, limit)
    else:
        zip_path = get_media(update, context, KEYWORD, MEDIA_TYPE, 1, limit)

    with open(zip_path, "rb") as misc:
        upload_file = misc.read()

    now = datetime.now()

    filename = '{}_{}_{}_{}.zip'.format(KEYWORD.title().replace(' ', ''), MEDIA_TYPE.title(), limit, now.strftime('%Y%m%d%H%M%S'))

    if limit > 1:
        filename = '{}_{}_{}_{}.zip'.format(KEYWORD.title().replace(' ', ''), MEDIA_TYPE.title() + 's', limit, now.strftime('%Y%m%d%H%M%S'))

    file_size = os.path.getsize(zip_path) / 1000 / 1000

    if file_size > 50:
        # print(zip_path)
        # context.bot.send_message(chat_id=update.effective_chat.id, text="Zip Archive Link: \n" + zip_path)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Zip Archive too large, please fewer " + MEDIA_TYPE)
    else:
        updater.bot.send_document(chat_id=update.effective_user.id, document=upload_file, filename=filename)
        os.remove(zip_path)


def add_beauty_space(data, length=10):
    data = str(data)
    if len(data) < length:
        for i in range(1, length - len(data)):
            data = data + ' '

    return data


updater = Updater(config.TELEGRAM_BOT_TOKEN, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start))
# updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CallbackQueryHandler(menu_main, pattern='menu_main'))
updater.dispatcher.add_handler(CallbackQueryHandler(menu_1_1, pattern='menu_1_1'))
updater.dispatcher.add_handler(CallbackQueryHandler(menu_1_2, pattern='menu_1_2'))

updater.dispatcher.add_handler(CallbackQueryHandler(menu_2_1, pattern='menu_2_1'))
updater.dispatcher.add_handler(CallbackQueryHandler(menu_3, pattern='menu_3'))
updater.dispatcher.add_handler(CallbackQueryHandler(menu_3_1, pattern='menu_3_1'))
updater.dispatcher.add_handler(CallbackQueryHandler(menu_4, pattern='menu_4'))

updater.dispatcher.add_handler(CallbackQueryHandler(one, pattern='one'))
updater.dispatcher.add_handler(CallbackQueryHandler(five, pattern='five'))
updater.dispatcher.add_handler(CallbackQueryHandler(ten, pattern='ten'))
updater.dispatcher.add_handler(CallbackQueryHandler(twenty, pattern='twenty'))
updater.dispatcher.add_handler(CallbackQueryHandler(fifty, pattern='fifty'))
updater.dispatcher.add_handler(CallbackQueryHandler(hundred, pattern='hundred'))

updater.dispatcher.add_handler(MessageHandler(Filters.text, text))

updater.dispatcher.add_error_handler(error)

updater.start_polling()
