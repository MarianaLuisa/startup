from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('iniciar_torneio/', views.iniciar_torneio, name='iniciar_torneio'),
    path('ranking/', views.ranking, name='ranking'),
    path('batalhas/', views.batalhas, name='batalhas'),
    path('batalha/<int:batalha_id>/', views.administrar_batalha, name='administrar_batalha'),
    path('campea/', views.campea, name='campea'),

    path('historico/<int:start_id>/', views.historico, name='historico'),
    path('exportar-dados/', views.exportar_dados, name='exportar_dados'),

    path('deletar/<int:id>/', views.deletar_startup, name='deletar_startup'),
    path('reiniciar/', views.reiniciar_sistema, name='reiniciar_sistema'),


]
