import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

import models
import decorators
import analysis
from chords import app
from database import session
from utils import upload_path


"""endpoint for returning a list of all the songs"""
@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
	songs = session.query(models.Song)
	songs = songs.all()

	"""return the list of songs as JSON"""
	data = json.dumps([song.as_dictionary() for song in songs])
	return Response(data, 200, mimetype="application/json")

"""endpoint for returning a single song"""
@app.route("/api/songs/<int:id>", methods=["GET"])
@decorators.accept("application/json")
def song_get(id):
	song = session.query(models.Song).get(id)

	if not song:
		message = "Could not find song with id {}".format(id)
		data = json.dumps({"message": message})
		return Response(data, 404, mimetype="application/json")

	data = json.dumps(song.as_dictionary())
	print ("data from song_get() is {}".format(data))
	return Response(data, 200, mimetype="application/json")



"""endpoint for adding a new song to the database"""
@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def song_post():
	data = request.json

	print("data from request.json in song_post() is {}".format(data))
	print ("data from ['file']['id'] is {}".format(data['file']['id']))
	print("session.query(models.File).get(data['file']['id']) is {}".format(session.query(models.File).get(data['file']['id'])))
	song = models.Song(file=session.query(models.File).get(data['file']['id']))
	session.add(song)
	session.commit()

	data = json.dumps(song.as_dictionary())
	headers = {"Location": url_for("song_get", id=song.id)}

	response_info = Response(data, 201, headers=headers, mimetype="application/json")
	print ("song_post response inf {}".format(response_info.data))
	return Response(data, 201, headers=headers, mimetype="application/json")

"""endpoint for editing a song"""
@app.route("/api/songs/<int:id>", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def song_edit(id):
	song = session.query(models.Song).filter(models.Song.id==id).first()
	data = request.json

	song.file.id = data["file"]["id"]
	song.file.filename = data["file"]["filename"]
	session.commit()

	data = json.dumps(song.as_dictionary())
	headers = {"Location": url_for("song_get", id=id)}

	return Response(data, 201, headers=headers, mimetype="application/json")

"""endpoint for accessing a file"""
@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
	"""
	end_from_directory function -> send a file from the given directory using send_file()
	where send_file()-> send contents of a file to a client, using the most efficient way possible
	"""
	return send_from_directory(upload_path(), filename)

"""endpoint for handling the file uploads"""
@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
	#try to access uploaded file from Flask's request.files dictionary
	file = request.files.get("file")
	if not file:
		data = {"message": "Could not find file data"}
		return Response(json.dumps(data), 422, mimetype="application/json")

	#secure_filename() --> function(from Werkzeug) which creates a safe version of the filename supplied by client
	filename = secure_filename(file.filename)
	#use the secure filename to create a File object and add it to the database and commit
	db_file = models.File(filename=filename)
	session.add(db_file)
	session.commit()
	#save file to an upload folder using our upload_path() function
	file.save(upload_path(filename))

	#return file information
	data = db_file.as_dictionary()
	print ("file data from file_post() is {}".format(data))
	return Response(json.dumps(data), 201, mimetype="application/json")