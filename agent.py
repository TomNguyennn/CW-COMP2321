#improvement: enchanced and stop fivefold repetition 
#increase win rate by avoiding stalemate 

import random
import time
import math
from extension.board_utils import list_legal_moves_for, take_notes, copy_piece_move

PIECE_VALUES = {
    'pawn': 70, #100
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

right_table = [
    [-10,  -5,   0,  -5, -10],
    [ -5,  10,  15,  10,  -5],
    [  0,  15,  25,  15,   0],  
    [ -5,  10,  15,  10,  -5],
    [-10,  -5,   0,  -5, -10]

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
    [-30, 5, 5, 5, -30],
    [-20, 5, 5, 5, -20],
    [20,  0,   0,   0,  20]
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
    [-50, -10, -10, -10, -50],
    [-50, 0, 0, 0, -50],
    [-50, 5, 10, 5, -50],
    [-50, 0, 0, 0, -50],
    [-50, -10, -10, -10, -50]
]


def get_starting_material(board):
    for piece in board.get_pieces():
        if piece.players.name == "white":
            white_materials[piece.name.lower()] += 1
        else:
            black_materials[piece.name.lower()] += 1
#approve
def get_current_material(board, player):
    """Count current material for a player"""
    material = {
        'pawn': 0,
        'knight': 0,
        'bishop': 0,
        'right': 0,
        'queen': 0,
        'king': 0
    }
    for piece in board.get_player_pieces(player):
        piece_name = piece.name.lower()
        if piece_name in material:
            material[piece_name] += 1
    return material
#approve 
def is_piece_under_attack(board, piece, opponent):
    """Check if a piece is under attack by opponent pieces"""
    try:
        piece_pos = piece.position
        opponent_moves = list_legal_moves_for(board, opponent)
        for opp_piece, move in opponent_moves:
            dest = getattr(move, "position", None)
            if dest and dest == piece_pos:
                return True
        return False
    except:
        return False

def simulate_move(board, piece, move):
    """Clone the board and apply the move, returning (temp_board, moved_piece)."""
    try:
        temp_board = board.clone()
        temp_board, temp_piece, temp_move = copy_piece_move(temp_board, piece, move)
        if not temp_piece or not temp_move:
            return None, None
        temp_piece.move(temp_move)
        return temp_board, temp_piece
    except Exception:
        return None, None

def get_attacked_squares(board, opponent):
    """Return set of (x,y) squares attacked by opponent."""
    attacked = set()
    for _, mv in list_legal_moves_for(board, opponent):
        dest = getattr(mv, "position", None)
        if dest:
            attacked.add((dest.x, dest.y))
    return attacked

def king_in_check(board, player):
    """Determine if player's king is attacked by opponent."""
    opponent = board.players[1] if board.players[0] == player else board.players[0]
    attacked = get_attacked_squares(board, opponent)
    for piece in board.get_player_pieces(player):
        if piece.name.lower() == 'king':
            return (piece.position.x, piece.position.y) in attacked
    return False

def get_all_endangered_pieces(board, player, opponent):
    """Get all pieces that are currently under attack, sorted by value (most valuable first)
    
    Returns a list of (piece, piece_value) tuples for all pieces under attack.
    This includes ALL pieces, not just important ones, so we can save any piece from capture.
    """
    endangered = []
    for piece in board.get_player_pieces(player):
        if is_piece_under_attack(board, piece, opponent):
            piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
            endangered.append((piece, piece_value))
    # Sort by value (most valuable first) so we prioritize saving more important pieces
    endangered.sort(key=lambda x: x[1], reverse=True)
    return endangered

def does_move_save_endangered_piece(board, move, endangered_piece, opponent):
    """Check if a move saves an endangered piece by moving it to a safe position"""
    dest = getattr(move, "position", None)
    if not dest:
        return False
    temp_board, temp_piece = simulate_move(board, endangered_piece, move)
    if not temp_board or not temp_piece:
        return False
    attacked = get_attacked_squares(temp_board, opponent)
    return (temp_piece.position.x, temp_piece.position.y) not in attacked

def evaluate_position(board, player): #fix this function
    score = 0
    opponent = board.players[1] if board.players[0] == player else board.players[0]
    player_in_check = king_in_check(board, player)
    opponent_in_check = king_in_check(board, opponent)
    
    # Material tracking - use material counters for evaluation
    player_material = get_current_material(board, player)
    opponent_material = get_current_material(board, opponent)
    
    # Material advantage evaluation (additional to piece values below)
    # This gives us a material-based score component
    for piece_type in PIECE_VALUES:
        material_diff = player_material[piece_type] - opponent_material[piece_type]
        if material_diff != 0:
            # Small bonus/penalty for material advantage
            score += material_diff * PIECE_VALUES[piece_type] * 0.1
    
    for piece in board.get_player_pieces(player):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score += piece_value
        
        pos = piece.position
        if piece.name.lower() == 'pawn':
            if player.name == "white":
                score += pawn_table[pos.y][pos.x]
                if pos.y == 1:
                    score += 500  # one step from promotion
                elif pos.y == 2:
                    score += 200  # two steps from promotion
            else:
                score += pawn_table[2 - pos.y][pos.x]
                if pos.y == 3:
                    score += 500  # one step from promotion
                elif pos.y == 2:
                    score += 200  # two steps from promotion
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
        
        # Piece safety evaluation - if important piece is under attack, penalize
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        if piece_value >= 500:  # Important pieces: rook, queen, king
            if is_piece_under_attack(board, piece, opponent):
                # Penalty for having important piece under attack
                score -= piece_value * 0.3  # 30% penalty for being attacked
    
    for piece in board.get_player_pieces(opponent):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score -= piece_value
        
        pos = piece.position
        if piece.name.lower() == 'pawn':
            if opponent.name == "white":
                score -= pawn_table[pos.y][pos.x]
                # Penalty for opponent pawns close to promotion
                if pos.y == 1:
                    score -= 500  # One step from promotion - huge penalty
                elif pos.y == 2:
                    score -= 200  # Two steps from promotion
            else:
                score -= pawn_table[2 - pos.y][pos.x]
                # Penalty for opponent pawns close to promotion
                if pos.y == 3:
                    score -= 500  # One step from promotion - huge penalty
                elif pos.y == 2:
                    score -= 200  # Two steps from promotion
        elif piece.name.lower() == 'knight':
            score -= knight_table[pos.y][pos.x]
        elif piece.name.lower() == 'king':
            score -= king_table_start_game[pos.y][pos.x]
        elif piece.name.lower() == 'bishop':
            score -= bishop_table[pos.y][pos.x]
        elif piece.name.lower() == 'right':
            score -= right_table[pos.y][pos.x]
        elif piece.name.lower() == 'queen':
            score -= queen_table[pos.y][pos.x]
    
    player_moves = len(list_legal_moves_for(board, player))
    opponent_moves = len(list_legal_moves_for(board, opponent))
    score += (player_moves - opponent_moves) * 10  
    
    if player_in_check:
        score -= 100
    if opponent_in_check:
        score += 100 #just fixed

        try:
            pass
        except: 
            pass
        
    
    return score

def order_moves(board, player, moves):
    """Order moves with safety evaluation - avoid moves that endanger pieces"""
    scored_moves = []
    opponent = board.players[1] if board.players[0] == player else board.players[0]
    
    # Get all currently endangered pieces (before any moves)
    endangered_pieces = get_all_endangered_pieces(board, player, opponent)
    
    for piece, move in moves:
        score = 0
        
        dest = getattr(move, "position", None)
        
        # 1. PAWN PROMOTION - Highest priority (huge bonus)
        if piece.name.lower() == 'pawn':
            move_extra = getattr(move, 'extra', {})
            if move_extra.get('promote') == 'Queen' or (hasattr(move, 'promote') and getattr(move, 'promote') == 'Queen'):
                score += 10000  # Promotion to queen - massive bonus
            # Also check by position (backup method)
            elif dest:
                if player.name == "white" and dest.y == 0:  # White promotes at row 0
                    score += 10000
                elif player.name == "black" and dest.y == 4:  # Black promotes at row 4
                    score += 10000
        
        # 2. MOVE SAFETY CHECK - Check if this move endangers pieces AFTER the move
        safety_penalty = 0
        temp_board, temp_piece = simulate_move(board, piece, move)
        if temp_board and temp_piece:
            for pc in temp_board.get_player_pieces(player):
                piece_value = PIECE_VALUES.get(pc.name.lower(), 0)
                if is_piece_under_attack(temp_board, pc, opponent):
                    if piece_value >= 2000:
                        safety_penalty += piece_value * 10
                    elif piece_value >= 500:
                        safety_penalty += piece_value * 8
                    elif piece_value >= 300:
                        safety_penalty += piece_value * 5
                    else:
                        safety_penalty += piece_value * 3

            moving_piece_value = PIECE_VALUES.get(temp_piece.name.lower(), 0)
            if is_piece_under_attack(temp_board, temp_piece, opponent):
                if moving_piece_value >= 2000:
                    safety_penalty += moving_piece_value * 20
                elif moving_piece_value >= 500:
                    safety_penalty += moving_piece_value * 15
                elif moving_piece_value >= 300:
                    safety_penalty += moving_piece_value * 8
                else:
                    safety_penalty += moving_piece_value * 5
        else:
            safety_penalty += 100000  # invalid move simulation => push down ordering
        
        # Apply safety penalty FIRST - this can make score very negative
        # If a move endangers a piece, it should be avoided even if it's a good capture
        score -= safety_penalty
        #take_notes(str(safety_penalty) + " :Safety penalty for move")
        
        # If safety penalty is very high (endangering valuable piece like queen),
        # still calculate other bonuses but the penalty will dominate
        # This ensures dangerous moves get very negative scores
        
        # 3. SAVE ENDANGERED PIECES - Move endangered pieces to safety (HIGH PRIORITY)
        # Check if this move saves any endangered piece by moving it to a safe position
        save_bonus = 0
        for endangered_piece, piece_value in endangered_pieces:
            # Check if this move moves the endangered piece to safety
            if piece == endangered_piece:
                if does_move_save_endangered_piece(board, move, endangered_piece, opponent):
                    # MASSIVE bonus for saving endangered pieces - should beat most other moves
                    # More valuable pieces get higher priority
                    if piece_value >= 500:  # Important pieces (rook, queen, king)
                        save_bonus += piece_value * 4  # 4x piece value for saving important piece
                    else:  # Less important pieces (pawn, knight, bishop)
                        save_bonus += piece_value * 2  # 2x piece value for saving less important piece
                    break  # Only count once per move
        
        score += save_bonus
        #take_notes(str(save_bonus) + " :Save bonus for move")
        # 4. CAPTURES - High priority (but safety comes first)
        if dest:
            for opp_piece in board.get_pieces():
                if opp_piece.player != player and opp_piece.position == dest:
                    capture_value = PIECE_VALUES.get(opp_piece.name.lower(), 0)
                    attacker_value = PIECE_VALUES.get(piece.name.lower(), 0)
                    # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
                    score += capture_value * 10
                    score -= attacker_value * 0.1
                    break
        
        # 5. CENTER CONTROL
        if dest:
            center_distance = abs(dest.x - 2) + abs(dest.y - 2)
            score -= center_distance * 5
        
        scored_moves.append((score, piece, move))
    
    scored_moves.sort(reverse=True, key=lambda x: x[0])
    return [(piece, move) for _, piece, move in scored_moves] 

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
    player_in_check = king_in_check(board, player)
    opponent_in_check = king_in_check(board, opponent)
    
    #track position of kings

    for piece in board.get_player_pieces(opponent):
        if piece.name.lower() == 'king':
            enemy_king_pos = piece.position
            break
    #track position kings
    for piece in board.get_player_pieces(player):
        if piece.name.lower() == 'king':
            player_king_pos = piece.position  
            break
    
    for piece in board.get_player_pieces(player):
        piece_value = PIECE_VALUES.get(piece.name.lower(), 0)
        score += piece_value
        
        pos = piece.position
        if piece.name.lower() == 'pawn':
            if player.name == "white":
                score += pawn_table[pos.y][pos.x]
                if pos.y == 1:
                    score += 500
                elif pos.y == 2:
                    score += 200
            else:
                score += pawn_table[2 - pos.y][pos.x]
                if pos.y == 3:
                    score += 500
                elif pos.y == 2:
                    score += 200
        elif piece.name.lower() == 'knight':
            score += knight_table[pos.y][pos.x]
        elif piece.name.lower() == 'king':
            score += king_table_mid_game[pos.y][pos.x]
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
            if opponent.name == "white":
                score -= pawn_table[pos.y][pos.x]
                if pos.y == 1:
                    score -= 500
                elif pos.y == 2:
                    score -= 200
            else:
                score -= pawn_table[2 - pos.y][pos.x]
                if pos.y == 3:
                    score -= 500
                elif pos.y == 2:
                    score -= 200
        elif piece.name.lower() == 'knight':
            score -= knight_table[pos.y][pos.x]
        elif piece.name.lower() == 'king':
            score -= king_table_mid_game[pos.y][pos.x]
        elif piece.name.lower() == 'bishop':
            score += bishop_table[pos.y][pos.x]
        elif piece.name.lower() == 'right':
            score += right_table[pos.y][pos.x]
        elif piece.name.lower() == 'queen':
            score += queen_table[pos.y][pos.x]    
    
    player_moves = len(list_legal_moves_for(board, player))
    opponent_moves = len(list_legal_moves_for(board, opponent))
    score += (player_moves - opponent_moves) * 10   
    
    if player_in_check:
        score -= 50
    if opponent_in_check:
        score += 50

    # King distance to center to encourage opposition in endgame
    if player_king_pos:
        distance = math.sqrt((2 - player_king_pos.x) ** 2 + (2 - player_king_pos.y) ** 2)
        score += distance * 10
    if enemy_king_pos:
        distance = math.sqrt((2 - enemy_king_pos.x) ** 2 + (2 - enemy_king_pos.y) ** 2)
        score -= distance * 10
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
            temp_board, _ = simulate_move(board, piece, move)
            if not temp_board:
                continue
            try:
                eval_score = minimax(temp_board, depth - 1, alpha, beta, False, player, start_time, time_limit, use_endgame)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  
            except Exception as e:
                continue
        return max_eval
    else:
        min_eval = float('inf')
        for piece, move in legal_moves:
            temp_board, _ = simulate_move(board, piece, move)
            if not temp_board:
                continue
            try:
                eval_score = minimax(temp_board, depth - 1, alpha, beta, True, player, start_time, time_limit, use_endgame)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  
            except Exception as e:
                continue
        return min_eval

#havent used this function yet
def filter_repeated_moves(board, legal_moves, position_history, player):
    filtered = []
    for piece, move in legal_moves:
        try:
            temp_board, _ = simulate_move(board, piece, move)
            if not temp_board:
                continue
            pos_hash = temp_board.fen()
            reps = position_history.get(pos_hash,0)

            if reps < 4:
                filtered.append((piece, move))
            else:
                score = evaluate_position(temp_board, piece.player)
                if score < -300:
                    filtered.append((piece, move))
        except:
            continue
    return filtered if filtered else legal_moves
    
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
    
    use_endgame = is_endgame(board)

    
    for depth in range(1, 15): 
        if time.time() - start_time > time_limit * 0.75:  
                break
            
        current_best = best_move
        current_best_score = -float('inf')
            
        for piece, move in legal_moves:
            if time.time() - start_time > time_limit * 0.80:
                break
                
            try:
                temp_board, _ = simulate_move(board, piece, move)
                if not temp_board:
                    continue
                score = minimax(temp_board, depth - 1, -float('inf'), float('inf'), False, player, start_time, time_limit, use_endgame)
                if score > current_best_score:
                        current_best_score = score
                        current_best = (piece, move)
            except Exception as e:
                continue
            
        if time.time() - start_time < time_limit * 0.80:
            best_move = current_best
            best_score = current_best_score
        #take_notes(" " + str(best_score) + " " + str(use_endgame))
    return best_move
