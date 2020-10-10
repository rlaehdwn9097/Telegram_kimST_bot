import telegram
import requests
import time
from pymongo import MongoClient
from bs4 import BeautifulSoup
import telegram_bot_makeDB as bot
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_MONGODB_URL = os.getenv('TELEGRAM_MONGODB_URL')


def latest_check():
    client = MongoClient(TELEGRAM_MONGODB_URL)
    db = client.telegram_bot_test
    collection = db['info']
    doc = collection.find()

    # 현재 아재 리스트
    aje_list = doc[0]['aje_list']

    # 추가된 건 없는 지 확인 후 담는 아재리스트
    latest_aje_list = doc[0]['latest_aje_list']

    # 추가된 아재 리스트
    new_aje_list =[]

    if(len(aje_list) != len(latest_aje_list)):
        for i in range(len(latest_aje_list), len(aje_list)):
            new_aje_list.append(aje_list[i])

    #print(new_aje_list)
    # DB 만들기
    bot.make_DB(new_aje_list)
    for k in range(len(new_aje_list)):

        # 아재들 업데이트
        db.info.update_one({}, {'$push': { 'latest_aje_list': new_aje_list[k]}})


