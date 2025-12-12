# Strong minimax-based agent with quiescence, transposition table, and improved evaluation
import time
import math
from extension.board_utils import list_legal_moves_for, copy_piece_move

PIECE_VALUES = {
    "pawn": 100,
    "knight": 320,
    "bishop": 330,
    "right": 500,
    "queen": 2000,
    "king": 4000,
}

PAWN_TABLE = [
    [0, 0, 0, 0, 0],
    [40, 40, 40, 40, 40],
    [20, 20, 30, 20, 20],
    [10, 10, 15, 10, 10],
    [0, 0, 0, 0, 0],
]

KNIGHT_TABLE = [
    [-40, -30, -20, -30, -40],
    [-30, 5, 10, 5, -30],
    [-20, 10, 20, 10, -20],
    [-30, 5, 10, 5, -30],
    [-40, -30, -20, -30, -40],
]

BISHOP_TABLE = [
    [-25, -10, -10, -10, -25],
    [-10, 0, 5, 0, -10],
    [-10, 10, 10, 10, -10],
    [-10, 0, 5, 0, -10],
    [-25, -10, -10, -10, -25],
]

ROOK_TABLE = [
    [-5, 0, 5, 0, -5],
    [0, 5, 10, 5, 0],
    [5, 10, 15, 10, 5],
    [0, 5, 10, 5, 0],
    [-5, 0, 5, 0, -5],
]

QUEEN_TABLE = [
    [-20, -10, -10, -10, -20],
    [-10, 0, 5, 0, -10],
    [-10, 5, 10, 5, -10],
    [-10, 0, 5, 0, -10],
    [-20, -10, -10, -10, -20],
]

KING_TABLE_MID = [
    [-40, -40, -40, -40, -40],
    [-30, -5, -5, -5, -30],
    [-20, -5, -5, -5, -20],
    [-10, 0, 0, 0, -10],
    [0, 5, 5, 5, 0],
]

KING_TABLE_END = [
    [-20, -10, -10, -10, -20],
    [-10, 0, 5, 0, -10],
    [-10, 5, 20, 5, -10],
    [-10, 0, 5, 0, -10],
    [-20, -10, -10, -10, -20],
]

INF = float("inf")


def other_player(board, player):
    return board.players[1] if board.players[0] == player else board.players[0]


def simulate_move(board, piece, move):
    try:
        temp_board = board.clone()
        temp_board, temp_piece, temp_move = copy_piece_move(temp_board, piece, move)
        if not temp_piece or not temp_move:
            return None, None
        temp_piece.move(temp_move)
        return temp_board, temp_piece
    except Exception:
        return None, None

def safe_legal_moves(board, player):
    """List legal moves but skip pieces with invalid positions to avoid crashes."""
    moves = []
    for pc in board.get_player_pieces(player):
        pos = getattr(pc, "position", None)
        if pos is None:
            continue
        try:
            for opt in pc.get_move_options():
                moves.append((pc, opt))
        except Exception:
            continue
    return moves


def get_attacked_squares(board, opponent):
    attacked = set()
    for _, mv in safe_legal_moves(board, opponent):
        dest = getattr(mv, "position", None)
        if dest:
            attacked.add((dest.x, dest.y))
    return attacked


def king_in_check(board, player):
    opp = other_player(board, player)
    attacked = get_attacked_squares(board, opp)
    for pc in board.get_player_pieces(player):
        if pc.name.lower() == "king":
            return (pc.position.x, pc.position.y) in attacked
    return False


def is_endgame(board):
    return len(list(board.get_pieces())) <= 6


def piece_square_value(piece, pos, player):
    if pos is None:
        return 0
    name = piece.name.lower()
    if name == "pawn":
        if player.name == "white":
            return PAWN_TABLE[pos.y][pos.x]
        return PAWN_TABLE[4 - pos.y][pos.x]
    if name == "knight":
        return KNIGHT_TABLE[pos.y][pos.x]
    if name == "bishop":
        return BISHOP_TABLE[pos.y][pos.x]
    if name == "right":
        return ROOK_TABLE[pos.y][pos.x]
    if name == "queen":
        return QUEEN_TABLE[pos.y][pos.x]
    return 0


