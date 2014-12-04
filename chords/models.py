import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from chords import app
from database import Base, engine

#file model --> create a new class for Files 
class File(Base):
	#give model a table name
	__tablename__ =  "files"

	#integer id column
	id = Column(Integer, Sequence('file_id_sequence'), primary_key=True)
	#string column for the filename
	name = Column(String(1024))
	#backref from the 1-1 relationship with the Song 
	song = relationship("Song", backref="file")

	def as_dictionary(self):
		file = {
			"id": self.id,
			"name": self.name
		}

#song model --> create new class for Songs
class Song(Base):
	#give model a table name
	__tablename__ = "songs"

	#integer column
	id = Column(Integer, Sequence('song_id_sequence'), primary_key=True)
	#column specifying a 1-1 relationship with a file
	file = Column(Integer, ForeignKey('files.id'))

	def as_dictionary(self):
		song = {
			"id": self.id,
			"file": {
				"id": self.file.id,
				"name": self.file.name,
			}
		}

#create the table in the database
Base.metadata.create_all(engine)


