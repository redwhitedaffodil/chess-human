"""Configuration settings for the chess bot."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration dataclass for all bot settings."""
    
    # Stockfish settings
    stockfish_path: str = "/usr/games/stockfish"
    analysis_time: float = 1.0  # seconds
    multipv_count: int = 15  # Number of principal variations to analyze
    
    # Humanization parameters
    target_elo_advantage: int = 300  # Target ELO advantage in centipawns
    elo_std_dev: int = 100  # Standard deviation for CP distribution
    obvious_move_threshold: int = 300  # CP difference to consider a move obvious
    
    # Timing parameters
    min_move_time: float = 0.5  # Minimum seconds before moving
    max_move_time: float = 2.0  # Maximum seconds before moving
    
    # Browser settings
    headless: bool = False
    chess_url: str = "https://www.chess.com/play/online"
    
    # Board settings
    square_size: Optional[int] = None  # Will be calculated from actual board
    board_offset_x: int = 0
    board_offset_y: int = 0
    
    # Logging
    log_level: str = "INFO"
