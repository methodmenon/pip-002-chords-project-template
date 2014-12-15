import os
from flask.ext.script import Manager
from chords.models import File
from chords.models import Song
from chords.database import session
from flask.ext.migrate import Migrate, MigrateCommand
from chords.database import Base


from chords import app

#create instance of Manager object
manager = Manager(app)

"""add command to the manager by by decorating a function with the manager.command decorator
name of function corresponds to name of argument which we give to manage script
ie: python manage.py run()"""
@manager.command
def run():
	#retreive port number from environment(if applicable) falling back on 8080 if it doesn't exist
	port = int(os.environ.get('PORT', 8080))
	#run development server, telling app to listen to the port designated
	app.run(host='0.0.0.0', port=port)

"""INITIALIZING MIGRATIONS
DB class designed to hold our metadata object.
Metada is used by Alembic to workout what the changes to our database schema should be. 
Helps us out with migrations. """
class DB(object):
	def __init__(self, metadata):
		self.metadata = metadata

#create instance of Flask-Migrate's Migrate class (passing in the app and an instance of the DB class)
migrate = Migrate(app, DB(Base.metadata))
#add all commands in Migrate class to our management script
manager.add_command('db', MigrateCommand)


"""At terminal run --> python manage.py db init
Initialize migrations by creating a folder called migrations 
which will store our migration scripts and configuration for Alembic"""

if __name__ == "__main__":
	manager.run()