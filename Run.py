import webbrowser #todo
#webbrowser.open("http://localhost:8998")

from modules import httpd
from modules import database

database.connect()
httpd.run()
