import random
import time
from extension.board_utils import list_legal_moves_for

PIECE_VALUES = {
    'pawn': 100,
    'knight': 320,
    'bishop': 330,
    'right': 500,  
    'queen': 900,
    'king': 20000
}

PAWN_TABLE = [
    [0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50],
    [10, 10, 20, 30, 10],
    [5,  5, 10, 25,  5],
    [0,  0,  0, 20,  0]
]

KNIGHT_TABLE = [
    [-50, -40, -30, -40, -50],
    [-40, -20,  0,   0, -40],
    [-30,  0,  10,  15, -30],
    [-40,  0,  15,  10, -40],
    [-50, -40, -30, -40, -50]
]

KING_TABLE = [
    [-30, -40, -40, -50, -30],
    [-30, -40, -40, -50, -30],
    [-30, -40, -40, -50, -30],
    [-20, -30, -30, -40, -20],
    [20,  20,   0,   0,  20]
]

def evaluate_position(board, player):

    score = 0
    opponent = board.players[1] if board.players[0] == player else board.players[0]
    
    for piece in board.get_player_pieces(player):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score += piece_value
        
        pos = piece.position
        if piece.name.lower() == 'pawn':
            if player.name == "white":
                score += PAWN_TABLE[pos.y][pos.x]
            else:
                score += PAWN_TABLE[4 - pos.y][pos.x]
        elif piece.name.lower() == 'knight':
            score += KNIGHT_TABLE[pos.y][pos.x]
        elif piece.name.lower() == 'king':
            score += KING_TABLE[pos.y][pos.x]
    
    for piece in board.get_player_pieces(opponent):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score -= piece_value
        
        pos = piece.position
        if piece.name.lower() == 'pawn':
            if opponent.name == "white":
                score -= PAWN_TABLE[pos.y][pos.x]
            else:
                score -= PAWN_TABLE[4 - pos.y][pos.x]
        elif piece.name.lower() == 'knight':
            score -= KNIGHT_TABLE[pos.y][pos.x]
        elif piece.name.lower() == 'king':
            score -= KING_TABLE[pos.y][pos.x]
    
    player_moves = len(list_legal_moves_for(board, player))
    opponent_moves = len(list_legal_moves_for(board, opponent))
    score += (player_moves - opponent_moves) * 10
    
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
    return [(piece, move) for _, piece, move in scored_moves]

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