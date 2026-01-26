from db.session import SessionLocal
from models.genre import Genre
# from models.movie import Movie
# from models.reviews import Review

#
# session = SessionLocal()
# new_genre = Genre(name='Fantasy')
#
# session.add(new_genre)
# session.commit()
#
# session.refresh(new_genre)
#
# genres = session.query(Genre).all()
#
# for genre in genres:
#     print(genre.id, genre.name)
#
# session.close()


def main():
    session = SessionLocal()
    try:
        f_genre = session.query(Genre).filter_by(name='NEW GENRE').first()

        # # UPDATE
        # f_genre.name = 'NEW GENRE'
        # session.commit()

        # DELETE
        session.delete(f_genre)
        session.commit()


        # if f_genre is None:
        #     f_genre = Genre(name='Fantasy')
        #     session.add(f_genre)
        #     session.commit()
        #     session.refresh(f_genre)
        # new_movie = Movie(
        #     title = 'Matrix 2',
        #     year = 2010,
        #     description = 'Фантастический фильм о мирах',
        #     genre = f_genre,
        # )
        # session.add(f_genre)
        # session.commit()
        # session.refresh(new_movie)
        #
        # print('Создан фильм:')
        # print(f"  ID: {new_movie.id}")
        # print(f"  Название: {new_movie.title}")
        # print(f"  Жанр: {new_movie.genre.name}")

    finally:
        session.close()


if __name__ == '__main__':
    main()