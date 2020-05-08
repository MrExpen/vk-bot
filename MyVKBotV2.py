# -*- coding: utf-8 -*-
import vk_api
import db
from voids import parse_message
import config
from vk_api.longpoll import VkLongPoll, VkEventType

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
        except:
            print("Some other error occurred!")