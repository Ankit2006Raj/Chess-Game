import os
import sys
from flask import Flask, jsonify, request, send_from_directory, render_template

# Locate game logic (prefer web/src, fallback to project src)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WEB_SRC = os.path.join(os.path.dirname(__file__), 'src')
if os.path.exists(WEB_SRC):
    SRC = WEB_SRC
else:
    SRC = os.path.join(ROOT, 'src')

if SRC not in sys.path:
    sys.path.insert(0, SRC)

from src.board import Board
from src.move import Move
from src.square import Square
from src.game_state import GameState
from src.move_history import MoveHistory
from src.ai_engine import AIEngine
from src.captured_pieces import CapturedPieces
from src.chess_clock import ChessClock
from src.game_persistence import GamePersistence
import copy

app = Flask(__name__, template_folder='templates', static_folder='static')

# In-memory single game instance (suitable for single-worker deployments)
GAME = {
    'board': Board(),
    'next_player': 'white',
    'history': [],
    'game_state': GameState(),
    'move_history': MoveHistory(),
    'ai_enabled': False,
    'ai_color': 'black',
    'ai_engine': AIEngine(difficulty='medium'),
    'captured_pieces': CapturedPieces(),
    'chess_clock': ChessClock(time_control='unlimited'),
    'persistence': GamePersistence()
}


def _short_name(long_name):
    mapping = {'pawn': 'p', 'rook': 'r', 'knight': 'n', 'bishop': 'b', 'queen': 'q', 'king': 'k'}
    return mapping.get(long_name, long_name[:1])


def serialize_board(board):
    pieces = []
    for r in range(8):
        for c in range(8):
            sq = board.squares[r][c]
            if sq.has_piece():
                p = sq.piece
                pieces.append({'row': r, 'col': c, 'name': _short_name(p.name), 'color': 'w' if p.color == 'white' else 'b'})

    last = None
    if getattr(board, 'last_move', None):
        last = {
            'initial': {'row': board.last_move.initial.row, 'col': board.last_move.initial.col},
            'final': {'row': board.last_move.final.row, 'col': board.last_move.final.col}
        }

    return {'rows': 8, 'cols': 8, 'pieces': pieces, 'last_move': last}


@app.route('/')
def index():
    # Add cache control headers to prevent caching
    response = app.make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/test')
