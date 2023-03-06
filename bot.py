import telebot
import configparser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import string

def run():
    try:
        config = configparser.ConfigParser()    
        config.read('config.ini', encoding='utf-8')

        API_KEY = config['bot_setup']['api_key']
        bot = telebot.TeleBot(API_KEY)

        cred = credentials.Certificate("./certificate.json")
        firebase_admin.initialize_app(cred,{
            "databaseURL" : config['bot_setup']['database_url']
        })

        db_ref = db.reference()

        message_counts = {}
        count_flag = {}
        
        @bot.message_handler(commands=['start'])
        def start(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'administrator' or chat_member.status == "creator":
                bot.reply_to(message, "Start message counting.")
                #message_counts.clear()
                #count_flag[chat_id] = True
                chat_ref = db_ref.child(str(chat_id))
                chat_ref.update({ "users": { user_id: { "msg_cnt": 0, "char_cnt": 0 } }, "count_flag": True })
            else:
                bot.send_message(chat_id, "You are not admin.")
                
        @bot.message_handler(commands=['end'])
        def end(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'administrator' or chat_member.status == "creator":
                bot.reply_to(message, "End message counting.")
                #count_flag[chat_id] = False
                chat_ref = db_ref.child(str(chat_id))
                chat_ref.update({ "count_flag": False })
            else:
                bot.send_message(chat_id, "You are not admin.")

        @bot.message_handler(commands=['show_msg_count'])
        def show_count(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            first_name = message.from_user.first_name or ""
            last_name = message.from_user.last_name or ""
            username = message.from_user.username or ""
            
            chat_ref = db_ref.child(str(chat_id))
            chat = chat_ref.get()
            if chat == None: return
            users_ref = chat_ref.child("users")
            user_ref = users_ref.child(str(user_id))
            user = user_ref.get()
            if user == None: count = 0
            else: count = user["msg_cnt"]

            bot.send_message(chat_id, f'{first_name} {last_name} {username} {user_id} The number of messages: {count}')
            
        @bot.message_handler(commands=['show_char_count'])
        def show_count(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            first_name = message.from_user.first_name or ""
            last_name = message.from_user.last_name or ""
            username = message.from_user.username or ""

            chat_ref = db_ref.child(str(chat_id))
            chat = chat_ref.get()
            if chat == None: return
            users_ref = chat_ref.child("users")
            user_ref = users_ref.child(str(user_id))
            user = user_ref.get()
            if user == None: count = 0
            else: count = user["char_cnt"]

            bot.send_message(chat_id, f'{first_name} {last_name} {username} {user_id} The number of text: {count}')
            
        @bot.message_handler(commands=['rank'])
        def rank(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'administrator' or chat_member.status == "creator":
                chat_ref = db_ref.child(str(chat_id))
                chat = chat_ref.get()
                if chat == None: return
                users_ref = chat_ref.child("users")
                users = users_ref.get()
                if users == None: return

                rank = sorted(users.items(), key=lambda x: x[1]["char_cnt"], reverse = True)
                length = len(rank)
                if length > 10: loop = 10
                else: loop = length
                print(rank)
                for i in range(loop):
                    chat_member = bot.get_chat_member(message.chat.id, rank[i][0])
                    first_name = chat_member.user.first_name or ""
                    last_name = chat_member.user.last_name or ""
                    username = chat_member.user.username or ""
                    count = rank[i][1]["char_cnt"]
                    bot.send_message(chat_id, f'No.{i+1}: {first_name} {last_name} {username} {user_id} The number of text: {count}')

            else:
                bot.send_message(chat_id, "You are not admin.")

        @bot.message_handler(commands=['help'])
        def help(message):
            bot.reply_to(message, "Following commands are supported: \n /start \n /end \n /show_msg_count \n /show_char_count \n /rank \n /info \n /help \n /status")

        @bot.message_handler(commands=['info'])
        def info(message):
            bot.reply_to(message, "Hello, I am a telegram message counting bot. I count and record the number of users' messages.")

        @bot.message_handler(commands=['status'])
        def status(message):
            bot.reply_to(message, "The bot is running.")
            
        @bot.message_handler(func=lambda message: True)
        def count_message(message):
            chat_id = message.chat.id
            user_id = message.from_user.id

            chat_ref = db_ref.child(str(chat_id))
            chat = chat_ref.get()

            if chat == None: return

            if chat["count_flag"]:
                users_ref = chat_ref.child("users")
                user_ref = users_ref.child(str(user_id))
                user = user_ref.get()

                cnt = 0
                for char in message.text:
                    if char in string.ascii_letters:
                        cnt += 1
                
                if user == None:
                    users_ref.update({ user_id: { "msg_cnt": 1, "char_cnt": cnt }})
                else:
                    new_msg_cnt = user["msg_cnt"] + 1
                    new_char_cnt = user["char_cnt"] + cnt
                    user_ref.update({ "msg_cnt": new_msg_cnt, "char_cnt": new_char_cnt })
            
        print("Hey, I am up....")
        bot.polling()

        
    except Exception as e:
        print(e)
        run()
    
run()