"""
Move History Manager - Tracks moves in algebraic notation
"""
from piece import Pawn, Knight, Bishop, Rook, Queen, King

class MoveHistory:
    
    def __init__(self):
        self.moves = []  # List of move dictionaries
        self.move_number = 1
    
    def add_move(self, board, piece, move, captured=False, is_check=False, is_checkmate=False):
        """Add a move to history in algebraic notation"""
        notation = self._to_algebraic_notation(board, piece, move, captured, is_check, is_checkmate)
        
        move_data = {
            'notation': notation,
            'piece': piece.name,
            'color': piece.color,
            'from': (move.initial.row, move.initial.col),
            'to': (move.final.row, move.final.col),
            'captured': captured,
            'move_number': self.move_number
        }
        
        self.moves.append(move_data)
        
        # Increment move number after black's move
        if piece.color == 'black':
            self.move_number += 1
        
        return notation
    
    def _to_algebraic_notation(self, board, piece, move, captured, is_check, is_checkmate):
        """Convert move to algebraic notation (e.g., Nf3, exd5, O-O)"""
        notation = ''
        
        # Check for castling
        if isinstance(piece, King):
            col_diff = move.final.col - move.initial.col
            if abs(col_diff) == 2:
                if col_diff > 0:
                    return 'O-O'  # Kingside castling
                else:
                    return 'O-O-O'  # Queenside castling
        
        # Piece prefix (except for pawns)
        if not isinstance(piece, Pawn):
            piece_symbols = {
                'knight': 'N',
                'bishop': 'B',
                'rook': 'R',
                'queen': 'Q',
                'king': 'K'
            }
            notation += piece_symbols.get(piece.name, '')
            
            # Add disambiguation if needed (multiple pieces of same type can move to same square)
            disambiguation = self._get_disambiguation(board, piece, move)
            notation += disambiguation
        else:
            # For pawn captures, include the file
            if captured:
                notation += self._col_to_file(move.initial.col)
        
        # Capture symbol
        if captured:
            notation += 'x'
        
        # Destination square
        notation += self._col_to_file(move.final.col)
        notation += str(8 - move.final.row)
        
        # Pawn promotion
        if isinstance(piece, Pawn) and (move.final.row == 0 or move.final.row == 7):
            notation += '=Q'  # Assuming promotion to queen
        
        # Check or checkmate
        if is_checkmate:
            notation += '#'
        elif is_check:
            notation += '+'
        
        return notation
    
    def _get_disambiguation(self, board, piece, move):
        """Get disambiguation letter/number if multiple pieces can move to same square"""
        same_type_pieces = []
        
        # Find all pieces of same type and color
        for row in range(8):
            for col in range(8):
                sq = board.squares[row][col]
                if sq.has_piece():
                    p = sq.piece
                    if (p.name == piece.name and p.color == piece.color and 
                        not (row == move.initial.row and col == move.initial.col)):
                        # Check if this piece can also move to the destination
                        board.calc_moves(p, row, col, bool=True)
                        for m in p.moves:
                            if m.final.row == move.final.row and m.final.col == move.final.col:
                                same_type_pieces.append((row, col))
                                break
        
        if not same_type_pieces:
            return ''
        
        # Check if file disambiguation is enough
        same_file = any(col == move.initial.col for row, col in same_type_pieces)
        same_rank = any(row == move.initial.row for row, col in same_type_pieces)
        
        if not same_file:
            return self._col_to_file(move.initial.col)
        elif not same_rank:
            return str(8 - move.initial.row)
        else:
            # Need both file and rank
            return self._col_to_file(move.initial.col) + str(8 - move.initial.row)
    
    def _col_to_file(self, col):
        """Convert column number to file letter (0->a, 1->b, etc.)"""
        return chr(ord('a') + col)
    
    def get_pgn_format(self):
        """Get moves in PGN (Portable Game Notation) format"""
        pgn = []
        white_move = None
        
        for move_data in self.moves:
            if move_data['color'] == 'white':
                white_move = move_data['notation']
            else:
                # Black's move - output the pair
                move_num = move_data['move_number'] - 1
                pgn.append(f"{move_num}. {white_move} {move_data['notation']}")
                white_move = None
        
        # If there's a remaining white move
        if white_move:
            pgn.append(f"{self.move_number}. {white_move}")
        
        return ' '.join(pgn)
    
    def get_last_move(self):
        """Get the last move"""
        return self.moves[-1] if self.moves else None
    
    def get_move_list(self):
        """Get formatted move list for display"""
        formatted = []
        white_move = None
        move_num = 1
        
        for move_data in self.moves:
            if move_data['color'] == 'white':
                white_move = move_data['notation']
                move_num = move_data['move_number']
            else:
                # Black's move - output the pair
                formatted.append({
                    'number': move_num,
                    'white': white_move,
                    'black': move_data['notation']
                })
                white_move = None
        
        # If there's a remaining white move
        if white_move:
            formatted.append({
                'number': move_num,
                'white': white_move,
                'black': ''
            })
        
        return formatted
    
    def clear(self):
        """Clear move history"""
        self.moves = []
        self.move_number = 1
    
    def undo_last_move(self):
        """Remove the last move from history"""
        if self.moves:
            last_move = self.moves.pop()
            # Decrement move number if we're undoing a black move
            if last_move['color'] == 'black':
                self.move_number -= 1
            return last_move
        return None
