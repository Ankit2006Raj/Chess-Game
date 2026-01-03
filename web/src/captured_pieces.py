"""
Captured Pieces Tracker - Manages captured pieces and material advantage
"""

class CapturedPieces:
    
    def __init__(self):
        self.white_captured = []  # Pieces captured by white (black pieces)
        self.black_captured = []  # Pieces captured by black (white pieces)
        
        self.piece_values = {
            'pawn': 1,
            'knight': 3,
            'bishop': 3,
            'rook': 5,
            'queen': 9,
            'king': 0  # King can't be captured
        }
    
    def add_captured_piece(self, piece, captured_by):
        """Add a captured piece to the appropriate list"""
        if captured_by == 'white':
            self.white_captured.append(piece.name)
        else:
            self.black_captured.append(piece.name)
    
    def get_captured_by_color(self, color):
        """Get pieces captured by a specific color"""
        if color == 'white':
            return self.white_captured
        else:
            return self.black_captured
    
    def get_material_advantage(self):
        """
        Calculate material advantage
        Returns: (color, advantage_value)
        Positive means white is ahead, negative means black is ahead
        """
        white_value = sum(self.piece_values.get(p, 0) for p in self.white_captured)
        black_value = sum(self.piece_values.get(p, 0) for p in self.black_captured)
        
        advantage = white_value - black_value
        
        if advantage > 0:
            return ('white', advantage)
        elif advantage < 0:
            return ('black', abs(advantage))
        else:
            return ('equal', 0)
    
    def get_captured_summary(self):
        """Get a summary of captured pieces for display"""
        return {
            'white_captured': self._count_pieces(self.white_captured),
            'black_captured': self._count_pieces(self.black_captured),
            'material_advantage': self.get_material_advantage()
        }
    
    def _count_pieces(self, pieces):
        """Count occurrences of each piece type"""
        counts = {}
        for piece in pieces:
            counts[piece] = counts.get(piece, 0) + 1
        return counts
    
    def clear(self):
        """Reset captured pieces"""
        self.white_captured = []
        self.black_captured = []
    
    def remove_last_capture(self, captured_by):
        """Remove the last captured piece (for undo)"""
        if captured_by == 'white' and self.white_captured:
            return self.white_captured.pop()
        elif captured_by == 'black' and self.black_captured:
            return self.black_captured.pop()
        return None
