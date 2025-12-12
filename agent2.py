#improvement: enchanced and stop fivefold repetition 
#increase win rate by avoiding stalemate 

import random
import time
import math
from extension.board_utils import list_legal_moves_for, take_notes


opening_book = {
    'pawn3-2': ('pawn3', 'move2'),
}

PIECE_VALUES = {
    'pawn': 100,
    'knight': 320,
    'bishop': 330,
    'right': 500,  
    'queen': 2000,
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

postion_history = {}

pawn_table = [
    [50,  50,  50,  50,  50],
    [30, 30, 30, 30, 30],
    [20, 20, 30, 10, 10],
    [10,  10, 20, 10,  10],
    [0,  0,  0, 0,  0]
]

knight_table = [
    [-50, -40, -30, -40, -50],
    [-40, 5,  10,   5, -40],
    [-30,  10,  15,  10, -30],
    [-40,  5,  15,  5, -40],
    [-50, -40, -30, -40, -50]
]

right_table = [
    [-10,  -5,   0,  -5, -10],
    [ -5,  10,  15,  10,  -5],
    [  0,  15,  25,  15,   0],  
    [ -5,  10,  15,  10,  -5],
    [-10,  -5,   0,  -5, -10]

]
right_table = [
    [-10,  -5,   0,  -5, -10],
    [ -5,  10,  15,  10,  -5],
    [  0,  15,  25,  15,   0],  
    [ -5,  10,  15,  10,  -5],
    [-10,  -5,   0,  -5, -10]

]


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
    [-30, -20, -20, -20, -30],
    [-20, 10, 0, 10, -20],
    [-20, 0, 30, 0, -20],
    [-20, 10, 0, 10, -20],
    [-30, -10, -10, -10, -30]
]


def get_starting_material(board):
    for piece in board.get_pieces():
        if piece.players.name == "white":
            white_materials[piece.name.lower()] += 1
        else:
            black_materials[piece.name.lower()] += 1


def evaluate_position(board, player): 
    score = 0
    opponent = board.players[1] if board.players[0] == player else board.players[0]
    
    for piece in board.get_player_pieces(player):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score += piece_value
        
        pos = piece.position
        if piece.name.lower() == 'pawn':
            if player.name == "black":
                score += pawn_table[pos.y][pos.x]
                # Bonus for pawns close to promotion (row 0)
                if pos.y == 1:
                    score += 100  # One step from promotion
                elif pos.y == 2:
                    score += 50  # Two steps from promotion
            else:
                score += pawn_table[2 - pos.y][pos.x]
                # Bonus for pawns close to promotion (row 4)
                if pos.y == 3:
                    score += 100  # One step from promotion
                elif pos.y == 2:
                    score += 50  # Two steps from promotion
        elif piece.name.lower() == 'knight':
            score += knight_table[pos.y][pos.x]
        elif piece.name.lower() == 'king':
            score += king_table_start_game[pos.y][pos.x]
        elif piece.name.lower() == 'bishop':
            score += bishop_table[pos.y][pos.x]
        elif piece.name.lower() == 'right':
            score += right_table[pos.y][pos.x]
        elif piece.name.lower() == 'queen':
            score += queen_table[pos.y][pos.x]
    
    for piece in board.get_player_pieces(opponent):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score -= piece_value
        
        pos = piece.position
        if piece.name.lower() == 'pawn':
            if opponent.name == "black":
                score -= pawn_table[pos.y][pos.x]
                # Penalty for opponent pawns close to promotion (row 0)
                if pos.y == 1:
                    score -= 100  # One step from promotion
                elif pos.y == 2:
                    score -= 50  # Two steps from promotion
            else:
                score -= pawn_table[2 - pos.y][pos.x]
                # Penalty for opponent pawns close to promotion (row 4)
                if pos.y == 3:
                    score -= 100  # One step from promotion
                elif pos.y == 2:
                    score -= 50  # Two steps from promotion
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
        try:
            if hasattr(board, 'fen') and hasattr(board, 'get_position_history'):
                pos_hand = board.fen()
                history = board.get_position_history()
                repetition_count = history.count(pos_hand)
                if repetition_count >= 4:
                    score -= 800  
                elif repetition_count == 3:
                    score -= 400
                elif repetition_count == 2:
                    score -= 150
                elif repetition_count == 1:
                    score -= 30
        except: 
            pass
        
    
    return score

