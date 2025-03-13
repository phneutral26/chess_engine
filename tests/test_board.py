import unittest
import chess
from chess_engine.board.board import Board

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()
    
    def test_initial_position(self):
        """Test that the initial position is set up correctly."""
        # Check that the board is in the initial position
        self.assertEqual(self.board.board.fen().split()[0], 
                         "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    
    def test_legal_moves(self):
        """Test that legal moves are generated correctly."""
        # In the initial position, there should be 20 legal moves
        self.assertEqual(len(self.board.get_legal_moves()), 20)
    
    def test_make_move(self):
        """Test making a move on the board."""
        # Make a move
        move = chess.Move.from_uci("e2e4")
        self.board.make_move(move)
        
        # Check that the move was made
        self.assertEqual(self.board.board.fen().split()[0], 
                         "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR")
    
    def test_undo_move(self):
        """Test undoing a move on the board."""
        # Make a move
        move = chess.Move.from_uci("e2e4")
        self.board.make_move(move)
        
        # Undo the move
        self.board.undo_move()
        
        # Check that the board is back in the initial position
        self.assertEqual(self.board.board.fen().split()[0], 
                         "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    
    def test_game_over(self):
        """Test detecting when the game is over."""
        # Initial position is not game over
        self.assertFalse(self.board.is_game_over())
        
        # Set up a checkmate position (Fool's mate)
        moves = ["f2f3", "e7e5", "g2g4", "d8h4"]
        for move_uci in moves:
            move = chess.Move.from_uci(move_uci)
            self.board.make_move(move)
        
        # Now the game should be over
        self.assertTrue(self.board.is_game_over())
        self.assertEqual(self.board.get_result(), "0-1")  # Black wins

if __name__ == "__main__":
    unittest.main() 