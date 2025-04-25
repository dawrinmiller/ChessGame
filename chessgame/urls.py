from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/new-game/', views.new_game, name='new_game'),
    path('api/game/<int:game_id>/move/', views.make_move, name='make_move'),
    path('api/game/<int:game_id>/state/', views.get_game_state, name='game_state'),
] 