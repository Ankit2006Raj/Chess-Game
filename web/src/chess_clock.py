"""
Chess Clock - Time control management
"""
import time

class ChessClock:
    
    # Time control presets (in seconds)
    TIME_CONTROLS = {
        'bullet': {'time': 60, 'increment': 0, 'name': 'Bullet (1+0)'},
        'blitz': {'time': 300, 'increment': 0, 'name': 'Blitz (5+0)'},
        'blitz_inc': {'time': 180, 'increment': 2, 'name': 'Blitz (3+2)'},
        'rapid': {'time': 600, 'increment': 0, 'name': 'Rapid (10+0)'},
        'rapid_inc': {'time': 600, 'increment': 5, 'name': 'Rapid (10+5)'},
        'classical': {'time': 1800, 'increment': 0, 'name': 'Classical (30+0)'},
        'unlimited': {'time': None, 'increment': 0, 'name': 'Unlimited'}
    }
    
    def __init__(self, time_control='unlimited'):
        """
        Initialize chess clock
        time_control: 'bullet', 'blitz', 'rapid', 'classical', or 'unlimited'
        """
        self.time_control = time_control
        control = self.TIME_CONTROLS.get(time_control, self.TIME_CONTROLS['unlimited'])
        
        self.white_time = control['time']  # Remaining time in seconds
        self.black_time = control['time']
        self.increment = control['increment']
        
        self.active_color = None
        self.start_time = None
        self.paused = False
        
        self.move_times = []  # Track time per move
    
    def start_turn(self, color):
        """Start timing for a player's turn"""
        if self.white_time is None:  # Unlimited time
            return
        
        self.active_color = color
        self.start_time = time.time()
        self.paused = False
    
    def end_turn(self, color):
        """End timing for a player's turn and add increment"""
        if self.white_time is None:  # Unlimited time
            return
        
        if self.active_color != color or self.start_time is None:
            return
        
        # Calculate elapsed time
        elapsed = time.time() - self.start_time
        
        # Deduct time
        if color == 'white':
            self.white_time = max(0, self.white_time - elapsed)
            # Add increment
            if self.increment > 0:
                self.white_time += self.increment
        else:
            self.black_time = max(0, self.black_time - elapsed)
            # Add increment
            if self.increment > 0:
                self.black_time += self.increment
        
        # Record move time
        self.move_times.append({
            'color': color,
            'time': elapsed,
            'remaining': self.white_time if color == 'white' else self.black_time
        })
        
        self.active_color = None
        self.start_time = None
    
    def get_remaining_time(self, color):
        """Get remaining time for a player"""
        if self.white_time is None:  # Unlimited time
            return None
        
        base_time = self.white_time if color == 'white' else self.black_time
        
        # If this player's clock is running, subtract elapsed time
        if self.active_color == color and self.start_time and not self.paused:
            elapsed = time.time() - self.start_time
            return max(0, base_time - elapsed)
        
        return base_time
    
    def is_time_up(self, color):
        """Check if a player has run out of time"""
        if self.white_time is None:  # Unlimited time
            return False
        
        remaining = self.get_remaining_time(color)
        return remaining <= 0
    
    def pause(self):
        """Pause the clock"""
        if self.active_color and self.start_time and not self.paused:
            # Save elapsed time
            elapsed = time.time() - self.start_time
            if self.active_color == 'white':
                self.white_time = max(0, self.white_time - elapsed)
            else:
                self.black_time = max(0, self.black_time - elapsed)
            
            self.paused = True
            self.start_time = None
    
    def resume(self):
        """Resume the clock"""
        if self.paused and self.active_color:
            self.start_time = time.time()
            self.paused = False
    
    def reset(self, time_control=None):
        """Reset the clock"""
        if time_control:
            self.time_control = time_control
        
        control = self.TIME_CONTROLS.get(self.time_control, self.TIME_CONTROLS['unlimited'])
        self.white_time = control['time']
        self.black_time = control['time']
        self.increment = control['increment']
        
        self.active_color = None
        self.start_time = None
        self.paused = False
        self.move_times = []
    
    def format_time(self, seconds):
        """Format time in MM:SS or HH:MM:SS"""
        if seconds is None:
            return "∞"
        
        seconds = int(seconds)
        
        if seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}:{secs:02d}"
    
    def get_time_display(self):
        """Get formatted time display for both players"""
        return {
            'white': self.format_time(self.get_remaining_time('white')),
            'black': self.format_time(self.get_remaining_time('black')),
            'white_seconds': self.get_remaining_time('white'),
            'black_seconds': self.get_remaining_time('black'),
            'active': self.active_color,
            'control': self.TIME_CONTROLS[self.time_control]['name']
        }
    
    def get_average_move_time(self, color):
        """Get average time per move for a player"""
        moves = [m for m in self.move_times if m['color'] == color]
        if not moves:
            return 0
        return sum(m['time'] for m in moves) / len(moves)
    
    def get_state(self):
        """Get complete clock state for saving"""
        return {
            'time_control': self.time_control,
            'white_time': self.white_time,
            'black_time': self.black_time,
            'increment': self.increment,
            'active_color': self.active_color,
            'paused': self.paused,
            'move_times': self.move_times
        }
    
    def load_state(self, state):
        """Load clock state from saved data"""
        self.time_control = state.get('time_control', 'unlimited')
        self.white_time = state.get('white_time')
        self.black_time = state.get('black_time')
        self.increment = state.get('increment', 0)
        self.active_color = state.get('active_color')
        self.paused = state.get('paused', False)
        self.move_times = state.get('move_times', [])
        self.start_time = None
