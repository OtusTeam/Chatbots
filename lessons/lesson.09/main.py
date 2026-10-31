from db.session import SessionLocal
from models.genry import Genre
# from models.movie import Movie
# from models.review import Review


session = SessionLocal()
# new_genre = Genre(name="Мелодрама")
# session.add(new_genre)
# session.commit()
#
# session.refresh(new_genre)

genres = session.query(Genre).all()

for genre in genres:
    print(genre.id, genre.name)

session.close()


