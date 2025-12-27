"""Game controller module for orchestrating the chess bot."""
import chess
import logging
import time
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .board_parser import BoardParser
from .engine_wrapper import EngineWrapper
from .humanizer import Humanizer
from .move_executor import MoveExecutor
from .config import Config


class GameController:
    """Main orchestrator for the chess bot."""
    
    def __init__(self, driver: WebDriver, config: Config):
        """
        Initialize the game controller.
        
        Args:
            driver: Selenium WebDriver instance
            config: Configuration object
        """
        self.driver = driver
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.board_parser = BoardParser()
        self.engine = EngineWrapper(
            config.stockfish_path,
            multipv=config.multipv_count
        )
        self.humanizer = Humanizer(
            target_elo_advantage=config.target_elo_advantage,
            elo_std_dev=config.elo_std_dev,
            obvious_move_threshold=config.obvious_move_threshold,
            min_move_time=config.min_move_time,
            max_move_time=config.max_move_time
        )
        
        self.move_executor: Optional[MoveExecutor] = None
        self.current_board: Optional[chess.Board] = None
        self.last_move_count = 0
    
    def _find_board_element(self):
        """Find the chess board element on the page."""
        try:
            # Wait for board to be present
            wait = WebDriverWait(self.driver, 10)
            board = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "wc-chess-board"))
            )
            return board
        except Exception as e:
            self.logger.error(f"Failed to find board element: {e}")
            return None
    
    def _is_our_turn(self, board: chess.Board) -> bool:
        """
        Determine if it's our turn to move.
        
        Args:
            board: Current chess board state
            
        Returns:
            True if it's our turn
        """
        # Check if the move count has changed
        current_move_count = len(board.move_stack)
        
        if current_move_count != self.last_move_count:
            self.last_move_count = current_move_count
            # After opponent moves, it's our turn
            return True
        
        return False
    
    def _detect_game_over(self, board: chess.Board) -> bool:
        """
        Check if the game is over.
        
        Args:
            board: Current chess board state
            
        Returns:
            True if game is over
        """
        if board.is_game_over():
            outcome = board.outcome()
            if outcome:
                self.logger.info(f"Game over: {outcome.termination.name}")
                if outcome.winner is not None:
                    winner = "White" if outcome.winner == chess.WHITE else "Black"
                    self.logger.info(f"Winner: {winner}")
                else:
                    self.logger.info("Game drawn")
            return True
        return False
    
    def _make_move(self, board: chess.Board):
        """
        Analyze position and make a move.
        
        Args:
            board: Current chess board state
        """
        # Analyze position
        self.logger.info("Analyzing position...")
        evaluations = self.engine.analyze(board, self.config.analysis_time)
        
        if not evaluations:
            self.logger.warning("No legal moves available")
            return
        
        # Log top moves
        self.logger.info(f"Top move: {evaluations[0].move.uci()} (score: {evaluations[0].score})")
        
        # Select move humanistically
        should_move, selected_move = self.humanizer.should_move(evaluations)
        
        if not should_move or selected_move is None:
            self.logger.warning("Humanizer decided not to move")
            return
        
        # Add realistic delay
        self.humanizer.add_realistic_delay()
        
        # Convert move to algebraic notation for logging
        from_square = chess.square_name(selected_move.from_square)
        to_square = chess.square_name(selected_move.to_square)
        
        self.logger.info(f"Moving piece from {from_square} to {to_square}!")
        
        # Execute move
        self.move_executor.execute_move(selected_move)
        
        # Update internal board state
        board.push(selected_move)
    
    def start(self):
        """Start the engine."""
        self.engine.start()
        self.logger.info("Engine started")
    
    def stop(self):
        """Stop the engine."""
        self.engine.quit()
        self.logger.info("Engine stopped")
    
    def run(self):
        """
        Main game loop.
        
        This method runs continuously, monitoring the game state and making moves.
        """
        self.start()
        
        try:
            # Find the board
            board_element = self._find_board_element()
            if not board_element:
                self.logger.error("Could not find chess board")
                return
            
            # Initialize move executor
            self.move_executor = MoveExecutor(
                self.driver,
                board_element,
                is_flipped=False
            )
            
            self.logger.info("Starting game loop...")
            
            # Main game loop
            while True:
                try:
                    # Get current board element (may change)
                    board_element = self._find_board_element()
                    if not board_element:
                        self.logger.warning("Board element not found, retrying...")
                        time.sleep(1)
                        continue
                    
                    # Parse board state
                    board = self.board_parser.parse_board(board_element)
                    self.current_board = board
                    
                    # Update move executor with current state
                    self.move_executor.update_board_state(
                        board_element,
                        self.board_parser.is_flipped
                    )
                    
                    # Check if game is over
                    if self._detect_game_over(board):
                        self.logger.info("Game finished")
                        break
                    
                    # Check if it's our turn
                    if self._is_our_turn(board):
                        self._make_move(board)
                    
                    # Small delay before next iteration
                    time.sleep(0.5)
                    
                except KeyboardInterrupt:
                    self.logger.info("Game interrupted by user")
                    break
                except Exception as e:
                    self.logger.error(f"Error in game loop: {e}", exc_info=True)
                    time.sleep(2)
        
        finally:
            self.stop()
