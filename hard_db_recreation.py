from data.database import db_session
from data.database.checks import Check
from data.database.groups import Group
from data.database.users import User

# Run this file if there are any problems with database

db_session.global_init('main.db')
sess = db_session.create_session()
sess.add(Group())
sess.add(User())
sess.add(Check())
sess.commit()
sess.delete(sess.query(Group).first())
sess.delete(sess.query(Check).first())
sess.delete(sess.query(User).first())
sess.commit()