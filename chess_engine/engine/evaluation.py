"""
Evaluation module for the chess engine.

This module provides functions for evaluating chess positions,
including material counting, piece-square tables, and mobility evaluation.
"""

import chess
from chess_engine.utils.constants import PIECE_VALUES
from chess_engine.utils.piece_tables import (
    PIECE_SQUARE_TABLES,
    KING_END_GAME_TABLE
)

# Precompute square indices for faster lookup
SQUARE_INDICES = {square: (square // 8, square % 8) for square in chess.SQUARES}

def is_endgame(board):
    """
    Determine if the position is an endgame based on material.

    Args:
        board: A chess.Board object

    Returns:
        bool: True if the position is an endgame, False otherwise
    """
    # Count the number of non-pawn pieces
    queens = (len(board.pieces(chess.QUEEN, chess.WHITE)) +
              len(board.pieces(chess.QUEEN, chess.BLACK)))
    
    # If no queens, it's likely an endgame
    if queens == 0:
        return True
        
    # Count total material (excluding kings and pawns)
    total_material = 0
    for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
        for color in [chess.WHITE, chess.BLACK]:
            total_material += len(board.pieces(piece_type, color)) * PIECE_VALUES[piece_type]
    
    # If total material is less than value of a rook + minor piece, it's endgame
    return total_material < (PIECE_VALUES[chess.ROOK] + PIECE_VALUES[chess.KNIGHT])

def evaluate_position(board):
    """
    Evaluate the current position on the board.

    Returns a score in centipawns from white's perspective.
    Positive values favor white, negative values favor black.

    Args:
        board: A chess.Board object

    Returns:
        int: The evaluation score in centipawns
    """
    # Quick checks for terminal positions
    if board.is_checkmate():
        # Return a large value if checkmate, considering who is checkmated
        return -10000 if board.turn == chess.WHITE else 10000

    if (board.is_stalemate() or board.is_insufficient_material() or
            board.is_fifty_moves() or board.is_repetition()):
        return 0  # Draw

    # Determine if we're in an endgame
    endgame = is_endgame(board)

    # Combined evaluation loop for material and position
    material_score = 0
    position_score = 0

    # Piece counts for faster endgame detection in future calls
    white_pieces = {piece_type: 0 for piece_type in range(1, 7)}
    black_pieces = {piece_type: 0 for piece_type in range(1, 7)}

    # Process all pieces in a single loop
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        # Count pieces
        if piece.color == chess.WHITE:
            white_pieces[piece.piece_type] += 1
        else:
            black_pieces[piece.piece_type] += 1

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
        rank, file = SQUARE_INDICES[square]

        if piece.color == chess.WHITE:
            position_score += table[7 - rank][file]
        else:
            position_score -= table[rank][file]

    # Simplified mobility evaluation - just count legal moves for the side to move
    # This is much faster than switching sides and counting both
    mobility_score = 0
    if board.turn == chess.WHITE:
        mobility_score = len(list(board.legal_moves)) * 3
    else:
        mobility_score = -len(list(board.legal_moves)) * 3

    # Combine all evaluation components
    total_score = material_score + position_score + mobility_score

    return total_score
