from chalice import Chalice
from chalice import BadRequestError
from random import choice
import re

# HELPER FILES
def validate_board(board):
    try:
        assert(len(board) == 9)
    except Exception:
        raise BadRequestError('Invalid board')
    return board

def empty_cells(board):
    empty_cells_iter = re.finditer(' ', board)
    empty_cells_list = [cell.start() for cell in empty_cells_iter]
    return empty_cells_list

def make_move(board):
    possible_moves = empty_cells(board)
    if possible_moves == []:
        return board
    random_move = int(choice(possible_moves))
    board = '{}{}{}'.format(
        board[:random_move], 'o', board[random_move+1:]
        )
    return board

# APPLICATION
app = Chalice(app_name='wavetictactoe')


@app.route('/')
def main():
    board = app.current_request.query_params.get('board')
    board = validate_board(board)
    board = make_move(board)
    return board