def test():
    # Test page to verify features are loaded
    response = app.make_response(render_template('test.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


# Explicit static route to ensure `/static/...` is served from the `web/static` folder
@app.route('/static-files/<path:filename>')
def static_files(filename):
    # Serve files from `web/static` under a custom path `/static-files/...`
    web_static = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
    return send_from_directory(web_static, filename)


@app.route('/__diag/static_check')
def diag_static_check():
    """Diagnostic: return info about the PNG we expect to serve."""
    web_static = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
    imgs_dir = os.path.join(web_static, 'images', 'imgs-80px')
    target = os.path.join(imgs_dir, 'white_pawn.png')
    info = {
        'web_static': web_static,
        'imgs_dir': imgs_dir,
        'target_path': target,
        'exists': os.path.exists(target),
    }
    try:
        if info['exists']:
            info['size_bytes'] = os.path.getsize(target)
        info['listing'] = sorted(os.listdir(imgs_dir))
    except Exception as e:
        info['listing_error'] = str(e)

    return jsonify(info)


@app.route('/static/images/<path:filename>')
def static_images(filename):
    # Serve images from the project's `assets/images` so we don't need to duplicate large files.
    images_dir = os.path.abspath(os.path.join(ROOT, 'assets', 'images'))
    return send_from_directory(images_dir, filename)


@app.route('/api/state')
def api_state():
    board = GAME['board']
    game_state = GAME['game_state']
    move_history = GAME['move_history']
    captured_pieces = GAME['captured_pieces']
    chess_clock = GAME['chess_clock']
    
    return jsonify({
        'board': serialize_board(board),
        'next_player': GAME['next_player'],
        'game_status': game_state.status,
        'status_message': game_state.get_status_message(),
        'is_check': game_state.in_check,
        'move_history': move_history.get_move_list(),
        'pgn': move_history.get_pgn_format(),
        'ai_enabled': GAME['ai_enabled'],
        'captured_pieces': captured_pieces.get_captured_summary(),
        'clock': chess_clock.get_time_display()
    })


@app.route('/api/reset', methods=['POST'])
def api_reset():
    data = request.get_json() or {}
    time_control = data.get('time_control', 'unlimited')
    
    GAME['board'] = Board()
    GAME['next_player'] = 'white'
    GAME['history'] = []
    GAME['game_state'] = GameState()
    GAME['move_history'] = MoveHistory()
    GAME['captured_pieces'] = CapturedPieces()
    GAME['chess_clock'] = ChessClock(time_control=time_control)
    
    # Start clock for white
    GAME['chess_clock'].start_turn('white')
    
    return jsonify({'ok': True})


@app.route('/api/move', methods=['POST'])
def api_move():
    data = request.get_json() or {}
    try:
        ir = int(data.get('initial_row'))
        ic = int(data.get('initial_col'))
        fr = int(data.get('final_row'))
        fc = int(data.get('final_col'))
    except Exception:
        return jsonify({'ok': False, 'error': 'invalid payload'})

    board = GAME['board']
    game_state = GAME['game_state']
    move_history = GAME['move_history']

    # Check if game is over
    if game_state.is_game_over():
        return jsonify({'ok': False, 'error': 'game is over'})

    # Save a deep copy of the board and current player so we can undo
    try:
        GAME['history'].append((copy.deepcopy(board), GAME['next_player'], copy.deepcopy(game_state), copy.deepcopy(move_history)))
    except Exception:
        # If deepcopy fails for some reason, clear history to avoid inconsistent state
        GAME['history'] = []

    if not Square.in_range(ir, ic, fr, fc):
        return jsonify({'ok': False, 'error': 'out of range'})

    sq = board.squares[ir][ic]
    if not sq.has_piece():
        return jsonify({'ok': False, 'error': 'no piece at initial'})

    piece = sq.piece
    if piece.color != GAME['next_player']:
        return jsonify({'ok': False, 'error': 'not your turn'})

    # calculate valid moves for this piece
    board.calc_moves(piece, ir, ic, bool=True)
    initial = Square(ir, ic)
    final_piece = board.squares[fr][fc].piece if board.squares[fr][fc].has_piece() else None
    final = Square(fr, fc, final_piece)
    move = Move(initial, final)

    if not board.valid_move(piece, move):
        return jsonify({'ok': False, 'error': 'invalid move'})

    # Check if capture
    captured_square = board.squares[fr][fc]
    captured = captured_square.has_piece()
    
    # Track captured piece
    if captured:
        captured_piece = captured_square.piece
        GAME['captured_pieces'].add_captured_piece(captured_piece, piece.color)
    
    # End clock for current player
    GAME['chess_clock'].end_turn(piece.color)

    # perform move
    board.move(piece, move, testing=False)
    board.set_true_en_passant(piece)

    # toggle next player
    GAME['next_player'] = 'white' if GAME['next_player'] == 'black' else 'black'
    
    # Start clock for next player
    GAME['chess_clock'].start_turn(GAME['next_player'])

    # Check game status
    status = game_state.check_game_status(board, GAME['next_player'])
    is_check = status == 'check'
    is_checkmate = status == 'checkmate'
    
    # Check for time out
    if GAME['chess_clock'].is_time_up(GAME['next_player']):
        game_state.status = 'timeout'
        game_state.winner = 'white' if GAME['next_player'] == 'black' else 'black'

    # Add move to history
    move_history.add_move(board, piece, move, captured, is_check, is_checkmate)

    # If AI is enabled and it's AI's turn, make AI move
    if GAME['ai_enabled'] and GAME['next_player'] == GAME['ai_color'] and status == 'active':
        ai_move_result = _make_ai_move()
        if ai_move_result:
            return jsonify({
                'ok': True,
                'board': serialize_board(board),
                'next_player': GAME['next_player'],
                'game_status': game_state.status,
                'status_message': game_state.get_status_message(),
                'is_check': game_state.in_check,
                'move_history': move_history.get_move_list(),
                'ai_moved': True
            })

    return jsonify({
        'ok': True,
        'board': serialize_board(board),
        'next_player': GAME['next_player'],
        'game_status': game_state.status,
        'status_message': game_state.get_status_message(),
        'is_check': game_state.in_check,
        'move_history': move_history.get_move_list()
    })


@app.route('/api/undo', methods=['POST'])
def api_undo():
    """Undo last move by restoring previous board snapshot from history."""
    if not GAME.get('history'):
        return jsonify({'ok': False, 'error': 'no history'})

    prev_board, prev_player, prev_game_state, prev_move_history = GAME['history'].pop()
    GAME['board'] = prev_board
    GAME['next_player'] = prev_player
    GAME['game_state'] = prev_game_state
    GAME['move_history'] = prev_move_history

    return jsonify({
        'ok': True,
        'board': serialize_board(GAME['board']),
        'next_player': GAME['next_player'],
        'game_status': GAME['game_state'].status,
        'status_message': GAME['game_state'].get_status_message(),
        'is_check': GAME['game_state'].in_check,
        'move_history': GAME['move_history'].get_move_list()
    })


@app.route('/api/ai/toggle', methods=['POST'])
def api_ai_toggle():
    """Enable or disable AI opponent"""
    data = request.get_json() or {}
    enabled = data.get('enabled', False)
    color = data.get('color', 'black')
    difficulty = data.get('difficulty', 'medium')
    
    GAME['ai_enabled'] = enabled
    GAME['ai_color'] = color
    GAME['ai_engine'] = AIEngine(difficulty=difficulty)
    
    # If enabling AI and it's AI's turn, make a move
    if enabled and GAME['next_player'] == color and not GAME['game_state'].is_game_over():
        _make_ai_move()
    
    return jsonify({
        'ok': True,
        'ai_enabled': GAME['ai_enabled'],
        'ai_color': GAME['ai_color'],
        'board': serialize_board(GAME['board']),
        'next_player': GAME['next_player'],
        'game_status': GAME['game_state'].status,
        'status_message': GAME['game_state'].get_status_message(),
        'move_history': GAME['move_history'].get_move_list()
    })


def _make_ai_move():
    """Internal function to make AI move"""
    board = GAME['board']
    game_state = GAME['game_state']
    move_history = GAME['move_history']
    
    best_move = GAME['ai_engine'].get_best_move(board, GAME['ai_color'])
    
    if best_move:
        piece, move = best_move
        # Find the actual piece on the board
        actual_piece = board.squares[move.initial.row][move.initial.col].piece
        
        if actual_piece:
            # Save history
            try:
                GAME['history'].append((copy.deepcopy(board), GAME['next_player'], copy.deepcopy(game_state), copy.deepcopy(move_history)))
            except Exception:
                GAME['history'] = []
            
            # Check if capture
            captured = board.squares[move.final.row][move.final.col].has_piece()
            
            # Make the move
            board.move(actual_piece, move, testing=False)
            board.set_true_en_passant(actual_piece)
            
            # Switch turn
            GAME['next_player'] = 'white' if GAME['next_player'] == 'black' else 'black'
            
            # Check game status
            status = game_state.check_game_status(board, GAME['next_player'])
            is_check = status == 'check'
            is_checkmate = status == 'checkmate'
            
            # Add to move history
            move_history.add_move(board, actual_piece, move, captured, is_check, is_checkmate)
            
            return True
    
    return False


@app.route('/api/valid_moves', methods=['POST'])
def api_valid_moves():
    """Get valid moves for a piece at a given position"""
    data = request.get_json() or {}
    try:
        row = int(data.get('row'))
        col = int(data.get('col'))
    except Exception:
        return jsonify({'ok': False, 'error': 'invalid payload'})
    
    board = GAME['board']
    
    if not Square.in_range(row, col):
        return jsonify({'ok': False, 'error': 'out of range'})
    
    sq = board.squares[row][col]
    if not sq.has_piece():
        return jsonify({'ok': False, 'moves': []})
    
    piece = sq.piece
    
    # Calculate valid moves
    board.calc_moves(piece, row, col, bool=True)
    
    # Convert moves to serializable format
    moves = []
    for move in piece.moves:
        is_capture = board.squares[move.final.row][move.final.col].has_piece()
        moves.append({
            'row': move.final.row,
            'col': move.final.col,
            'is_capture': is_capture
        })
    
    return jsonify({'ok': True, 'moves': moves})


@app.route('/api/save', methods=['POST'])
def api_save():
    """Save current game"""
    data = request.get_json() or {}
    filename = data.get('filename')
    
    game_data = {
        'board': GAME['board'],
        'next_player': GAME['next_player'],
        'move_history': GAME['move_history'].moves,
        'game_status': GAME['game_state'].status,
        'captured_pieces': GAME['captured_pieces'].get_captured_summary(),
        'time_white': GAME['chess_clock'].white_time,
        'time_black': GAME['chess_clock'].black_time,
        'ai_enabled': GAME['ai_enabled'],
        'ai_color': GAME['ai_color'],
        'ai_difficulty': GAME['ai_engine'].difficulty
    }
    
    try:
        saved_filename = GAME['persistence'].save_game(game_data, filename)
        return jsonify({'ok': True, 'filename': saved_filename})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


@app.route('/api/load', methods=['POST'])
def api_load():
    """Load a saved game"""
    data = request.get_json() or {}
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'ok': False, 'error': 'filename required'})
    
    try:
        game_data = GAME['persistence'].load_game(filename)
        
        # Reconstruct board from saved state
        GAME['board'] = Board()
        board_state = game_data.get('board_state')
        if board_state and board_state.get('pieces'):
            # Clear board
            for row in range(8):
                for col in range(8):
                    GAME['board'].squares[row][col].piece = None
            
            # Place pieces
            from src.piece import Pawn, Knight, Bishop, Rook, Queen, King
            piece_classes = {
                'pawn': Pawn,
                'knight': Knight,
                'bishop': Bishop,
                'rook': Rook,
                'queen': Queen,
                'king': King
            }
            
            for piece_data in board_state['pieces']:
                piece_class = piece_classes.get(piece_data['name'])
                if piece_class:
                    piece = piece_class(piece_data['color'])
                    piece.moved = piece_data.get('moved', False)
                    GAME['board'].squares[piece_data['row']][piece_data['col']].piece = piece
        
        # Restore game state
        GAME['next_player'] = game_data.get('next_player', 'white')
        
        # Restore move history
        GAME['move_history'] = MoveHistory()
        for move_data in game_data.get('move_history', []):
            GAME['move_history'].moves.append(move_data)
        
        # Restore game state
        GAME['game_state'] = GameState()
        GAME['game_state'].status = game_data.get('game_status', 'active')
        
        # Restore clock
        GAME['chess_clock'].white_time = game_data.get('time_white')
        GAME['chess_clock'].black_time = game_data.get('time_black')
        
        # Restore AI settings
        GAME['ai_enabled'] = game_data.get('ai_enabled', False)
        GAME['ai_color'] = game_data.get('ai_color', 'black')
        
        return jsonify({
            'ok': True,
            'board': serialize_board(GAME['board']),
            'next_player': GAME['next_player'],
            'move_history': GAME['move_history'].get_move_list(),
            'game_status': GAME['game_state'].status
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


@app.route('/api/saved_games', methods=['GET'])
def api_saved_games():
    """List all saved games"""
    try:
        games = GAME['persistence'].list_saved_games()
        return jsonify({'ok': True, 'games': games})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


@app.route('/api/delete_game', methods=['POST'])
def api_delete_game():
    """Delete a saved game"""
    data = request.get_json() or {}
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'ok': False, 'error': 'filename required'})
    
    try:
        success = GAME['persistence'].delete_game(filename)
        return jsonify({'ok': success})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


@app.route('/api/export_pgn', methods=['POST'])
def api_export_pgn():
    """Export game as PGN file"""
    data = request.get_json() or {}
    filename = data.get('filename')
    
    game_data = {
        'game_status': GAME['game_state'].status,
        'winner': GAME['game_state'].winner,
        'pgn': GAME['move_history'].get_pgn_format()
    }
    
    try:
        pgn_filename = GAME['persistence'].export_pgn(game_data, filename)
        return jsonify({'ok': True, 'filename': pgn_filename})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


@app.route('/api/clock/set', methods=['POST'])
def api_set_clock():
    """Set time control"""
    data = request.get_json() or {}
    time_control = data.get('time_control', 'unlimited')
    
    GAME['chess_clock'] = ChessClock(time_control=time_control)
    GAME['chess_clock'].start_turn(GAME['next_player'])
    
    return jsonify({'ok': True, 'clock': GAME['chess_clock'].get_time_display()})


if __name__ == '__main__':
    # Run without the reloader for predictable background starts from automation
    app.run(host='127.0.0.1', debug=False, port=int(os.environ.get('PORT', 5000)))
