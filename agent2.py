#improvement: enchanced and stop fivefold repetition 
#increase win rate by avoiding stalemate 

import random
import time
import math
from extension.board_utils import list_legal_moves_for

PIECE_VALUES = {
    'pawn': 100,
    'knight': 320,
    'bishop': 330,
    'right': 500,  
    'queen': 900,
    'king': 4000 
}

white_materials = {
    'pawn': 0,
    'knight': 0,
    'bishop': 0,
    'right': 0,
    'queen': 0,
    'king': 0
}

black_materials = {
    'pawn': 0,
    'knight': 0,
    'bishop': 0,
    'right': 0,
    'queen': 0,
    'king': 0
}


pawn_table = [
    [0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50],
    [10, 10, 20, 30, 10],
    [5,  5, 10, 25,  5],
    [0,  0,  0, 20,  0]
]

knight_table = [
    [-50, -40, -30, -40, -50],
    [-40, 5,  10,   5, -40],
    [-30,  10,  15,  10, -30],
    [-40,  5,  15,  5, -40],
    [-50, -40, -30, -40, -50]
]

"""
    [-50, -40, -30, -40, -50],
    [-40, 5,  10,   5, -40],
    [-30,  10,  15,  10, -30],
    [-40,  5,  15,  5, -40],
    [-50, -40, -30, -40, -50]
"""
king_table_mid_game = [
    [-30, -40, -40, -50, -30],
    [-30, -40, -40, -50, -30],
    [-30, -40, -40, -50, -30],
    [-20, -30, -30, -40, -20],
    [20,  20,   0,   0,  20]
]

king_table_start_game = [
    [-50, -30, -20, -30, -50],
    [-30, -10, 0, -10, -30],
    [-30, 20, 40, 20, -30],
    [-30, 20, 30, 20, -30],
    [-50, -30, -20, -30, -50]
]

bishop_table = [
    [-20, -10, -10, -10, -20],
    [-10, 5, 0, 5, -10],
    [-10, 10, 0, 10, -10],
    [-10, 5, 0, 5, -10],
    [-20, -10, -10, -10, -20]
]

queen_table = [
    [-20, -10, -10, -10, -20],
    [-10, 0, 0, 0, -10],
    [-10, 0, 5, 0, -10],
    [-10, 0, 0, 0, -10],
    [-20, -10, -10, -10, -20]
]


def get_starting_material(board):
    for piece in board.get_pieces():
        if piece.players.name == "white":
            white_materials[piece.name.lower()] += 1
        else:
            black_materials[piece.name.lower()] += 1


def evaluate_position(board, player): #fix this function


    score = 0
    opponent = board.players[1] if board.players[0] == player else board.players[0]
    
    for piece in board.get_player_pieces(player):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score += piece_value
        
        pos = piece.position
        if piece.name.lower() == 'pawn':
            if player.name == "white":
                score += pawn_table[pos.y][pos.x]
            else:
                score += pawn_table[2 - pos.y][pos.x]
        elif piece.name.lower() == 'knight':
            score += knight_table[pos.y][pos.x]
        elif piece.name.lower() == 'king':
            score += king_table_start_game[pos.y][pos.x]
        elif piece.name.lower() == 'bishop':
            score += bishop_table[pos.y][pos.x]
        elif piece.name.lower() == 'right':
            score += bishop_table[pos.y][pos.x]
        elif piece.name.lower() == 'queen':
            score += queen_table[pos.y][pos.x]
    
    for piece in board.get_player_pieces(opponent):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score -= piece_value
        
        pos = piece.position
        if piece.name.lower() == 'pawn':
            if opponent.name == "white":
                score -= pawn_table[pos.y][pos.x]
            else:
                score -= pawn_table[2 - pos.y][pos.x]
        elif piece.name.lower() == 'knight':
            score -= knight_table[pos.y][pos.x]
        elif piece.name.lower() == 'king':
            score -= king_table_start_game[pos.y][pos.x]
        elif piece.name.lower() == 'bishop':
            score -= bishop_table[pos.y][pos.x]
        elif piece.name.lower() == 'right':
            score -= bishop_table[pos.y][pos.x]
        elif piece.name.lower() == 'queen':
            score -= queen_table[pos.y][pos.x]
    
    player_moves = len(list_legal_moves_for(board, player))
    opponent_moves = len(list_legal_moves_for(board, opponent))
    score += (player_moves - opponent_moves) * 10   #why?
    
    for piece in board.get_player_pieces(player):
        if piece.name.lower() == 'king':
            try:
                if hasattr(piece, 'is_in_check') and piece.is_in_check():
                    score -= 50
            except:
                pass
    
    for piece in board.get_player_pieces(opponent):
        if piece.name.lower() == 'king':
            try:
                if hasattr(piece, 'is_in_check') and piece.is_in_check():
                    score += 50
            except:
                pass
    
    return score

def order_moves(board, player, moves):

    scored_moves = []
    
    for piece, move in moves:
        score = 0
        
        dest = getattr(move, "position", None)
        if dest:
            for opp_piece in board.get_pieces():
                if opp_piece.player != player and opp_piece.position == dest:
                    score += PIECE_VALUES.get(opp_piece.name.lower(), 0) * 10
                    score -= PIECE_VALUES.get(piece.name.lower(), 0)
                    break
        
        if dest:
            center_distance = abs(dest.x - 2) + abs(dest.y - 2)
            score -= center_distance * 5
        
        scored_moves.append((score, piece, move))
    
    scored_moves.sort(reverse=True, key=lambda x: x[0])
    return [(piece, move) for _, piece, move in scored_moves] #explain this 

