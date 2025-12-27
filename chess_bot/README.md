# Chess Bot - Humanized Chess Playing Automation

A sophisticated chess bot that plays chess on chess.com with human-like behavior, using Stockfish for analysis and intelligent move selection to simulate realistic playing patterns.

## Features

- **Humanized Move Selection**: Uses centipawn (CP) distribution with configurable ELO advantage
- **Realistic Timing**: Random delays between moves (0.5s - 2.0s)
- **Multi-PV Analysis**: Analyzes up to 15 principal variations using Stockfish
- **Smart Move Detection**: Identifies obvious moves (forced recaptures, avoiding blunders)
- **Board State Parsing**: Extracts chess position from chess.com's DOM
- **Automated Move Execution**: Uses Selenium for precise click-based move execution

## Project Structure

```
chess_bot/
├── src/
│   ├── __init__.py
│   ├── board_parser.py      # DOM → chess.Board conversion
│   ├── engine_wrapper.py    # Stockfish integration
│   ├── humanizer.py         # Move selection logic
│   ├── move_executor.py     # Selenium click actions
│   ├── game_controller.py   # Main orchestration
│   └── config.py            # Settings & constants
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_humanizer.py
│   └── test_executor.py
├── requirements.txt
├── README.md
└── main.py
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Stockfish chess engine installed on your system
- Google Chrome browser

### Steps

1. Clone the repository:
```bash
git clone https://github.com/redwhitedaffodil/chess-human.git
cd chess-human/chess_bot
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Stockfish:
   - **Ubuntu/Debian**: `sudo apt-get install stockfish`
   - **macOS**: `brew install stockfish`
   - **Windows**: Download from [stockfishchess.org](https://stockfishchess.org/download/)

4. Update the Stockfish path in `src/config.py` if needed (default: `/usr/games/stockfish`)

## Usage

1. Run the bot:
```bash
python main.py
```

2. The browser will open and navigate to chess.com
3. Log in to your chess.com account
4. Start a game (online or vs computer)
5. Press Enter in the terminal when ready
6. The bot will automatically play moves

## Configuration

Edit `src/config.py` to customize bot behavior:

### Stockfish Settings
- `stockfish_path`: Path to Stockfish executable
- `analysis_time`: Time per move for analysis (seconds)
- `multipv_count`: Number of variations to analyze (1-15)

### Humanization Parameters
- `target_elo_advantage`: Target ELO advantage in centipawns (default: 300)
- `elo_std_dev`: Standard deviation for CP distribution (default: 100)
- `obvious_move_threshold`: CP difference for obvious moves (default: 300)

### Timing Parameters
- `min_move_time`: Minimum thinking time (default: 0.5s)
- `max_move_time`: Maximum thinking time (default: 2.0s)

### Browser Settings
- `headless`: Run browser in headless mode (default: False)
- `chess_url`: Chess.com URL to navigate to

## How It Works

### 1. Board Parsing
The bot extracts the current chess position from chess.com's DOM by:
- Locating the `wc-chess-board` element
- Parsing piece CSS classes (e.g., `piece wk square-51`)
- Converting square notation to algebraic format
- Detecting board orientation (flipped for black)

### 2. Position Analysis
Stockfish analyzes the position with multi-PV to get multiple good moves:
- Evaluates top 15 candidate moves
- Converts scores to centipawns from player's perspective
- Handles mate scores appropriately

### 3. Move Selection
The humanizer selects moves using a probabilistic approach:
- Samples a CP setpoint from normal distribution (mean=300, std=100)
- Filters moves that maintain target evaluation
- Detects obvious moves (>300cp better than alternatives)
- Weights selection toward better moves
- Plays obvious moves immediately

### 4. Move Execution
Moves are executed via Selenium:
- Converts UCI moves to pixel coordinates
- Handles flipped board transformations
- Uses ActionChains for click sequences
- Adds realistic delays before moving

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific test files:
```bash
python -m pytest tests/test_parser.py
python -m pytest tests/test_humanizer.py
python -m pytest tests/test_executor.py
```

## Dependencies

- **selenium**: Browser automation
- **python-chess**: Chess logic and board representation
- **numpy**: Statistical distributions for humanization
- **webdriver-manager**: Automatic ChromeDriver management

## Troubleshooting

### Board Not Detected
- Ensure you're on a chess.com game page
- Check browser console for errors
- Verify `wc-chess-board` element exists

### Stockfish Not Found
- Update `stockfish_path` in config.py
- Verify Stockfish is installed: `stockfish` (should open UCI interface)

### Moves Not Executing
- Check board size calculation
- Verify click coordinates are correct
- Ensure no popups are blocking the board

## Disclaimer

This bot is for educational purposes only. Using automation tools may violate chess.com's Terms of Service. Use at your own risk.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Author

Created as a technical demonstration of chess automation with humanized behavior.
