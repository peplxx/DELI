import json

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from data.config import default_groups_limit

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    alias = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    grouplimit = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    groupss = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    # Payment info
    number = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    bank = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def fill(self, id, username, name, surname, alias,
             grouplimit=default_groups_limit, group=[]):
        self.id = id
        self.name = name
        self.surname = surname
        self.username = username
        self.alias = alias
        self.grouplimit = grouplimit
        self.groupss = json.dumps(group)
    def add_group(self, group_id):
        groups = json.loads(self.groupss)
        groups += [group_id]
        self.groupss = json.dumps(groups)

    @property
    def groups(self) -> list:
        return json.loads(self.groupss)

