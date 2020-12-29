import yaml
from pytelelogger.telelogger import TeleLogger

if __name__ == '__main__':
    with open('cfg.yaml', 'r') as f:
        data = yaml.safe_load(f)

    tl = TeleLogger(data['token'], data['user_name'])

    print(data)
