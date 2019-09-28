from app import create_app
from app import db

from app.models import User
from app.models import Organization
from app.models import Event

from config import TestConfig

from datetime import datetime, timedelta

import unittest
import requests
import json


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register(self):
        u1 = {"name": "pavel", "surname": "new", "email":"sorvihead@gmail.com", "password": "123"}
        u2 = {"name": "zheka", "surname": "bikov", "email":"sorvihead1@gmail.com", "password": "123"}
        u3 = {"name": "roma", "surname": "piskunov", "email":"sorvihead2@gmail.com", "password": "123"}
        u4 = {"name": "vika", "surname": "volokitina", "email":"sorvihead3@gmail.com", "password": "123"}
        user1 = User()
        user2 = User()
        user3 = User()
        user4 = User()
        user1.from_dict(u1, new_user=True)
        user2.from_dict(u2, new_user=True)
        user3.from_dict(u3, new_user=True)
        user4.from_dict(u4, new_user=True)

        data = {
            'id': None,
            'name': None,
            'surname': None,
            'bdate': None,
            'phone_number': None,
            'key_abilities': None,
            'education': None,
            'last_seen': None,
            'about_me': None,
            '_links': {
                'self': '123',
                'avatar': None
            }
        }

        db.session.add_all([user1, user2, user3, user4])
        db.session.commit()
        for user in User.query.all():
            data['id'] = user.id
            data['name'] = user.name
            data['surname'] = user.surname
            data['last_seen'] = user.last_seen.isoformat() + 'Z'
            dct_user = user.to_dict()
            data['_links']['avatar'] = dct_user['_links']['avatar']
            self.assertEqual(data, dct_user)

    def test_edit_profile(self):
        u1 = User(name='pavel', surname='wer', email='123')
        u1.set_password('123')
        u2 = User(name='pavel', surname='wer', email='1234')
        u2.set_password('123')
        u3 = User(name='pavel', surname='wer', email='1235')
        u3.set_password('123')
        db.session.add_all([u1, u2, u3])
        db.session.commit()

        data1 = {"surname": "new", "about_me": "lolollol"}
        data2 = {"phone_number": "+79997195330"}
        data3 = {"key_abilities": "english"}
        u1 = User.query.get(1)
        u2 = User.query.get(2)
        u3 = User.query.get(3)
        old_data1 = u1.to_dict()
        old_data2 = u2.to_dict()
        old_data3 = u3.to_dict()
        u1.from_dict(data1)
        u2.from_dict(data2)
        u3.from_dict(data3)
        old_data1['surname'] = 'new'
        old_data1['about_me'] = 'lolollol'
        old_data2['phone_number'] = '+79997195330'
        old_data3['key_abilities'] = 'english'
        print(old_data3, u3.to_dict())


        self.assertEqual(old_data1, u1.to_dict())
        self.assertEqual(old_data2, u2.to_dict())
        self.assertEqual(old_data3, u3.to_dict())


if __name__ == "__main__":
    unittest.main(verbosity=2)