import time

current_user = ('poker4grig', "1")
presence_msg = {
    "action": "presence"
}

auth_msg = {
    "action": "authenticate"
}


def send_message(msg):
    if msg["action"] == 'presence':
        msg["time"] = time.time()
        msg["type"] = "online"
        msg.update({"user": {"account_name": current_user[0],
                             "status": "In contact"}})
    elif msg["action"] == 'authenticate':
        msg["time"] = time.time()
        msg["type"] = 'online'
        msg.update({"user": {"account_name": current_user[0],
                             "password": current_user[1]}})
    else:
        return None
    return msg

# presence_msg = {
#     "action": "presence",
#     "time": time.time(),
#     "type": "online",
#     "user": {
#         "account_name": "222",
#         "status": "In contact"
#     }
# }
# auth_msg = {
#     "action": "authenticate",
#     "time": time.time(),
#     "user": {
#         "account_name": current_user[0],
#         "password": current_user[1]
#     }
# }
