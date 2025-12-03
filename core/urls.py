from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet)
router.register(r'agenda', views.AgendaViewSet)
router.register(r'orcamentos', views.OrcamentoViewSet)
router.register(r'materiais', views.MaterialViewSet)
router.register(r'recebimentos', views.RecebimentoViewSet)
router.register(r'parcelas', views.ParcelaViewSet)
router.register(r'comissoes', views.ComissaoViewSet)
router.register(r'arquitetos', views.ArquitetoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]