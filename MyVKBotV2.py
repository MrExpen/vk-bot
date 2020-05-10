# -*- coding: utf-8 -*-
import vk_api
import time
from voids import parse_message
import config
from vk_api.longpoll import VkLongPoll, VkEventType

print('started at', time.strftime("%Y.%m.%d %H:%M:%S", time.localtime()))

def main():
    vk_session = vk_api.VkApi(token=config.TOKEN)
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                parse_message(event, vk_session)


if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print('\nKeyboardInterrupt at', time.strftime("%Y.%m.%d %H:%M:%S", time.localtime()))
            break
        except:
            print("Some error occurred at", time.strftime("%Y.%m.%d %H:%M:%S", time.localtime()))