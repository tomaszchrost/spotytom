from src import model
from src import database

db_filter = database.DatabaseFilter("username", "\"tomaszchrost\"", "=")
user = model.User.load([db_filter])
user.init_lastfm()
