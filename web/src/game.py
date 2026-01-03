import pygame

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square
from game_state import GameState
from move_history import MoveHistory
from ai_engine import AIEngine
from captured_pieces import CapturedPieces
from chess_clock import ChessClock

class Game:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
        self.game_state = GameState()
        self.move_history = MoveHistory()
        self.ai_enabled = False
        self.ai_color = 'black'
        self.ai_engine = AIEngine(difficulty='medium')
        self.captured_pieces = CapturedPieces()
        self.chess_clock = ChessClock(time_control='unlimited')
        self.valid_moves_for_selected = []  # Store valid moves for highlighting

    # blit methods

    def show_bg(self, surface):
        theme = self.config.theme
        
        for row in range(ROWS):
            for col in range(COLS):
                # color
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                # rect
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

                # row coordinates
                if col == 0:
                    # color
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    # blit
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 7:
                    # color
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                # piece ?
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    
                    # all pieces except dragger piece
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            # loop all valid moves
            for move in piece.moves:
                # Check if this is a capture move
                is_capture = self.board.squares[move.final.row][move.final.col].has_piece()
                
                # Different colors for captures vs normal moves
                if is_capture:
                    # Red tint for captures
                    color = (220, 100, 100) if (move.final.row + move.final.col) % 2 == 0 else (180, 60, 60)
                else:
                    # Normal move highlight
                    color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                
                # rect
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)
                
                # Draw a circle in the center for non-capture moves
                if not is_capture:
                    center = (move.final.col * SQSIZE + SQSIZE // 2, move.final.row * SQSIZE + SQSIZE // 2)
                    pygame.draw.circle(surface, color, center, 15)

    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                # color
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                # rect
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            # color
            color = (180, 180, 180)
            # rect
            rect = (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
            # blit
            pygame.draw.rect(surface, color, rect, width=3)

    # other methods

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'
        
        # Check game status after turn change
        status = self.game_state.check_game_status(self.board, self.next_player)
        
        # If AI is enabled and it's AI's turn, make AI move
        if self.ai_enabled and self.next_player == self.ai_color and status == 'active':
            self.make_ai_move()

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()
    
    def set_time_control(self, time_control):
        """Set time control for the game"""
        self.chess_clock = ChessClock(time_control=time_control)
    
    def get_captured_pieces_display(self):
        """Get captured pieces for display"""
        return self.captured_pieces.get_captured_summary()
    
    def get_clock_display(self):
        """Get clock display"""
        return self.chess_clock.get_time_display()
    
    def enable_ai(self, enabled=True, color='black', difficulty='medium'):
        """Enable or disable AI opponent"""
        self.ai_enabled = enabled
        self.ai_color = color
        self.ai_engine = AIEngine(difficulty=difficulty)
    
    def make_ai_move(self):
        """Make AI move"""
        best_move = self.ai_engine.get_best_move(self.board, self.ai_color)
        
        if best_move:
            piece, move = best_move
            # Find the actual piece on the board
            actual_piece = self.board.squares[move.initial.row][move.initial.col].piece
            
            if actual_piece:
                # Check if capture
                captured_square = self.board.squares[move.final.row][move.final.col]
                captured = captured_square.has_piece()
                
                # Track captured piece
                if captured:
                    captured_piece = captured_square.piece
                    self.captured_pieces.add_captured_piece(captured_piece, self.ai_color)
                
                # End clock for AI
                self.chess_clock.end_turn(self.ai_color)
                
                # Make the move
                self.board.move(actual_piece, move, testing=False)
                self.board.set_true_en_passant(actual_piece)
                
                # Add to move history
                status = self.game_state.check_game_status(self.board, self.next_player)
                is_check = status == 'check'
                is_checkmate = status == 'checkmate'
                self.move_history.add_move(self.board, actual_piece, move, captured, is_check, is_checkmate)
                
                # Play sound
                self.play_sound(captured)
                
                # Switch turn
                self.next_player = 'white' if self.next_player == 'black' else 'black'
                
                # Start clock for next player
                self.chess_clock.start_turn(self.next_player)
                
                # Check game status for the new player
                self.game_state.check_game_status(self.board, self.next_player)
    
    def get_game_status(self):
        """Get current game status"""
        return self.game_state.get_status_message()
    
    def is_game_over(self):
        """Check if game is over"""
        return self.game_state.is_game_over()