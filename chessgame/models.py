from django.db import models
import chess

class Game(models.Model):
    GAME_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('WHITE_WIN', 'White Won'),
        ('BLACK_WIN', 'Black Won'),
        ('DRAW', 'Draw'),
    ]

    fen = models.CharField(max_length=100, default=chess.STARTING_FEN)
    status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
# ^^^ Grabs the current state of the board using its Fen (Starting is:"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1) and it stores it in status = models.charfield. ^^^

    def get_board(self):
        return chess.Board(self.fen)
    
# ^^^ Pulls the chessboard to reference for the code(AS AN OBJECT)^^^
    
    def is_valid_move(self, move_uci):
        board = self.get_board()
        try:
            move = chess.Move.from_uci(move_uci)
            return move in board.legal_moves
        except ValueError:
            return False
        

    def make_move(self, move_uci):
        if not self.is_valid_move(move_uci):
            return False
        
        board = self.get_board()
        try:
            # Handle promotion moves (they will include the promotion piece)
            if len(move_uci) == 5:  # e.g., "e7e8q"
                move = chess.Move.from_uci(move_uci)
            else:  # Regular moves
                move = chess.Move.from_uci(move_uci)
            
            board.push(move)
            
            # Update game status
            if board.is_checkmate():
                self.status = 'WHITE_WIN' if not board.turn else 'BLACK_WIN'
            elif board.is_stalemate() or board.is_insufficient_material() or board.is_fifty_moves() or board.is_repetition():
                self.status = 'DRAW'
            
            self.fen = board.fen()
            self.save()
            
            return {
                'success': True,
                'is_check': board.is_check(),
                'is_game_over': board.is_game_over(),
                'status': self.status
            }
        except ValueError:
            return False
    
# ^^^ Move validation(Will ensure that the move is legal and updates the game state) then makes move if it is legal^^^ 

    def get_winner(self):
        return 'WHITE' if self.status == 'WHITE_WIN' else 'BLACK' if self.status == 'BLACK_WIN' else None
    
# ^^^ Returns the winner of the game ^^^

    def get_status_message(self):
        if self.status == 'WHITE_WIN':
            return "Game over! You win!"
        elif self.status == 'BLACK_WIN':
            return "Game over! You lost!"
        elif self.status == 'DRAW':
            return "Game over! It's a draw!"
        elif self.status == 'ACTIVE':
            return "Game in progress."
        else:
            return "Unknown game status."

    