"""
Move utility functions for the chess engine.

This module provides utility functions for parsing and handling chess moves.
"""

import chess

def parse_move(move_str, board):
    """
    Parse a move string into a chess.Move object.

    Args:
        move_str: A string representing a move (e.g., "e2e4", "g1f3")
        board: A chess.Board objec

    Returns:
        A chess.Move object if the move is valid, None otherwise
    """
    try:
        # Try to parse as UCI move
        move = chess.Move.from_uci(move_str)
        if move in board.legal_moves:
            return move
    except ValueError:
        pass

    try:
        # Try to parse as SAN move
        move = board.parse_san(move_str)
        return move
    except ValueError:
        pass

    return None
