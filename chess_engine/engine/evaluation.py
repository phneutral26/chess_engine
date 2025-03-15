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
    rooks = len(board.pieces(chess.ROOK, chess.WHITE)) + len(board.pieces(chess.ROOK, chess.BLACK))
    minors = (
        len(board.pieces(chess.BISHOP, chess.WHITE)) +
        len(board.pieces(chess.BISHOP, chess.BLACK)) +
        len(board.pieces(chess.KNIGHT, chess.WHITE)) +
        len(board.pieces(chess.KNIGHT, chess.BLACK))
    )

    # Endgame if both sides have no queens or if both sides have at most one minor piece
    return queens == 0 or (queens <= 1 and rooks <= 2 and minors <= 1)

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
    if board.is_checkmate():
        # Return a large value if checkmate, considering who is checkmated
        return -10000 if board.turn == chess.WHITE else 10000

    if (board.is_stalemate() or board.is_insufficient_material() or
            board.is_fifty_moves() or board.is_repetition()):
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

    # 5 centipawns per move advantage
    mobility_score = (white_moves - black_moves) * 5

    # Combine all evaluation components
    total_score = material_score + position_score + mobility_score

    return total_score
