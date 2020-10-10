import requests
import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# 나중엔 아재들 리스트 만들어서 url 아재들 아이디 넣어줘야함
# headers 같은 경우 Investing.com 에서 bot 으로 인식해서 그거 피하려면 넣어줘야함.
# url = f'https://kr.investing.com/members/contributors/206724413/comments'
# .env 파일 만들어서 
load_dotenv()
TELEGRAM_MONGODB_URL = os.getenv('TELEGRAM_MONGODB_URL')

def make_DB(new_aje_list):
    # new_aje_list 를 디비에서 비교해서 해야할 거 같다.


    for k in range(len(new_aje_list)):

        url = f'https://kr.investing.com/members/{new_aje_list[k]}/comments'
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

            """
            # 3. 글쓴 날짜 (datetime format 으로 가공)
            #print(search_list_date[i].get_text())
            
            ##   2020-10-08
            ##   원래는 이렇게 하려고 했는데 
            ##   가까운 일자는 1분 전, 10시간 전... 이렇게 표기되어서 
            ##   최근 남긴 댓글 시각은 datetime으로 바꾸기 어렵다.
            ##   날짜보다는 내용이 중요하니 일단은 빼도록 하겠다. 
            
            ##   2020-10-10
            ##   1분 전, 10시간 전, 이런 경우 현재 시각을 받아와서 
            ##   해당하는 시간을 빼주면 될 거 같은데 귀찮다 이말.
            
            ##   년도 : [0:4], 월 : [7:9], 일 :[10:12], 시 : [14:16], 분 : [17:19]   
            ##         예외사항 시간 같은 경우 한자리면 가공해줘야함 1:00 -> 01:00            
            #print("======datetime 형식으로 바꿈======")
        
            tmp_year = search_list_date[i].get_text()[0:4]
            tmp_month = search_list_date[i].get_text()[6:8]
            tmp_day = search_list_date[i].get_text()[10:12]
        
            if search_list_date[i].get_text()[15] == ':':
                tmp_hour = '0' + search_list_date[i].get_text()[14]
                tmp_min = search_list_date[i].get_text()[16:18]
        
            else:
                tmp_hour = search_list_date[i].get_text()[14:16]
                tmp_min = search_list_date[i].get_text()[17:19]
        
            tmp_datetime = tmp_year + '-' + tmp_month +'-' + tmp_day + ' ' +tmp_hour + ':' + tmp_min
            #print(datetime.datetime.strptime(tmp_datetime, '%Y-%m-%d %H:%M'))
            result_datetime = datetime.datetime.strptime(tmp_datetime, '%Y-%m-%d %H:%M')
            result_list_date.append(result_datetime)
            """

            # 4. 댓글 내용
            # print(search_list_content[i].get_text())
            result_list_content.append(search_list_content[i].get_text())

        client = MongoClient(TELEGRAM_MONGODB_URL)
        db = client.telegram_bot_test

        for i in range(len(result_list_content)):
            # 몽고디비 아틀라스 sort 후 저장하고 싶은데 안되서 기냥 이렇게 함

            data = {
                # 'date': result_list_date[len(result_list_date)-i-1],
                'writer': result_writer,
                'stockName': result_list_stockName[len(result_list_date) - i - 1],
                'href': result_list_href[len(result_list_date) - i - 1],
                'content': result_list_content[len(result_list_date) - i - 1]
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
