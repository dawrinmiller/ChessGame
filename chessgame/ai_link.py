import os
import chess
import chess.engine


class StockfishLink:
    """Interface for Stockfish chess engine."""

    def __init__(self, engine_path=None):
        """Initialize Stockfish, and attributes."""

        # Check if the engine path is provided, otherwise build it automatically
        self.engine_path = engine_path or self.get_engine_path()
        
        # Raise an error if the engine path does not exist
        if not os.path.exists(self.engine_path):
            raise FileNotFoundError(f"Stockfish engine not found at {self.engine_path}")
        
        # Start the Stockfish engine, set the difficulty.
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.skill_level = 10
        self.set_difficulty(self.skill_level)


    def get_engine_path(self):
        """Build engine_path automatically."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "stockfish", "stockfish.exe")
    

    # def start_engine(self):
    #     """Start Stockfish engine"""
    
    #     if not os.path.exists(self.engine_path):
    #         raise FileNotFoundError(f"Stockfish engine not found at {self.engine_path}")
    #     self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)


    def get_best_move(self, fen, time_limit=1.0):
        """
        Get a move from Stockfish using the provided FEN string.

        :param fen: FEN string representing the current board state
        :param time_limit: Time limit for Stockfish to think (in seconds)
        :return: The best move in UCI format (e.g., "e2e4")
        """

        # Send the FEN string to Stockfish and get the best move
        board = chess.Board(fen)
        self.engine.configure({"Skill Level": self.skill_level})
        result = self.engine.play(board, chess.engine.Limit(time=time_limit))
        return result.move.uci()


    def set_difficulty(self, level_or_preset):
        """
        Set the difficulty level of Stockfish: can be an integer (1-20) or a string ("easy", "medium", "hard")
        """

        presets = {
            "easy": 2,
            "medium": 10,
            "hard": 18
        }

        if isinstance(level_or_preset, str):
            self.skill_level = presets.get(level_or_preset.lower(), 10)
        else:
            self.skill_level = max(1, min(level_or_preset, 20))


    def close(self):
        """Stop Stockfish engine"""
        if self.engine:
            self.engine.quit()