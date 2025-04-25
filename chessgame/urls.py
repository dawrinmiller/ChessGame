from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_game/', views.new_game, name='new_game'),
    path('make_move/<int:game_id>/', views.make_move, name='make_move'),
    path('get_game_state/<int:game_id>/', views.get_game_state, name='get_game_state'),
] 