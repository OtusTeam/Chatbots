from db.session import Base, engine
from models.genry import Genre
from models.movie import Movie
from models.review import Review


if __name__ == '__main__':
    print("Создаем таблицы")
    Base.metadata.create_all(bind=engine)
    print("Создали таблицы")