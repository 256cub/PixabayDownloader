#!/usr/bin/python
import datetime
import os
import random
import re
from datetime import datetime
from os.path import exists

import requests
import config


def download(cycle, url, media_id, path):
    now = datetime.now()
    if exists(path):
        print('{} | {} | {} | {} | {}'.format(add_beauty_space(cycle), add_beauty_space(media_id), add_beauty_space('EXIST'), add_beauty_space(now.strftime('%Y-%m-%d %H:%M:%S')), url))
    else:
        result = requests.get(url).content
        with open(path, 'wb') as handler:
            handler.write(result)
            print('{} | {} | {} | {} | {}'.format(add_beauty_space(cycle), add_beauty_space(media_id), add_beauty_space('DOWNLOAD'), add_beauty_space(now.strftime('%Y-%m-%d %H:%M:%S')), url))


def get_media(keyword, page):
    urls = []
    media_type = 'image'

    url = config.PIXABAY_IMAGE_URL.format(config.PIXABAY_API, keyword, page, config.PIXABAY_LIMIT_PER_PAGE)
    print(url)

    response = requests.get(url)
    data = response.json()

    print('MATCH {} {}'.format(data['total'], media_type.title() + 's'))

    if not os.path.exists(media_type):
        os.makedirs(media_type)

    random.shuffle(data['hits'])

    for nr, hit in enumerate(data['hits']):

        path = '{}{}/{}/{}.jpg'.format(config.APP_PATH, media_type, keyword.replace(' ', '_'), hit['id'])

        # Check whether the specified path exists or not
        dir_path = '{}{}/{}'.format(config.APP_PATH, media_type, keyword.replace(' ', '_'))
        is_exist = os.path.exists(dir_path)
        if not is_exist:
            os.makedirs(dir_path)

        download(nr, hit['largeImageURL'], hit['id'], path)

        urls.append(path)


def add_beauty_space(data, length=10):
    data = str(data)
    if len(data) < length:
        for i in range(1, length - len(data)):
            data = data + ' '

    return data


KEYWORD = 'abstract'

for page in range(1, 7):
    get_media(KEYWORD,  page)

