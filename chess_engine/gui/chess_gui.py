import sys
import os
import chess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QMessageBox,
                            QDialog, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QImage

from chess_engine.engine.search import SearchEngine
from chess_engine.utils.constants import PIECE_SYMBOLS
from chess_engine.board.board import Board

class GameSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Settings")
        self.setModal(True)
        self.setFixedSize(400, 200)  # Reduced height since we removed color selection

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Game mode selection
        mode_label = QLabel("Select Game Mode:")
        layout.addWidget(mode_label)

        self.mode_group = QButtonGroup(self)
        vs_engine = QRadioButton("Play vs Engine")
        vs_player = QRadioButton("Play vs Player")
        vs_engine.setChecked(True)  # Default selection
        self.mode_group.addButton(vs_engine, 1)
        self.mode_group.addButton(vs_player, 2)
        layout.addWidget(vs_engine)
        layout.addWidget(vs_player)

        # Start button
        start_btn = QPushButton("Start Game")
        start_btn.clicked.connect(self.accept)
        start_btn.setFixedHeight(40)
        layout.addWidget(start_btn)

    def get_settings(self):
        """Return the selected game settings."""
        vs_engine = self.mode_group.checkedId() == 1
        return {
            'vs_engine': vs_engine,
            'play_as_white': False  # Always play as black when vs engine
        }

class ChessBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 600)
        self.square_size = 75  # Fixed square size for better visibility
        self.selected_square = None
        self.valid_moves = []

        # Colors
        self.light_square = QColor("#F0D9B5")
        self.dark_square = QColor("#B58863")
        self.highlight_color = QColor(255, 255, 0, 100)
        self.selected_color = QColor(255, 255, 0, 150)

        # Load piece images
        self.piece_images = {}
        self.load_piece_images()

    def load_piece_images(self):
        """Load piece images from the assets directory."""
        # TODO: Implement piece image loading
        # For now, we'll use Unicode characters
        pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the board
        for rank in range(8):
            for file in range(8):
                x = file * self.square_size
                y = (7 - rank) * self.square_size

                # Draw square
                color = self.light_square if (rank + file) % 2 == 0 else self.dark_square
                painter.fillRect(x, y, self.square_size, self.square_size, color)

                # Highlight selected square
                if self.selected_square and self.selected_square == chess.square(file, rank):
                    painter.fillRect(x, y, self.square_size, self.square_size, self.selected_color)

                # Highlight valid moves
                if chess.square(file, rank) in self.valid_moves:
                    painter.fillRect(x, y, self.square_size, self.square_size, self.highlight_color)

                # Draw piece
                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                if piece:
                    self.draw_piece(painter, piece, x, y)

    def draw_piece(self, painter, piece, x, y):
        """Draw a chess piece on the board."""
        # Use Unicode characters for now
        symbol = PIECE_SYMBOLS[piece.symbol()]
        painter.setPen(QPen(Qt.GlobalColor.black if piece.color == chess.WHITE else Qt.GlobalColor.white))
        font = painter.font()
        font.setPointSize(int(self.square_size * 0.8))  # Make pieces 80% of square size
        painter.setFont(font)
        painter.drawText(x, y, self.square_size, self.square_size, Qt.AlignmentFlag.AlignCenter, symbol)

    def mousePressEvent(self, event):
        """Handle mouse clicks on the board."""
        if event.button() == Qt.MouseButton.LeftButton:
            file = int(event.position().x() // self.square_size)
            rank = 7 - int(event.position().y() // self.square_size)
            square = chess.square(file, rank)

            if 0 <= file < 8 and 0 <= rank < 8:
                self.handle_square_click(square)

    def handle_square_click(self, square):
        """Handle clicking on a square."""
        if self.selected_square is None:
            # Select a piece
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                # Get all legal moves from this square, including castling
                self.valid_moves = [move.to_square for move in self.board.legal_moves
                                  if move.from_square == square]
                self.update()
        else:
            # Try to make a move
            move = chess.Move(self.selected_square, square)

            # Handle pawn promotion
            if (self.board.piece_at(self.selected_square) and
                self.board.piece_at(self.selected_square).piece_type == chess.PAWN and
                ((self.board.turn == chess.WHITE and chess.square_rank(square) == 7) or
                 (self.board.turn == chess.BLACK and chess.square_rank(square) == 0))):
                # Show promotion dialog
                promotion_piece = self.show_promotion_dialog()
                if promotion_piece:
                    move = chess.Move(self.selected_square, square, promotion=promotion_piece)
                else:
                    self.selected_square = None
                    self.valid_moves = []
                    self.update()
                    return

            if move in self.board.legal_moves:
                self.make_move(move)
            self.selected_square = None
            self.valid_moves = []
            self.update()

    def show_promotion_dialog(self):
        """Show a dialog for pawn promotion piece selection."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Choose Promotion Piece")
        dialog.setFixedSize(300, 150)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create buttons for each promotion piece
        pieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        buttons = []

        for piece in pieces:
            btn = QPushButton(PIECE_SYMBOLS[chess.piece_symbol(piece, self.board.turn)])
            btn.setFixedHeight(40)
            font = btn.font()
            font.setPointSize(20)
            btn.setFont(font)
            btn.clicked.connect(lambda checked, p=piece: dialog.done(p))
            buttons.append(btn)
            layout.addWidget(btn)

        # Show dialog and get resul
        result = dialog.exec()
        if result in pieces:
            return resul
        return None

    def make_move(self, move):
        """Make a move on the board."""
        # Find the main window and make the move
        main_window = self.window()
        if isinstance(main_window, ChessGUI):
            main_window.make_move(move)

    def sizeHint(self):
        """Return the preferred size of the widget."""
        return QSize(self.square_size * 8, self.square_size * 8)

class ChessGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Show settings dialog
        settings_dialog = GameSettingsDialog(self)
        if settings_dialog.exec() == QDialog.DialogCode.Accepted:
            settings = settings_dialog.get_settings()
            self.vs_engine = settings['vs_engine']
            self.play_as_white = settings['play_as_white']  # Will be False when vs engine
        else:
            sys.exit()

        # Initialize board and search engine
        self.board = Board()
        if self.vs_engine:
            self.search_engine = SearchEngine(self.board)
            self.play_as_white = False  # Ensure playing as black vs engine

        # Set search parameters
        self.depth = 4
        self.time_limit = 3.0

        self.init_ui()

        # If playing against engine, make the engine's first move (as white)
        if self.vs_engine:
            self.engine_move()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Chess Engine' if self.vs_engine else 'Chess Game')
        self.setFixedSize(800, 700)  # Fixed window size with room for controls

        # Create central widget and layou
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)  # Add some spacing between elements
        layout.setContentsMargins(20, 20, 20, 20)  # Add margins around the layou

        # Create chess board
        self.chess_board = ChessBoard()
        self.chess_board.board = self.board.board
        layout.addWidget(self.chess_board, alignment=Qt.AlignmentFlag.AlignCenter)

        # Create status bar
        self.status_bar = self.statusBar()
        self.update_status()

        # Create control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # Add spacing between buttons

        new_game_btn = QPushButton('New Game')
        new_game_btn.clicked.connect(self.new_game)
        new_game_btn.setFixedHeight(30)  # Set fixed button heigh
        button_layout.addWidget(new_game_btn)

        undo_btn = QPushButton('Undo Move')
        undo_btn.clicked.connect(self.undo_move)
        undo_btn.setFixedHeight(30)  # Set fixed button heigh
        button_layout.addWidget(undo_btn)

        layout.addLayout(button_layout)

    def make_move(self, move):
        """Make a move and let the engine play if it's its turn."""
        self.board.make_move(move)
        self.chess_board.update()
        self.update_status()

        # Let the engine play if it's its turn
        if self.vs_engine and not self.board.is_game_over():
            if ((self.play_as_white and self.board.board.turn == chess.BLACK) or
                (not self.play_as_white and self.board.board.turn == chess.WHITE)):
                self.engine_move()

    def new_game(self):
        """Start a new game."""
        # Show settings dialog
        settings_dialog = GameSettingsDialog(self)
        if settings_dialog.exec() == QDialog.DialogCode.Accepted:
            settings = settings_dialog.get_settings()
            self.vs_engine = settings['vs_engine']
            self.play_as_white = settings['play_as_white']

            self.board = Board()
            if self.vs_engine:
                self.search_engine = SearchEngine(self.board)
            self.chess_board.board = self.board.board
            self.chess_board.selected_square = None
            self.chess_board.valid_moves = []
            self.chess_board.update()
            self.update_status()

            # If playing against engine, make the engine's first move (as white)
            if self.vs_engine:
                self.engine_move()

    def update_status(self):
        """Update the status bar with current game state."""
        if self.board.is_game_over():
            result = self.board.get_result()
            if result == "1-0":
                status = "White wins!"
            elif result == "0-1":
                status = "Black wins!"
            else:
                status = "Draw!"
        else:
            status = f"{'White' if self.board.board.turn == chess.BLACK else 'Black'} to move"  # Fixed turn indicator

        self.status_bar.showMessage(status)

    def undo_move(self):
        """Undo the last move."""
        if len(self.board.board.move_stack) > 0:
            self.board.undo_move()
            self.chess_board.selected_square = None
            self.chess_board.valid_moves = []
            self.chess_board.update()
            self.update_status()

    def engine_move(self):
        """Make the engine's move."""
        move = self.search_engine.get_best_move(self.depth, self.time_limit)
        if move:
            self.board.make_move(move)
            self.chess_board.update()
            self.update_status()
        else:
            QMessageBox.warning(self, "Error", "Engine couldn't find a move!")

def main():
    app = QApplication(sys.argv)
    gui = ChessGUI()
    gui.show()
    sys.exit(app.exec())
