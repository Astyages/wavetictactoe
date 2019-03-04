from chalice import Chalice
from chalice import BadRequestError
from random import choice
import re

# GLOBAL VARIABLES
SERVER = 'o'
PLAYER = 'x'


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

def determine_turn(board):
    possible_moves = empty_cells(board)
    server_moves = board.count(SERVER)
    player_moves = board.count(PLAYER)
    if abs(server_moves - player_moves) > 1:
        raise BadRequestError('Implausible board state')

    if len(possible_moves) == 9:
        # empty board, anyone can start
        return SERVER
    elif server_moves == player_moves:
        # plausibly server's turn:
        return SERVER
    elif server_moves > player_moves:
        return PLAYER
    elif server_moves < player_moves:
        return SERVER

def match_state(board):
    possible_moves = empty_cells(board)
    if possible_moves == []:
        # no more moves; draw
        return board, 'GAME OVER'

    server_board_eval = board.replace(SERVER, '1')
    player_board_eval = board.replace(PLAYER, '1')    
    winning_moves = [
        r'111......', r'...111...', r'......111',  # horizontal
        r'1..1..1..', r'.1..1..1.', r'..1..1..1',  # vertical
        r'1...1...1', r'..1.1.1..'  # diagonal
        ]
    server_board_eval = [re.search(move, server_board_eval) 
                         for move in winning_moves]
    server_board_eval = [True  
                         for move in server_board_eval 
                         if move is not None]
    player_board_eval = [re.search(move, player_board_eval)        
                         for move in winning_moves]
    player_board_eval = [True         
                         for move in player_board_eval
                         if move is not None]
    server_won = sum(server_board_eval) >= 1
    player_won = sum(player_board_eval) >= 1
    if server_won or player_won:
       return board, 'GAME OVER'
    
    return board, 'GAME ONGOING'

# APPLICATION
app = Chalice(app_name='wavetictactoe')


@app.route('/')
def main():
    board = app.current_request.query_params.get('board')
#    board = validate_board(board)
#    board = make_move(board)
    board = match_state(board)
    return board
