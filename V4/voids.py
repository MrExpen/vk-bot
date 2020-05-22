import vk_api
import random
import vk_api.keyboard
import time

def parse_message(event, vk_session):
    user = vk_session.method('users.get', {'user_id': event.user_id})[0]
    print(time.strftime("%Y.%m.%d %H:%M:%S", time.localtime()),
          "{0[first_name]} {0[last_name]}: {1.text}".format(user, event))
