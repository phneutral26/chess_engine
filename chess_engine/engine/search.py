"""
Search module for the chess engine.

This module implements the search algorithm for finding the best move,
using minimax with alpha-beta pruning and iterative deepening.
"""

import time
import chess
from chess_engine.engine.evaluation import evaluate_position
from chess_engine.engine.move_ordering import order_moves

class SearchEngine:
    """
    Chess engine search algorithm implementation using minimax with alpha-beta pruning.
    """

    def __init__(self, board):
        """Initialize the search engine with a board."""
        self.board = board
        self.nodes_searched = 0
        self.max_depth = 0
        self.best_move = None
        self.move_scores = {}
        self.transposition_table = {}
        self.killer_moves = [[] for _ in range(20)]  # Store killer moves for each ply
        self.history_table = {}  # Store history heuristic scores

    def reset_stats(self):
        """Reset search statistics."""
        self.nodes_searched = 0
        self.best_move = None
        self.move_scores = {}
        # Keep the transposition table between moves for better performance
        # self.transposition_table = {}
        
    def clear_tables(self):
        """Clear all tables for a fresh search."""
        self.transposition_table = {}
        self.killer_moves = [[] for _ in range(20)]
        self.history_table = {}

    def add_killer_move(self, move, ply):
        """Add a killer move for the given ply."""
        if ply < len(self.killer_moves) and move not in self.killer_moves[ply]:
            if len(self.killer_moves[ply]) >= 2:
                self.killer_moves[ply].pop()  # Remove the oldest killer move
            self.killer_moves[ply].insert(0, move)  # Add new killer move at the front

    def update_history_score(self, move, depth):
        """Update the history score for a move."""
        key = (move.from_square, move.to_square)
        if key not in self.history_table:
            self.history_table[key] = 0
        self.history_table[key] += depth * depth  # Square the depth for more impact

    def alpha_beta(self, depth, alpha, beta, ply=0):
        """
        Alpha-beta pruning search.

        Args:
            depth: Current search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            ply: Current ply (distance from root)

        Returns:
            float: The evaluation score of the position
        """
        # Check for game over conditions
        if self.board.is_game_over():
            if self.board.board.is_checkmate():
                return float('-inf')  # Loss for the current player
            return 0.0  # Draw

        # Return evaluation if we've reached the maximum depth
        if depth <= 0:
            return evaluate_position(self.board.board)

        # Generate a unique key for the current position
        position_key = self.board.board.fen()
        
        # Check if we've already evaluated this position at this depth or deeper
        if position_key in self.transposition_table and self.transposition_table[position_key][1] >= depth:
            return self.transposition_table[position_key][0]

        self.nodes_searched += 1
        
        # Get legal moves
        legal_moves = list(self.board.board.legal_moves)
        
        # If no legal moves, it's a checkmate or stalemate
        if not legal_moves:
            return float('-inf') if self.board.board.is_check() else 0.0

        # Order moves using our move ordering function
        previous_best = None
        if position_key in self.transposition_table and len(self.transposition_table[position_key]) > 2:
            previous_best = self.transposition_table[position_key][2]  # Best move from previous search
            
        ordered_moves = order_moves(
            self.board.board, 
            legal_moves, 
            previous_best, 
            self.killer_moves[ply] if ply < len(self.killer_moves) else None
        )

        best_value = float('-inf')
        best_move = None
        
        # Try each move
        for move in ordered_moves:
            self.board.make_move(move)
            value = -self.alpha_beta(depth - 1, -beta, -alpha, ply + 1)
            self.board.undo_move()

            if value > best_value:
                best_value = value
                best_move = move
                
            alpha = max(alpha, value)
            
            # Alpha-beta cutoff
            if alpha >= beta:
                # This is a good move that caused a cutoff, so it's a potential killer move
                if not self.board.board.is_capture(move) and not move.promotion:
                    self.add_killer_move(move, ply)
                    self.update_history_score(move, depth)
                break

        # Store the result in the transposition table, including the best move
        self.transposition_table[position_key] = (best_value, depth, best_move)
        
        return best_value

    def iterative_deepening(self, max_depth, time_limit):
        """
        Perform iterative deepening search.

        Args:
            max_depth: Maximum search depth
            time_limit: Maximum search time in seconds

        Returns:
            chess.Move: The best move found
        """
        start_time = time.time()
        best_move = None
        self.nodes_searched = 0

        # Clear killer moves for a fresh search
        self.killer_moves = [[] for _ in range(20)]

        for depth in range(1, max_depth + 1):
            # Check if we've exceeded the time limit
            if time.time() - start_time > time_limit * 0.8:  # Use 80% of time for search, save 20% for move selection
                break

            alpha = float('-inf')
            beta = float('inf')

            # Get all legal moves
            legal_moves = list(self.board.board.legal_moves)
            if not legal_moves:
                return None

            # Order moves using our move ordering function
            ordered_moves = order_moves(self.board.board, legal_moves, best_move)

            best_value = float('-inf')
            current_best_move = None

            # Try each move
            for move in ordered_moves:
                self.board.make_move(move)
                value = -self.alpha_beta(depth - 1, -beta, -alpha, 1)  # Start at ply 1
                self.board.undo_move()

                # Store move score for potential future move ordering
                self.move_scores[move.uci()] = value

                if value > best_value:
                    best_value = value
                    current_best_move = move

                alpha = max(alpha, value)

                # Check if we've exceeded the time limit
                if time.time() - start_time > time_limit * 0.9:  # Use 90% of time as hard cutoff
                    break

            # Update best move if we completed this depth
            if current_best_move:
                best_move = current_best_move
                
            # Print some info about the search progress
            elapsed = time.time() - start_time
            print(f"Depth {depth}: evaluated {self.nodes_searched} nodes in {elapsed:.2f}s")

        return best_move

    def get_best_move(self, max_depth=4, time_limit=5.0):
        """
        Get the best move for the current position.

        Args:
            max_depth: Maximum depth to search
            time_limit: Maximum time to search in seconds

        Returns:
            chess.Move: The best move found
        """
        return self.iterative_deepening(max_depth, time_limit)
