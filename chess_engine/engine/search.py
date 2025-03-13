import chess
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
        """Alpha-beta pruning search."""
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_position()
        
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return float('-inf')
        
        for move in legal_moves:
            self.board.push(move)
            value = -self.alpha_beta(depth - 1, -beta, -alpha)
            self.board.pop()
            
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        
        return alpha
    
    def evaluate_position(self):
        """Evaluate the current position."""
        if self.board.is_checkmate():
            return float('-inf') if self.board.turn == chess.WHITE else float('inf')
        elif self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0.0
        
        # Material evaluation
        score = 0
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0  # King's value is not counted in material
        }
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                value = piece_values[piece.piece_type]
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        
        # Return score from white's perspective
        return score if self.board.turn == chess.WHITE else -score
    
    def iterative_deepening(self, max_depth, time_limit):
        """Perform iterative deepening search."""
        start_time = time.time()
        best_move = None
        
        for depth in range(1, max_depth + 1):
            # Check if we've exceeded the time limit
            if time.time() - start_time > time_limit:
                break
                
            alpha = float('-inf')
            beta = float('inf')
            
            # Get all legal moves
            legal_moves = list(self.board.legal_moves)  # Use python-chess's legal_moves property
            if not legal_moves:
                return None
                
            best_value = float('-inf')
            
            # Try each move
            for move in legal_moves:
                self.board.push(move)
                value = -self.alpha_beta(depth - 1, -beta, -alpha)
                self.board.pop()
                
                if value > best_value:
                    best_value = value
                    best_move = move
                
                alpha = max(alpha, value)
                
                # Check if we've exceeded the time limit
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
            The best move found
        """
        return self.iterative_deepening(max_depth, time_limit) 