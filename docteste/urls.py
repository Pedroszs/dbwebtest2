from django.urls import path
from . import views
from .views import exibir_contrato, gerar_contrato_especifico

urlpatterns = [
    path('', views.home, name='home'),
    path('gerar_contrato_especifico/', views.gerar_contrato_especifico, name='gerar_contrato_especifico'),# Verifique se não há erro de digitação
    path('exibir_contrato/<str:nome_arquivo>/', exibir_contrato, name='exibir_contrato'),
]

