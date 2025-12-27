"""Stockfish engine wrapper for chess analysis."""
import chess
import chess.engine
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class MoveEvaluation:
    """Represents a move with its evaluation."""
    move: chess.Move
    score: int  # Centipawn score (positive = good for white)
    is_mate: bool = False
    mate_in: Optional[int] = None


class EngineWrapper:
    """Wrapper for Stockfish engine with multi-PV analysis."""
    
    def __init__(self, stockfish_path: str, multipv: int = 15):
        """
        Initialize the engine wrapper.
        
        Args:
            stockfish_path: Path to Stockfish executable
            multipv: Number of principal variations to analyze
        """
        self.stockfish_path = stockfish_path
        self.multipv = multipv
        self.engine: Optional[chess.engine.SimpleEngine] = None
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.quit()
    
    def start(self):
        """Start the Stockfish engine."""
        if self.engine is None:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
    
    def quit(self):
        """Quit the Stockfish engine."""
        if self.engine is not None:
            self.engine.quit()
            self.engine = None
    
    def _score_to_centipawns(self, score: chess.engine.Score, board: chess.Board) -> tuple[int, bool, Optional[int]]:
        """
        Convert a score to centipawns from current player's perspective.
        
        Args:
            score: chess.engine.Score object
            board: Current board position
            
        Returns:
            Tuple of (centipawns, is_mate, mate_in_moves)
        """
        # Get score relative to white
        pov_score = score.white()
        
        if pov_score.is_mate():
            mate_in = pov_score.mate()
            # Convert mate score to high centipawn value
            # Positive mate = winning, negative = losing
            if mate_in > 0:
                cp = 10000 - mate_in * 100
            else:
                cp = -10000 - mate_in * 100
            
            # Flip for black
            if board.turn == chess.BLACK:
                cp = -cp
                
            return (cp, True, mate_in)
        else:
            cp = pov_score.score()
            # Flip for black's perspective
            if board.turn == chess.BLACK:
                cp = -cp
            return (cp, False, None)
    
    def analyze(self, board: chess.Board, time_limit: float = 1.0) -> List[MoveEvaluation]:
        """
        Analyze position and return top moves with evaluations.
        
        Args:
            board: chess.Board to analyze
            time_limit: Time limit for analysis in seconds
            
        Returns:
            List of MoveEvaluation objects sorted by score (best first)
        """
        if self.engine is None:
            raise RuntimeError("Engine not started. Call start() first.")
        
        if board.is_game_over():
            return []
        
        # Run multi-PV analysis
        info = self.engine.analyse(
            board,
            chess.engine.Limit(time=time_limit),
            multipv=min(self.multipv, board.legal_moves.count())
        )
        
        evaluations = []
        
        # Handle both single PV and multi-PV results
        if not isinstance(info, list):
            info = [info]
        
        for pv_info in info:
            if 'pv' not in pv_info or len(pv_info['pv']) == 0:
                continue
            
            move = pv_info['pv'][0]
            score = pv_info.get('score')
            
            if score is None:
                continue
            
            cp, is_mate, mate_in = self._score_to_centipawns(score, board)
            
            evaluations.append(MoveEvaluation(
                move=move,
                score=cp,
                is_mate=is_mate,
                mate_in=mate_in
            ))
        
        # Sort by score (highest first from current player's perspective)
        evaluations.sort(key=lambda x: x.score, reverse=True)
        
        return evaluations
    
    def get_best_move(self, board: chess.Board, time_limit: float = 1.0) -> Optional[chess.Move]:
        """
        Get the best move for the current position.
        
        Args:
            board: chess.Board to analyze
            time_limit: Time limit for analysis in seconds
            
        Returns:
            Best move or None if game is over
        """
        evaluations = self.analyze(board, time_limit)
        if evaluations:
            return evaluations[0].move
        return None
