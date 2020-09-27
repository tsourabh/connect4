from schema.models import Game
from config.config import *
from utils.utils import generate_string
from collections import defaultdict
from schema.validation import validate_game
from flask import Flask, jsonify, request
from flask.views import MethodView
import copy

initialize_db(app)
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Welcome to Connect4 API Service. Please Use Postman to use API'})


class StartGame(MethodView):

    @staticmethod
    def get():
        """
        creates new game
        :return: game_id
        """
        data = {}
        unique_id = generate_string()
        while True:
            exists = Game.objects(gameId=unique_id)
            if exists:
                unique_id = generate_string()
            else:
                break
        data['gameId'] = unique_id
        data['turn'] = 0
        data['board'] = [[None] * 7] * 6
        data['is_over'] = False
        data['winner'] = ''
        data['moves'] = []
        data = validate_game(data)
        if data['ok']:
            game = Game(**data['data']).save()
            game.save()
            return jsonify({'message': 'Game created successfully!', 'ok': True, 'gameId': game.gameId}), 200
        else:
            return jsonify({'message': str(data['message']), 'ok': False}), 400


class GameAPI(MethodView):
    """
    /api/game/<game_id>
    """

    def __init__(self):
        self.turn = 0
        self.rows = 6
        self.columns = 7
        self.board = [[None]*self.columns]*self.rows
        self.is_over = False
        self.winner = True
        self.moves = []
        self.COLORS_MAP = {
            0: "YELLOW",
            1: "RED"
        }
        self.REVERSE_MAP = {
            "YELLOW": 0,
            "RED": 1
        }

    @staticmethod
    def _get_game(game_id):
        res = Game.objects(gameId=game_id)
        game = defaultdict()
        if res:
            res = res[0]
            game['board'] = res['board']
            game['is_over'] = res['is_over']
            game['winner'] = res['winner']
            game['turn'] = res['turn']
            game['moves'] = res['moves']

            return game
        else:
            return False

    def _load_game(self, game):
        if not game:
            return False
        game = copy.deepcopy(game)
        self.turn = game.get('turn')
        self.board = game.get('board')
        self.is_over = game.get('is_over')
        self.winner = game.get('winner')
        self.moves = game.get('moves')
        return True

    def get(self, game_id):
        """
        get game
        :param game_id:
        :return: game_board
        """
        data = self._get_game(game_id)
        del data['board']
        return jsonify({
            'ok': True,
            'data': data
        })

    def _save_game(self, game_id):
        data = defaultdict()
        data['turn'] = self.turn
        data['board'] = self.board
        data['is_over'] = self.is_over
        data['winner'] = self.winner
        data['moves'] = self.moves
        game = Game.objects.get(gameId=game_id).update(**data)
        if game:
            return jsonify({'ok': True, 'game': game}), 200
        else:
            return jsonify({'ok': False, 'Message': game}), 400

    def _place_piece(self, column):
        if self.board[0][column] is None:
            flag = True
            for r in range(self.rows):
                if self.board[r][column] is not None:
                    flag = False
                    break
            if r == self.rows - 1 and flag:
                self.board[r][column] = self.turn
            else:
                self.board[r-1][column] = self.turn
            return r
        else:
            return False

    def _check_winner(self, tile):
        for x in range(self.columns):
            for y in range(self.rows):
                try:
                    if self.board[y][x] == tile and self.board[y][x + 1] == tile and self.board[y][x + 2] == tile and \
                            self.board[y][x + 3] == tile:
                        self.is_over = True
                        self.winner = self.COLORS_MAP[self.turn]
                        return True
                except IndexError:
                    pass
        return False

    def post(self, game_id):
        game = self._load_game(self._get_game(game_id))
        if not game:
            return jsonify({'ok': False, 'Message': 'Game not found'})
        if not self.is_over:

            body = request.get_json()
            color = str(body['turn']).upper()
            turn = self.REVERSE_MAP[color]
            if self.turn != turn:
                return jsonify({'ok': False, 'Message': f'Invalid Move. {self.COLORS_MAP[self.turn]}\'s turn'})
            else:
                column = int(body.get('column', None))
                if 0 <= column <= 6:
                    row = self._place_piece(column)
                    if row:
                        res = self._check_winner(self.turn)
                        self.moves.append({'turn': self.COLORS_MAP[self.turn], 'column': column})
                        this_turn = self.COLORS_MAP[self.turn]
                        self.turn = 1 - self.turn
                        self._save_game(game_id=game_id)
                        if res:
                            return jsonify({
                                'ok': True,
                                'Message': f'Congratulations, {this_turn} wins.',
                            })
                        return jsonify({
                            'ok': True,
                            'Message': f'{this_turn} placed at board[{row}][{column}]',
                        })
                    else:
                        return jsonify({'ok': False, 'Message': f'Column Full'})
                else:
                    return jsonify({'ok': False, 'Message': f'Invalid column Id'})
        else:
            return jsonify({'ok': False, 'Message': 'Game is over. Start a new game.', 'winner': f'{self.winner}'})


app.add_url_rule("/api/game/", view_func=StartGame.as_view("start_game"))
app.add_url_rule("/api/game/<game_id>", view_func=GameAPI.as_view("game_api"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(PORT))
