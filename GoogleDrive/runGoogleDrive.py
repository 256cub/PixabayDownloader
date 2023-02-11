import requests
import os
import math

from os.path import exists
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
drive = GoogleDrive(gauth)


# keyword = input("Keyword to Search: ")

keywords = ['cryptocurrency', 'money', 'currency', 'blockchain', 'finance', 'coin', 'digital', 'business']

for keyword in keywords:

    parent_id = 'TODO'
    folder_id = False
    folders_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(parent_id)}).GetList()
    for folder in folders_list:
        if folder['title'] == keyword.capitalize():
            folder_id = folder['id']
            break

    if not folder_id:
        folder = drive.CreateFile({'title': keyword.capitalize(), 'parents': [{'id': parent_id}], 'mimeType': "application/vnd.google-apps.folder"})
        folder.Upload()
        folder_id = folder['id']

    url = "https://pixabay.com/api/?key=TODO&q=" + keyword + "&image_type=photo&orientation=horizontal"

    response = requests.get(url)

    data = response.json()
    print('TOTAL IMAGES: {}'.format(data['total']))

    # path = 'images/' + keyword
    path = 'images'
    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print("The new directory is created!")

    per_page = 200

    total_pages = int(math.ceil(data['total']/per_page))
    total = 0
    for page in range(1, total_pages + 1):

        url = "https://pixabay.com/api/?key=TODO&q=" + keyword + "&image_type=photo&orientation=horizontal&page={}&per_page={}".format(page, per_page)

        response = requests.get(url)
        data = response.json()

        for nr, hit in enumerate(data['hits']):
            total = total + 1
            path_to_file = '/PYTHON/PixabayDownloader/{}/{}.jpg'.format(path, hit['id'])
            file_exists = exists(path_to_file)

            if file_exists:
                print('{} | {} | {} | {} | {}'.format(total, nr, hit['id'], 'EXIST', hit['largeImageURL']))
            else:
                img_data = requests.get(hit['largeImageURL']).content
                with open(path_to_file, 'wb') as handler:
                    handler.write(img_data)
                    print('{} | {} | {} | {} | {}'.format(total, nr, hit['id'], 'DOWNLOADING', hit['largeImageURL']))

            file_list = drive.ListFile({'q': "\'" + folder_id + "\'" + " in parents and trashed=false"}).GetList()
            exist = False
            for file in file_list:
                if file['title'] == '{}.jpg'.format(hit['id']):
                    exist = True

            if not exist:
                gfile = drive.CreateFile({'parents': [{'id': folder_id}]})
                gfile.SetContentFile(path_to_file)
                gfile['title'] = '{}.jpg'.format(hit['id'])
                gfile.Upload()  # Upload the file.
