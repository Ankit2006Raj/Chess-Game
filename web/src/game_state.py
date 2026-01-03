"""
Game State Manager - Handles checkmate, stalemate, and game status
"""
from piece import King

class GameState:
    
    def __init__(self):
        self.status = 'active'  # active, checkmate, stalemate, draw
        self.winner = None
        self.in_check = False
        self.checking_pieces = []
    
    def check_game_status(self, board, current_player):
        """
        Check if the game is over (checkmate/stalemate) or if player is in check
        Returns: status ('active', 'checkmate', 'stalemate', 'check')
        """
        self.in_check = self._is_in_check(board, current_player)
        has_legal_moves = self._has_legal_moves(board, current_player)
        
        if not has_legal_moves:
            if self.in_check:
                self.status = 'checkmate'
                self.winner = 'black' if current_player == 'white' else 'white'
                return 'checkmate'
            else:
                self.status = 'stalemate'
                return 'stalemate'
        
        if self.in_check:
            self.status = 'check'
            return 'check'
        
        self.status = 'active'
        return 'active'
    
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
        self.checking_pieces = []
        opponent_color = 'black' if color == 'white' else 'white'
        
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece() and square.piece.color == opponent_color:
                    piece = square.piece
                    board.calc_moves(piece, row, col, bool=False)
                    
                    for move in piece.moves:
                        if move.final.row == king_pos[0] and move.final.col == king_pos[1]:
                            self.checking_pieces.append((row, col))
                            return True
        
        return False
    
    def _has_legal_moves(self, board, color):
        """Check if the player has any legal moves"""
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece() and square.piece.color == color:
                    piece = square.piece
                    board.calc_moves(piece, row, col, bool=True)
                    
                    if len(piece.moves) > 0:
                        return True
        
        return False
    
    def is_game_over(self):
        """Check if the game is over"""
        return self.status in ['checkmate', 'stalemate', 'draw']
    
    def get_status_message(self):
        """Get human-readable status message"""
        if self.status == 'checkmate':
            winner_name = self.winner.capitalize()
            return f'Checkmate! {winner_name} wins!'
        elif self.status == 'stalemate':
            return 'Stalemate! Game is a draw.'
        elif self.status == 'check':
            return 'Check!'
        elif self.status == 'draw':
            return 'Draw!'
        else:
            return 'Game in progress'
    
    def reset(self):
        """Reset game state"""
        self.status = 'active'
        self.winner = None
        self.in_check = False
        self.checking_pieces = []
