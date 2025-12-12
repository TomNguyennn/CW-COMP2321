# Reverse-engineered opponent agent based on game1.txt analysis
# Black player strategy: aggressive captures, strategic positioning

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

def evaluate_position(board, player):
    """Simple evaluation function prioritizing material and captures"""
    score = 0
    opponent = board.players[1] if board.players[0] == player else board.players[0]
    
    # Material count
    for piece in board.get_player_pieces(player):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score += piece_value
    
    for piece in board.get_player_pieces(opponent):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score -= piece_value
    
    # Mobility bonus
    player_moves = len(list_legal_moves_for(board, player))
    opponent_moves = len(list_legal_moves_for(board, opponent))
    score += (player_moves - opponent_moves) * 5
    
    # Check bonus
    for piece in board.get_player_pieces(opponent):
        if piece.name.lower() == 'king':
            try:
                if hasattr(piece, 'is_in_check') and piece.is_in_check():
                    score += 100
            except:
                pass
    
    return score

def order_moves(board, player, moves):
    """Order moves: captures first (especially high-value), then by position"""
    scored_moves = []
    
    for piece, move in moves:
        score = 0
        
        dest = getattr(move, "position", None)
        if dest:
            # Check for captures - prioritize high-value captures
            for opp_piece in board.get_pieces():
                if opp_piece.player != player and opp_piece.position == dest:
                    capture_value = PIECE_VALUES.get(opp_piece.name.lower(), 0)
                    piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
                    # High bonus for capturing valuable pieces
                    score += capture_value * 20
                    # Small penalty for losing piece value
                    score -= piece_value * 0.1
                    break
        
        # Center control bonus
        if dest:
            center_distance = abs(dest.x - 2) + abs(dest.y - 2)
            score -= center_distance * 3
        
        scored_moves.append((score, piece, move))
    
    # Sort by score (highest first)
    scored_moves.sort(reverse=True, key=lambda x: x[0])
    return [(piece, move) for _, piece, move in scored_moves]

def minimax(board, depth, alpha, beta, maximizing_player, player, start_time, time_limit):
    """Minimax with alpha-beta pruning"""
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

def filter_repeated_moves(board, legal_moves, position_history, player):
    """Filter out moves that would lead to excessive repetitions"""
    filtered = []
    for piece, move in legal_moves:
        try:
            move.make()
            pos_hash = board.fen()
            reps = position_history.get(pos_hash, 0)
            
            # Avoid moves that would lead to 4+ repetitions
            if reps < 4:
                filtered.append((piece, move))
            move.undo()
        except:
            try:
                move.undo()
            except:
                pass
            continue
    return filtered if filtered else legal_moves

def agent(board, player, var):
    """
    Black opponent agent reverse-engineered from game1.txt
    Strategy: Aggressive captures, strategic positioning, avoid repetition
    """
    time_limit = getattr(var, 'thinking_time', 5.0) if hasattr(var, 'thinking_time') else var[1] if isinstance(var, list) else 5.0
    start_time = time.time()
    
    # Build position history to avoid repetition
    position_history = {}
    if hasattr(board, 'get_position_history'):
        for pos in board.get_position_history():
            position_history[pos] = position_history.get(pos, 0) + 1
    
    legal_moves = list_legal_moves_for(board, player)
    
    if not legal_moves:
        return None, None
    
    if len(legal_moves) == 1:
        return legal_moves[0]
    
    # Filter out moves causing excessive repetition
    legal_moves = filter_repeated_moves(board, legal_moves, position_history, player)
    
    # Order moves (captures first)
    legal_moves = order_moves(board, player, legal_moves)
    
    best_move = legal_moves[0]
    best_score = -float('inf')
    
    # Iterative deepening minimax
    for depth in range(1, 12): 
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
