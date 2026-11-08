from sqlalchemy import text
from db.session import engine


def main():
    with engine.connect() as connection:
        print("Успешное подключение")
        result = connection.execute(text("SELECT 1"))
        row = result.fetchone()
        print(row)


if __name__ == '__main__':

    main()