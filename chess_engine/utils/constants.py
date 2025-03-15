"""
Constants module for the chess engine.

This module contains shared constants used throughout the chess engine,
including piece values, Unicode representations, and other configuration values.
"""

import chess

# Unicode chess pieces for internal representation
UNICODE_PIECES = {
    chess.PAWN: '♟',
    chess.KNIGHT: '♞',
    chess.BISHOP: '♝',
    chess.ROOK: '♜',
    chess.QUEEN: '♛',
    chess.KING: '♚'
}

# Chess piece Unicode characters for GUI (includes color)
PIECE_SYMBOLS = {
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔'
}

# Piece values in centipawns
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}
