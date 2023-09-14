import json

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from string import ascii_uppercase
import random
from data.config import max_users_in_group
from loader import session
from .users import User


def generate_keyword(len=10):
    return ''.join([random.choice(ascii_uppercase) for _ in range(len)])


class Group(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'groups'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    keyword = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    admin = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    userss = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    max_users = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def fill(self, admin, name, max_users=max_users_in_group):
        self.name = name
        self.keyword = generate_keyword()
        self.admin = admin
        self.userss = json.dumps([admin])
        self.max_users = max_users

    def add_user(self, user_id):
        users = json.loads(self.userss)
        users += [user_id]
        self.userss = json.dumps(users)

    @property
    def users(self):
        return json.loads(self.userss)

    @property
    def users_names(self):
        users = [user for user in session.query(User).all() if user.id in self.users]
        members = [user.name for user in users]
        return members
