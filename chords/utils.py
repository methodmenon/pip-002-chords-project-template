import os.path

from chords import app

"""
function for returning the path of where we want the file to exist
"""

def upload_path(filename=""):
    return os.path.join(app.root_path, app.config["UPLOAD_FOLDER"], filename)
