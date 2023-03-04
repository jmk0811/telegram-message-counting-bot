import telebot
import configparser

def run():
    try:
        config = configparser.ConfigParser()    
        config.read('config.ini', encoding='utf-8') 

        API_KEY = config['bot_setup']['api_key']
        bot = telebot.TeleBot(API_KEY)

        message_counts = {}
        count_flag = {}
        
        @bot.message_handler(commands=['start'])
        def start(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'administrator' or chat_member.status == "creator":
                bot.reply_to(message, "메세지 기록을 시작합니다.")
                message_counts.clear()
                count_flag[chat_id] = True
            else:
                bot.send_message(chat_id, "운영자가 아닙니다.")
                
        @bot.message_handler(commands=['end'])
        def end(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'administrator' or chat_member.status == "creator":
                bot.reply_to(message, "메세지 기록을 종료합니다.")
                count_flag[chat_id] = False
            else:
                bot.send_message(chat_id, "운영자가 아닙니다.")

        @bot.message_handler(commands=['show_msg_count'])
        def show_count(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            first_name = message.from_user.first_name or ""
            last_name = message.from_user.last_name or ""
            username = message.from_user.username or ""
            if (chat_id, user_id) in message_counts:
                count = message_counts[(chat_id, user_id)][0]
            else:
                count = 0

            bot.send_message(chat_id, f'{first_name} {last_name} {username} {user_id} The number of messages: {count}')
            
        @bot.message_handler(commands=['show_char_count'])
        def show_count(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            first_name = message.from_user.first_name or ""
            last_name = message.from_user.last_name or ""
            username = message.from_user.username or ""
            if (chat_id, user_id) in message_counts:
                count = message_counts[(chat_id, user_id)][1]
            else:
                count = 0

            bot.send_message(chat_id, f'{first_name} {last_name} {username} {user_id} The number of text: {count}')
            
        @bot.message_handler(commands=['rank'])
        def rank(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'administrator' or chat_member.status == "creator":
                rank = sorted(message_counts.items(), key=lambda x: x[1][1], reverse = True)
                rank = [x for x in rank if x[0][0] == chat_id]
                print(rank)
                length = len(rank)
                if length > 10: loop = 10
                else: loop = length
                for i in range(loop):
                    chat_member = bot.get_chat_member(message.chat.id, rank[i][0][1])
                    first_name = chat_member.user.first_name or ""
                    last_name = chat_member.user.last_name or ""
                    username = chat_member.user.username or ""
                    count = rank[i][1][1]
                    bot.send_message(chat_id, f'No.{i+1}: {first_name} {last_name} {username} {user_id} The number of text: {count}')
            else:
                bot.send_message(chat_id, "운영자가 아닙니다.")

        @bot.message_handler(commands=['help'])
        def help(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            bot.reply_to(message, "전 다음 명령어들을 지원합니다. \n /start \n /end \n /show_msg_count \n /show_char_count \n /rank \n /info \n /help \n /status")

        @bot.message_handler(commands=['info'])
        def info(message):
            bot.reply_to(message, "전 텔레그램 메세지 카운터 봇 입니다. 유저들의 메세지와 글자 수를 기록합니다.")

        @bot.message_handler(commands=['status'])
        def status(message):
            bot.reply_to(message, "봇이 작동중입니다.")
            
        @bot.message_handler(func=lambda message: True)
        def count_message(message):
            chat_id = message.chat.id
            if chat_id in count_flag and count_flag[chat_id]:
                user_id = message.from_user.id
                if (chat_id, user_id) in message_counts:
                    message_counts[(chat_id, user_id)][0] += 1
                    message_counts[(chat_id, user_id)][1] += len(message.text)
                else:
                    message_counts[(chat_id, user_id)] = [1, len(message.text)]
            
        print("Hey, I am up....")
        bot.polling()

        
    except Exception as e:
        print(e)
        run()
    
run()