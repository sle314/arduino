from app.arduino import app
from app.settings import local as settings

def start(port=5000):
	app.debug = True
	app.template_folder = settings.TEMPLATE_FOLDER
	app.run(port = int(port))