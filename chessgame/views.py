from django.shortcuts import render
from django.http import JsonResponse
from .models import Game
from .ai_link import StockfishLink
import json


stockfish = StockfishLink()

# Creates The Fish 

def index(request):
    return render(request, 'chessgame/index.html')

# ^^^ Displays the home page of the chess game by calling to the index.html page ^^^

def new_game(request):
    game = Game.objects.create()
    return JsonResponse({
        'game_id': game.id,
        'fen': game.fen,
        'status': game.status
    })
 
# ^^^ Creates a new game inside the python database by calling id (Automatic in django), fen and status
 
def make_move(request, game_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    try:
        game = Game.objects.get(id=game_id)
        data = json.loads(request.body)
        move = data.get('move')

# ^^^ Takes every new move as a POST request and uses djangos gameid to find what game to update ^^^

        if not move:
            return JsonResponse({'error': 'Move is required'}, status=400)
            
        if game.make_move(move):
            # After player's move, make AI move
            ai_move = stockfish.get_best_move(game.fen)
            game.make_move(ai_move)
            
            return JsonResponse({
                'success': True,
                'fen': game.fen,
                'status': game.status,
                'ai_move': ai_move
            })
        else:
            return JsonResponse({'error': 'Invalid move'}, status=400)
            
#^^^ First checks if whats input is a move(It will be) then calls to the make_move function to verify if the move is legal and if it is it moves and if its not it sends out a message "Invalid move" ^^^

    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
#^^^ Catches if the game its trying to move in is not there or the JSON doesnt make sense^^^

def get_game_state(request, game_id):
    try:
        game = Game.objects.get(id=game_id)
        return JsonResponse({
            'game_id': game.id,
            'fen': game.fen,
            'status': game.status
        })
    
# ^^^ Gathers the game state after any action and updates the board accordingly for both sides and reads board status (CHECKMATE,STALEMATE,ACTIVE,CHECK etc,)  ^^^

    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    
#^^^ Catches if the game its trying to move in is not there ^^^
