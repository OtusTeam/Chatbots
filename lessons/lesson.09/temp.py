import sqlite3


conn = sqlite3.connect('temp.db')
cursor = conn.cursor()

cursor.execute("CREATE TABLE ...")
cursor.execute("INSERT INTO ...")
conn.commit()

cursor.execute("SELECT * FROM movie")
rows = cursor.fetchall()

conn.close()

=======================

movies = session.query(Movie).filter(Movie.year >= 2000).all()
for movie in movies:
    pass