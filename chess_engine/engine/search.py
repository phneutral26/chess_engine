"""
Search module for the chess engine.

This module implements the search algorithm for finding the best move,
using minimax with alpha-beta pruning and iterative deepening.
"""

import time
from chess_engine.engine.evaluation import evaluate_position

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

    def reset_stats(self):
        """Reset search statistics."""
        self.nodes_searched = 0
        self.best_move = None
        self.move_scores = {}

    def alpha_beta(self, depth, alpha, beta):
        """
        Alpha-beta pruning search.

        Args:
            depth: Current search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning

        Returns:
            float: The evaluation score of the position
        """
        if depth == 0 or self.board.is_game_over():
            return evaluate_position(self.board.board)

        legal_moves = list(self.board.board.legal_moves)
        if not legal_moves:
            return float('-inf')

        for move in legal_moves:
            self.board.make_move(move)
            value = -self.alpha_beta(depth - 1, -beta, -alpha)
            self.board.undo_move()

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return alpha

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

        for depth in range(1, max_depth + 1):
            # Check if we've exceeded the time limi
            if time.time() - start_time > time_limit:
                break

            alpha = float('-inf')
            beta = float('inf')

            # Get all legal moves
            legal_moves = list(self.board.board.legal_moves)
            if not legal_moves:
                return None

            best_value = float('-inf')

            # Try each move
            for move in legal_moves:
                self.board.make_move(move)
                value = -self.alpha_beta(depth - 1, -beta, -alpha)
                self.board.undo_move()

                if value > best_value:
                    best_value = value
                    best_move = move

                alpha = max(alpha, value)

                # Check if we've exceeded the time limi
                if time.time() - start_time > time_limit:
                    break

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
