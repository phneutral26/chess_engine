import chess
import numpy as np

# Piece values in centipawns
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Piece-square tables for positional evaluation
# These tables encourage pieces to occupy favorable squares
PAWN_TABLE = np.array([
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]).reshape(8, 8)

KNIGHT_TABLE = np.array([
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]).reshape(8, 8)

BISHOP_TABLE = np.array([
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5,  5,  5,  5,  5,-10,
    -10,  0,  5,  0,  0,  5,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]).reshape(8, 8)

ROOK_TABLE = np.array([
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]).reshape(8, 8)

QUEEN_TABLE = np.array([
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]).reshape(8, 8)

KING_MIDDLE_GAME_TABLE = np.array([
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]).reshape(8, 8)

KING_END_GAME_TABLE = np.array([
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]).reshape(8, 8)

PIECE_SQUARE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_MIDDLE_GAME_TABLE
}

def is_endgame(board):
    """Determine if the position is an endgame based on material."""
    # Count the number of non-pawn pieces
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
    rooks = len(board.pieces(chess.ROOK, chess.WHITE)) + len(board.pieces(chess.ROOK, chess.BLACK))
    minors = (len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.BLACK)) +
              len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.BLACK)))
    
    # Endgame if both sides have no queens or if both sides have at most one minor piece
    return queens == 0 or (queens <= 1 and rooks <= 2 and minors <= 1)

def evaluate_position(board):
    """
    Evaluate the current position on the board.
    Returns a score in centipawns from white's perspective.
    Positive values favor white, negative values favor black.
    """
    if board.is_checkmate():
        # Return a large value if checkmate, considering who is checkmated
        return -10000 if board.turn == chess.WHITE else 10000
    
    if board.is_stalemate() or board.is_insufficient_material() or board.is_fifty_moves() or board.is_repetition():
        return 0  # Draw
    
    # Material evaluation
    material_score = 0
    
    # Piece-square evaluation
    position_score = 0
    
    endgame = is_endgame(board)
    
    # Iterate through all pieces on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        
        # Material value
        value = PIECE_VALUES[piece.piece_type]
        if piece.color == chess.WHITE:
            material_score += value
        else:
            material_score -= value
        
        # Position value
        if piece.piece_type == chess.KING and endgame:
            table = KING_END_GAME_TABLE
        else:
            table = PIECE_SQUARE_TABLES[piece.piece_type]
        
        # Get the position value from the piece-square table
        # For black pieces, we need to flip the square index
        rank = square // 8
        file = square % 8
        
        if piece.color == chess.WHITE:
            position_score += table[7 - rank][file]
        else:
            position_score -= table[rank][file]
    
    # Mobility evaluation (number of legal moves)
    mobility_score = 0
    
    # Store the current turn
    current_turn = board.turn
    
    # Count white's moves
    board.turn = chess.WHITE
    white_moves = len(list(board.legal_moves))
    
    # Count black's moves
    board.turn = chess.BLACK
    black_moves = len(list(board.legal_moves))
    
    # Restore the original turn
    board.turn = current_turn
    
    mobility_score = (white_moves - black_moves) * 5  # 5 centipawns per move advantage
    
    # Combine all evaluation components
    total_score = material_score + position_score + mobility_score
    
    return total_score 