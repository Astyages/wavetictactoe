from chalice import Chalice
from chalice import BadRequestError
from random import choice
from math import inf 
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

def empty_spaces(board):
    empty_spaces_iter = re.finditer(' ', board)
    empty_spaces_list = [cell.start() for cell in empty_spaces_iter]
    return empty_spaces_list

def determine_turn(board):
    possible_moves = empty_spaces(board)
    server_moves = board.count(SERVER)
    player_moves = board.count(PLAYER)
    #if abs(server_moves - player_moves) > 1:
    #    raise BadRequestError('Implausible board state')

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
    possible_moves = empty_spaces(board)
    if possible_moves == []:
        # no more moves; draw
        return board, 'GAME OVER', 0

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
    if server_won:
        return board, 'SERVER WON', +1
    elif player_won:
        return board, 'PLAYER WON', -1
    
    return board, 'GAME ONGOING', 0

def minimax(board, depth, player):
    print(board)
    # worst scores
    if player == SERVER:
        best = [None, -inf]
    elif player == PLAYER:
        best = [None, +inf]
    
    board, game_state, score = match_state(board)
    if game_state != 'GAME ONGOING':
        final_score = score
        return [None, final_score]

    for space in empty_spaces(board):
        board = '{}{}{}'.format(
            board[:space], player, board[space+1:]
            )
        next_player = determine_turn(board)
        score = minimax(board, depth + 1, next_player)
        score[0] = space
        
        if player == SERVER:
            if score[1] > best[1]:
                best = score  
        elif player == PLAYER:
            if score[1] < best[1]:
                best = score  

    return best

def make_move(board):
    possible_moves = empty_spaces(board)
    if possible_moves == []:
        return board

    depth = len(board) - len(possible_moves)
    player = determine_turn(board)
    if player != SERVER:
        return board

    if depth == 0:
        move = choice(range(10))
    else:
        move = minimax(board, depth, player)
        move = move[0]

    board = '{}{}{}'.format(
        board[:move], SERVER, board[move+1:]
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
