class DevelopmentConfig(object):
    DATABASE_URI = "sqlite:///chords-development.db"
    DEBUG = True
    UPLOAD_FOLDER = "uploads"

class TestingConfig(object):
    DATABASE_URI = "sqlite://"
    DEBUG = True
    UPLOAD_FOLDER = "test-uploads"

"""
Config using Postgresql as our database instead of SQL from repo

class DevelopmentConfig(object):
	DATABASE_URI = "postgresql://vivek:math@localhost/vivek"
	DEBUG = True
	UPLOAD_FOLDER = "uploads"

class TestingConfig(object):
	DATABASE_URI = "postgresql://vivek:math@localhost/vivek"
	DEBUG = True
	UPLOAD_FOLDER = "test-uploads"

"""