def order_moves(board, player, moves, position_history=None):

    scored_moves = []
    
    for piece, move in moves:
        score = 0
        
        # Check for pawn promotion moves - give huge bonus
        move_extra = getattr(move, 'extra', {})
        if move_extra.get('promote') == 'Queen':
            score += 10000  # Huge bonus for promotion
        
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

#no implementation 
def is_endgame(board):
    total_piece = 0
    for piece in board.get_pieces():
        if piece:
            total_piece += 1

    return total_piece <= 6

#havent used this function yet
#def update_postion_history(board, pos_his):
    pos_hash = board.fen()
    if pos_hash in pos_his:
        pos_his[pos_hash] += 1
    else:
        pos_his[pos_hash] = 1


#def evaluate_repetition(board, pos_his):
    count = 0
    score = evaluate_position(board, board.players[0])
    pos_hash = board.fen()
    repetition_count = pos_his.count(pos_hash)
    if repetition_count >= 3:
        score -= 500
    elif repetition_count == 2:
        score -= 200
    elif repetition_count == 1:
        score -= 50
    return score

#havent used this function yet

def endgame_evaluate_position(board, player):
    score = 0
    opponent = board.players[1] if board.players[0] == player else board.players[0]
    enemy_king_pos = None
    player_king_pos = None  # Fixed variable name
    
    for piece in board.get_player_pieces(opponent):
        if piece.name.lower() == 'king':
            enemy_king_pos = piece.position
            break
    
    for piece in board.get_player_pieces(player):
        if piece.name.lower() == 'king':
            player_king_pos = piece.position  # Fixed variable name
            break
    
    for piece in board.get_player_pieces(player):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score += piece_value
        
        pos = piece.position
        if piece.name.lower() == 'pawn':
            if player.name == "white":
                score += pawn_table[pos.y][pos.x]
                # Bonus for pawns close to promotion (row 0)
                if pos.y == 1:
                    score += 200  # One step from promotion
                elif pos.y == 2:
                    score += 100  # Two steps from promotion
            else:
                score += pawn_table[2 - pos.y][pos.x]
                # Bonus for pawns close to promotion (row 4)
                if pos.y == 3:
                    score += 200  # One step from promotion
                elif pos.y == 2:
                    score += 100  # Two steps from promotion
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
                # Penalty for opponent pawns close to promotion (row 0)
                if pos.y == 1:
                    score -= 200  # One step from promotion
                elif pos.y == 2:
                    score -= 100  # Two steps from promotion
            else:
                # Penalty for opponent pawns close to promotion (row 4)
                if pos.y == 3:
                    score -= 200  # One step from promotion
                elif pos.y == 2:
                    score -= 100  # Two steps from promotion
    
    player_moves = len(list_legal_moves_for(board, player))
    opponent_moves = len(list_legal_moves_for(board, opponent))
    score += (player_moves - opponent_moves) * 10   
    
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
def minimax(board, depth, alpha, beta, maximizing_player, player, start_time, time_limit, use_endgame=False):
    if time.time() - start_time > time_limit * 0.95:
        if use_endgame:
            return endgame_evaluate_position(board, player)
        return evaluate_position(board, player)
    
    if depth == 0:
        if use_endgame:
            return endgame_evaluate_position(board, player)
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
            move_made = False
            try:
                move.make()
                move_made = True
                
                eval_score = minimax(board, depth - 1, alpha, beta, False, player, start_time, time_limit, use_endgame)
                
                move.undo()
                move_made = False
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  
            except Exception as e:
                if move_made:
                    try:
                        move.undo()
                    except:
                        pass
                continue
        return max_eval
    else:
        min_eval = float('inf')
        for piece, move in legal_moves:
            move_made = False
            try:
                move.make()
                move_made = True
                
                eval_score = minimax(board, depth - 1, alpha, beta, True, player, start_time, time_limit, use_endgame)
                
                move.undo()
                move_made = False
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  
            except Exception as e:
                if move_made:
                    try:
                        move.undo()
                    except:
                        pass
                continue
        return min_eval

