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
print()
print("Мультфильм в базе: ")
# genre = session.query(Genre).filter_by(name="Мультфильм").first()
genre = session.query(Genre).filter_by(name="NEW Mult").first()

print()
print(f" - {genre.id}: {genre.name}")

# UPDATE
# genre.name = "NEW Mult"
# session.commit()


# DELETE
session.delete(genre)
session.commit()


session.close()


