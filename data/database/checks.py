"""
Module Documentation: check.py
This module contains the Check class, which is used to represent and manage check-related information in a database.
"""

import json
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Check(SqlAlchemyBase, SerializerMixin):
    """
    Class Check
    Represents a check in the database.

    Attributes:
        tablename (str): The name of the table in the database.
        id (sqlalchemy.Column): The unique identifier of the check (primary key).
        text (sqlalchemy.Column): The text description of the check.
        sum (sqlalchemy.Column): The sum of the check's amount.
        userss (sqlalchemy.Column): The JSON string representing the users associated with the check.
        done (sqlalchemy.Column): The JSON string representing the users who have paid the check.
        creator (sqlalchemy.Column): The ID of the check's creator.

    Methods:
        fill: Fills the check object with given data.
        users: Returns the list of users associated with the check.
        payed: Returns the list of users who have paid the check.
        add_payed: Adds a user to the list of users who have paid the check.
        part: Returns the calculated part of the check's sum divided by the number of users.
    """

    tablename = 'checks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sum = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    userss = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    done = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def fill(self, text: str, sum: int, users: list, creator_id: int, payed=[]):
        """
        Fills the check object with given data.

        Args:
            text (str): The text description of the check.
            sum (int): The sum of the check's amount.
            users (list): The list of users associated with the check.
            creator_id (int): The ID of the check's creator.
            payed (list, optional): The list of users who have paid the check. Defaults to an empty list.
        """
        self.text = text
        self.sum = sum
        self.userss = json.dumps(users)
        self.creator = creator_id
        self.done = json.dumps(payed)

    @property
    def users(self) -> list:
        """
        Getter method to retrieve the list of users associated with the check.

        Returns:
            list: The list of users associated with the check.
        """
        return json.loads(self.userss)

    @property
    def payed(self) -> list:
        """
        Getter method to retrieve the list of users who have paid the check.

        Returns:
            list: The list of users who have paid the check.
        """
        return json.loads(self.done)

    @payed.setter
    def payed(self, value: list):
        """
        Setter method to update the list of users who have paid the check.

        Args:
            value (list): The updated list of users who have paid the check.
        """
        self.done = json.dumps(value)

    @property
    def part(self) -> int:
        """
        Calculates and returns the part of the check's sum divided by the number of users.

        Returns:
            int: The calculated part of the check's sum divided by the number of users.
        """
        return round(self.sum / len(self.users))

    def add_payed(self, user: int):
        """
        Adds a user to the list of users who have paid the check.

        Args:
            user (int): The ID of the user to be added.
        """
        prev = self.payed
        prev += [user]
        self.done = json.dumps(prev)