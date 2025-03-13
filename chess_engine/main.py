import chess
import sys
import time

from chess_engine.board.board import Board
from chess_engine.engine.search import SearchEngine
from chess_engine.utils.display import print_board, print_move_history

def parse_move(move_str, board):
    """
    Parse a move string into a chess.Move object.
    
    Args:
        move_str: A string representing a move (e.g., "e2e4", "g1f3")
        board: A chess.Board object
        
    Returns:
        A chess.Move object if the move is valid, None otherwise
    """
    try:
        # Try to parse as UCI move
        move = chess.Move.from_uci(move_str)
        if move in board.board.legal_moves:
            return move
    except ValueError:
        pass
    
    try:
        # Try to parse as SAN move
        move = board.board.parse_san(move_str)
        return move
    except ValueError:
        pass
    
    return None

def play_against_engine():
    """Play a game against the chess engine."""
    board = Board()
    search_engine = SearchEngine(board)
    
    # Ask the user which color they want to play
    while True:
        color = input("Do you want to play as white or black? (w/b): ").lower()
        if color in ['w', 'b']:
            break
        print("Invalid input. Please enter 'w' for white or 'b' for black.")
    
    player_is_white = color == 'w'
    engine_turn = not player_is_white
    
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
        if (board.board.turn == chess.WHITE and not player_is_white) or \
           (board.board.turn == chess.BLACK and player_is_white):
            print("Engine is thinking...")
            start_time = time.time()
            move = search_engine.get_best_move(depth, time_limit)
            elapsed_time = time.time() - start_time
            
            if move:
                print(f"Engine plays: {board.board.san(move)} ({move.uci()}) in {elapsed_time:.2f}s")
                board.make_move(move)
            else:
                print("Engine couldn't find a move!")
        else:
            # Player's turn
            while True:
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
                
                move = parse_move(move_str, board)
                if move:
                    board.make_move(move)
                    break
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
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
