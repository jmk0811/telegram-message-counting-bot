import configparser

def create_config():
    config = configparser.ConfigParser()
    
    config['bot_setup'] = {}
    config['bot_setup']['api_key'] = '<YOUR API KEY>'
    
    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)

create_config()