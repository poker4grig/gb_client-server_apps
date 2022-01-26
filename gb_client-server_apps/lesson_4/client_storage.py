import time

presence_msg = {
    "action": "presence",
    "time": time.time(),
    "type": "online",
    "user": {
        "account_name": "222",
        "status": "In contact"
    }
}

auth_msg = {
    "action": "authenticate",
    "time": time.time(),
    "user": {
        "account_name": "poker4grig",
        "password": "1"
    }
}