def is_endgame(board):
    total_piece = 0
    for piece in board.get_pieces():
        if piece:
            total_piece += 1

    return total_piece <= 6

def endgame_evaluate_position(board, player):
    score = 0
    opponent = board.players[1] if board.players[0] == player else board.players[0]
    enemy_king_pos = None
    player_king_pos = None
    for piece in board.get_player_pieces(opponent):
        if piece.name.lower() == 'king':
            enemy_king_pos = piece.position
            break
    for piece in board.get_player_pieces(player):
        if piece.name.lower() == 'king':
            our_king_pos = piece.position
            break
    
    for piece in board.get_player_pieces(player):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score += piece_value
        
        pos = piece.position
        if piece.name.lower() == 'pawn':
            if player.name == "white":
                score += pawn_table[pos.y][pos.x]
            else:
                score += pawn_table[2 - pos.y][pos.x]
        elif piece.name.lower() == 'knight':
            score += knight_table[pos.y][pos.x]
        elif piece.name.lower() == 'king':
            score += king_table_start_game[pos.y][pos.x]
        elif piece.name.lower() == 'bishop':
            score += bishop_table[pos.y][pos.x]
        elif piece.name.lower() == 'right':
            score += bishop_table[pos.y][pos.x]
        elif piece.name.lower() == 'queen':
            score += queen_table[pos.y][pos.x]

        
    
    for piece in board.get_player_pieces(opponent):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score -= piece_value
    
    player_moves = len(list_legal_moves_for(board, player))
    opponent_moves = len(list_legal_moves_for(board, opponent))
    score += (player_moves - opponent_moves) * 10   #why?
    
    for piece in board.get_player_pieces(player):
        if piece.name.lower() == 'king':
            try:
                if hasattr(piece, 'is_in_check') and piece.is_in_check():
                    score -= 50

                #our king distance to middle     
                if player_king_pos:
                    distance = math.sqrt((2 - player_king_pos.x) ** 2 + (2 - player_king_pos.y) ** 2)
                    score += distance * 10
            except:
                pass
    
    for piece in board.get_player_pieces(opponent):
        if piece.name.lower() == 'king':
            try:
                if hasattr(piece, 'is_in_check') and piece.is_in_check():
                    score += 50
                if enemy_king_pos:
                    distance = math.sqrt((2 - enemy_king_pos.x) ** 2 + (2 - enemy_king_pos.y) ** 2)
                    score -= distance * 10
            except:
                pass
    
    return score
def minimax(board, depth, alpha, beta, maximizing_player, player, start_time, time_limit):

    if time.time() - start_time > time_limit * 0.95:
        return evaluate_position(board, player)
    
    if depth == 0:
        return evaluate_position(board, player)
    
    current_player = player if maximizing_player else (
        board.players[1] if board.players[0] == player else board.players[0]
    )
    
    legal_moves = list_legal_moves_for(board, current_player)
    
    if not legal_moves:
        if maximizing_player:
            return -999999  
        else:
            return 999999   

    legal_moves = order_moves(board, current_player, legal_moves)
    
    if maximizing_player:
        max_eval = -float('inf')
        for piece, move in legal_moves:
            try:
                move.make()
                
                eval_score = minimax(board, depth - 1, alpha, beta, False, player, start_time, time_limit)
                
                move.undo()
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  
            except Exception as e:

                try:
                    move.undo()
                except:
                    pass
                continue
        return max_eval
    else:
        min_eval = float('inf')
        for piece, move in legal_moves:
            try:

                move.make()
                

                eval_score = minimax(board, depth - 1, alpha, beta, True, player, start_time, time_limit)
                

                move.undo()
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  
            except Exception as e:

                try:
                    move.undo()
                except:
                    pass
                continue
        return min_eval

"""
def my_minimax(board, depth, position, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_position(board, position)
    if maximizing_player:
        maxEval = -float('inf')
        for moves in list_legal_moves_for(board, position):
            eval = my_minimax(board, depth - 1, moves, False)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return maxEval

    else: 
        minEval = float('inf')
        for moves in list_legal_moves_for(board, position):
            eval = my_minimax(board, depth - 1, moves, True)
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return minEval
"""
    
def agent(board, player, var):
    time_limit = getattr(var, 'thinking_time', 5.0)
    start_time = time.time()
    
    legal_moves = list_legal_moves_for(board, player)
    
    if not legal_moves:
        return None, None
    
    if len(legal_moves) == 1:
        return legal_moves[0]
    
    legal_moves = order_moves(board, player, legal_moves)
    
    best_move = legal_moves[0]
    best_score = -float('inf')
    
    for depth in range(1, 15): 
        if time.time() - start_time > time_limit * 0.75:  
            break
        
        current_best = best_move
        current_best_score = -float('inf')
        
        for piece, move in legal_moves:
            if time.time() - start_time > time_limit * 0.80:
                break
            
            try:
                move.make()
                
                score = minimax(board, depth - 1, -float('inf'), float('inf'), 
                              False, player, start_time, time_limit)
                
                move.undo()
                
                if score > current_best_score:
                    current_best_score = score
                    current_best = (piece, move)
            except Exception as e:
                try:
                    move.undo()
                except:
                    pass
                continue
        
        if time.time() - start_time < time_limit * 0.80:
            best_move = current_best
            best_score = current_best_score
    
    return best_move