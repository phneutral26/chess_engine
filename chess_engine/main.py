"""
Main module for the chess engine.

This module provides the main entry point for the chess engine,
including the command-line interface and game logic.
"""

import time
import chess

from chess_engine.board.board import Board
from chess_engine.engine.search import SearchEngine
from chess_engine.utils.display import print_board, print_move_history
from chess_engine.utils.move_utils import parse_move

def play_against_engine():
    """
    Play a game against the chess engine.

    This function sets up a game between the user and the chess engine,
    handling user input and displaying the game state.
    """
    board = Board()
    search_engine = SearchEngine(board)

    # Ask the user which color they want to play
    while True:
        color = input("Do you want to play as white or black? (w/b): ").lower()
        if color in ['w', 'b']:
            break
        print("Invalid input. Please enter 'w' for white or 'b' for black.")

    player_is_white = color == 'w'

    # Set search parameters
    depth = 4
    time_limit = 3.0

    print("\nGame started!")
    print("Enter moves in UCI format (e.g., 'e2e4') or SAN format (e.g., 'e4').")
    print("Type 'quit' to exit, 'undo' to take back a move, or 'board' to display the board.")

    while not board.is_game_over():
        print_board(board.board)

        if board.board.turn == chess.WHITE:
            print("\nWhite to move")
        else:
            print("\nBlack to move")

        # Check if it's the engine's turn
        if ((board.board.turn == chess.WHITE and not player_is_white) or
                (board.board.turn == chess.BLACK and player_is_white)):
            print("Engine is thinking...")
            start_time = time.time()
            move = search_engine.get_best_move(depth, time_limit)
            elapsed_time = time.time() - start_time

            if move:
                san_move = board.board.san(move)
                print(f"Engine plays: {san_move} ({move.uci()}) in {elapsed_time:.2f}s")
                board.make_move(move)
            else:
                print("Engine couldn't find a move!")
        else:
            # Player's turn
            valid_move_made = False
            while not valid_move_made:
                move_str = input("\nYour move: ").strip().lower()

                if move_str == 'quit':
                    print("Thanks for playing!")
                    return

                if move_str == 'board':
                    print_board(board.board)
                    continue

                if move_str == 'undo':
                    if len(board.board.move_stack) >= 2:
                        board.undo_move()  # Undo engine's move
                        board.undo_move()  # Undo player's move
                        print("Took back the last two moves.")
                    elif len(board.board.move_stack) == 1:
                        board.undo_move()  # Undo player's move
                        print("Took back your move.")
                    else:
                        print("No moves to undo.")
                    continue

                move = parse_move(move_str, board.board)
                if move:
                    board.make_move(move)
                    valid_move_made = True
                else:
                    print("Invalid move. Please try again.")

    # Game over
    print_board(board.board)
    print_move_history(board.board)

    result = board.get_result()
    if result == "1-0":
        print("White wins!")
    elif result == "0-1":
        print("Black wins!")
    else:
        print("Game drawn!")

def main():
    """Main entry point for the chess engine."""
    print("Welcome to the Chess Engine!")
    print("===========================")

    while True:
        print("\nMenu:")
        print("1. Play against the engine")
        print("2. Quit")

        choice = input("\nEnter your choice (1-2): ")

        if choice == '1':
            play_against_engine()
        elif choice == '2':
            print("Goodbye!")
            break
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
