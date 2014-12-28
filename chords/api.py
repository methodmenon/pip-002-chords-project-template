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
	songs = session.query(models.Song).all()

	"""return the list of songs as JSON"""
	data = json.dumps([song.as_dictionary() for song in songs])

	"""Following query and print statements is to view data 
	from both tables in the database
	files = session.query(models.File).all()
	file_data = json.dumps([file.as_dictionary() for file in files])
	#begin print statements
	print("songs_get data is {}".format(data))
	print ""
	print ""
	print("files info is {}".format(file_data))
	##end of print statements
	"""
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
	return Response(data, 200, mimetype="application/json")



"""endpoint for adding a new song to the database"""
@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def song_post():
	data = request.json
	song = models.Song(file_id=data['file']['id'])
	session.add(song)
	session.commit()

	"""Print outs to view how data looks during execution above
	print("print outs from song_post()")
	print("data from request.json in song_post() is {}".format(data))
	print ("data from ['file']['id'] is {}".format(data['file']['id']))
	print("session.query(models.File).get(data['file']['id']) is {}".format(session.query(models.File).get(data['file']['id'])))
	"""

	data = json.dumps(song.as_dictionary())
	headers = {"Location": url_for("song_get", id=song.id)}

	response_info = Response(data, 201, headers=headers, mimetype="application/json")

	#Print out to view how info above looks
	print ("final song_post response inf {}".format(response_info.data))
	
	return Response(data, 201, headers=headers, mimetype="application/json")

"""endpoint for editing a song"""
@app.route("/api/songs/<int:id>", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def song_edit(id):
	song = session.query(models.Song).get(id)

	if not song:
		message = "Could not find song with id {}".format(id)
		data = json.dumps({"message": message})
		return Response(data, 404, mimetype="application/json")

	song_file = session.query(models.File).filter_by(id=song.file_id).first()
	data = request.json
	song_file.filename = data["filename"]
	session.commit()

	"""Print outs to veiw how data looks during execution above
	print("print outs from song_edit()")
	print("Orig son file data is {}".format(song.as_dictionary()))
	print("Orig file data is {}".format(song_file.as_dictionary()))
	print("data from test is showing as {}".format(data))
	"""
	data = json.dumps(song.as_dictionary())

	"""Print out to see how data above looks
	print("song_edit() final response data")
	"""
	headers = {"Location": url_for("song_get", id=id)}

	return Response(data, 201, headers=headers, mimetype="application/json")

"""end point for deleting a song"""
@app.route("/api/songs/<int:id>/delete", methods=["GET", "POST"])
#@decorators.accept("application/json")
#@decorators.require("application/json")
def song_delete(id):
	song = session.query(models.Song).get(id)

	if not song:
		message = "Could not find song with id {}".format(id)
		data = json.dumps({"message":message})
		return Response(data, 404, mimetype="application/json")

	song_file = session.query(models.File).filter_by(id=song.file_id).first()
	print song_file.filename
	os.remove(upload_path(song_file.filename))
	session.delete(song_file)
	session.commit()

	message = "Song with id {} has been deleted".format(id)
	data = json.dumps({"message":message})
	return Response(data, 201, mimetype="application/json")


"""endpoint for audio analysis"""
@app.route("/api/songs/<int:id>/analysis")
#@decorators.accept("application/json")
#@decorators.require("application/json")
def song_analyze(id):
	#check wether a song with the correct ID exists
	song = session.query(models.Song).get(id)
	if not song:
		message = "Could not find song with id {}".format(id)
		data = json.dumps({"message": message})
		return Response(data, 404, mimetype="application/json")
	#get the filename of the song from the database
	song_file = session.query(models.File).filter_by(id=song.file_id).first()
	#save file to an upload folder using upload_path() function
	song_file_path = upload_path(song_file.filename)
	#call analyse function, passing in path of the uploaded file
	file_analysis = analysis.analyse(song_file_path)
	data = json.dumps(file_analysis)
	#return results of analysis function as a JSON object
	return Response(data, 201, mimetype="application/json")

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

	"""View how data above looks
	print ("file data from file_post() is {}".format(data))
	print ("")
	print("Response data is {}".format(json.dumps(data)))
	"""
	return Response(json.dumps(data), 201, mimetype="application/json")