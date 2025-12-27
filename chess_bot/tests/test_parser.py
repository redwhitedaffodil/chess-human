"""Unit tests for board parser module."""
import unittest
from unittest.mock import Mock, MagicMock
import chess
from chess_bot.src.board_parser import BoardParser


class TestBoardParser(unittest.TestCase):
    """Test cases for BoardParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = BoardParser()
    
    def test_square_notation_to_index_valid(self):
        """Test valid square notation conversions."""
        # Test corners
        self.assertEqual(self.parser._square_notation_to_index('square-11'), 0)  # a1
        self.assertEqual(self.parser._square_notation_to_index('square-81'), 7)  # h1
        self.assertEqual(self.parser._square_notation_to_index('square-18'), 56)  # a8
        self.assertEqual(self.parser._square_notation_to_index('square-88'), 63)  # h8
        
        # Test common squares
        self.assertEqual(self.parser._square_notation_to_index('square-51'), 4)  # e1
        self.assertEqual(self.parser._square_notation_to_index('square-52'), 12)  # e2
        self.assertEqual(self.parser._square_notation_to_index('square-45'), 35)  # d5
    
    def test_square_notation_to_index_invalid(self):
        """Test invalid square notations."""
        self.assertIsNone(self.parser._square_notation_to_index('invalid'))
        self.assertIsNone(self.parser._square_notation_to_index('square-99'))
        self.assertIsNone(self.parser._square_notation_to_index('square-00'))
        self.assertIsNone(self.parser._square_notation_to_index('square-123'))
        self.assertIsNone(self.parser._square_notation_to_index(''))
    
    def test_parse_piece_class_white(self):
        """Test parsing white piece classes."""
        self.assertEqual(
            self.parser._parse_piece_class('piece wk square-51'),
            ('w', 'k')
        )
        self.assertEqual(
            self.parser._parse_piece_class('piece wq square-41'),
            ('w', 'q')
        )
        self.assertEqual(
            self.parser._parse_piece_class('piece wp square-52'),
            ('w', 'p')
        )
    
    def test_parse_piece_class_black(self):
        """Test parsing black piece classes."""
        self.assertEqual(
            self.parser._parse_piece_class('piece bk square-58'),
            ('b', 'k')
        )
        self.assertEqual(
            self.parser._parse_piece_class('piece bq square-48'),
            ('b', 'q')
        )
        self.assertEqual(
            self.parser._parse_piece_class('piece bn square-27'),
            ('b', 'n')
        )
    
    def test_parse_piece_class_invalid(self):
        """Test invalid piece classes."""
        self.assertIsNone(self.parser._parse_piece_class('no-piece'))
        self.assertIsNone(self.parser._parse_piece_class('square-51'))
        self.assertIsNone(self.parser._parse_piece_class(''))
    
    def test_detect_board_orientation_normal(self):
        """Test detecting normal board orientation."""
        mock_element = Mock()
        mock_element.get_attribute.return_value = 'chess-board'
        
        result = self.parser.detect_board_orientation(mock_element)
        
        self.assertFalse(result)
        self.assertFalse(self.parser.is_flipped)
    
    def test_detect_board_orientation_flipped(self):
        """Test detecting flipped board orientation."""
        mock_element = Mock()
        mock_element.get_attribute.return_value = 'chess-board flipped'
        
        result = self.parser.detect_board_orientation(mock_element)
        
        self.assertTrue(result)
        self.assertTrue(self.parser.is_flipped)
    
    def test_parse_board_starting_position(self):
        """Test parsing a starting position."""
        # Mock board element with starting position pieces
        mock_board = Mock()
        mock_board.get_attribute.return_value = 'chess-board'
        
        # Mock piece elements
        mock_pieces = []
        
        # White pieces
        piece_data = [
            ('wp square-12', 'piece wp square-12'),  # a2 pawn
            ('wn square-21', 'piece wn square-21'),  # b1 knight
            ('wr square-11', 'piece wr square-11'),  # a1 rook
            ('wk square-51', 'piece wk square-51'),  # e1 king
        ]
        
        for _, class_str in piece_data:
            mock_piece = Mock()
            mock_piece.get_attribute.return_value = class_str
            mock_pieces.append(mock_piece)
        
        mock_board.find_elements.return_value = mock_pieces
        
        board = self.parser.parse_board(mock_board)
        
        self.assertIsInstance(board, chess.Board)
        # Verify some pieces are placed
        self.assertIsNotNone(board.piece_at(chess.A2))  # White pawn
        self.assertIsNotNone(board.piece_at(chess.B1))  # White knight
        self.assertIsNotNone(board.piece_at(chess.A1))  # White rook
        self.assertIsNotNone(board.piece_at(chess.E1))  # White king


if __name__ == '__main__':
    unittest.main()
