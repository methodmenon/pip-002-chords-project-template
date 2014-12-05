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

#endpoint for returning a list of all the songs
@app.route("/api/songs", methods=["GET"])
def songs_get():
	songs = session.query(models.Song)
	songs = songs.all()

	#return the list of songs as JSON
	data = json.dumps([song.as_dictionary() for song in songs])
	return Response(data, 200, mimetype="application/json")

#endpoint for returning a single song
@app.route("/api/song/<id:song_id>", methods=["GET"])
def song_get(song_id):
	song = session.query(models.Song).get(id)

	data = json.dumps(song.as_dictionary())
	return Response(data, 200, mimetype="application/json")


#endpoint for adding a new song to the database
@app.route("/api/songs", methods=["POST"])
	data = request.json

	song = models.Song(file_name=data["file_name"])
	session.add(song)
	session.commit()

	data = json.dumps(song.as_dictionary())
	headers = {"Location": url_for("song_get", id=song.id)}

	return Response(data, 201, headers=headers, mimetype="application/json")




