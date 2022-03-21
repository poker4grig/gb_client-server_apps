import os
import sys
import time
import unittest
from lesson_2_7.common.variables import PRESENCE
from lesson_2_7.common.utils import send_message, get_message

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestSendMessage(unittest.TestCase):

    def setUp(self) -> None:
        self.good_msg = PRESENCE
        self.bad_msg = {
            "action": "bad",
            "time": time.time(),
            "user": {
                "account_name": 'sergey',
                "password": '123'
            }
        }
        self.check_user = {'action': 'presence',
                           'time': 1.1,
                           'type': "online",
                           'user': {'account_name': 'poker4grig',
                                    'status': 'In contact'}}

    def test_msg_is_not_none(self):
        """Проверяем, что сообщение сформировано
        """
        test1 = send_message(self.good_msg)
        self.assertIsNotNone(test1)

    def test_no_msg(self):
        """Проверяем, что сообщение не сформировано
        """
        test2 = send_message(self.bad_msg)
        self.assertIsNone(test2)

    def test_user_in_msg(self):
        """Проверяем, что поле "user" содержится в сообщении
        """
        test3 = send_message(self.good_msg)
        self.assertIn("user", test3)

    def test_correct_content(self):
        """Проверяем, что в сообщении содержатся корректные данные
        """
        test4 = send_message(self.good_msg)
        test4["time"] = 1.1
        self.assertEqual(test4, self.check_user)


if __name__ == '__main__':
    unittest.main()
