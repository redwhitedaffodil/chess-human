"""Board parser module for extracting chess board state from DOM."""
import chess
from typing import Optional
from selenium.webdriver.remote.webelement import WebElement


class BoardParser:
    """Parses chess.com's DOM to extract board state."""
    
    def __init__(self):
        """Initialize the board parser."""
        self.is_flipped = False
    
    @staticmethod
    def _square_notation_to_index(square_notation: str) -> Optional[int]:
        """
        Convert square-XY notation to chess square index.
        
        Args:
            square_notation: String like 'square-51' where X=file(1-8), Y=rank(1-8)
            
        Returns:
            Chess square index (0-63) or None if invalid
        """
        try:
            # Extract the number from 'square-XY'
            if not square_notation.startswith('square-'):
                return None
            
            num_str = square_notation.split('-')[1]
            if len(num_str) != 2:
                return None
            
            file_num = int(num_str[0])  # 1-8
            rank_num = int(num_str[1])  # 1-8
            
            # Validate range
            if not (1 <= file_num <= 8 and 1 <= rank_num <= 8):
                return None
            
            # Convert to 0-based indices
            file_idx = file_num - 1  # 0-7 (a-h)
            rank_idx = rank_num - 1  # 0-7 (1-8)
            
            # Calculate square index (a1=0, h8=63)
            square_idx = rank_idx * 8 + file_idx
            
            return square_idx
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def _parse_piece_class(piece_class: str) -> Optional[tuple[str, str]]:
        """
        Parse piece type and color from CSS class.
        
        Args:
            piece_class: CSS class string like 'piece wk square-51'
            
        Returns:
            Tuple of (color, piece_type) or None if not a piece
            Colors: 'w' or 'b'
            Piece types: 'p', 'n', 'b', 'r', 'q', 'k'
        """
        classes = piece_class.split()
        
        for cls in classes:
            if len(cls) == 2 and cls[0] in ['w', 'b']:
                color = cls[0]
                piece_type = cls[1]
                
                if piece_type in ['p', 'n', 'b', 'r', 'q', 'k']:
                    return (color, piece_type)
        
        return None
    
    def detect_board_orientation(self, board_element: WebElement) -> bool:
        """
        Detect if the board is flipped (playing as black).
        
        Args:
            board_element: Selenium WebElement of the chess board
            
        Returns:
            True if board is flipped, False otherwise
        """
        try:
            # Check for flipped class or attribute
            class_attr = board_element.get_attribute('class') or ''
            if 'flipped' in class_attr.lower():
                self.is_flipped = True
                return True
            
            # Alternative: check data-orientation attribute
            orientation = board_element.get_attribute('data-orientation')
            if orientation == 'black':
                self.is_flipped = True
                return True
                
        except Exception:
            pass
        
        self.is_flipped = False
        return False
    
    def parse_board(self, board_element: WebElement) -> chess.Board:
        """
        Parse the DOM chess board and return a chess.Board object.
        
        Args:
            board_element: Selenium WebElement of wc-chess-board
            
        Returns:
            chess.Board object representing current position
        """
        board = chess.Board()
        board.clear()  # Start with empty board
        
        # Detect board orientation
        self.detect_board_orientation(board_element)
        
        try:
            # Find all piece elements
            # Assuming pieces have class 'piece' and additional classes for type
            pieces = board_element.find_elements('css selector', '[class*="piece"]')
            
            for piece_elem in pieces:
                class_attr = piece_elem.get_attribute('class') or ''
                
                # Parse piece type and color
                piece_info = self._parse_piece_class(class_attr)
                if not piece_info:
                    continue
                
                color_char, piece_type = piece_info
                
                # Find square notation in classes
                square_notation = None
                for cls in class_attr.split():
                    if cls.startswith('square-'):
                        square_notation = cls
                        break
                
                if not square_notation:
                    continue
                
                # Convert to square index
                square_idx = self._square_notation_to_index(square_notation)
                if square_idx is None:
                    continue
                
                # Create chess piece
                color = chess.WHITE if color_char == 'w' else chess.BLACK
                
                piece_map = {
                    'p': chess.PAWN,
                    'n': chess.KNIGHT,
                    'b': chess.BISHOP,
                    'r': chess.ROOK,
                    'q': chess.QUEEN,
                    'k': chess.KING
                }
                
                piece = chess.Piece(piece_map[piece_type], color)
                board.set_piece_at(square_idx, piece)
        
        except Exception as e:
            # If parsing fails, return starting position
            board.reset()
        
        return board
