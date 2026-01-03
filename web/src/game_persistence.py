"""
Game Persistence - Save and load games
"""
import json
import os
from datetime import datetime
import pickle

class GamePersistence:
    
    def __init__(self, save_directory='saved_games'):
        self.save_directory = save_directory
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Create save directory if it doesn't exist"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def save_game(self, game_data, filename=None):
        """
        Save game state to file
        game_data should include: board, move_history, game_state, etc.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chess_game_{timestamp}.json"
        
        filepath = os.path.join(self.save_directory, filename)
        
        # Convert game data to serializable format
        serializable_data = {
            'timestamp': datetime.now().isoformat(),
            'board_state': self._serialize_board(game_data.get('board')),
            'next_player': game_data.get('next_player'),
            'move_history': game_data.get('move_history', []),
            'game_status': game_data.get('game_status', 'active'),
            'captured_pieces': game_data.get('captured_pieces', {}),
            'time_white': game_data.get('time_white', 0),
            'time_black': game_data.get('time_black', 0),
            'ai_enabled': game_data.get('ai_enabled', False),
            'ai_color': game_data.get('ai_color', 'black'),
            'ai_difficulty': game_data.get('ai_difficulty', 'medium')
        }
        
        with open(filepath, 'w') as f:
            json.dump(serializable_data, f, indent=2)
        
        return filename
    
    def load_game(self, filename):
        """Load game state from file"""
        filepath = os.path.join(self.save_directory, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Save file not found: {filename}")
        
        with open(filepath, 'r') as f:
            game_data = json.load(f)
        
        return game_data
    
    def list_saved_games(self):
        """List all saved games"""
        if not os.path.exists(self.save_directory):
            return []
        
        files = [f for f in os.listdir(self.save_directory) if f.endswith('.json')]
        
        games = []
        for filename in files:
            filepath = os.path.join(self.save_directory, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    games.append({
                        'filename': filename,
                        'timestamp': data.get('timestamp'),
                        'next_player': data.get('next_player'),
                        'moves': len(data.get('move_history', [])),
                        'status': data.get('game_status', 'active')
                    })
            except Exception:
                continue
        
        # Sort by timestamp, newest first
        games.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return games
    
    def delete_game(self, filename):
        """Delete a saved game"""
        filepath = os.path.join(self.save_directory, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def _serialize_board(self, board):
        """Convert board to serializable format"""
        if board is None:
            return None
        
        pieces = []
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece():
                    piece = square.piece
                    pieces.append({
                        'row': row,
                        'col': col,
                        'name': piece.name,
                        'color': piece.color,
                        'moved': piece.moved
                    })
        
        return {
            'pieces': pieces,
            'last_move': self._serialize_move(board.last_move) if hasattr(board, 'last_move') and board.last_move else None
        }
    
    def _serialize_move(self, move):
        """Convert move to serializable format"""
        if move is None:
            return None
        
        return {
            'initial': {'row': move.initial.row, 'col': move.initial.col},
            'final': {'row': move.final.row, 'col': move.final.col}
        }
    
    def export_pgn(self, game_data, filename=None):
        """Export game in PGN format"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chess_game_{timestamp}.pgn"
        
        filepath = os.path.join(self.save_directory, filename)
        
        # Create PGN content
        pgn_content = self._create_pgn_content(game_data)
        
        with open(filepath, 'w') as f:
            f.write(pgn_content)
        
        return filename
    
    def _create_pgn_content(self, game_data):
        """Create PGN format content"""
        lines = []
        
        # PGN headers
        lines.append('[Event "Casual Game"]')
        lines.append(f'[Date "{datetime.now().strftime("%Y.%m.%d")}"]')
        lines.append('[White "Player"]')
        lines.append('[Black "Player/AI"]')
        
        result = '*'
        if game_data.get('game_status') == 'checkmate':
            winner = game_data.get('winner', 'unknown')
            result = '1-0' if winner == 'white' else '0-1'
        elif game_data.get('game_status') == 'stalemate':
            result = '1/2-1/2'
        
        lines.append(f'[Result "{result}"]')
        lines.append('')
        
        # Moves
        pgn_moves = game_data.get('pgn', '')
        if pgn_moves:
            lines.append(pgn_moves + ' ' + result)
        else:
            lines.append(result)
        
        return '\n'.join(lines)
