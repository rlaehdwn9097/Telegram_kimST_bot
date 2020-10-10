# 웹에서 긁어서 리스트에 똑같이 넣고
# 디비 저장되어 있는 것 최근 하나 마지막 것을 가져온다.
# 비교해서 새로운 값들 있으면 SendMessage


# 비교는 디비 가장 최근 코멘트를 기준으로
# 웹에서 가져온 코멘트와 같아지는 인덱스를 찾고
# new_crawled_list_comment[0 : (찾은 인덱스)] 까지 웹에서 크롤링한 값을 SendMessage 하고
# SendMessage 한 갑들을 다시 DB에 넣어준다.
# 순서는 뒤에서부터 앞으로
# 왜냐하면 몽고디비가 순서를 따로 정하지 않기 때문에
# 아틀라스에 보기 좋게 늦은 시간부터 차례로 넣어줘야 마지막 값에는 가장 최근 값이 들어가기 때문

import telegram
import requests
import time
from pymongo import MongoClient
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_MONGODB_URL = os.getenv('TELEGRAM_MONGODB_URL')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def update():
    # 1. 디비에서 최신 값 가져오기.
    client = MongoClient(TELEGRAM_MONGODB_URL)
    db = client.telegram_bot_test
    collection = db['info']
    doc = collection.find()

    aje_list = doc[0]['aje_list']

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    id = TELEGRAM_CHAT_ID


    for k in range(len(aje_list)):
        #마지막 데이터 가져오기
        collection = db[aje_list[k]]
        doc = collection.find({}).sort("_id", -1)
        doc_content = doc[0]['content']
        doc_writer = doc[0]['writer']
        #print(doc_content)

        # 웹에서 크롤
        # 나중엔 아재들 리스트 만들어서 url 아재들 아이디 넣어줘야함
        # headers 같은 경우 Investing.com 에서 bot 으로 인식해서 그거 피하려면 넣어줘야함.
        #url = f'https://kr.investing.com/members/contributors/206724413/comments'

        url = f'https://kr.investing.com/members/{aje_list[k]}/comments'
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(url, headers = headers)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        # tag 찾고 원하는 데이터 값들 리스트 나눠서 넣어줌.
        search_tag = soup.select_one('#contentSection > div.arial_12.clear')
        search_list_stockName = search_tag.select('div > div > div > a')
        search_list_date = search_tag.select('div > div > div > span')
        search_list_content = search_tag.select('div > div > div > div.commentText')

        #bot = telegram.Bot(token='1057919117:AAGmpYjwHG2Tk9_bAz7ic-1f199Wy62_yEY')
        #id = -445817392

        # 가독성을 위해 리스트 하나 더 만듬. 필요없긴함.
        result_list_href =[]
        result_list_stockName =[]
        result_list_date =[]
        result_list_content = []

        for i,j in enumerate(search_list_content):
            """   1. 하이퍼링크, 2. 종목명, 3. 글쓴 날짜(뺌), 4. 내용   """
            # 1. 하이퍼링크
            #print("https://kr.investing.com"+search_list_stockName[i]['href'])
            result_list_href.append("https://kr.investing.com"+search_list_stockName[i]['href'])

            # 2. 종목 명
            #print(search_list_stockName[i].get_text())
            result_list_stockName.append(search_list_stockName[i].get_text())

            # 4. 댓글 내용
            # print(search_list_content[i].get_text())
            result_list_content.append(search_list_content[i].get_text())


        for i,j in enumerate(result_list_content):
            length = len(result_list_content)
            # 1,2,3 체크
            # 3,2,1 디비 저장
            if j == doc_content:
                #print("update 시작")
                i-=1
                #print("시작 인덱스 값 : ")
                #print(i)
                while(i >= 0):
                    #print("메세지 보냅니다")
                    # 메세지 보내고
                    bot.sendMessage(chat_id=id, text="=========================\n작성자 : " + doc_writer)
                    bot.sendMessage(chat_id=id, text="종목 명 : "+result_list_stockName[i])
                    bot.sendMessage(chat_id=id, text=result_list_href[i])
                    bot.sendMessage(chat_id=id, text=result_list_content[i]+"\n=========================")
                    time.sleep(5)
                    # 디비 저장하고
                    data = {
                        # 'date': result_list_date[len(result_list_date)-i-1],
                        'writer' : doc_writer,
                        'stockName': result_list_stockName[i],
                        'href': result_list_href[i],
                        'content': result_list_content[i]
                    }
                    collection = db[aje_list[k]]
                    result = collection.insert_one(data)
                    #db.test.insert_one(data)
                    i -= 1








