import requests
import os
import math
import csv
import pandas as pd

from os.path import exists
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

parent_id = 'TODO'
rows = []
folders_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(parent_id)}).GetList()
for folder in folders_list:
    file_list = drive.ListFile({'q': "\'" + folder['id'] + "\'" + " in parents and trashed=false"}).GetList()
    for file in file_list:
        print('https://drive.google.com/uc?export=view&id={}'.format(file['id']))

        current = dict()
        current['keyword'] = folder['title']
        current['title'] = file['title']
        current['url'] = 'https://drive.google.com/uc?export=view&id={}'.format(file['id'])

        rows.append(current)


# with open('test.csv', 'w', newline='') as file:
#     mywriter = csv.writer(file, delimiter=',')
#     mywriter.writerows(rows)


df = pd.DataFrame(rows)
df.to_csv('links.csv')