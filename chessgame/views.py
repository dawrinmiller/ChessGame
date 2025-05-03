from django.shortcuts import render
from django.http import JsonResponse
from .models import Game
from .ai_link import StockfishLink
import json
import logging
from django.views.decorators.csrf import csrf_exempt
import chess

# Imports and adds security exemption

logger = logging.getLogger(__name__)

stockfish = StockfishLink()

# Creates The Fish 

def index(request):
    return render(request, 'chessgame/index.html') 

# ^^^ Displays the home page of the chess game by calling to the index.html page ^^^

def new_game(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            custom_fen = data.get('fen')
            if custom_fen:
                # Validate the FEN string before creating the game
                try:
                    chess.Board(custom_fen)  # This will raise an exception if FEN is invalid
                    game = Game.objects.create(fen=custom_fen)
                except ValueError:
                    return JsonResponse({'error': 'Invalid FEN string'}, status=400)
            else:
                # Use default starting position if no FEN provided
                game = Game.objects.create(fen=chess.STARTING_FEN)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        # Handle GET request - always use default starting position
        game = Game.objects.create(fen=chess.STARTING_FEN)
    
    return JsonResponse({
        'game_id': game.id,
        'fen': game.fen,
        'status': game.status,
        'status_message': game.get_status_message(),
    })
 
# ^^^ Creates a new game inside the python database by calling id (Automatic in django), fen and status
 
def make_move(request, game_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    try:
        game = Game.objects.get(id=game_id)
        data = json.loads(request.body)
        difficulty = data.get('difficulty')
        move = data.get('move')
        print("Received move:", move)
        print("Current FEN:", game.fen)

        if not move:
            return JsonResponse({'error': 'Move is required'}, status=400)
        
        move_result = game.make_move(move)
        print("Move result:", move_result)
        if move_result:
            evaluation = stockfish.evaluate_fen(game.fen)
            # Convert evaluation to centipawns (int) if possible
            eval_cp = 0
            if isinstance(evaluation, int):
                eval_cp = evaluation
            elif isinstance(evaluation, str) and evaluation.startswith('Mate'):
                eval_cp = None  # For mate, don't adjust difficulty
            else:
                try:
                    eval_cp = int(evaluation)
                except Exception:
                    eval_cp = 0
            # Only make AI move if game isn't over
            if game.status == 'ACTIVE':
                ai_move, ai_stats = stockfish.get_dynamic_move(game.fen, eval_cp)
                game.make_move(ai_move)
                evaluation = stockfish.evaluate_fen(game.fen)
            else:
                ai_stats = {}
            return JsonResponse({
                'success': True,
                'fen': game.fen,
                'status_message': game.get_status_message(),
                'status': game.status,
                'evaluation': evaluation,
                'ai_stats': ai_stats
            })
        else:
            return JsonResponse({'error': 'Invalid move'}, status=400)
            
    except Exception as e:
        print("Exception in make_move:", e)
        return JsonResponse({'error': 'Move failed'}, status=500)

#^^^ First checks if whats input is a move(It will be) then calls to the make_move function to verify if the move is legal and if it is it moves and if its not it sends out a message "Invalid move" ^^^

def get_game_state(request, game_id):
    try:
        game = Game.objects.get(id=game_id)
        evaluation = stockfish.evaluate_fen(game.fen)
        return JsonResponse({
            'game_id': game.id,
            'fen': game.fen,
            'status': game.status,
            'evaluation': evaluation
        })
    
# ^^^ Gathers the game state after any action and updates the board accordingly for both sides and reads board status (CHECKMATE,STALEMATE,ACTIVE,CHECK etc,)  ^^^

    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    
#^^^ Catches if the game its trying to move in is not there ^^^

@csrf_exempt
def set_ai_level(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            level = data.get('level')
            if level is not None and 0 <= int(level) <= 20:
                stockfish.set_difficulty(int(level))
                return JsonResponse({'success': True, 'level': int(level)})
            else:
                return JsonResponse({'error': 'Level must be between 0 and 20'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'POST request required'}, status=400)


#View to allow the AI to change difficulty