from flask import request
from database_setup import session, User

def authenticate(called_func):
    def wrap(*args, **kwargs):
        token = request.cookies.get('token')
        result = session.query(User).where(User.token == token).all()
        if result:
            user_id = result[0].id
        else:
            user_id = None
        return called_func(user_id, *args, **kwargs)

    wrap.__name__ = called_func.__name__
    return wrap
