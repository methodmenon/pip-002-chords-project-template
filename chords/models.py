import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from chords import app
from database import Base, engine, session

#song model --> create new class for Songs
class Song(Base):
	#give model a table name
	__tablename__ = "songs"

	#integer column
	id = Column(Integer, Sequence('song_id_sequence'), primary_key=True)
	#column specifying a 1-1 relationship with a file
	file_id = Column(Integer, ForeignKey('files.id'))

	def as_dictionary(self):
		file = session.query(File).filter_by(id=self.file_id).first()
		return {
			"id": self.id,
			"file": {
				"id": file.id,
				"name": file.filename
			}
		}

#file model --> create a new class for Files 
class File(Base):
	#give model a table name
	__tablename__ =  "files"

	#integer id column
	id = Column(Integer, Sequence('file_id_sequence'), primary_key=True)
	#string column for the filename
	filename = Column(String(1024))
	#backref from the 1-1 relationship with the Song 
	song = relationship("Song", backref="file")
	#how song is represented
	def __repr__(self):
		return "Instance of File Class (filename=%r)" % self.filename

	def as_dictionary(self):
		return {
			"id": self.id,
			"filename": self.filename,
			"path": url_for("uploaded_file", filename=self.filename)
		}

#create the table in the database
Base.metadata.create_all(engine)