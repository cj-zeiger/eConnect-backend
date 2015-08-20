from flask.ext.login import UserMixin

class User(UserMixin):
    username='admin'
    password='hashedpassword'
    id=1

    def check_password(pwd):
        if pwd == password:
            return True
        else:
            return False