def filter_repeated_moves(board, legal_moves, position_history, player):
    """
    Filter out moves that would lead to 4+ repetitions (avoiding fivefold repetition).
    If all moves would cause repetition, return a random move to break the cycle.
    """
    filtered = []
    for piece, move in legal_moves:
        move_made = False
        try:
            move.make()
            move_made = True
            pos_hash = board.fen()
            # Check how many times this position has occurred
            reps = position_history.get(pos_hash, 0)
            
            # Strictly avoid moves that would lead to 4+ repetitions (fivefold repetition)
            if reps < 4:
                move.undo()
                move_made = False
                filtered.append((piece, move))
            # Only allow 4+ repetition moves if we're in a desperate situation (checkmate threat)
            else:
                move.undo()
                move_made = False
                # Check if we're in check - if so, we might need to accept repetition
                try:
                    if hasattr(piece, 'is_in_check') and piece.is_in_check():
                        # In check, might need to accept repetition to avoid checkmate
                        filtered.append((piece, move))
                except:
                    pass
        except Exception as e:
            # Always ensure move is undone if it was made
            if move_made:
                try:
                    move.undo()
                except:
                    pass
            continue
    
    # If all moves would cause 4+ repetitions, use random selection to break the cycle
    if not filtered:
        # Randomly select from all moves to break the repetition cycle
        if legal_moves:
            return [random.choice(legal_moves)]
        return legal_moves
    
    return filtered
#def fen(board, player):
#    fen_parts = []
#    for piece in board.get_player_pieces(player):
#        fen_parts.append(f"{piece.name[0].upper()}{piece.position.x}{piece.position.y}")
#    return ''.join(sorted(fen_parts))


#def log_board_position(board):
#    for piece in board.get_pieces():
#        pos_hash = fen(board, piece.player)
#        if pos_hash in postion_history:
#            postion_history[pos_hash] += 1
#        else:
            #postion_history[pos_hash] = 1

def agent(board, player, var):
    time_limit = getattr(var, 'thinking_time', 5.0)
    start_time = time.time()
    #take_notes(" " + fen(board, player) + "\n")

    position_history = {}
    for pos in board:
        position_history[pos] = position_history.get(pos, 0) + 1
    
    legal_moves = list_legal_moves_for(board, player)
    
    if not legal_moves:
        return None, None
    
    if len(legal_moves) == 1:
        return legal_moves[0]
    
    # Store original count before filtering
    original_move_count = len(legal_moves)
    
    # Filter out moves causing 5th repetition (strictly avoid 4+ repetitions)
    legal_moves = filter_repeated_moves(board, legal_moves, position_history, player)
    
    # If we had to use random selection to break repetition, return it immediately
    if len(legal_moves) == 1 and original_move_count > 1:
        # Check if this was a random selection to break repetition
        move_made = False
        try:
            test_move = legal_moves[0]
            test_move[1].make()
            move_made = True
            pos_hash = board.fen()
            reps = position_history.get(pos_hash, 0)
            test_move[1].undo()
            move_made = False
            if reps >= 4:
                # This was a random move to break repetition, return it
                return legal_moves[0]
        except:
            # Always ensure move is undone if exception occurred
            if move_made:
                try:
                    legal_moves[0][1].undo()
                except:
                    pass
    
    # Order moves with repetition penalties
    legal_moves = order_moves(board, player, legal_moves, position_history)
    
    best_move = legal_moves[0]
    best_score = -float('inf')
    
    # Check if we're in endgame
    use_endgame = is_endgame(board)
    
    for depth in range(1, 15): 
        if time.time() - start_time > time_limit * 0.75:  
            break
        
        current_best = best_move
        current_best_score = -float('inf')
        
        for piece, move in legal_moves:
            if time.time() - start_time > time_limit * 0.80:
                break
            
            move_made = False
            try:
                move.make()
                move_made = True
                
                score = minimax(board, depth - 1, -float('inf'), float('inf'), 
                              False, player, start_time, time_limit, use_endgame)
                
                move.undo()
                move_made = False
                
                if score > current_best_score:
                    current_best_score = score
                    current_best = (piece, move)
            except Exception as e:
                # Always ensure move is undone if exception occurred
                if move_made:
                    try:
                        move.undo()
                    except:
                        pass
                continue
        
        if time.time() - start_time < time_limit * 0.80:
            best_move = current_best
            best_score = current_best_score
    take_notes(best_move)
    return best_move