def evaluate_position(board, root_player):
    opp = other_player(board, root_player)
    score = 0
    endgame = is_endgame(board)
    king_table = KING_TABLE_END if endgame else KING_TABLE_MID

    attacked_by_opp = get_attacked_squares(board, opp)
    attacked_by_me = get_attacked_squares(board, root_player)

    for piece in board.get_player_pieces(root_player):
        name = piece.name.lower()
        val = PIECE_VALUES.get(name, 0)
        score += val
        pos = piece.position
        if pos is None:
            continue
        if name == "king":
            score += king_table[pos.y][pos.x]
        else:
            score += piece_square_value(piece, pos, root_player)
        if name == "pawn":
            if (root_player.name == "white" and pos.y == 1) or (root_player.name == "black" and pos.y == 3):
                score += 250
        if (pos.x, pos.y) in attacked_by_opp:
            score -= val * 0.3

    for piece in board.get_player_pieces(opp):
        name = piece.name.lower()
        val = PIECE_VALUES.get(name, 0)
        score -= val
        pos = piece.position
        if pos is None:
            continue
        if name == "king":
            score -= king_table[pos.y][pos.x]
        else:
            score -= piece_square_value(piece, pos, opp)
        if name == "pawn":
            if (opp.name == "white" and pos.y == 1) or (opp.name == "black" and pos.y == 3):
                score -= 250
        if (pos.x, pos.y) in attacked_by_me:
            score += val * 0.3

    mobility = len(safe_legal_moves(board, root_player)) - len(safe_legal_moves(board, opp))
    score += mobility * 8

    if king_in_check(board, root_player):
        score -= 100
    if king_in_check(board, opp):
        score += 100

    return score


def order_moves(board, player, moves):
    opp = other_player(board, player)
    ordered = []
    for piece, move in moves:
        dest = getattr(move, "position", None)
        score = 0
        if getattr(move, "extra", {}).get("promote") == "Queen":
            score += 10000
        if dest:
            for op_piece in board.get_player_pieces(opp):
                if op_piece.position == dest:
                    score += PIECE_VALUES.get(op_piece.name.lower(), 0) * 10
                    score -= PIECE_VALUES.get(piece.name.lower(), 0)
                    break
            score -= (abs(dest.x - 2) + abs(dest.y - 2)) * 3
        ordered.append((score, piece, move))
    ordered.sort(reverse=True, key=lambda x: x[0])
    return [(p, m) for _, p, m in ordered]


def quiescence(board, root_player, alpha, beta, start_time, time_limit):
    if time.time() - start_time > time_limit * 0.98:
        return evaluate_position(board, root_player)
    stand_pat = evaluate_position(board, root_player)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    player = root_player
    opp = other_player(board, player)
    capture_moves = []
    for piece, move in safe_legal_moves(board, player):
        dest = getattr(move, "position", None)
        if not dest:
            continue
        for op_piece in board.get_player_pieces(opp):
            if op_piece.position == dest:
                capture_moves.append((piece, move))
                break
    capture_moves = order_moves(board, player, capture_moves)

    for piece, move in capture_moves:
        temp_board, _ = simulate_move(board, piece, move)
        if not temp_board:
            continue
        score = -quiescence(temp_board, opp, -beta, -alpha, start_time, time_limit)
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha


def minimax(board, depth, alpha, beta, maximizing, root_player, start_time, time_limit, tt):
    if time.time() - start_time > time_limit * 0.98:
        return evaluate_position(board, root_player)
    key = None
    try:
        key = (board.fen(), depth, maximizing)
    except Exception:
        pass
    if key and key in tt:
        return tt[key]

    player = root_player if maximizing else other_player(board, root_player)
    legal = safe_legal_moves(board, player)
    if depth == 0 or not legal:
        return quiescence(board, root_player, alpha, beta, start_time, time_limit)

    legal = order_moves(board, player, legal)
    best = -INF if maximizing else INF

    for piece, move in legal:
        temp_board, _ = simulate_move(board, piece, move)
        if not temp_board:
            continue
        score = minimax(temp_board, depth - 1, alpha, beta, not maximizing, root_player, start_time, time_limit, tt)
        if maximizing:
            best = max(best, score)
            alpha = max(alpha, score)
        else:
            best = min(best, score)
            beta = min(beta, score)
        if beta <= alpha:
            break
    if key:
        tt[key] = best
    return best


def agent(board, player, var):
    time_limit = getattr(var, "thinking_time", 5.0)
    start_time = time.time()
    legal_moves = safe_legal_moves(board, player)
    if not legal_moves:
        return None, None
    if len(legal_moves) == 1:
        return legal_moves[0]

    legal_moves = order_moves(board, player, legal_moves)
    best_move = legal_moves[0]
    tt = {}

    max_depth = 6
    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit * 0.7:
            break
        current_best = best_move
        current_score = -INF
        for piece, move in legal_moves:
            if time.time() - start_time > time_limit * 0.8:
                break
            temp_board, _ = simulate_move(board, piece, move)
            if not temp_board:
                continue
            score = minimax(temp_board, depth - 1, -INF, INF, False, player, start_time, time_limit, tt)
            if score > current_score:
                current_score = score
                current_best = (piece, move)
        best_move = current_best
    return best_move
