import os
import sys
import time
import unittest
from lesson_5.server_storage import action_presence, err_presence_response, \
    contact_list, check_request

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestActionPresence(unittest.TestCase):

    def setUp(self) -> None:
        self.request = {
            "action": "presence",
            "time": time.time(),
            "type": "online",
            "user": {
                "account_name": "222",
                "status": "In contact"
            }
        }

    def tearDown(self) -> None:
        pass

    def test_answer_is_not_none(self):
        """Проверяем, что функция action_presence возвращает ответ
        """
        test_1 = action_presence(self.request, contact_list)
        self.assertIsNotNone(test_1)

    def test_answer_in_bytes(self):
        """Проверяем, что возвращаемый ответ это байты
        """
        test_2 = action_presence(self.request, contact_list)
        self.assertIsInstance(test_2, bytes)

    def test_user_in_request(self):
        """Проверяем, что в результате функции получен не ответ об ошибке (400)
        """
        test_3 = action_presence(self.request, contact_list)
        self.assertIsNot(test_3, err_presence_response)

    def test_contact_list_update(self):
        """Проверяем, что если пользователя нет в листе контактов, то он
        добавится в этот лист
        """
        test_4 = action_presence(self.request, contact_list)
        self.assertIn(self.request["user"]["account_name"], contact_list)


class TestCheckRequest(unittest.TestCase):

    def setUp(self) -> None:
        self.request = {
            "action": "presence",
            "time": time.time(),
            "type": "online",
            "user": {
                "account_name": "222",
                "status": "In contact"
            }
        }
        self.bad_request = {
            "action": "bad",
            "time": time.time(),
            "type": "online",
            "user": {
                "account_name": "222",
                "status": "In contact"
            }
        }

    def tearDown(self) -> None:
        pass

    def test_check_is_not_none(self):
        """Проверяем, что функция check_request возвращает ответ
        """
        test_5 = check_request(self.request)
        self.assertIsNotNone(test_5)

    def test_check_is_none(self):
        """Проверяем, что функция check_request возвращает None
        """
        test_6 = check_request(self.bad_request)
        self.assertIsNone(test_6)


if __name__ == '__main__':
    unittest.main()
