"""
AI Chess Engine using Minimax with Alpha-Beta Pruning
"""
import copy
import random
from piece import Pawn, Knight, Bishop, Rook, Queen, King

class AIEngine:
    
    def __init__(self, difficulty='medium'):
        """
        difficulty: 'easy' (depth 1-2), 'medium' (depth 3), 'hard' (depth 4)
        """
        self.difficulty = difficulty
        self.depth_map = {'easy': 2, 'medium': 3, 'hard': 4}
        self.max_depth = self.depth_map.get(difficulty, 3)
        self.nodes_evaluated = 0
        
    def get_best_move(self, board, color):
        """Find the best move for the given color using minimax"""
        self.nodes_evaluated = 0
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        all_moves = self._get_all_valid_moves(board, color)
        
        if not all_moves:
            return None
        
        # Add some randomness for easy difficulty
        if self.difficulty == 'easy' and random.random() < 0.3:
            return random.choice(all_moves)
        
        # Shuffle moves to add variety when scores are equal
        random.shuffle(all_moves)
        
        for piece, move in all_moves:
            # Make move on a copy
            temp_board = copy.deepcopy(board)
            temp_piece = temp_board.squares[move.initial.row][move.initial.col].piece
            temp_board.move(temp_piece, move, testing=True)
            
            # Evaluate position
            score = self._minimax(temp_board, self.max_depth - 1, alpha, beta, False, color)
            
            if score > best_score:
                best_score = score
                best_move = (piece, move)
            
            alpha = max(alpha, score)
        
        return best_move
    
    def _minimax(self, board, depth, alpha, beta, maximizing, ai_color):
        """Minimax algorithm with alpha-beta pruning"""
        self.nodes_evaluated += 1
        
        if depth == 0:
            return self._evaluate_board(board, ai_color)
        
        if maximizing:
            max_eval = float('-inf')
            moves = self._get_all_valid_moves(board, ai_color)
            
            if not moves:
                # Check if it's checkmate or stalemate
                if self._is_in_check(board, ai_color):
                    return -10000  # Checkmate
                return 0  # Stalemate
            
            for piece, move in moves:
                temp_board = copy.deepcopy(board)
                temp_piece = temp_board.squares[move.initial.row][move.initial.col].piece
                temp_board.move(temp_piece, move, testing=True)
                
                eval_score = self._minimax(temp_board, depth - 1, alpha, beta, False, ai_color)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_eval
        else:
            min_eval = float('inf')
            opponent_color = 'black' if ai_color == 'white' else 'white'
            moves = self._get_all_valid_moves(board, opponent_color)
            
            if not moves:
                # Check if it's checkmate or stalemate
                if self._is_in_check(board, opponent_color):
                    return 10000  # Opponent is checkmated (good for us)
                return 0  # Stalemate
            
            for piece, move in moves:
                temp_board = copy.deepcopy(board)
                temp_piece = temp_board.squares[move.initial.row][move.initial.col].piece
                temp_board.move(temp_piece, move, testing=True)
                
                eval_score = self._minimax(temp_board, depth - 1, alpha, beta, True, ai_color)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_eval
    
    def _get_all_valid_moves(self, board, color):
        """Get all valid moves for a given color"""
        moves = []
        
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece() and square.piece.color == color:
                    piece = square.piece
                    board.calc_moves(piece, row, col, bool=True)
                    
                    for move in piece.moves:
                        moves.append((piece, move))
        
        return moves
    
    def _is_in_check(self, board, color):
        """Check if the given color's king is in check"""
        # Find king position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = board.squares[row][col].piece
                if piece and isinstance(piece, King) and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False
        
        # Check if any opponent piece can attack the king
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece() and square.piece.color == opponent_color:
                    piece = square.piece
                    board.calc_moves(piece, row, col, bool=False)
                    
                    for move in piece.moves:
                        if move.final.row == king_pos[0] and move.final.col == king_pos[1]:
                            return True
        
        return False
    
    def _evaluate_board(self, board, ai_color):
        """Evaluate the board position"""
        score = 0
        
        # Piece values
        piece_values = {
            'pawn': 100,
            'knight': 320,
            'bishop': 330,
            'rook': 500,
            'queen': 900,
            'king': 20000
        }
        
        # Position bonuses for pieces (encourages good placement)
        pawn_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]
        
        knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
        
        bishop_table = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ]
        
        rook_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [0,  0,  0,  5,  5,  0,  0,  0]
        ]
        
        queen_table = [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [-5,  0,  5,  5,  5,  5,  0, -5],
            [0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ]
        
        king_table = [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [20, 20,  0,  0,  0,  0, 20, 20],
            [20, 30, 10,  0,  0, 10, 30, 20]
        ]
        
        position_tables = {
            'pawn': pawn_table,
            'knight': knight_table,
            'bishop': bishop_table,
            'rook': rook_table,
            'queen': queen_table,
            'king': king_table
        }
        
        # Evaluate all pieces
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece():
                    piece = square.piece
                    piece_value = piece_values.get(piece.name, 0)
                    
                    # Get position bonus
                    pos_table = position_tables.get(piece.name, [[0]*8 for _ in range(8)])
                    pos_row = row if piece.color == 'white' else 7 - row
                    position_bonus = pos_table[pos_row][col]
                    
                    piece_score = piece_value + position_bonus
                    
                    if piece.color == ai_color:
                        score += piece_score
                    else:
                        score -= piece_score
        
        return score
