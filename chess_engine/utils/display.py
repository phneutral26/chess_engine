"""
Display utilities for the chess engine.

This module provides functions for displaying the chess board and game information
in a terminal environment using ANSI colors and Unicode chess symbols.
"""

import chess
from chess_engine.utils.constants import UNICODE_PIECES

# ANSI color codes for terminal outpu
RESET = "\033[0m"
BLACK_PIECE = "\033[30m"  # Black tex
WHITE_PIECE = "\033[97m"  # White tex
BLACK_SQUARE = "\033[45m"  # Purple background
WHITE_SQUARE = "\033[46m"  # Cyan background

def get_piece_symbol(piece):
    """Get the Unicode symbol for a chess piece."""
    if piece is None:
        return ' '

    symbol = UNICODE_PIECES[piece.piece_type]
    return symbol

def print_board(board):
    """
    Print the chess board in the terminal with colored squares and Unicode pieces.

    Args:
        board: A chess.Board objec
    """
    print("  a b c d e f g h")
    print("  ---------------")

    for rank in range(7, -1, -1):
        print(f"{rank + 1}|", end="")

        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)

            # Determine square color (alternating pattern)
            is_white_square = (rank + file) % 2 == 0
            bg_color = WHITE_SQUARE if is_white_square else BLACK_SQUARE

            # Determine piece color
            if piece is not None:
                fg_color = WHITE_PIECE if piece.color == chess.WHITE else BLACK_PIECE
            else:
                fg_color = WHITE_PIECE

            # Print the square with the piece
            print(f"{bg_color}{fg_color}{get_piece_symbol(piece)}{RESET}", end="")

        print(f"|{rank + 1}")

    print("  ---------------")
    print("  a b c d e f g h")

def print_move_history(board):
    """
    Print the move history of the game.

    Args:
        board: A chess.Board objec
    """
    if len(board.move_stack) == 0:
        print("No moves played yet.")
        return

    print("\nMove history:")
    for i, move in enumerate(board.move_stack):
        if i % 2 == 0:
            print(f"{i//2 + 1}. {move}", end="")
        else:
            print(f" {move}")

    # Add a newline if the last move was white's
    if len(board.move_stack) % 2 == 1:
        print()
    print()
