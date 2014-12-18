import unittest
import os
import shutil
import json
from urlparse import urlparse
from StringIO import StringIO

# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "chords.config.TestingConfig"

from chords import app
from chords import models
from chords.utils import upload_path
from chords.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the chords API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())

    def testGetSongs(self):
        """getting a list of songs"""
        songA = models.Song(file=models.File(filename="songA.mp3"))
        songB = models.Song(file=models.File(filename="songB.mp3"))
        songC = models.Song(file=models.File(filename="songC.mp3"))
        session.add_all([songA, songB, songC])
        session.commit()

        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype,"application/json")

        data = json.loads(response.data)

        songA = data[0]
        self.assertEqual(songA["id"], 1)
        self.assertEqual(songA["file"]["id"], 1)
        self.assertEqual(songA["file"]["filename"], "songA.mp3")

        songB = data[1]
        self.assertEqual(songB["id"], 2)
        self.assertEqual(songB["file"]["id"], 2)
        self.assertEqual(songB["file"]["filename"], "songB.mp3")

        songC = data[2]
        self.assertEqual(songC["id"], 3)
        self.assertEqual(songC["file"]["id"], 3)
        self.assertEqual(songC["file"]["filename"], "songC.mp3")

    def testGetSong(self):
        """getting a specific song by the song's id"""
        songA = models.Song(file=models.File(filename="songA.mp3"))
        songB = models.Song(file=models.File(filename="songB.mp3"))
        session.add_all([songA, songB])
        session.commit()

        response = self.client.get("/api/songs/{}".format(songB.id),
            headers=[("Accept", "application/json")]
            )
        data = json.loads(response.data)

        self.assertEqual(data["id"], 2)
        self.assertEqual(data["file"]["filename"], "songB.mp3")

    def testGetNonExistentSong(self):
        """getting song which does not exist"""
        response = self.client.get("/api/songs/1",
            headers=[("Accept", "application/json")]
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data["message"], "Could not find song with id 1")

    def testSongPost(self):
        """adding a song"""
        data = {
            "file":
            {
                "id":1,
                "filename": "songA.mp3"
                }
        }

        response = self.client.post("/api/songs",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")

        self.assertEqual(urlparse(response.headers.get("Location")).path, "/api/songs/1")

        data = json.loads(response.data)
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["file"]["id"], 1)
        self.assertEqual(data["file"]["filename"], "songA.mp3")

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)

        song = songs[0]
        self.assertEqual(song.id, 1)
        self.assertEqual(song.file.id, 1)
        self.assertEqual(song.file.filename, "songA.mp3")

    def testSongEdit(self):
        """editing a song"""
        #add 3 songs to the database
        songA = models.Song(file=models.File(filename="songA.mp3"))
        songB = models.Song(file=models.File(filename="songB.mp3"))
        songC = models.Song(file=models.File(filename="songC.mp3"))
        session.add_all([songA, songB, songC])
        session.commit()

        #edit song with new data

        data = {
            "file": {
                "id": 2,
                "filename": "new songB.mp3"        
            }
        }

        response = self.client.post("/api/songs/{}".format(songB.id),
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
            )


        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,"/api/songs/2")


        data = json.loads(response.data)
        self.assertEqual(data["id"], 2)
        self.assertEqual(data["file"]["id"], 2)
        self.assertEqual(data["file"]["filename"], "new songB.mp3")

        #making sure 3 songs still exist in the database
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 3)

        songA = songs[0]
        self.assertEqual(songA.id, 1)
        self.assertEqual(songA.file.id, 1)
        self.assertEqual(songA.file.filename, "songA.mp3")

        songB = songs[1]
        self.assertEqual(songB.id, 2)
        self.assertEqual(songB.file.id, 2)
        self.assertEqual(songB.file.filename, "new songB.mp3")

        songC = songs[2]
        self.assertEqual(songC.id, 3)
        self.assertEqual(songC.file.id, 3)
        self.assertEqual(songC.file.filename, "songC.mp3")

    def testUnsupportedAcceptHeader(self):
        response = self.client.get("/api/songs",
            headers = [("Accept", "application/xml")]
            )

        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data["message"], "Request must accept application/json data")

    """test for Invalid data"""

    """test for adding a file to an upload folder and then accessing it via a HTTP request"""
    def test_get_uploaded_file(self):
        #get location where file will exist and create the file
        path = upload_path("test.txt")
        #write file contents
        with open(path, "w") as f:
            f.write("File contents")

        #response object created through the GET request to the new file
        response = self.client.get("/uploads/test.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(response.data, "File contents")

    """test for uploading a simple text file to the server"""
    def test_file_upload(self):
        #construct form as dictionary
        #use instance of Python's StringIO class to simulate a file object
        data = {
            "file": (StringIO("File contents"), "test.txt")
        }

        #send dictionary to api/files endpoint with content-type of multipart/form-data
        response = self.client.post("/api/files",
            data=data,
            content_type="multipart/form-data",
            headers=[("Accept", "application/json")]
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        #make sure response data points to a url where the file can be accessed
        self.assertEqual(urlparse(data["path"]).path, "/uploads/test.txt")

        #make sure the file has been saved correctly in the uploads folder
        path = upload_path("test.txt")
        self.assertTrue(os.path.isfile(path))
        with open(path) as f:
            contents = f.read()
        self.assertEqual(contents, "File contents")

