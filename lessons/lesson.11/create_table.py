from db.session import engine, Base
from models.genre import Genre
from models.movie import Movie
from models.reviews import Review


if __name__ == '__main__':
    print('Creating tables...')
    Base.metadata.create_all(bind=engine)
    print('Tables created.')