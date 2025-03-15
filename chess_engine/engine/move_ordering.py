"""
Move ordering module for the chess engine.

This module provides functions for ordering moves to improve
the efficiency of alpha-beta pruning by examining the most promising
moves first.
"""

import chess
from chess_engine.utils.constants import PIECE_VALUES

# MVV-LVA (Most Valuable Victim - Least Valuable Aggressor) table
# Higher values are better captures
MVV_LVA = [
    [0, 0, 0, 0, 0, 0, 0],  # victim K, aggressor K, Q, R, B, N, P, None
    [50, 51, 52, 53, 54, 55, 0],  # victim Q, aggressor K, Q, R, B, N, P, None
    [40, 41, 42, 43, 44, 45, 0],  # victim R, aggressor K, Q, R, B, N, P, None
    [30, 31, 32, 33, 34, 35, 0],  # victim B, aggressor K, Q, R, B, N, P, None
    [20, 21, 22, 23, 24, 25, 0],  # victim N, aggressor K, Q, R, B, N, P, None
    [10, 11, 12, 13, 14, 15, 0],  # victim P, aggressor K, Q, R, B, N, P, None
    [0, 0, 0, 0, 0, 0, 0],  # victim None, aggressor K, Q, R, B, N, P, None
]

def score_move(board, move, previous_best_move=None, killer_moves=None):
    """
    Score a move for move ordering.
    
    Higher scores will be searched first.
    
    Args:
        board: A chess.Board object
        move: A chess.Move object to score
        previous_best_move: The best move from a previous search at the same position
        killer_moves: A list of killer moves for the current ply
        
    Returns:
        int: A score for the move (higher is better)
    """
    score = 0
    
    # If this move was the best move from a previous search, give it highest priority
    if previous_best_move and move == previous_best_move:
        return 10000
    
    # If this move is a killer move, give it high priority
    if killer_moves and move in killer_moves:
        return 9000
    
    # Check if the move is a capture
    if board.is_capture(move):
        victim_type = board.piece_at(move.to_square).piece_type
        aggressor_type = board.piece_at(move.from_square).piece_type
        
        # Use MVV-LVA table for scoring captures
        score += MVV_LVA[victim_type][aggressor_type]
        
        # Bonus for capturing with a less valuable piece
        score += (PIECE_VALUES[victim_type] - PIECE_VALUES[aggressor_type] // 100)
        
        # Extra bonus for capturing undefended pieces
        if not board.is_attacked_by(not board.turn, move.to_square):
            score += 50
    
    # Bonus for promotions
    if move.promotion:
        score += PIECE_VALUES[move.promotion] - PIECE_VALUES[chess.PAWN]
    
    # Bonus for checks
    board_copy = board.copy()
    board_copy.push(move)
    if board_copy.is_check():
        score += 30
    
    # Bonus for pawn advances in the center
    if board.piece_at(move.from_square) and board.piece_at(move.from_square).piece_type == chess.PAWN:
        # Central pawns
        if move.from_square % 8 in [3, 4]:
            score += 10
        
        # Passed pawns
        rank = move.to_square // 8
        if board.turn == chess.WHITE and rank >= 5:
            score += rank - 4
        elif board.turn == chess.BLACK and rank <= 2:
            score += 3 - rank
    
    return score

def order_moves(board, moves, previous_best_move=None, killer_moves=None):
    """
    Order moves for better alpha-beta pruning efficiency.
    
    Args:
        board: A chess.Board object
        moves: A list of legal moves to order
        previous_best_move: The best move from a previous search at the same position
        killer_moves: A list of killer moves for the current ply
        
    Returns:
        list: The moves ordered by potential value (best first)
    """
    # Score each move
    scored_moves = [(move, score_move(board, move, previous_best_move, killer_moves)) for move in moves]
    
    # Sort by score (descending)
    scored_moves.sort(key=lambda x: x[1], reverse=True)
    
    # Return just the moves in the new order
    return [move for move, _ in scored_moves] 