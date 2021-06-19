from flask_login import UserMixin


class User(UserMixin):
    def __init__(self):
        self.id = 'qwe'
        self.password = 123
        # self.id = information[0]
        # self.password = information[1]
        # self.email = information[2]
        # self.phone = information[3]

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @staticmethod
    def get(user_id):
        """try to return user_id corresponding User object.
        This method is used by load_user callback function
        """
        if not user_id:
            return None
        try:
            if user_id == 1:  # 最好从文件或数据库读取id（这里为简单写死为1了）
                return User()
        except:
            return None
        return None
