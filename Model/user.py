from flask_login import UserMixin


class User(UserMixin):

    slideID = {}
    pass


users = [
    {'id': '1', 'username': '1', 'password': '123456'},
    {'id': '2', 'username': '2', 'password': '123456'},
    {'id': '3', 'username': '3', 'password': '123456'},
    {'id': '4', 'username': '4', 'password': '123456'},
    {'id': '5', 'username': '5', 'password': '123456'},
    {'id': '6', 'username': '6', 'password': '123456'}
]


def query_user(user_name=None, user_id=None):
    for user in users:
        if user_name and user_name == user['username']:
            return user
        if user_id and user_id == user['id']:
            return user
    return None
