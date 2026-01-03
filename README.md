# ♔ Chess Master - Professional Web Chess Application

A feature-rich, web-based chess game built with Python Flask and modern JavaScript. Play against AI opponents, track your moves, manage time controls, and enjoy a beautiful, responsive interface.
<img width="1339" height="655" alt="image" src="https://github.com/user-attachments/assets/065c4e0a-a634-438e-9166-bfd447cff419" />


![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.2-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

## ✨ Features

### Core Gameplay
- **Full Chess Rules Implementation** - Complete chess logic with all standard rules
- **Valid Move Highlighting** - Visual indicators for legal moves and captures
- **Move Validation** - Real-time validation preventing illegal moves
- **Check & Checkmate Detection** - Automatic game state detection
- **Stalemate Detection** - Recognizes draw conditions

### AI Opponent
- **Three Difficulty Levels** - Easy, Medium, and Hard AI opponents
- **Configurable AI Color** - Play as White or Black against the computer
- **Smart Move Evaluation** - AI uses position evaluation and move scoring

### Time Controls
- **Multiple Time Formats**
  - Unlimited (No time limit)
  - Bullet (1+0)
  - Blitz (5+0, 3+2)
  - Rapid (10+0, 10+5)
  - Classical (30+0)
- **Live Clock Display** - Real-time countdown for both players
- **Time-Out Detection** - Automatic loss on time expiration

### Game Management
- **Save/Load Games** - Persist game state to disk
- **Move History** - Complete move notation in algebraic format
- **PGN Export** - Export games in standard PGN format
- **Undo Moves** - Step back through game history
- **Captured Pieces Tracking** - Visual display of captured pieces
- **Material Advantage** - Real-time material count

### User Interface
- **Modern, Responsive Design** - Beautiful gradient UI with smooth animations
- **Drag & Drop** - Intuitive piece movement
- **Board Flip** - View from either player's perspective
- **Coordinate Display** - Optional board coordinates
- **Visual Feedback** - Highlights for last move, valid moves, and checks

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Ankit2006Raj/chess-master.git
cd chess-master
```

2. **Install dependencies**
```bash
cd web
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Open your browser**
Navigate to `http://127.0.0.1:5000`

## 🎮 How to Play

### Basic Controls
- **Click or Drag** pieces to move them
- **Valid moves** are highlighted when you select a piece
- **Capture moves** are shown with a red border
- **Undo** button to take back moves
- **Reset** to start a new game

### Keyboard Shortcuts (Desktop Version)
- `T` - Change theme
- `R` - Reset game
- `A` - Toggle AI
- `H` - Print move history
- `S` - Print game status

### Game Options
1. **Time Control** - Select from dropdown before starting a new game
2. **AI Opponent** - Enable AI, choose color and difficulty
3. **Display Options** - Toggle valid move highlights and coordinates

## 📁 Project Structure

```
chess-master/
├── web/
│   ├── app.py                 # Flask application & API endpoints
│   ├── requirements.txt       # Python dependencies
│   ├── src/                   # Game logic modules
│   │   ├── ai_engine.py       # AI opponent implementation
│   │   ├── board.py           # Chess board logic
│   │   ├── game.py            # Game state management
│   │   ├── piece.py           # Chess piece classes
│   │   ├── move.py            # Move representation
│   │   ├── game_state.py      # Check/checkmate detection
│   │   ├── move_history.py    # Move tracking & PGN
│   │   ├── chess_clock.py     # Time control logic
│   │   ├── captured_pieces.py # Captured pieces tracking
│   │   └── game_persistence.py # Save/load functionality
│   ├── templates/
│   │   └── index.html         # Web interface
│   ├── static/
│   │   ├── images/            # Chess piece images
│   │   └── sounds/            # Move & capture sounds
│   └── saved_games/           # Saved game files
└── scripts/
    └── push_to_github.ps1     # Deployment script
```

## 🛠️ Technology Stack

### Backend
- **Flask** - Lightweight Python web framework
- **Python 3.8+** - Core game logic and AI

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with gradients and animations
- **Vanilla JavaScript** - No framework dependencies
- **Drag & Drop API** - Native browser support

### Features Implementation
- **RESTful API** - JSON-based communication
- **Session Management** - In-memory game state
- **File I/O** - Game persistence in JSON format

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/state` | GET | Get current game state |
| `/api/reset` | POST | Start a new game |
| `/api/move` | POST | Make a move |
| `/api/undo` | POST | Undo last move |
| `/api/valid_moves` | POST | Get valid moves for a piece |
| `/api/ai/toggle` | POST | Enable/disable AI |
| `/api/save` | POST | Save current game |
| `/api/load` | POST | Load saved game |
| `/api/saved_games` | GET | List all saved games |
| `/api/export_pgn` | POST | Export game as PGN |
| `/api/clock/set` | POST | Set time control |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- AI may take a few seconds to calculate moves on hard difficulty
- Game state is stored in memory (single-worker deployment only)
- Browser refresh will reset the current game

## 🔮 Future Enhancements

- [ ] Multiplayer support (online play)
- [ ] User authentication and profiles
- [ ] Game analysis and move suggestions
- [ ] Opening book integration
- [ ] Endgame tablebase support
- [ ] Tournament mode
- [ ] Mobile app version
- [ ] Database persistence (PostgreSQL/MongoDB)

## 👨‍💻 Author

**Ankit Raj**  
AIML Student | Web Developer

- 🌐 GitHub: [@Ankit2006Raj](https://github.com/Ankit2006Raj)
- 💼 LinkedIn: [Ankit Raj](https://www.linkedin.com/in/ankit-raj-226a36309)
- 📧 Email: ankit9905163014@gmail.com

---

<div align="center">

### ⭐ Star this repository if you found it helpful!

Made with ❤️ by Ankit Raj

</div>
"# Chess-Game" 
