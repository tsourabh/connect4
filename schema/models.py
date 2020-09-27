from config.config import database as db


class Game(db.Document):
    gameId = db.StringField(required=True, unique=True)
    turn = db.IntField()
    board = db.ListField()
    is_over = db.BooleanField()
    winner = db.StringField()
    moves = db.ListField()
