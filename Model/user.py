from flask_login import UserMixin


class User(UserMixin):
    pass


users = [
    {'id': '1', 'username': '1', 'password': '123456'},
    {'id': '2', 'username': '2', 'password': '123456'},
    {'id': '3', 'username': '3', 'password': '123456'},
    {'id': '4', 'username': '4', 'password': '123456'},
    {'id': '5', 'username': '5', 'password': '123456'},
    {'id': '6', 'username': '6', 'password': '123456'}
]


def query_user(user_name):
    for user in users:
        if user_name == user['username']:
            return user
