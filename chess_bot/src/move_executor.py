"""Move executor module for performing chess moves via Selenium."""
import chess
from typing import Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains


class MoveExecutor:
    """Executes chess moves by clicking on the board."""
    
    def __init__(self, driver: WebDriver, board_element: WebElement, is_flipped: bool = False):
        """
        Initialize the move executor.
        
        Args:
            driver: Selenium WebDriver instance
            board_element: WebElement representing the chess board
            is_flipped: Whether the board is flipped (playing as black)
        """
        self.driver = driver
        self.board_element = board_element
        self.is_flipped = is_flipped
        self.square_size = None
        self._calculate_square_size()
    
    def _calculate_square_size(self):
        """Calculate the size of each square on the board."""
        try:
            board_size = self.board_element.size
            # Assuming board is square
            self.square_size = board_size['width'] / 8
        except Exception:
            # Default fallback
            self.square_size = 60
    
    def _square_to_coordinates(self, square: chess.Square) -> Tuple[int, int]:
        """
        Convert a chess square to pixel coordinates on the board.
        
        Args:
            square: chess.Square (0-63)
            
        Returns:
            Tuple of (x, y) pixel coordinates relative to board element
        """
        # Get file (0-7) and rank (0-7) from square index
        file_idx = chess.square_file(square)
        rank_idx = chess.square_rank(square)
        
        # Handle flipped board
        if self.is_flipped:
            file_idx = 7 - file_idx
            rank_idx = 7 - rank_idx
        
        # Calculate pixel position (center of square)
        # Ranks are numbered from bottom (0) to top (7)
        # But visually, rank 7 is at the top, so we need to flip
        visual_rank = 7 - rank_idx
        
        x = int((file_idx + 0.5) * self.square_size)
        y = int((visual_rank + 0.5) * self.square_size)
        
        return (x, y)
    
    def execute_move(self, move: chess.Move):
        """
        Execute a chess move by clicking on the board.
        
        Args:
            move: chess.Move object to execute
        """
        from_square = move.from_square
        to_square = move.to_square
        
        # Get coordinates for both squares
        from_x, from_y = self._square_to_coordinates(from_square)
        to_x, to_y = self._square_to_coordinates(to_square)
        
        # Create action chain for clicking
        actions = ActionChains(self.driver)
        
        # Move to the piece and click
        actions.move_to_element_with_offset(self.board_element, from_x, from_y)
        actions.click()
        
        # Move to destination and click
        actions.move_to_element_with_offset(self.board_element, to_x, to_y)
        actions.click()
        
        # Perform the actions
        actions.perform()
    
    def execute_uci_move(self, uci_move: str):
        """
        Execute a move given in UCI notation.
        
        Args:
            uci_move: UCI format move string (e.g., 'e2e4')
        """
        move = chess.Move.from_uci(uci_move)
        self.execute_move(move)
    
    def update_board_state(self, board_element: WebElement, is_flipped: bool):
        """
        Update the board element and flip state.
        
        Args:
            board_element: New board element
            is_flipped: New flip state
        """
        self.board_element = board_element
        self.is_flipped = is_flipped
        self._calculate_square_size()
