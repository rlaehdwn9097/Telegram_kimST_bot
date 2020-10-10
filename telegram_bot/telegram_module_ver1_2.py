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

##  계속 쓰일 변수들 전역 변수 선언해 버림
##  나중에 class 화 진행하면서 넣어줘야함

##   전역변수들
##   몽고디비 기본적인 설정
client = MongoClient(TELEGRAM_MONGODB_URL)

db = client.telegram_bot_test

##   텔레그램 기본적인 설정
bot = telegram.Bot(token=TELEGRAM_TOKEN)
chat_id = TELEGRAM_CHAT_ID


def __init__():
    # 추후 아재들 아이디 값을 채팅창에서 추가할 수 있도록 할 것이기 때문에 (aje_list(main) 에 추가할 것)
    # 먼저 아재 리스트 아이디 값 추가된 건 없는 지 확인 후 (aje_list(main) 와 latest_aje_list(tmp) 를 비교한다.)
    # 추가된 게 없으면 그냥 지나가고
    # 있으면 추가된 아재들 DB 를 만들어 준다.
    # 그러면 update()를 진행하면서 아재들 댓글 업뎃을 볼 수 있다.

    # 추가된 아재들 있는 지 확인 -> 아재 리스트 업데이트 -> 새로오신 아재들 DB 만들어드리기
    update_new_aje_list()
    make_new_aje_DB()

def get_aje_list():
    global client
    global db
    collection = db['info']
    doc = collection.find()

    # 현재 아재 리스트
    aje_list = doc[0]['aje_list']

    return aje_list


def get_latest_aje_list():
    collection = db['info']
    doc = collection.find()

    # 현재 아재 리스트
    latest_aje_list = doc[0]['latest_aje_list']

    return latest_aje_list


def get_new_aje_list():
    ##   2020-10-10
    ##   나중엔 중복체크하는 것도 넣어야한다.
    ##   아재 리스트에 있는 아재도 다시 넣을 수 있기 떄문

    aje_list = get_aje_list()
    latest_aje_list = get_latest_aje_list()
    new_aje_list = []

    if len(aje_list) != len(latest_aje_list):
        for i in range(len(latest_aje_list), len(aje_list)):
            new_aje_list.append(aje_list[i])

    return new_aje_list


def update_new_aje_list():

    new_aje_list = get_new_aje_list()

    for k in range(len(new_aje_list)):
        db.info.update_one({}, {'$push': {'latest_aje_list': new_aje_list[k]}})


def get_webData_from_ajeId(aje_id):
    url = f'https://kr.investing.com/members/{aje_id}/comments'
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = requests.get(url, headers=headers)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    # tag 찾고 원하는 데이터 값들 리스트 나눠서 넣어줌.
    search_writer = soup.select_one('#contentSection > h1')
    search_tag = soup.select_one('#contentSection > div.arial_12.clear')
    search_list_stockName = search_tag.select('div > div > div > a')
    search_list_date = search_tag.select('div > div > div > span')
    search_list_content = search_tag.select('div > div > div > div.commentText')

    # 가독성을 위해 리스트 하나 더 만듬. 필요없긴함.
    result_writer = search_writer.get_text()
    # print(result_writer)
    result_list_href = []
    result_list_stockName = []
    result_list_date = []
    result_list_content = []

    for i, j in enumerate(search_list_content):
        """   1. 하이퍼링크, 2. 종목명, 3. 글쓴 날짜(뺌), 4. 내용   """
        # 1. 하이퍼링크
        # print("https://kr.investing.com"+search_list_stockName[i]['href'])
        result_list_href.append("https://kr.investing.com" + search_list_stockName[i]['href'])

        # 2. 종목 명
        # print(search_list_stockName[i].get_text())
        result_list_stockName.append(search_list_stockName[i].get_text())

        # 4. 댓글 내용
        # print(search_list_content[i].get_text())
        result_list_content.append(search_list_content[i].get_text())

    webData_from_ajeID = {
        'result_writer': result_writer,
        'result_list_stockName': result_list_stockName,
        'result_list_href': result_list_href,
        'result_list_content': result_list_content,
    }

    # print("보내는 webData : ")
    # print(webData_from_ajeID)

    return webData_from_ajeID


