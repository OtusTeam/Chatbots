from db.session import SessionLocal
from models.genry import Genre


session = SessionLocal()
new_genre = Genre(name="Мюзикл")

session.add(new_genre)
print(f" - {new_genre.id}: {new_genre.name}")

session.commit()

session.refresh(new_genre)

print(f" - {new_genre.id}: {new_genre.name}")

session.close()


