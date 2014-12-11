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
        songA = models.Song(file=models.File(name="songA.mp3"))
        songB = models.Song(file=models.File(name="songB.mp3"))
        songC = models.Song(file=models.File(name="songC.mp3"))
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
        self.assertEqual(songA["file"]["name"], "songA.mp3")

        songB = data[1]
        self.assertEqual(songB["id"], 2)
        self.assertEqual(songB["file"]["id"], 2)
        self.assertEqual(songB["file"]["name"], "songB.mp3")

        songC = data[2]
        self.assertEqual(songC["id"], 3)
        self.assertEqual(songC["file"]["id"], 3)
        self.assertEqual(songC["file"]["name"], "songC.mp3")

    def testGetSong(self):
        """getting a specific song by the song's id"""
        songA = models.Song(file=models.File(name="songA.mp3"))
        songB = models.Song(file=models.File(name="songB.mp3"))
        session.add_all([songA, songB])
        session.commit()

        response = self.client.get("/api/songs/{}".format(songB.id),
            headers=[("Accept", "application/json")]
            )
        data = json.loads(response.data)

        self.assertEqual(data["id"], 2)
        self.assertEqual(data["file"]["name"], "songB.mp3")

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
                "name": "songA.mp3"
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
        self.assertEqual(data["file"]["name"], "songA.mp3")

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)

        song = songs[0]
        self.assertEqual(song.id, 1)
        self.assertEqual(song.file.id, 1)
        self.assertEqual(song.file.name, "songA.mp3")

    def testSongEdit(self):
        """editing a song"""
        #add 3 songs to the database
        songA = models.Song(file=models.File(name="songA.mp3"))
        songB = models.Song(file=models.File(name="songB.mp3"))
        songC = models.Song(file=models.File(name="songC.mp3"))
        session.add_all([songA, songB, songC])
        session.commit()

        #edit song with new data
        data = {
            "file": {
                "id": 2,
                "name": "new songB.mp3"        
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
        self.assertEqual(data["file"]["name"], "new songB.mp3")

        #making sure 3 songs still exist in the database
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 3)

        songA = songs[0]
        self.assertEqual(songA.id, 1)
        self.assertEqual(songA.file.id, 1)
        self.assertEqual(songA.file.name, "songA.mp3")

        songB = songs[1]
        self.assertEqual(songB.id, 2)
        self.assertEqual(songB.file.id, 2)
        self.assertEqual(songB.file.name, "new songB.mp3")

        songC = songs[2]
        self.assertEqual(songC.id, 3)
        self.assertEqual(songC.file.id, 3)
        self.assertEqual(songC.file.name, "songC.mp3")

    def testUnsupportedAcceptHeader(self):
        response = self.client.get("/api/songs",
            headers = [("Accept", "application/xml")]
            )

        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data["message"], "Request must accept application/json data")

 ##add test for Invalid data
