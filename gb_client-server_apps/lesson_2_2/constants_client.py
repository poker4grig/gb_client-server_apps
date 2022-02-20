ADDR = '127.0.0.1'
PORT = 7777
TIMEOUT = 0.5

SIZE_OF_RECV = 4096
CURRENT_USER = ('poker4grig', "1")

AUTH_MSG = {
    "action": "authenticate"
}

RESPONSE_CODE_ALERT = {
    100: "basic notification ",
    101: "important notice",
    200: 'OK',
    201: "object created",
    202: "accepted",
    400: "wrong request/JSON object",
    401: "not authorized",
    402: "wrong login/password",
    403: "user forbidden",
    404: "user/chat is missing from the server",
    409: "there is already a connection with this login",
    410: "destination exists but is not available (offline)",
    500: "server error"
}