def get_firstDBData_from_ajeId(aje_id):
    collection = db[aje_id]
    doc = collection.find({}).sort("_id", -1)
    doc_content = doc[0]['content']
    doc_writer = doc[0]['writer']

    firstDBData_from_ajeId = {
        'writer': doc_writer,
        'content': doc_content
    }

    return firstDBData_from_ajeId

def make_new_aje_DB():
    new_aje_list = get_new_aje_list()

    for k in range(len(new_aje_list)):

        # get_webData_from_ajeId 함수로 부터 딕션어리를 리턴받는다.
        webData_from_ajeId = get_webData_from_ajeId(new_aje_list[k])
        length = len(webData_from_ajeId['result_list_content'])

        for i in range(length):
            # 몽고디비 아틀라스 sort 후 저장하고 싶은데 안되서 기냥 이렇게 함
            # 최근 데이터가 앞에 오기 때문에 pivot 을 찾은 뒤 거꾸로 디비에 저장함.

            data = {
                # 'date': result_list_date[len(result_list_date)-i-1],
                'writer': webData_from_ajeId['result_writer'],
                'stockName': webData_from_ajeId['result_list_stockName'][length - i - 1],
                'href': webData_from_ajeId['result_list_href'][length - i - 1],
                'content': webData_from_ajeId['result_list_content'][length - i - 1]
            }

            # Step 3: Insert data object directly into MongoDB via insert_one
            # result = db.test.insert_one(data)
            collection = db[new_aje_list[k]]
            result = collection.insert_one(data)
            # result = f'db.{var}.insert_one(data)'
            # Step 4: Print to the console the ObjectID of the new document
            print('Created {0} as {1}'.format(i + 1, result.inserted_id))

        # Step 5: Tell us that you are done
        print('finished inserting data')


def check_update():
    global bot
    global chat_id
    print("update 에 들어왔습니다.")
    for i in bot.getUpdates():
        print(i.message)

    # 1. 디비에서 최신 값 가져오기.
    global client
    db = client.telegram_bot_test
    collection = db['info']
    doc = collection.find()

    aje_list = doc[0]['aje_list']
    # print("update 에서 aje_list")
    # print(aje_list)

    for k in range(len(aje_list)):
        # 마지막 데이터 가져오기
        firstDBData = get_firstDBData_from_ajeId(aje_list[k])
        doc_content = firstDBData['content']
        doc_writer = firstDBData['writer']
        print(doc_writer)
        webData = get_webData_from_ajeId(aje_list[k])

        for i, j in enumerate(webData['result_list_content']):
            length = len(webData['result_list_content'])
            # 1,2,3 체크
            # 3,2,1 디비 저장
            if j == doc_content:
                # print("update 시작")
                i -= 1
                # print("시작 인덱스 값 : ")
                # print(i)
                while (i >= 0):
                    # print("메세지 보냅니다")
                    # 메세지 보내고
                    bot.sendMessage(chat_id=chat_id,
                                    text="=========================\n작성자 : " + webData['result_writer'])
                    bot.sendMessage(chat_id=chat_id, text="종목 명 : " + webData['result_list_stockName'][i])
                    bot.sendMessage(chat_id=chat_id, text=webData['result_list_href'][i])
                    bot.sendMessage(chat_id=chat_id,
                                    text=webData['result_list_content'][i] + "\n=========================")
                    time.sleep(5)
                    # 디비 저장하고
                    data = {
                        # 'date': result_list_date[len(result_list_date)-i-1],
                        'writer': webData['result_writer'],
                        'stockName': webData['result_list_stockName'][i],
                        'href': webData['result_list_href'][i],
                        'content': webData['result_list_content'][i]
                    }
                    collection = db[aje_list[k]]
                    result = collection.insert_one(data)
                    # db.test.insert_one(data)
                    i -= 1
