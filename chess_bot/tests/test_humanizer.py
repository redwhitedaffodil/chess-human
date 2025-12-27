"""Unit tests for humanizer module."""
import unittest
import chess
import numpy as np
from unittest.mock import Mock, patch
from chess_bot.src.humanizer import Humanizer
from chess_bot.src.engine_wrapper import MoveEvaluation


class TestHumanizer(unittest.TestCase):
    """Test cases for Humanizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.humanizer = Humanizer(
            target_elo_advantage=300,
            elo_std_dev=100,
            obvious_move_threshold=300,
            min_move_time=0.5,
            max_move_time=2.0
        )
    
    def test_sample_cp_setpoint(self):
        """Test CP setpoint sampling."""
        # Sample multiple times and check distribution
        samples = [self.humanizer._sample_cp_setpoint() for _ in range(100)]
        
        # All samples should be non-negative
        self.assertTrue(all(s >= 0 for s in samples))
        
        # Mean should be roughly around target (with some variance)
        mean = np.mean(samples)
        self.assertGreater(mean, 200)  # Reasonable lower bound
        self.assertLess(mean, 400)     # Reasonable upper bound
    
    def test_is_obvious_move_large_gap(self):
        """Test obvious move detection with large score gap."""
        evaluations = [
            MoveEvaluation(move=chess.Move.from_uci('e2e4'), score=500),
            MoveEvaluation(move=chess.Move.from_uci('d2d4'), score=100),
        ]
        
        result = self.humanizer._is_obvious_move(evaluations)
        self.assertTrue(result)
    
    def test_is_obvious_move_small_gap(self):
        """Test obvious move detection with small score gap."""
        evaluations = [
            MoveEvaluation(move=chess.Move.from_uci('e2e4'), score=200),
            MoveEvaluation(move=chess.Move.from_uci('d2d4'), score=180),
        ]
        
        result = self.humanizer._is_obvious_move(evaluations)
        self.assertFalse(result)
    
    def test_is_obvious_move_avoiding_blunder(self):
        """Test obvious move detection when avoiding blunder."""
        evaluations = [
            MoveEvaluation(move=chess.Move.from_uci('e2e4'), score=100),
            MoveEvaluation(move=chess.Move.from_uci('d2d4'), score=-500),
        ]
        
        result = self.humanizer._is_obvious_move(evaluations)
        self.assertTrue(result)
    
    def test_is_obvious_move_single_move(self):
        """Test obvious move with only one legal move."""
        evaluations = [
            MoveEvaluation(move=chess.Move.from_uci('e2e4'), score=100),
        ]
        
        result = self.humanizer._is_obvious_move(evaluations)
        self.assertTrue(result)
    
    def test_select_move_obvious(self):
        """Test move selection with obvious move."""
        evaluations = [
            MoveEvaluation(move=chess.Move.from_uci('e2e4'), score=600),
            MoveEvaluation(move=chess.Move.from_uci('d2d4'), score=100),
        ]
        
        move = self.humanizer.select_move(evaluations)
        self.assertEqual(move.uci(), 'e2e4')
    
    def test_select_move_from_candidates(self):
        """Test move selection from multiple candidates."""
        evaluations = [
            MoveEvaluation(move=chess.Move.from_uci('e2e4'), score=200),
            MoveEvaluation(move=chess.Move.from_uci('d2d4'), score=190),
            MoveEvaluation(move=chess.Move.from_uci('c2c4'), score=185),
        ]
        
        # Set seed for reproducibility
        np.random.seed(42)
        
        move = self.humanizer.select_move(evaluations)
        # Should return one of the moves
        self.assertIn(move.uci(), ['e2e4', 'd2d4', 'c2c4'])
    
    def test_select_move_empty_list(self):
        """Test move selection with empty evaluation list."""
        move = self.humanizer.select_move([])
        self.assertIsNone(move)
    
    @patch('time.sleep')
    def test_add_realistic_delay(self, mock_sleep):
        """Test realistic delay addition."""
        self.humanizer.add_realistic_delay()
        
        # Verify sleep was called once
        mock_sleep.assert_called_once()
        
        # Verify delay is within bounds
        delay = mock_sleep.call_args[0][0]
        self.assertGreaterEqual(delay, 0.5)
        self.assertLessEqual(delay, 2.0)
    
    def test_should_move_with_valid_evaluations(self):
        """Test should_move with valid evaluations."""
        evaluations = [
            MoveEvaluation(move=chess.Move.from_uci('e2e4'), score=200),
        ]
        
        should_move, move = self.humanizer.should_move(evaluations)
        
        self.assertTrue(should_move)
        self.assertIsNotNone(move)
    
    def test_should_move_with_empty_evaluations(self):
        """Test should_move with empty evaluations."""
        should_move, move = self.humanizer.should_move([])
        
        self.assertFalse(should_move)
        self.assertIsNone(move)


if __name__ == '__main__':
    unittest.main()
