from src import model
from src import database

db_filter = database.DatabaseFilter("username", "\"TEST_USER\"", "=")
user = model.User.load([db_filter])
print(user.username)
print(user.pass_hash)
