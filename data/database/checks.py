import json

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Check(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'checks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sum = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    userss = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    done = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def fill(self, text: str, sum: int, users: list, creator_id: int, payed=[]):
        self.text = text
        self.sum = sum
        self.userss = json.dumps(users)
        self.creator = creator_id
        self.done = json.dumps(payed)

    @property
    def users(self) -> list:
        return json.loads(self.userss)

    @property
    def payed(self) -> list:
        return json.loads(self.done)

    @payed.setter
    def payed(self, value: list):
        self.done = json.dumps(value)

    @property
    def part(self) -> int:
        return round(self.sum / len(self.users))

    def add_payed(self, user: int):
        prev = self.payed
        prev += [user]
        self.done = json.dumps(prev)
