from django.shortcuts import render

def index(request):
    # Renders the chess game interface template
    return render(request, 'chessgame/index.html')
