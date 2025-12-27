"""Unit tests for move executor module."""
import unittest
from unittest.mock import Mock, MagicMock, patch
import chess
from chess_bot.src.move_executor import MoveExecutor


class TestMoveExecutor(unittest.TestCase):
    """Test cases for MoveExecutor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_driver = Mock()
        self.mock_board = Mock()
        self.mock_board.size = {'width': 480, 'height': 480}
        
        self.executor = MoveExecutor(
            self.mock_driver,
            self.mock_board,
            is_flipped=False
        )
    
    def test_calculate_square_size(self):
        """Test square size calculation."""
        self.assertEqual(self.executor.square_size, 60)  # 480 / 8
    
    def test_square_to_coordinates_a1(self):
        """Test coordinate calculation for a1."""
        # a1 = square 0 (file 0, rank 0)
        x, y = self.executor._square_to_coordinates(chess.A1)
        
        # File 0, centered at 0.5 * 60 = 30
        # Rank 0 (visual rank 7), centered at 7.5 * 60 = 450
        self.assertEqual(x, 30)
        self.assertEqual(y, 450)
    
    def test_square_to_coordinates_h1(self):
        """Test coordinate calculation for h1."""
        x, y = self.executor._square_to_coordinates(chess.H1)
        
        # File 7, centered at 7.5 * 60 = 450
        # Rank 0 (visual rank 7), centered at 7.5 * 60 = 450
        self.assertEqual(x, 450)
        self.assertEqual(y, 450)
    
    def test_square_to_coordinates_a8(self):
        """Test coordinate calculation for a8."""
        x, y = self.executor._square_to_coordinates(chess.A8)
        
        # File 0, centered at 0.5 * 60 = 30
        # Rank 7 (visual rank 0), centered at 0.5 * 60 = 30
        self.assertEqual(x, 30)
        self.assertEqual(y, 30)
    
    def test_square_to_coordinates_e4(self):
        """Test coordinate calculation for e4."""
        x, y = self.executor._square_to_coordinates(chess.E4)
        
        # File 4 (e), centered at 4.5 * 60 = 270
        # Rank 3 (4th rank), visual rank 4, centered at 4.5 * 60 = 270
        self.assertEqual(x, 270)
        self.assertEqual(y, 270)
    
    def test_square_to_coordinates_flipped(self):
        """Test coordinate calculation with flipped board."""
        executor_flipped = MoveExecutor(
            self.mock_driver,
            self.mock_board,
            is_flipped=True
        )
        
        # a1 on flipped board should be at h8 position
        x, y = executor_flipped._square_to_coordinates(chess.A1)
        
        # Flipped: file 7, rank 7 -> visual rank 0
        self.assertEqual(x, 450)
        self.assertEqual(y, 30)
    
    @patch('chess_bot.src.move_executor.ActionChains')
    def test_execute_move(self, mock_action_chains):
        """Test move execution."""
        mock_actions = MagicMock()
        mock_action_chains.return_value = mock_actions
        
        move = chess.Move.from_uci('e2e4')
        self.executor.execute_move(move)
        
        # Verify ActionChains was created with driver
        mock_action_chains.assert_called_once_with(self.mock_driver)
        
        # Verify move_to_element_with_offset was called twice
        self.assertEqual(mock_actions.move_to_element_with_offset.call_count, 2)
        
        # Verify click was called twice
        self.assertEqual(mock_actions.click.call_count, 2)
        
        # Verify perform was called
        mock_actions.perform.assert_called_once()
    
    @patch('chess_bot.src.move_executor.ActionChains')
    def test_execute_uci_move(self, mock_action_chains):
        """Test UCI move execution."""
        mock_actions = MagicMock()
        mock_action_chains.return_value = mock_actions
        
        self.executor.execute_uci_move('d2d4')
        
        # Verify ActionChains was used
        mock_action_chains.assert_called_once()
        mock_actions.perform.assert_called_once()
    
    def test_update_board_state(self):
        """Test updating board state."""
        new_mock_board = Mock()
        new_mock_board.size = {'width': 640, 'height': 640}
        
        self.executor.update_board_state(new_mock_board, True)
        
        self.assertEqual(self.executor.board_element, new_mock_board)
        self.assertTrue(self.executor.is_flipped)
        self.assertEqual(self.executor.square_size, 80)  # 640 / 8


if __name__ == '__main__':
    unittest.main()
