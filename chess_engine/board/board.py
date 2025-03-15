"""
Board module for the chess engine.

This module provides a wrapper around the python-chess Board class,
adding additional functionality specific to the chess engine.
"""

import chess

class Board:
    """
    Chess board representation using the python-chess library.
    This class serves as a wrapper around the chess.Board class.
    """

    def __init__(self):
        """Initialize a new chess board in the starting position."""
        self.board = chess.Board()

    def get_legal_moves(self):
        """Get all legal moves in the current position."""
        return list(self.board.legal_moves)

    def make_move(self, move):
        """Make a move on the board."""
        self.board.push(move)

    def undo_move(self):
        """Undo the last move."""
        self.board.pop()

    def is_game_over(self):
        """Check if the game is over."""
        return self.board.is_game_over()

    def get_result(self):
        """Get the result of the game."""
        if not self.board.is_game_over():
            return None

        if self.board.is_checkmate():
            return "1-0" if self.board.turn == chess.BLACK else "0-1"
        return "1/2-1/2"  # Draw

    def get_fen(self):
        """Get the FEN representation of the current position."""
        return self.board.fen()

    def set_fen(self, fen):
        """Set the board to a position given by FEN."""
        self.board.set_fen(fen)

    def __str__(self):
        """String representation of the board."""
        return str(self.board)
