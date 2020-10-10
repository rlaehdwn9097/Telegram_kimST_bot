from telegram_module_ver1_4 import kimST_bot as bot

if __name__ == "__main__":

    kimSTbot = bot()

    # init 은 추가된 아재 확인 후 디비 만드는 작업 (없으면 DB 안 만듬)
    # 나중에 채팅 기능 넣으면 명령어 받았을 때만 작동하도록 할 것
    kimSTbot.aje_list_update_check()

    # update 함수는 기존에 있는 아재 리스트를 확인 후
    # 아재들마다 web data 가 업데이트 된 건 없는 지 확인 후
    # 업데이트된 아재가 있으면 톡으로 알려주는 기능
    # 이건 주기적으로 실행할 예정
    kimSTbot.content_update_check()
