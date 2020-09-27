from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError

game_schema = {
    "type": "object",
    "properties": {
        "gameId": {
            "type": "string"
        },
        "turn": {
            "type": "number",
        },
        "board": {
            "type": "array",
        },
        "is_over": {
            "type": "boolean"
        },
        "winner": {
            "type": "string"
        },
        "moves": {
            "type": "array"
        }
    },
    "additionalProperties": False
}


def validate_game(data):
    try:
        validate(data, game_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}
