from db.session import SessionLocal
from models.genry import Genre
# from models.movie import Movie
# from models.review import Review


session = SessionLocal()
# new_genre1 = Genre(name="Мюзикл")
# new_genre2 = Genre(name="Боевик")
# new_genre3 = Genre(name="Ужасы")
#
# session.add_all([new_genre1, new_genre2, new_genre3])
#
# session.commit()

print("Все жанры в базе: ")
genres = session.query(Genre).all()

for genre in genres:
    print(f" - {genre.id}: {genre.name}")

print()
print("Комедия в базе: ")
action_genres = session.query(Genre).filter_by(name="Comedy").first()
if action_genres is not None:
    print(f" - {action_genres.id}: {action_genres.name}")

session.close()


