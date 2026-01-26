from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.session import Base

#
# class BaseMovi(Base):
#     pass
# class Genre(BaseMovi):


class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    lang = Column(String)


    # movies = relationship("Movie", back_populates="genre")  # genre.movies
