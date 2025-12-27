"""Humanizer module for selecting chess moves in a human-like manner."""
import chess
import numpy as np
import random
import time
from typing import List, Optional, Tuple
from .engine_wrapper import MoveEvaluation


class Humanizer:
    """Implements human-like move selection and timing."""
    
    def __init__(self, 
                 target_elo_advantage: int = 300,
                 elo_std_dev: int = 100,
                 obvious_move_threshold: int = 300,
                 min_move_time: float = 0.5,
                 max_move_time: float = 2.0):
        """
        Initialize the humanizer.
        
        Args:
            target_elo_advantage: Target ELO advantage in centipawns
            elo_std_dev: Standard deviation for CP distribution
            obvious_move_threshold: CP threshold for obvious moves
            min_move_time: Minimum time before making a move (seconds)
            max_move_time: Maximum time before making a move (seconds)
        """
        self.target_elo_advantage = target_elo_advantage
        self.elo_std_dev = elo_std_dev
        self.obvious_move_threshold = obvious_move_threshold
        self.min_move_time = min_move_time
        self.max_move_time = max_move_time
    
    def _sample_cp_setpoint(self) -> int:
        """
        Sample a centipawn setpoint from normal distribution.
        
        Returns:
            Target centipawn evaluation
        """
        # Use normal distribution centered at target_elo_advantage
        cp_setpoint = int(np.random.normal(self.target_elo_advantage, self.elo_std_dev))
        # Ensure it's at least somewhat positive to avoid blunders
        return max(cp_setpoint, 0)
    
    def _is_obvious_move(self, evaluations: List[MoveEvaluation]) -> bool:
        """
        Detect if there's an obvious move (e.g., forced recapture, avoiding blunder).
        
        Args:
            evaluations: List of move evaluations sorted by score
            
        Returns:
            True if the best move is obvious
        """
        if len(evaluations) < 2:
            return True
        
        best_score = evaluations[0].score
        second_best_score = evaluations[1].score
        
        # If the best move is significantly better (>300cp), it's obvious
        if best_score - second_best_score > self.obvious_move_threshold:
            return True
        
        # If avoiding a blunder (second best is much worse)
        if second_best_score < -self.obvious_move_threshold:
            return True
        
        return False
    
    def select_move(self, evaluations: List[MoveEvaluation]) -> Optional[chess.Move]:
        """
        Select a move from the list of evaluations in a human-like way.
        
        Args:
            evaluations: List of MoveEvaluation objects sorted by score
            
        Returns:
            Selected move or None
        """
        if not evaluations:
            return None
        
        # If it's an obvious move, play the best move
        if self._is_obvious_move(evaluations):
            return evaluations[0].move
        
        # Sample a CP setpoint
        cp_setpoint = self._sample_cp_setpoint()
        
        # Find moves that maintain the target evaluation
        # We want moves where: best_score - move_score <= (best_score - cp_setpoint)
        # Simplifies to: move_score >= cp_setpoint
        
        best_score = evaluations[0].score
        
        # Select from top moves that are within acceptable range
        acceptable_moves = []
        
        for eval_move in evaluations:
            # Calculate how much worse this move is than the best
            score_drop = best_score - eval_move.score
            
            # Accept moves that don't drop below our setpoint
            # or are within reasonable range of best move
            if eval_move.score >= cp_setpoint or score_drop < self.elo_std_dev:
                acceptable_moves.append(eval_move)
        
        if not acceptable_moves:
            # If no moves meet criteria, just play the best move
            return evaluations[0].move
        
        # Randomly select from acceptable moves
        # Weight towards better moves
        weights = []
        for move_eval in acceptable_moves:
            # Higher score = higher weight
            # Use exponential weighting to prefer better moves
            weight = np.exp(move_eval.score / 200.0)  # Scale factor
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        probabilities = [w / total_weight for w in weights]
        
        # Select move based on weighted probabilities
        selected_idx = np.random.choice(len(acceptable_moves), p=probabilities)
        
        return acceptable_moves[selected_idx].move
    
    def add_realistic_delay(self):
        """Add a random delay to simulate human thinking time."""
        delay = random.uniform(self.min_move_time, self.max_move_time)
        time.sleep(delay)
    
    def should_move(self, evaluations: List[MoveEvaluation]) -> Tuple[bool, Optional[chess.Move]]:
        """
        Decide whether to make a move and which move to make.
        
        Args:
            evaluations: List of move evaluations
            
        Returns:
            Tuple of (should_move, selected_move)
        """
        if not evaluations:
            return (False, None)
        
        move = self.select_move(evaluations)
        return (move is not None, move)
