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
        songA = models.Song(file_name=models.File(name="songA.mp3"))
        songB = models.Song(file_name=models.File(name="songB.mp3"))
        songC = models.Song(file_name=models.File(name="songC.mp3"))
        session.add_all([songA, songB, songC])
        session.commit()

        response = self.client.get("/api/songs")

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


