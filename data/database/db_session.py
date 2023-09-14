import sqlalchemy as sa
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = dec.declarative_base()

__factory = None

def global_init(db_file):
    global __factory

    import sqlite3
    with sqlite3.connect(f'{db_file}') as db:
        cursor = db.cursor()
        query = """CREATE TABLE IF NOT EXISTS users(id INTEGER, name TEXT,
         surname TEXT,
          username TEXT,
          alias TEXT,
          grouplimit INTEGER,
          groupss TEXT) """
        cursor.execute(query)
    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    #conn_str = os.environ.get('DATABASE_URL') or f'sqlite:///{db_file.strip()}?check_same_thread=False'
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)

def create_session() -> Session:
    global __factory
    return __factory()
