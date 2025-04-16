from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),

    path('ranking/', views.ranking, name='ranking'),
    path('batalhas/', views.batalhas, name='batalhas'),
    path('admin_batalha/<int:batalha_id>/', views.administrar_batalha, name='administrar_batalha'),
    path('historico/<int:start_id>/', views.historico, name='historico'),
    path('exportar/json/', views.exportar_json, name='exportar_json'),
    path('exportar/csv/', views.exportar_csv, name='exportar_csv'),
]
